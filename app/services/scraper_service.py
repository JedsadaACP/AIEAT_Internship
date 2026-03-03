"""
AIEAT Scraper Service - News discovery and content extraction.

Ported from V11.ipynb with production-ready structure:
- Async RSS/Sitemap/Homepage discovery
- Waterfall content fetching (aiohttp -> Playwright)
- Content extraction (trafilatura/newspaper)
- Database integration (replaces CSV)
"""
import asyncio
import aiohttp
import hashlib
import json
import os
import re
import ssl
import time
import certifi
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional, Any
from urllib.parse import urlparse, urljoin

import feedparser
from bs4 import BeautifulSoup
import trafilatura
from newspaper import Article

from app.utils.logger import get_app_logger
from app.utils.exceptions import (
    ScraperError,
    SourceNotReachableError,
    ContentExtractionError,
    RSSParseError,
)
from app.services.database_manager import DatabaseManager

logger = get_app_logger(__name__)


class ScraperConfig:
    """Load and manage scraper configuration."""
    
    def __init__(self, config_dir: str = None, db=None):
        if config_dir is None:
            from app.utils.paths import get_config_dir
            config_dir = get_config_dir()
        
        self.config_dir = config_dir
        self._db = db
        self._load_configs()
    
    def _load_configs(self):
        """Load all configuration files."""
        # Scraper config
        with open(os.path.join(self.config_dir, "scraper_config.json"), 'r') as f:
            self.settings = json.load(f)
        
        # Keywords from DB ONLY (No JSON fallback)
        try:
            db = self._db
            if db is None:
                from app.services.database_manager import DatabaseManager
                db = DatabaseManager()
            self.keywords = db.get_keywords()
            if not self.keywords:
                logger.warning("No keywords in DB. Scraper will not match any articles.")
                self.keywords = []
            else:
                logger.info(f"Loaded {len(self.keywords)} keywords from DB")
        except Exception as e:
            logger.error(f"Failed to load keywords from DB: {e}")
            self.keywords = []
        
        # Paywall signals
        with open(os.path.join(self.config_dir, "paywall_signals.json"), 'r') as f:
            self.paywall = json.load(f)
        
        # Sources from DB ONLY (No JSON fallback)
        try:
            db = self._db
            if db is None:
                from app.services.database_manager import DatabaseManager
                db = DatabaseManager()
            db_sources = db.get_all_sources()
            if db_sources:
                self.sources = [{'name': s['domain_name'], 'url': s['base_url']} for s in db_sources]
                logger.info(f"Loaded {len(self.sources)} sources from DB")
            else:
                logger.warning("No sources in DB. Scraper has nothing to scrape.")
                self.sources = []
        except Exception as e:
            logger.error(f"Failed to load sources from DB: {e}")
            self.sources = []
        
        # Load date_limit_days from DB profile (override JSON config)
        try:
            db = self._db
            if db is None:
                from app.services.database_manager import DatabaseManager
                db = DatabaseManager()
            profile = db.get_system_profile()
            if profile and profile.get('date_limit_days'):
                self.settings['date_limit_days'] = profile['date_limit_days']
                logger.info(f"Date limit from DB: {profile['date_limit_days']} days")
        except Exception as e:
            logger.warning(f"DB date_limit_days failed ({e}), using JSON fallback")
        
        logger.info(f"Config ready: {len(self.sources)} sources, {len(self.keywords)} keywords")


class ContentValidator:
    """Validate and filter content."""
    
    def __init__(self, config: ScraperConfig):
        self.config = config
    
    def is_paywall(self, content: str) -> bool:
        """Check if content contains paywall signals."""
        if len(content) > self.config.paywall.get('max_length_for_check', 5000):
            return False
        content_lower = content.lower()
        for signal in self.config.paywall.get('signals', []):
            if signal.lower() in content_lower:
                return True
        return False
    
    def matches_keywords(self, text: str) -> List[str]:
        """Check if text matches any keywords."""
        text_lower = text.lower()
        matched = []
        for kw in self.config.keywords:
            kw_lower = kw.lower()
            if kw_lower == "a.i.":
                if "a.i." in text_lower or re.search(r'\bai\b', text_lower):
                    matched.append(kw)
            else:
                if kw_lower in text_lower:
                    matched.append(kw)
        return matched
    
    def is_same_domain(self, article_url: str, source_url: str) -> bool:
        """Check if article is from same domain as source."""
        article = urlparse(article_url).netloc.replace('www.', '')
        source = urlparse(source_url).netloc.replace('www.', '')
        return article == source or article.endswith('.' + source)
    
    @staticmethod
    def clean_text(text: str) -> str:
        """Clean text by removing extra whitespace."""
        if not text:
            return ""
        return re.sub(r'\s+', ' ', text).strip()


