"""
Script to create V8 Scraper Notebook with proper JSON structure.
"""
import json

# Cell source code as strings
cell1_markdown = """# 🚀 V8 News Scraper - Parallel Processing Architecture

**Version:** 8.0  
**Features:**
- ⚡ Parallel source processing (ThreadPoolExecutor)
- 📁 Sources loaded from JSON configuration file
- 📊 tqdm progress bars for all operations
- 🔇 Silent fail with error logging
- 📄 Clean CSV output"""

cell2_imports = """# ============================================================================
# CELL 1: IMPORTS
# ============================================================================
import json, re, os, logging, hashlib, time, warnings
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field, asdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urljoin, urlparse
warnings.filterwarnings('ignore')

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import feedparser
from bs4 import BeautifulSoup
import pandas as pd
from tqdm.notebook import tqdm
from newspaper import Article, Config as NewspaperConfig

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[logging.FileHandler('scraper_v8.log', mode='w')]
)
logger = logging.getLogger(__name__)
print("✅ All imports loaded successfully")"""

cell3_config = '''# ============================================================================
# CELL 2: CONFIGURATION (User-Editable)
# ============================================================================

SOURCES_FILE = "sources.json"
with open(SOURCES_FILE, 'r') as f:
    sources_data = json.load(f)
    SOURCES = [(s['name'], s['url']) for s in sources_data['sources']]
print(f"📰 Loaded {len(SOURCES)} sources from {SOURCES_FILE}")

KEYWORDS = [
    "artificial intelligence", "machine learning", "deep learning", "neural network",
    "generative ai", "large language model", "llm", "chatgpt", "gpt-4", "gpt-5",
    "claude", "gemini", "copilot", "midjourney", "stable diffusion", "dall-e",
    "openai", "anthropic", "google ai", "meta ai", "microsoft ai",
    "semiconductor", "chip", "nvidia", "amd", "intel", "tsmc", "gpu", "cpu", "tpu",
    "arm", "qualcomm", "asml", "samsung semiconductor",
    "tech industry", "silicon valley", "startup", "venture capital", "ipo",
    "big tech", "faang", "tech layoff", "tech regulation",
    "renewable energy", "solar", "wind energy", "battery", "ev", "electric vehicle",
    "clean energy", "climate tech", "carbon capture", "nuclear energy", "fusion",
    "ai regulation", "tech policy", "antitrust", "data privacy", "gdpr",
    "ai safety", "ai ethics", "ai governance"
]

CONFIG = {
    "date_range_days": 7,
    "timeout_seconds": 10,
    "retry_count": 1,
    "max_workers": None,
    "article_workers": 8,
    "rss_paths": ["/feed", "/rss", "/feeds/all.rss", "/rss.xml", "/feed.xml", "/atom.xml", "/index.xml", "/news/feed", "/blog/feed"],
    "api_paths": ["/api/articles", "/api/posts", "/api/news", "/api/v1/articles"],
    "min_content_length": 200,
    "min_title_length": 10,
    "time_budget_rss": 30,
    "time_budget_api": 20,
    "time_budget_html": 60,
    "time_budget_homepage": 90,
    "output_file": "scraped_news_v8.csv",
    "telemetry_file": "scraping_telemetry_v8.csv"
}

if CONFIG["max_workers"] is None:
    CONFIG["max_workers"] = min(os.cpu_count() * 2, 16)

print(f"⚙️  Config: {CONFIG['max_workers']} workers, {CONFIG['date_range_days']} days, {CONFIG['timeout_seconds']}s timeout")'''

