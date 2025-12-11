"""
📰 NEWS SCRAPER MODULE
Complete Web Scraping Pipeline with Data Standardization

Features:
- Multi-method scraping (RSS, HTML, API)
- Automatic data standardization (dates, content, keywords)
- Comprehensive logging
- Single CSV output with clean data
"""

import feedparser
import newspaper
import requests
import csv
import hashlib
import json
import xml.etree.ElementTree as ET
import re
import logging
import time
from datetime import datetime, timedelta
from urllib.parse import urljoin, urlparse
from data_standardizer import standardize_dataset

# ============================================================================
# 2. CONFIGURE LOGGING
# ============================================================================
LOG_FILENAME = "scraper_execution.log"
logger = logging.getLogger("NewsScraperModule")
logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler(LOG_FILENAME, encoding='utf-8')
file_handler.setLevel(logging.DEBUG)
file_formatter = logging.Formatter("%(asctime)s [%(levelname)-8s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
file_handler.setFormatter(file_formatter)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter("[%(levelname)s] %(message)s")
console_handler.setFormatter(console_formatter)

logger.addHandler(file_handler)
logger.addHandler(console_handler)

# ============================================================================
# 3. CONFIGURATION & CONSTANTS
# ============================================================================
OUTPUT_FILENAME = "scraped_data.csv"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

DAYS_LOOKBACK = 14
MIN_CONTENT_LENGTH = 300
REQUEST_TIMEOUT = 5
MAX_ARTICLES_PER_SOURCE = 50

SOURCES_CONFIG = [
    {"domain_name": "TechCrunch", "base_url": "https://techcrunch.com"},
    {"domain_name": "The Verge", "base_url": "https://theverge.com"},
    {"domain_name": "Wired", "base_url": "https://wired.com"},
    {"domain_name": "Blognone", "base_url": "https://blognone.com"},
    {"domain_name": "BBC Tech", "base_url": "https://bbc.com/news/technology"},
    {"domain_name": "Ars Technica", "base_url": "https://arstechnica.com"},
    {"domain_name": "Engadget", "base_url": "https://engadget.com"},
    {"domain_name": "CNBC Tech", "base_url": "https://cnbc.com/technology"},
    {"domain_name": "VentureBeat", "base_url": "https://venturebeat.com"},
    {"domain_name": "The Markup", "base_url": "https://themarkup.org"},
    {"domain_name": "MIT Tech Review", "base_url": "https://technologyreview.com"},
]

KEYWORDS_CONFIG = ["AI", "Artificial Intelligence", "Machine Learning", "Data", "Google", "Microsoft", "Meta", "NVIDIA", "Crypto"]

# ============================================================================
# 4. HELPER FUNCTIONS
# ============================================================================
def generate_hash(url):
    """Generate SHA-256 hash of URL for deduplication"""
    return hashlib.sha256(url.encode()).hexdigest()

def is_date_valid(date_tuple):
    """Check if published date is within lookback period"""
    if not date_tuple:
        return True
    try:
        published_date = datetime(*date_tuple[:6])
        cutoff_date = datetime.now() - timedelta(days=DAYS_LOOKBACK)
        return published_date >= cutoff_date
    except:
        return True

def get_matched_keywords(headline, content, keywords):
    """Find which keywords match in headline/content (case-insensitive)"""
    text = (headline + " " + content).lower()
    matched = []
    for keyword in keywords:
        if keyword.lower() in text:
            matched.append(keyword)
    return matched

def strip_html_tags(html_text):
    """Remove HTML tags from text"""
    if not html_text:
        return ""
    html_text = re.sub(r'<script[^>]*>.*?</script>', '', html_text, flags=re.DOTALL)
    html_text = re.sub(r'<style[^>]*>.*?</style>', '', html_text, flags=re.DOTALL)
    html_text = re.sub(r'<[^>]+>', '', html_text)
    return html_text

def safe_request(url, timeout=REQUEST_TIMEOUT):
    """Make HTTP request with error handling"""
    try:
        headers = {'User-Agent': USER_AGENT}
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        return response
    except Exception as e:
        logger.debug(f"Request failed for {url}: {str(e)[:50]}")
        return None

# ============================================================================
# 5. RSS SCRAPING METHOD
# ============================================================================
def resolve_rss_link(base_url):
    """Discover RSS feed URL for a website"""
    rss_patterns = ["/feed", "/feeds/latest.xml", "/rss", "/rss.xml", "/feed/rss", "/atom.xml", "/feed.xml"]
    
    for pattern in rss_patterns:
        rss_url = urljoin(base_url, pattern)
        try:
            feed = feedparser.parse(rss_url)
            if feed.entries:
                return rss_url
        except:
            continue
    return None

def scrape_rss(sources, keywords):
    """Scrape articles via RSS feeds"""
    all_articles = []
    logger.info("Starting RSS scraping...")
    
    for source in sources:
        logger.info(f"Processing RSS for: {source['domain_name']}")
        
        feed_url = resolve_rss_link(source['base_url'])
        if not feed_url:
            logger.debug(f"  No RSS feed found")
            continue
        
        try:
            feed = feedparser.parse(feed_url)
            logger.debug(f"  Found {len(feed.entries)} entries")
            
            for entry in feed.entries[:MAX_ARTICLES_PER_SOURCE]:
                try:
                    headline = entry.get('title', 'Unknown')
                    article_url = entry.get('link', '')
                    
                    if not article_url:
                        continue
                    if hasattr(entry, 'published_parsed') and not is_date_valid(entry.published_parsed):
                        continue
                    
                    article = newspaper.Article(article_url)
                    article.download()
                    article.parse()
                    
                    if not article.text or len(article.text) < MIN_CONTENT_LENGTH:
                        continue
                    
                    matched = get_matched_keywords(headline, article.text, keywords)
                    if not matched:
                        continue
                    
                    row = {
                        "source": source['domain_name'],
                        "headline": headline,
                        "author": article.authors[0] if article.authors else "Unknown",
                        "url": article_url,
                        "published": entry.get('published', datetime.now().isoformat()),
                        "keywords": matched,
                        "content_snippet": article.text[:100],
                        "url_hash": generate_hash(article_url),
                        "full_content": article.text,
                        "matched_tags": matched,
                        "status": "New",
                        "method": "rss"
                    }
                    all_articles.append(row)
                    logger.debug(f"  ✓ {headline[:40]}...")
                    
                except Exception as e:
                    logger.debug(f"  Error: {str(e)[:40]}")
                    continue
                    
        except Exception as e:
            logger.debug(f"  RSS error: {str(e)[:40]}")
            continue
    
    logger.info(f"RSS scraping complete: {len(all_articles)} articles")
    return all_articles

# ============================================================================
# 6. STATIC HTML SCRAPING METHOD
# ============================================================================
def discover_sitemaps(base_url):
    """Find sitemap URLs from robots.txt"""
    sitemaps = []
    try:
        robots_url = urljoin(base_url, "/robots.txt")
        response = safe_request(robots_url)
        if response:
            for line in response.text.split('\n'):
                if line.lower().startswith('sitemap:'):
                    sitemap_url = line.split(':', 1)[1].strip()
                    sitemaps.append(sitemap_url)
    except:
        pass
    return sitemaps

def parse_sitemap_urls(sitemap_url):
    """Extract article URLs from XML sitemap"""
    urls = []
    try:
        response = safe_request(sitemap_url)
        if response:
            root = ET.fromstring(response.content)
            for loc in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc'):
                urls.append(loc.text)
    except:
        pass
    return urls

def scrape_html(sources, keywords):
    """Scrape articles via static HTML (sitemaps)"""
    all_articles = []
    logger.info("Starting static HTML scraping...")
    
    for source in sources:
        logger.info(f"Processing HTML for: {source['domain_name']}")
        article_count = 0
        
        article_urls = []
        sitemaps = discover_sitemaps(source['base_url'])
        
        for sitemap_url in sitemaps:
            urls = parse_sitemap_urls(sitemap_url)
            article_urls.extend(urls)
        
        logger.debug(f"  Found {len(article_urls)} URLs")
        
        for url in article_urls[:MAX_ARTICLES_PER_SOURCE]:
            if article_count >= MAX_ARTICLES_PER_SOURCE:
                break
                
            try:
                article = newspaper.Article(url)
                article.download()
                article.parse()
                
                if not article.text or len(article.text) < MIN_CONTENT_LENGTH:
                    continue
                
                matched = get_matched_keywords(article.title, article.text, keywords)
                if not matched:
                    continue
                
                row = {
                    "source": source['domain_name'],
                    "headline": article.title or "Unknown",
                    "author": article.authors[0] if article.authors else "Unknown",
                    "url": url,
                    "published": article.publish_date.isoformat() if article.publish_date else datetime.now().isoformat(),
                    "keywords": matched,
                    "content_snippet": article.text[:100],
                    "url_hash": generate_hash(url),
                    "full_content": article.text,
                    "matched_tags": matched,
                    "status": "New",
                    "method": "html"
                }
                all_articles.append(row)
                article_count += 1
                logger.debug(f"  ✓ {article.title[:40] if article.title else 'Unknown'}...")
                
            except Exception as e:
                logger.debug(f"  Error: {str(e)[:40]}")
                continue
        
        logger.debug(f"  Extracted {article_count} articles")
    
    logger.info(f"HTML scraping complete: {len(all_articles)} articles")
    return all_articles

# ============================================================================
# 7. API SCRAPING METHOD
# ============================================================================
KNOWN_API_PATTERNS = {
    "wordpress": {
        "endpoint": "/wp-json/wp/v2/posts",
        "params": {"per_page": 100, "orderby": "date"},
        "type": "wordpress"
    }
}

def discover_api(base_url):
    """Discover API endpoints for a website"""
    for cms, pattern_info in KNOWN_API_PATTERNS.items():
        api_url = urljoin(base_url, pattern_info["endpoint"])
        response = safe_request(api_url)
        if response and response.status_code == 200:
            try:
                response.json()
                logger.debug(f"  Found {cms} API")
                return {"endpoint": pattern_info["endpoint"], "type": cms}
            except:
                pass
    return None

def parse_wordpress_api(json_data):
    """Parse WordPress REST API response"""
    articles = []
    if isinstance(json_data, list):
        for item in json_data:
            articles.append({
                "headline": item.get("title", {}).get("rendered", "Unknown"),
                "content": item.get("content", {}).get("rendered", ""),
                "author": item.get("_embedded", {}).get("author", [{}])[0].get("name", "Unknown"),
                "url": item.get("link", ""),
                "published": item.get("date", datetime.now().isoformat())
            })
    return articles

def scrape_api(sources, keywords):
    """Scrape articles via API endpoints"""
    all_articles = []
    logger.info("Starting API scraping...")
    
    for source in sources:
        logger.info(f"Processing API for: {source['domain_name']}")
        
        api_info = discover_api(source['base_url'])
        if not api_info:
            logger.debug(f"  No API found")
            continue
        
        try:
            api_url = urljoin(source['base_url'], api_info["endpoint"])
            params = KNOWN_API_PATTERNS.get(api_info["type"], {}).get("params", {})
            
            response = safe_request(api_url)
            if not response:
                continue
            
            json_data = response.json()
            
            if api_info["type"] == "wordpress":
                articles = parse_wordpress_api(json_data)
            else:
                articles = []
            
            logger.debug(f"  Parsed {len(articles)} articles")
            
            for article in articles[:MAX_ARTICLES_PER_SOURCE]:
                try:
                    content = strip_html_tags(article.get("content", ""))
                    headline = article.get("headline", "")
                    url = article.get("url", "")
                    
                    if not url or len(content) < MIN_CONTENT_LENGTH:
                        continue
                    
                    matched = get_matched_keywords(headline, content, keywords)
                    if not matched:
                        continue
                    
                    row = {
                        "source": source['domain_name'],
                        "headline": headline,
                        "author": article.get("author", "Unknown"),
                        "url": url,
                        "published": article.get("published", datetime.now().isoformat()),
                        "keywords": matched,
                        "content_snippet": content[:100],
                        "url_hash": generate_hash(url),
                        "full_content": content,
                        "matched_tags": matched,
                        "status": "New",
                        "method": "api"
                    }
                    all_articles.append(row)
                    logger.debug(f"  ✓ {headline[:40]}...")
                    
                except Exception as e:
                    logger.debug(f"  Error: {str(e)[:40]}")
                    continue
                    
        except Exception as e:
            logger.debug(f"  API error: {str(e)[:40]}")
            continue
    
    logger.info(f"API scraping complete: {len(all_articles)} articles")
    return all_articles

# ============================================================================
# 8. DATA CLEANING & STANDARDIZATION
# ============================================================================
def clean_and_standardize(articles):
    """Apply all cleaning and standardization"""
    logger.info(f"Starting data standardization ({len(articles)} articles)...")
    
    articles = standardize_dataset(articles)
    
    seen_urls = set()
    unique_articles = []
    duplicates = 0
    
    for article in articles:
        url_hash = article.get("url_hash", "")
        if url_hash and url_hash not in seen_urls:
            seen_urls.add(url_hash)
            unique_articles.append(article)
        else:
            duplicates += 1
    
    logger.info(f"Standardization complete: {len(unique_articles)} unique, {duplicates} duplicates")
    return unique_articles

# ============================================================================
# 9. DATA EXPORT TO CSV
# ============================================================================
def export_to_csv(articles, filename):
    """Export article data to CSV file"""
    logger.info(f"Exporting to CSV: {filename}")
    
    if not articles:
        logger.warning("No articles to export")
        return 0
    
    try:
        fieldnames = articles[0].keys()
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(articles)
        
        logger.info(f"✅ Exported {len(articles)} articles to {filename}")
        return len(articles)
        
    except Exception as e:
        logger.error(f"Error exporting to CSV: {str(e)}")
        return 0

# ============================================================================
# 10. MAIN EXECUTION
# ============================================================================
if __name__ == "__main__":
    logger.info("=" * 70)
    logger.info("NEWS SCRAPER MODULE STARTED")
    logger.info("=" * 70)
    
    start_time = time.time()
    
    print("\n🚀 PHASE 1: DATA COLLECTION")
    print("━" * 70)
    
    rss_articles = scrape_rss(SOURCES_CONFIG, KEYWORDS_CONFIG)
    print(f"   RSS: {len(rss_articles)} articles")
    
    html_articles = scrape_html(SOURCES_CONFIG, KEYWORDS_CONFIG)
    print(f"   HTML: {len(html_articles)} articles")
    
    api_articles = scrape_api(SOURCES_CONFIG, KEYWORDS_CONFIG)
    print(f"   API: {len(api_articles)} articles")
    
    print("\n🔀 PHASE 2: MERGING DATASETS")
    print("━" * 70)
    
    all_articles = rss_articles + html_articles + api_articles
    logger.info(f"Total articles before cleaning: {len(all_articles)}")
    print(f"   Total collected: {len(all_articles)} articles")
    
    print("\n🧹 PHASE 3: CLEANING & STANDARDIZATION")
    print("━" * 70)
    
    cleaned_articles = clean_and_standardize(all_articles)
    logger.info(f"Total articles after cleaning: {len(cleaned_articles)}")
    print(f"   Unique after dedup: {len(cleaned_articles)} articles")
    
    print("\n💾 PHASE 4: EXPORT TO CSV")
    print("━" * 70)
    
    exported_count = export_to_csv(cleaned_articles, OUTPUT_FILENAME)
    
    elapsed_time = time.time() - start_time
    
    print("\n📊 EXECUTION SUMMARY")
    print("━" * 70)
    print(f"   RSS articles:       {len(rss_articles):>5}")
    print(f"   HTML articles:      {len(html_articles):>5}")
    print(f"   API articles:       {len(api_articles):>5}")
    print(f"   Total collected:    {len(all_articles):>5}")
    print(f"   Duplicates removed: {len(all_articles) - exported_count:>5}")
    print(f"   Final exported:     {exported_count:>5}")
    print(f"   Execution time:     {elapsed_time:>6.1f}s")
    print(f"   Output file:        {OUTPUT_FILENAME}")
    print("━" * 70)
    
    logger.info(f"\n✅ SCRAPER COMPLETED SUCCESSFULLY")
    logger.info(f"Final: {exported_count} unique articles in {elapsed_time:.1f}s")
    logger.info("=" * 70)