class ArticleDiscoverer:
    """Discover article URLs from various sources."""
    
    RSS_PATHS = [
        '/feed', '/rss', '/rss.xml', '/feed.xml', '/atom.xml',
        '/index.xml', '/feed/', '/rss/',
        '/news/feed', '/news/rss', '/news/rss.xml',
        '/tech/feed', '/technology/feed', '/technology/rss.xml',
        '/blog/feed', '/blog/rss',
        '/feeds/posts/default', '/feed/atom',
        '/.rss', '/rss/news'
    ]
    
    SITEMAP_PATHS = [
        '/sitemap.xml', '/sitemap_index.xml', 
        '/news-sitemap.xml', '/sitemap-news.xml', '/post-sitemap.xml'
    ]
    
    def __init__(self, config: ScraperConfig):
        self.config = config
    
    async def discover_rss(self, session: aiohttp.ClientSession, base_url: str) -> Tuple[List[Tuple[str, str]], str]:
        """Discover articles via RSS feeds."""
        for path in self.RSS_PATHS:
            feed_url = urljoin(base_url, path)
            try:
                async with session.get(feed_url, timeout=5) as r:
                    if r.status == 200:
                        content = await r.text()
                        if '<?xml' in content[:100] or '<rss' in content[:100] or '<feed' in content[:100]:
                            feed = feedparser.parse(content)
                            found_urls = []
                            for entry in feed.entries:
                                if hasattr(entry, 'link'):
                                    found_urls.append((entry.link, getattr(entry, 'published', '')))
                            if found_urls:
                                return found_urls, "rss"
            except Exception as e:
                logger.debug(f"RSS probe failed for {feed_url}: {e}")
                continue
        return [], "None"
    
    async def discover_sitemap(self, session: aiohttp.ClientSession, base_url: str) -> Tuple[List[Tuple[str, str]], str]:
        """Discover articles via sitemap."""
        articles = []
        max_articles = self.config.settings.get('max_articles_per_source', 50)
        
        for path in self.SITEMAP_PATHS:
            sitemap_url = urljoin(base_url, path)
            try:
                async with session.get(sitemap_url, timeout=10) as r:
                    if r.status == 200:
                        text = await r.text()
                        if '<urlset' not in text and '<sitemapindex' not in text:
                            continue
                        soup = BeautifulSoup(text, 'xml')
                        
                        # Handle sitemap index
                        for sitemap in soup.find_all('sitemap')[:3]:
                            loc = sitemap.find('loc')
                            if loc:
                                try:
                                    async with session.get(loc.text, timeout=10) as sub_r:
                                        if sub_r.status == 200:
                                            sub_text = await sub_r.text()
                                            sub_soup = BeautifulSoup(sub_text, 'xml')
                                            for url_tag in sub_soup.find_all('url')[:50]:
                                                loc_tag = url_tag.find('loc')
                                                lastmod = url_tag.find('lastmod')
                                                if loc_tag:
                                                    articles.append((loc_tag.text, lastmod.text if lastmod else ''))
                                except Exception as e:
                                    logger.debug(f"Sitemap sub-fetch failed for {loc.text}: {e}")
                                    pass
                        
                        # Direct URL list
                        for url_tag in soup.find_all('url')[:50]:
                            loc = url_tag.find('loc')
                            lastmod = url_tag.find('lastmod')
                            if loc:
                                articles.append((loc.text, lastmod.text if lastmod else ''))
                        
                        if articles:
                            return articles[:max_articles], "sitemap"
            except Exception as e:
                logger.debug(f"Sitemap probe failed for {sitemap_url}: {e}")
                continue
        return [], "None"
    
    async def discover_homepage(self, session: aiohttp.ClientSession, base_url: str) -> Tuple[List[Tuple[str, str]], str]:
        """Discover articles from homepage links."""
        max_articles = self.config.settings.get('max_articles_per_source', 50)
        try:
            async with session.get(base_url, timeout=10) as r:
                if r.status == 200:
                    html = await r.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    urls = []
                    for a in soup.find_all('a', href=True):
                        full_url = urljoin(base_url, a['href'])
                        if base_url in full_url and len(full_url) > len(base_url) + 10:
                            urls.append((full_url, ''))
                    return list(set(urls))[:max_articles], "homepage"
        except Exception:
            pass
        return [], "None"
    
    async def discover(self, session: aiohttp.ClientSession, base_url: str) -> Tuple[List[Tuple[str, str]], str]:
        """Try all discovery methods."""
        # Try RSS first (fastest)
        links, method = await self.discover_rss(session, base_url)
        if links:
            return links, method
        
        # Try sitemap
        links, method = await self.discover_sitemap(session, base_url)
        if links:
            return links, method
        
        # Fall back to homepage
        return await self.discover_homepage(session, base_url)