cell4_utilities = '''# ============================================================================
# CELL 3: CORE UTILITIES
# ============================================================================

@dataclass
class ScrapedArticle:
    title: str
    url: str
    published_date: Optional[str] = None
    content: str = ""
    source_name: str = ""
    source_url: str = ""
    method: str = ""
    keywords_matched: List[str] = field(default_factory=list)
    scrape_timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

class HTTPClient:
    def __init__(self, timeout: int = 10, retries: int = 1):
        self.timeout = timeout
        self.session = requests.Session()
        retry_strategy = Retry(total=retries, backoff_factor=0.5, status_forcelist=[429, 500, 502, 503, 504])
        adapter = HTTPAdapter(max_retries=retry_strategy, pool_connections=20, pool_maxsize=20)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        })
    
    def get(self, url: str, **kwargs) -> Optional[requests.Response]:
        try:
            response = self.session.get(url, timeout=self.timeout, **kwargs)
            response.raise_for_status()
            return response
        except:
            return None
    
    def get_json(self, url: str) -> Optional[Dict]:
        try:
            response = self.get(url, headers={'Accept': 'application/json'})
            return response.json() if response else None
        except:
            return None

http = HTTPClient(timeout=CONFIG["timeout_seconds"], retries=CONFIG["retry_count"])

def parse_date(date_input: Any) -> Optional[datetime]:
    if date_input is None:
        return None
    if hasattr(date_input, 'tm_year'):
        try:
            return datetime(*date_input[:6])
        except:
            return None
    if isinstance(date_input, datetime):
        return date_input
    if isinstance(date_input, str):
        for fmt in ["%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%d %b %Y", "%B %d, %Y"]:
            try:
                clean_date = re.sub(r'[+-]\\d{2}:\\d{2}$', '', date_input).replace('Z', '').strip()
                return datetime.strptime(clean_date, fmt)
            except:
                continue
    return None

def clean_text(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r'\\s+', ' ', text)
    for pattern in [r'Share this article.*', r'Subscribe to.*', r'Advertisement', r'ADVERTISEMENT']:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)
    return text.strip()

def is_within_date_range(date: Optional[datetime], days: int) -> bool:
    if date is None:
        return True
    return date >= datetime.now() - timedelta(days=days)

def matches_keywords(text: str, keywords: List[str]) -> List[str]:
    if not text:
        return []
    text_lower = text.lower()
    return [kw for kw in keywords if kw.lower() in text_lower]

def generate_article_hash(url: str, title: str) -> str:
    return hashlib.md5(f"{url.lower().strip()}{title.lower().strip()}".encode()).hexdigest()

print("✅ Core utilities loaded")'''

cell5_discovery = '''# ============================================================================
# CELL 4: DISCOVERY MODULE
# ============================================================================

def discover_rss_feed(base_url: str, paths: List[str]) -> Optional[str]:
    for path in paths:
        feed_url = urljoin(base_url, path)
        response = http.get(feed_url)
        if response and response.status_code == 200:
            content_type = response.headers.get('content-type', '').lower()
            if 'xml' in content_type or 'rss' in content_type:
                feed = feedparser.parse(response.content)
                if feed.entries:
                    return feed_url
    response = http.get(base_url)
    if response:
        soup = BeautifulSoup(response.text, 'html.parser')
        rss_link = soup.find('link', type=re.compile(r'(rss|atom)', re.I))
        if rss_link and rss_link.get('href'):
            return urljoin(base_url, rss_link['href'])
    return None

def discover_api_endpoint(base_url: str, paths: List[str]) -> Optional[str]:
    for path in paths:
        api_url = urljoin(base_url, path)
        data = http.get_json(api_url)
        if data and isinstance(data, (list, dict)):
            items = data if isinstance(data, list) else data.get('articles', data.get('posts', data.get('items', [])))
            if items:
                return api_url
    return None

print("✅ Discovery module loaded")'''