class ContentExtractor:
    """Extract content from HTML."""
    
    # CSS/HTML garbage patterns to remove from author names
    CSS_GARBAGE_PATTERNS = [
        r'--[A-Za-z-]+',  # CSS custom properties like --c-author-card
        r'\b(Align-Items|Display|Flex|Gap|Var|Border|Background|Margin|Padding|Width|Height|Color|Font|Media|Min-Width|Max-Width)\b',
        r'\b(Center|Solid|None|Important|First-Child|Shrink)\b',
        r'\.Post-[A-Za-z-]+',  # CSS class selectors
        r'\b(Li|Div|Span|Ul|Ol|Nav|Header|Footer|Section|Article)\b',  # Common HTML element names leaked
    ]
    
    @staticmethod
    def clean_author(author: str) -> str:
        """Clean CSS/HTML garbage from author name."""
        if not author:
            return ''
        
        # Remove CSS garbage patterns
        for pattern in ContentExtractor.CSS_GARBAGE_PATTERNS:
            author = re.sub(pattern, '', author, flags=re.IGNORECASE)
        
        # Split by comma and clean each part
        parts = [p.strip() for p in author.split(',')]
        
        # Filter out empty parts and parts that look like garbage
        clean_parts = []
        for part in parts:
            # Skip empty or too short
            if len(part) < 2:
                continue
            # Skip if looks like CSS (has too many capital letters in middle)
            if re.search(r'[A-Z]{2,}[a-z]+[A-Z]', part):
                continue
            # Skip if starts with special chars
            if re.match(r'^[.\-_#]', part):
                continue
            # Keep valid names (basic check: has at least one letter)
            if re.search(r'[a-zA-Z]', part):
                clean_parts.append(part.strip())
        
        # Limit to first 3 authors
        clean_parts = clean_parts[:3]
        
        return ', '.join(clean_parts) if clean_parts else ''
    
    @staticmethod
    def extract(html: str, url: str) -> Tuple[str, str, str]:
        """Extract title, author, and content from HTML."""
        title = ''
        author = ''
        text = ''
        
        # Try trafilatura first
        try:
            result = trafilatura.bare_extraction(html)
            if result:
                text = result.get('text', '')
                title = result.get('title', '')
                author = result.get('author', '')
        except Exception as e:
            logger.error(f"Trafilatura extraction failed: {e}")
        
        # Fall back to newspaper if needed
        if not text or len(text) < 200:
            try:
                article = Article(url)
                article.set_html(html)
                article.parse()
                text = article.text
                title = title or article.title
                author = author or (', '.join(article.authors) if article.authors else '')
            except Exception as e:
                logger.error(f"Newspaper extraction failed: {e}")
        
        # Clean author name
        author = ContentExtractor.clean_author(author)
        
        return text, title, author