cell6_scrapers = '''# ============================================================================
# CELL 5: SCRAPERS
# ============================================================================

newspaper_config = NewspaperConfig()
newspaper_config.browser_user_agent = http.session.headers['User-Agent']
newspaper_config.request_timeout = CONFIG["timeout_seconds"]
newspaper_config.fetch_images = False
newspaper_config.memoize_articles = False

def fetch_article_content(url: str) -> Tuple[str, str]:
    try:
        article = Article(url, config=newspaper_config)
        article.download()
        article.parse()
        return article.title or "", clean_text(article.text or "")
    except:
        return "", ""

def scrape_rss(feed_url: str, source_name: str, source_url: str, time_budget: float) -> List[ScrapedArticle]:
    articles = []
    start_time = time.time()
    try:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries[:30]:
            if time.time() - start_time > time_budget:
                break
            title = entry.get('title', '')
            url = entry.get('link', '')
            if not url or not title:
                continue
            pub_date = parse_date(entry.get('published_parsed') or entry.get('updated_parsed'))
            content = entry.get('summary', '') or entry.get('description', '')
            if len(content) < CONFIG["min_content_length"]:
                _, content = fetch_article_content(url)
            articles.append(ScrapedArticle(title=title, url=url, published_date=pub_date.isoformat() if pub_date else None,
                content=clean_text(content), source_name=source_name, source_url=source_url, method="rss"))
    except Exception as e:
        logger.warning(f"RSS scrape failed for {source_name}: {e}")
    return articles

def scrape_api(api_url: str, source_name: str, source_url: str, time_budget: float) -> List[ScrapedArticle]:
    articles = []
    start_time = time.time()
    try:
        data = http.get_json(api_url)
        if not data:
            return []
        items = data if isinstance(data, list) else data.get('articles', data.get('posts', data.get('items', data.get('data', []))))
        for item in items[:30]:
            if time.time() - start_time > time_budget:
                break
            title = item.get('title') or item.get('headline', '')
            url = item.get('url') or item.get('link', '')
            if not url or not title:
                continue
            if not url.startswith('http'):
                url = urljoin(source_url, url)
            pub_date = parse_date(item.get('published_at') or item.get('date') or item.get('publishedAt'))
            content = item.get('content') or item.get('body') or item.get('description', '')
            if len(content) < CONFIG["min_content_length"]:
                _, content = fetch_article_content(url)
            articles.append(ScrapedArticle(title=title, url=url, published_date=pub_date.isoformat() if pub_date else None,
                content=clean_text(content), source_name=source_name, source_url=source_url, method="api"))
    except Exception as e:
        logger.warning(f"API scrape failed for {source_name}: {e}")
    return articles

def scrape_html(base_url: str, source_name: str, time_budget: float) -> List[ScrapedArticle]:
    articles = []
    start_time = time.time()
    try:
        response = http.get(base_url)
        if not response:
            return []
        soup = BeautifulSoup(response.text, 'html.parser')
        seen_urls = set()
        links = []
        for selector in ['article a[href]', '.article a[href]', '.post a[href]', 'a[href*="/article/"]', 'a[href*="/news/"]']:
            for link in soup.select(selector):
                href = link.get('href', '')
                if href and href not in seen_urls:
                    full_url = urljoin(base_url, href)
                    if urlparse(full_url).netloc == urlparse(base_url).netloc:
                        seen_urls.add(href)
                        links.append(full_url)
        
        def fetch_one(url):
            if time.time() - start_time > time_budget:
                return None
            title, content = fetch_article_content(url)
            if title and len(content) >= CONFIG["min_content_length"]:
                return ScrapedArticle(title=title, url=url, content=content, source_name=source_name, source_url=base_url, method="html")
            return None
        
        with ThreadPoolExecutor(max_workers=CONFIG["article_workers"]) as executor:
            for result in executor.map(fetch_one, links[:20]):
                if result:
                    articles.append(result)
    except Exception as e:
        logger.warning(f"HTML scrape failed for {source_name}: {e}")
    return articles

def scrape_homepage(base_url: str, source_name: str, time_budget: float) -> List[ScrapedArticle]:
    articles = []
    start_time = time.time()
    try:
        response = http.get(base_url)
        if not response:
            return []
        soup = BeautifulSoup(response.text, 'html.parser')
        article_urls = []
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            full_url = urljoin(base_url, href)
            parsed = urlparse(full_url)
            if parsed.netloc != urlparse(base_url).netloc:
                continue
            path = parsed.path.lower()
            if any(skip in path for skip in ['/tag/', '/category/', '/author/', '/login', '/signup']):
                continue
            if any(pattern in path for pattern in ['/20', '/article', '/news/', '/story/', '/post/']):
                if full_url not in article_urls:
                    article_urls.append(full_url)
        
        def fetch_one(url):
            if time.time() - start_time > time_budget:
                return None
            title, content = fetch_article_content(url)
            if title and len(content) >= CONFIG["min_content_length"]:
                return ScrapedArticle(title=title, url=url, content=content, source_name=source_name, source_url=base_url, method="homepage")
            return None
        
        with ThreadPoolExecutor(max_workers=CONFIG["article_workers"]) as executor:
            for result in executor.map(fetch_one, article_urls[:25]):
                if result:
                    articles.append(result)
    except Exception as e:
        logger.warning(f"Homepage scrape failed for {source_name}: {e}")
    return articles

print("✅ Scraper functions loaded")'''

cell7_filters = '''# ============================================================================
# CELL 6: FILTERS
# ============================================================================

def filter_by_date(articles: List[ScrapedArticle], days: int) -> List[ScrapedArticle]:
    return [a for a in articles if is_within_date_range(parse_date(a.published_date), days)]

def filter_by_keywords(articles: List[ScrapedArticle], keywords: List[str]) -> List[ScrapedArticle]:
    filtered = []
    for article in articles:
        matched = matches_keywords(f"{article.title} {article.content}", keywords)
        if matched:
            article.keywords_matched = matched
            filtered.append(article)
    return filtered

def filter_by_quality(articles: List[ScrapedArticle], min_content: int = 200, min_title: int = 10) -> List[ScrapedArticle]:
    return [a for a in articles if len(a.content) >= min_content and len(a.title) >= min_title]

def deduplicate(articles: List[ScrapedArticle]) -> List[ScrapedArticle]:
    seen = set()
    unique = []
    for article in articles:
        h = generate_article_hash(article.url, article.title)
        if h not in seen:
            seen.add(h)
            unique.append(article)
    return unique

def apply_filters(articles, date_range_days=7, keywords=None, min_content=200):
    articles = filter_by_date(articles, date_range_days)
    if keywords:
        articles = filter_by_keywords(articles, keywords)
    articles = filter_by_quality(articles, min_content_length=min_content)
    return deduplicate(articles)

print("✅ Filter functions loaded")'''

cell8_orchestrator = '''# ============================================================================
# CELL 7: ORCHESTRATOR
# ============================================================================

@dataclass
class SourceResult:
    source_name: str
    source_url: str
    method_used: str
    articles_found: int
    articles_after_filter: int
    elapsed_seconds: float
    success: bool
    error: Optional[str] = None

def scrape_source(source_name: str, source_url: str) -> Tuple[List[ScrapedArticle], SourceResult]:
    start_time = time.time()
    articles = []
    method_used = "none"
    error = None
    
    try:
        # Try RSS
        rss_url = discover_rss_feed(source_url, CONFIG["rss_paths"])
        if rss_url:
            articles = scrape_rss(rss_url, source_name, source_url, CONFIG["time_budget_rss"])
            if articles:
                method_used = "rss"
        
        # Try API
        if not articles:
            api_url = discover_api_endpoint(source_url, CONFIG["api_paths"])
            if api_url:
                articles = scrape_api(api_url, source_name, source_url, CONFIG["time_budget_api"])
                if articles:
                    method_used = "api"
        
        # Try HTML
        if not articles:
            articles = scrape_html(source_url, source_name, CONFIG["time_budget_html"])
            if articles:
                method_used = "html"
        
        # Try Homepage
        if not articles:
            articles = scrape_homepage(source_url, source_name, CONFIG["time_budget_homepage"])
            if articles:
                method_used = "homepage"
    except Exception as e:
        error = str(e)
        logger.error(f"Error scraping {source_name}: {e}")
    
    raw_count = len(articles)
    articles = apply_filters(articles, CONFIG["date_range_days"], KEYWORDS, CONFIG["min_content_length"])
    
    return articles, SourceResult(
        source_name=source_name, source_url=source_url, method_used=method_used,
        articles_found=raw_count, articles_after_filter=len(articles),
        elapsed_seconds=round(time.time() - start_time, 2), success=len(articles) > 0, error=error
    )

def scrape_all_sources_parallel(sources, max_workers):
    all_articles = []
    all_results = []
    
    print(f"\\n🚀 Starting parallel scrape with {max_workers} workers...")
    print(f"📰 Processing {len(sources)} sources\\n")
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_source = {executor.submit(scrape_source, name, url): (name, url) for name, url in sources}
        
        with tqdm(total=len(sources), desc="Scraping sources", unit="source") as pbar:
            for future in as_completed(future_to_source):
                source_name, source_url = future_to_source[future]
                try:
                    articles, result = future.result()
                    all_articles.extend(articles)
                    all_results.append(result)
                    status = "✓" if result.success else "✗"
                    pbar.set_postfix_str(f"{status} {source_name[:20]}: {result.articles_after_filter}")
                except Exception as e:
                    logger.error(f"Failed {source_name}: {e}")
                    all_results.append(SourceResult(source_name, source_url, "none", 0, 0, 0, False, str(e)))
                pbar.update(1)
    
    return deduplicate(all_articles), all_results

print("✅ Orchestrator loaded")'''