class ScraperService:
    """Main scraper service orchestrating all components."""
    
    def __init__(self, db: DatabaseManager = None, config: ScraperConfig = None):
        self.db = db or DatabaseManager()
        self.config = config or ScraperConfig(db=self.db)
        self.validator = ContentValidator(self.config)
        self.discoverer = ArticleDiscoverer(self.config)
        self.extractor = ContentExtractor()
        
        # Stats
        self.stats = {
            'total_sources': 0,
            'successful_sources': 0,
            'total_articles': 0,
            'new_articles': 0,
            'duplicates': 0,
            'errors': 0
        }
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date string to datetime."""
        if not date_str:
            return None
        formats = [
            '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d',
            '%a, %d %b %Y %H:%M:%S', '%a, %d %b %Y'
        ]
        for fmt in formats:
            try:
                return datetime.strptime(str(date_str)[:25].replace(' GMT', '').replace(' +0000', ''), fmt)
            except ValueError:
                pass
        return None
    
    def _is_too_old(self, date_str: str) -> bool:
        """Check if article is too old."""
        dt = self._parse_date(date_str)
        if not dt:
            return False  # Don't filter if no date
        limit_days = self.config.settings.get('date_limit_days', 14)
        return dt < datetime.now() - timedelta(days=limit_days)
    
    async def _fetch_content(self, session: aiohttp.ClientSession, url: str) -> Tuple[Optional[str], str]:
        """Fetch content with retry logic."""
        max_retries = self.config.settings.get('max_retries', 3)
        timeout = self.config.settings.get('request_timeout', 10)
        
        for attempt in range(max_retries):
            try:
                async with session.get(url, timeout=timeout) as response:
                    if response.status == 200:
                        return await response.text(), "fast"
                    elif response.status == 429:
                        await asyncio.sleep(2 ** attempt)
            except Exception as e:
                logger.error(f"Fetch failed for {url}: {e}")
                await asyncio.sleep(1)
        
        return None, "failed"
    
    async def _process_source(self, session: aiohttp.ClientSession, source: Dict) -> int:
        """Process a single source and return count of new articles."""
        name = source['name']
        url = source['url']
        new_count = 0
        start_time = time.time()
        
        time_limit = self.config.settings.get('time_limit_per_source', 60)
        max_articles = self.config.settings.get('max_articles_per_source', 50)
        min_content = self.config.settings.get('min_content_length', 200)
        
        # Discover articles
        try:
            links, method = await self.discoverer.discover(session, url)
        except Exception as e:
            logger.warning(f"Discovery failed for {name}: {e}")
            self.stats['errors'] += 1
            return 0
        
        if not links:
            logger.debug(f"No articles found for {name}")
            return 0
        
        logger.info(f"Found {len(links)} links for {name} via {method}")
        
        # Process each link
        for link, date in links[:max_articles]:
            # Time limit check
            if time.time() - start_time > time_limit:
                break
            
            # Date filter
            if self._is_too_old(date):
                continue
            
            # Domain check
            if not self.validator.is_same_domain(link, url):
                continue
            
            # Check if already exists
            url_hash = DatabaseManager.generate_url_hash(link)
            if self.db.article_exists(url_hash):
                self.stats['duplicates'] += 1
                continue
            
            # Fetch content
            html, fetch_method = await self._fetch_content(session, link)
            if not html:
                continue
            
            # Paywall check
            if self.validator.is_paywall(html):
                continue
            
            # Extract content
            text, headline, author = self.extractor.extract(html, link)
            if not text or len(text) < min_content:
                continue
            
            text = self.validator.clean_text(text)
            
            # Keyword check
            keywords = self.validator.matches_keywords(text)
            if not keywords:
                continue
            
            # Save to database
            try:
                article_id = self.db.insert_article(
                    source_name=name,
                    source_url=url,
                    headline=headline or text[:100].replace('\n', ' ') + '...',
                    article_url=link,
                    content=text,
                    published_at=date or None,
                    author_name=author or None
                )
                if article_id:
                    # Save tags!
                    self.db.add_article_tags(article_id, keywords)
                    
                    new_count += 1
                    self.stats['new_articles'] += 1
                    logger.debug(f"Saved: {headline[:50]}...")
                    
                    # Check article save cap (configurable)
                    max_save = self.config.settings.get('max_articles_saved_per_source', 30)
                    if new_count >= max_save:
                        break
            except Exception as e:
                logger.error(f"Failed to save article: {e}")
                self.stats['errors'] += 1
        
        if new_count == 0 and links:
            logger.info(f"{name}: Found {len(links)} links, but 0 passed filters (Check keywords/dates)")
        
        if new_count > 0:
            self.stats['successful_sources'] += 1
        
        self.stats['total_articles'] += new_count
        return new_count
    
    async def run(self, sources: List[Dict] = None, progress_callback = None) -> Dict:
        """
        Run the scraper.
        
        Args:
            sources: List of sources to scrape. If None, uses all from config.
            progress_callback: Optional callback(current, total, source_name)
        
        Returns:
            Stats dictionary
        """
        sources = sources or self.config.sources
        self.stats = {
            'total_sources': len(sources),
            'successful_sources': 0,
            'total_articles': 0,
            'new_articles': 0,
            'duplicates': 0,
            'errors': 0,
            'start_time': datetime.now().isoformat(),
        }
        
        start_time = time.time()
        concurrent = self.config.settings.get('concurrent_sources', 10)
        batch_size = self.config.settings.get('batch_size', 5)
        user_agent = self.config.settings.get('user_agent', 'Mozilla/5.0')
        
        logger.info(f"Starting scrape of {len(sources)} sources (batch={batch_size})")
        
        # Add User-Agent header to avoid 403 errors
        headers = {"User-Agent": user_agent}
        
        # Ensure SSL works in frozen executable
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        
        # Optimized connection pooling
        connector = aiohttp.TCPConnector(
            limit=concurrent * 2,     # Total connection pool
            limit_per_host=3,         # Max per host
            ttl_dns_cache=300,        # DNS cache 5 min
            enable_cleanup_closed=True,
            ssl=ssl_context
        )
        
        # Faster timeout settings
        timeout = aiohttp.ClientTimeout(
            total=self.config.settings.get('request_timeout', 8),
            connect=3,
            sock_read=5
        )
        
        async with aiohttp.ClientSession(connector=connector, headers=headers, timeout=timeout) as session:
            # Process in batches for speed
            for i in range(0, len(sources), batch_size):
                batch = sources[i:i + batch_size]
                
                # Build progress message with first source name
                first_source = batch[0].get('name', batch[0].get('domain_name', 'unknown'))
                if len(batch) > 1:
                    progress_msg = f"{first_source} + {len(batch)-1} more"
                else:
                    progress_msg = first_source
                
                # Call progress callback
                if progress_callback:
                    current_count = min(i + batch_size, len(sources))
                    should_continue = progress_callback(current_count, len(sources), progress_msg)
                    if should_continue is False:
                        logger.info("Scraper stopped by user")
                        break
                
                # Run batch concurrently
                tasks = [self._process_source(session, source) for source in batch]
                await asyncio.gather(*tasks)
        
        elapsed = time.time() - start_time
        self.stats['elapsed_seconds'] = round(elapsed, 2)
        self.stats['elapsed_minutes'] = round(elapsed / 60, 2)
        self.stats['end_time'] = datetime.now().isoformat()
        
        logger.info(
            f"Scrape complete: {self.stats['new_articles']} new articles "
            f"from {self.stats['successful_sources']}/{len(sources)} sources "
            f"in {self.stats['elapsed_minutes']:.2f} min"
        )
        
        return self.stats


# CLI entry point
if __name__ == "__main__":
    import sys
    
    async def main():
        scraper = ScraperService()
        
        def progress(current, total, name):
            print(f"\r[{current}/{total}] {name}...", end="", flush=True)
        
        stats = await scraper.run(progress_callback=progress)
        print()  # Newline after progress
        print(f"\n📊 Results:")
        print(f"  New articles: {stats['new_articles']}")
        print(f"  Sources with articles: {stats['successful_sources']}/{stats['total_sources']}")
        print(f"  Duplicates skipped: {stats['duplicates']}")
        print(f"  Errors: {stats['errors']}")
        print(f"  Time: {stats['elapsed_minutes']:.2f} minutes")
    
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    asyncio.run(main())