cell9_main = '''# ============================================================================
# CELL 8: MAIN EXECUTION
# ============================================================================

print("=" * 70)
print("🚀 V8 NEWS SCRAPER - PARALLEL EXECUTION")
print("=" * 70)
print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"📰 Sources: {len(SOURCES)} | 🔑 Keywords: {len(KEYWORDS)}")
print(f"📅 Date range: {CONFIG['date_range_days']} days | ⚡ Workers: {CONFIG['max_workers']}")
print("=" * 70)

scrape_start = time.time()
all_articles, telemetry = scrape_all_sources_parallel(SOURCES, CONFIG["max_workers"])
total_time = time.time() - scrape_start

print("\\n" + "=" * 70)
print("✅ SCRAPING COMPLETE")
print("=" * 70)
print(f"⏱️  Total time: {total_time/60:.1f} min ({total_time:.0f}s)")
print(f"📊 Articles: {len(all_articles)}")
print(f"✓  Success: {sum(1 for r in telemetry if r.success)}/{len(telemetry)}")
print("=" * 70)'''

cell10_export = '''# ============================================================================
# CELL 9: EXPORT TO CSV
# ============================================================================

articles_data = [asdict(article) for article in all_articles]
df_articles = pd.DataFrame(articles_data)

if 'keywords_matched' in df_articles.columns:
    df_articles['keywords_matched'] = df_articles['keywords_matched'].apply(lambda x: ', '.join(x) if x else '')

df_articles.to_csv(CONFIG["output_file"], index=False, encoding='utf-8')
print(f"✅ Articles saved to: {CONFIG['output_file']} ({len(df_articles)} rows)")

telemetry_data = [asdict(r) for r in telemetry]
df_telemetry = pd.DataFrame(telemetry_data)
df_telemetry.to_csv(CONFIG["telemetry_file"], index=False, encoding='utf-8')
print(f"✅ Telemetry saved to: {CONFIG['telemetry_file']} ({len(df_telemetry)} sources)")

print("\\n📰 Sample articles:")
if not df_articles.empty:
    display(df_articles[['title', 'source_name', 'method', 'published_date']].head(10))'''

cell11_analytics = '''# ============================================================================
# CELL 10: ANALYTICS
# ============================================================================

print("=" * 70)
print("📊 SCRAPING ANALYTICS")
print("=" * 70)

print("\\n📈 Articles by Method:")
for method, count in df_articles.groupby('method').size().sort_values(ascending=False).items():
    pct = count / len(df_articles) * 100 if len(df_articles) > 0 else 0
    print(f"   • {method.upper():10} : {count:4} ({pct:.1f}%)")

print("\\n✅ Source Success Rate:")
successful = sum(1 for r in telemetry if r.success)
print(f"   • Successful: {successful}/{len(telemetry)} ({successful/len(telemetry)*100:.1f}%)")

print("\\n🏆 Top 10 Sources:")
display(df_telemetry.nlargest(10, 'articles_after_filter')[['source_name', 'articles_after_filter', 'method_used', 'elapsed_seconds']])

print("\\n🐢 Slowest Sources:")
display(df_telemetry.nlargest(5, 'elapsed_seconds')[['source_name', 'elapsed_seconds', 'method_used']])

failed_sources = df_telemetry[~df_telemetry['success']]
if len(failed_sources) > 0:
    print(f"\\n❌ Failed Sources ({len(failed_sources)}):")
    for _, row in failed_sources.head(10).iterrows():
        print(f"   • {row['source_name']}")

print("\\n⏱️ Timing Summary:")
print(f"   • Total: {total_time/60:.1f} min")
print(f"   • Avg/source: {df_telemetry['elapsed_seconds'].mean():.1f}s")
print(f"   • Median/source: {df_telemetry['elapsed_seconds'].median():.1f}s")

print("\\n" + "=" * 70)
print("🎉 V8 Scraper Complete!")
print("=" * 70)'''

# Build notebook structure
notebook = {
    "cells": [
        {"cell_type": "markdown", "metadata": {}, "source": cell1_markdown.split('\n')},
        {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": cell2_imports.split('\n')},
        {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": cell3_config.split('\n')},
        {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": cell4_utilities.split('\n')},
        {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": cell5_discovery.split('\n')},
        {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": cell6_scrapers.split('\n')},
        {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": cell7_filters.split('\n')},
        {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": cell8_orchestrator.split('\n')},
        {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": cell9_main.split('\n')},
        {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": cell10_export.split('\n')},
        {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": cell11_analytics.split('\n')},
    ],
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3.13.0"}
    },
    "nbformat": 4,
    "nbformat_minor": 5
}

# Write notebook
with open('Scraper_v8_Parallel.ipynb', 'w', encoding='utf-8') as f:
    json.dump(notebook, f, indent=1, ensure_ascii=False)

print("✅ Created Scraper_v8_Parallel.ipynb with 11 cells")
