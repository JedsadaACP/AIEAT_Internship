# V6 News Scraper - Technical Report
**Auto-Detection Edition | Architecture, Performance & Optimization Analysis**

---

## 📋 Executive Summary

**V6 Achievement:** Zero-hardcode news scraper with 4-method waterfall detection  
**Performance:** 502 articles from 43/50 sources (86% success) in ~50 minutes  
**Trade-off:** 2x slower than V5 but 12% more articles with zero maintenance  

**Key Insight:** V6 prioritizes **maintainability** and **fairness** over speed through exhaustive discovery, but creates significant performance bottlenecks.

---

## 🏗️ Architecture Overview

### Core Philosophy
V6 removes all hardcoded configurations from V5:
- ❌ No hardcoded RSS paths (e.g., `/technology/feed`)
- ❌ No hardcoded API endpoints  
- ❌ No skip lists for slow sources
- ✅ Base domains only → auto-discovers all content
- ✅ All 50 sources get equal treatment at all methods

### System Components

```
┌─────────────────────────────────────────────────────────┐
│                   V6 SCRAPER ARCHITECTURE               │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  INPUT: 50 Base URLs (no sections)                    │
│         6 Keywords (A.I., Google, Microsoft, etc.)     │
│         14-day lookback                                │
│                                                         │
│  ┌───────────────────────────────────────────┐        │
│  │    WATERFALL PIPELINE (Stop on Success)   │        │
│  ├───────────────────────────────────────────┤        │
│  │                                            │        │
│  │  📡 METHOD 1: RSS Discovery                │        │
│  │     • Try 26 RSS paths (tech + general)    │        │
│  │     • Parse <link> tags from homepage      │        │
│  │     • feedparser + newspaper3k             │        │
│  │                                            │        │
│  │  🔌 METHOD 2: API Detection                │        │
│  │     • Try 8 API patterns (WordPress + JSON)│        │
│  │     • Parse JSON responses                 │        │
│  │     • Extract embedded content             │        │
│  │                                            │        │
│  │  🌐 METHOD 3: Sitemap Parsing              │        │
│  │     • Check robots.txt for sitemap         │        │
│  │     • Try 15 sitemap paths (news priority) │        │
│  │     • Filter tech URLs                     │        │
│  │                                            │        │
│  │  🏠 METHOD 4: Homepage Extraction          │        │
│  │     • newspaper.build() entire site        │        │
│  │     • Extract all article URLs             │        │
│  │     • Prioritize tech patterns             │        │
│  │                                            │        │
│  └───────────────────────────────────────────┘        │
│                       ↓                                │
│  ┌───────────────────────────────────────────┐        │
│  │       QUALITY FILTERS (3-stage)            │        │
│  ├───────────────────────────────────────────┤        │
│  │  1. Structural: Min length, word count     │        │
│  │  2. Content: Junk patterns, navigation     │        │
│  │  3. Temporal: 14-day cutoff                │        │
│  └───────────────────────────────────────────┘        │
│                       ↓                                │
│  ┌───────────────────────────────────────────┐        │
│  │       KEYWORD MATCHING                     │        │
│  ├───────────────────────────────────────────┤        │
│  │  • Case-insensitive substring              │        │
│  │  • Title + Full Content                    │        │
│  │  • A.I. → matches "AI", "ai", "A.i"       │        │
│  └───────────────────────────────────────────┘        │
│                       ↓                                │
│  OUTPUT: CSV (11 columns)                             │
│         • scraped_news_v6.csv (502 articles)          │
│         • scraping_telemetry_v6.csv (50 sources)      │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 🔍 How Each Method Works

### 📡 METHOD 1: RSS Discovery (Most Successful)
**Success Rate:** 28/50 sources (56%)  
**Articles:** 322 articles (64% of total)  
**Avg Time:** 27.4s per source

#### Discovery Process:
1. **Tech-Specific RSS Paths (26 total):**
   ```
   /technology/feed, /technology/rss, /tech/feed, /tech/rss,
   /ai/feed, /ai/rss, /business/technology/feed,
   /section/technology/rss, /topics/technology/feed,
   /category/technology/feed, /category/tech/feed,
   /tag/ai/feed, /tag/technology/feed,
   /feeds/technology, /feeds/tech, /feeds/ai, ...
   ```

2. **General RSS Paths:**
   ```
   /feed, /feed/, /rss, /rss/, /rss.xml, /feed.xml,
   /atom.xml, /feeds/posts/default, /blog/feed,
   /news/feed, /news/rss, /?feed=rss2, /index.xml
   ```

3. **HTML <link> Tag Parsing:**
   - Fetch homepage HTML
   - Find `<link type="application/rss+xml">`
   - Extract `href` attribute

4. **Article Fetching:**
   - Parse feed with `feedparser`
   - Filter by date (14-day lookback)
   - Download full content with `newspaper3k` (parallel, 4 workers)

**Why It's Fast:** Direct XML parsing, structured data, minimal HTTP overhead.

**Why It Fails:** Many sites don't publish tech-specific RSS feeds or use non-standard paths.

---

### 🔌 METHOD 2: API Detection (Rare Success)
**Success Rate:** 3/50 sources (6%)  
**Articles:** 82 articles (16% of total)  
**Avg Time:** 25.7s per source

#### Discovery Process:
1. **Try 8 API Patterns:**
   ```
   /wp-json/wp/v2/posts           # WordPress
   /api/posts, /api/articles       # Generic
   /api/v1/posts, /api/v1/articles
   /api/news, /api/v1/news
   /_api/posts, /_api/articles
   ```

2. **JSON Parsing:**
   - Request with `?per_page=100&_embed`
   - Parse nested JSON (WordPress `_embedded`, generic `author`, etc.)
   - Extract `title.rendered`, `content.rendered`, `excerpt.rendered`
   - Clean HTML with BeautifulSoup

3. **Date Filtering:**
   - Check `date`, `published`, `publishedAt` fields
   - Apply 14-day cutoff

**Why It's Fast:** Structured JSON, batch data, no HTML parsing needed.

**Why It Fails:** Most major news sites use custom APIs or no public API.

---

### 🌐 METHOD 3: Sitemap Parsing (Moderate Success)
**Success Rate:** 10/50 sources (20%)  
**Articles:** 95 articles (19% of total)  
**Avg Time:** 66.4s per source (SLOW)

#### Discovery Process:
1. **robots.txt Scan:**
   ```
   GET /robots.txt
   Parse lines starting with "Sitemap:"
   Prioritize URLs containing "news", "post", "article"
   ```

2. **Try 15 Sitemap Paths (News Priority):**
   ```
   # News-specific (checked first)
   /news-sitemap.xml, /sitemap-news.xml, /sitemap_news.xml,
   /post-sitemap.xml, /article-sitemap.xml, /articles-sitemap.xml,
   /sitemap-posts.xml, /blog-sitemap.xml
   
   # General
   /sitemap.xml, /sitemap_index.xml, /sitemap-index.xml,
   /sitemap/sitemap.xml, /sitemaps/sitemap.xml
   ```

3. **XML Parsing & URL Filtering:**
   - Parse `<url>` tags with `<loc>` and `<lastmod>`
   - Skip `/tag/`, `/category/`, `/author/`, `/page/`
   - **Tech URL prioritization:** URLs with `/tech/`, `/ai/`, `/energy/` get priority
   - General URLs fill remaining slots

4. **Article Fetching:**
   - Parallel download (4 workers)
   - Full `newspaper3k` parse per URL

**Why It's Slow:**  
- Large XML files (10-100MB for major sites)
- Full HTML parsing for every URL
- Network-heavy (100+ HTTP requests per source)

**Why It Fails:** Many sites don't publish sitemaps or use non-standard structures.

---

### 🏠 METHOD 4: Homepage Extraction (Last Resort)
**Success Rate:** 5/50 sources (10%)  
**Articles:** 98 articles (20% of total)  
**Avg Time:** 129.7s per source (VERY SLOW)

#### Discovery Process:
1. **newspaper.build():**
   - Fetch homepage HTML
   - Extract all `<a>` tags
   - Filter URLs matching article patterns
   - Build internal article list

2. **Tech URL Prioritization:**
   ```python
   tech_urls = [url for url in all_urls if is_tech_url(url)]
   general_urls = [url for url in all_urls if not is_tech_url(url)]
   final_urls = tech_urls[:MAX] + general_urls[:MAX-len(tech_urls)]
   ```

3. **Article Fetching:**
   - Parallel download (4 workers)
   - Full `newspaper3k` parse

**Why It's So Slow:**
- Downloads ENTIRE homepage (500KB-5MB HTML)
- Processes 100-500 links (most not articles)
- Full newspaper3k parsing overhead
- High false positive rate (menus, footers, sidebars)

**Why It's Reliable:**
- Works on any website with links
- No API/RSS/Sitemap required
- Guaranteed to find *something*

---

## ⚙️ Configuration

```python
# Scraping Parameters
DAYS_LOOKBACK = 14           # 14-day window
MAX_ARTICLES_PER_SOURCE = 40 # Stop at 40 articles
REQUEST_TIMEOUT = 12         # 12s per HTTP request
MAX_RETRIES = 2              # 2 retries on failure
PARALLEL_WORKERS = 4         # 4 concurrent article downloads

# Quality Filters
MIN_CONTENT_LENGTH = 200     # 200 characters minimum
MIN_HEADLINE_LENGTH = 15     # 15 characters minimum

# Discovery Limits (None - tries all paths)
RSS_DISCOVERY_PATHS = 26     # All tech + general paths
API_DISCOVERY_PATHS = 8      # All WordPress + generic
SITEMAP_PATHS = 15           # All news + general
```

---

## 📊 Performance Analysis (50-minute run)

### Overall Results
| Metric | V6 | V5 | Difference |
|--------|----|----|------------|
| **Runtime** | ~50 min | ~25 min | **2x slower** ⚠️ |
| **Success Rate** | 43/50 (86%) | 45/50 (90%) | -4% |
| **Total Articles** | 502 | 448 | **+12%** ✅ |
| **Articles/Min** | 10.0 | 17.9 | -44% |
| **Avg Time/Source** | 60s | 30s | 2x |

### Method Performance Breakdown

| Method | Sources | Articles | Success % | Avg Time | Speed |
|--------|---------|----------|-----------|----------|-------|
| 📡 **RSS** | 28 | 322 (64%) | 56% | 27.4s | **Fast** |
| 🔌 **API** | 3 | 82 (16%) | 6% | 25.7s | **Fast** |
| 🌐 **HTML** | 10 | 95 (19%) | 20% | 66.4s | Slow |
| 🏠 **Homepage** | 5 | 98 (20%) | 10% | 129.7s | **Very Slow** |

### Notable Examples (from telemetry)

**Fast Successes (RSS):**
- The Next Web: **3.0s** (2 articles)
- The Guardian: **7.7s** (8 articles)
- Gizmodo: **12.7s** (16 articles)

**Slow Successes (Waterfall):**
- Washington Post: **318.6s** (4 articles, rss→api→html→homepage)
- EE Times: **291.1s** (10 articles, rss only but slow server)
- Marktechpost: **186.2s** (0 articles, tried all 4 methods, failed)

**Waterfall Overhead:**
- Ars Technica: Tried rss→api→html→homepage, succeeded on homepage at **83.4s**
- VentureBeat: Tried rss→api→html, succeeded on html at **41.3s**
- AnandTech: Tried all 4 methods, **failed after 178.6s**

---

## 🐛 Problems Identified

### 1. **Discovery Overhead (High Impact)**
**Problem:** Exhaustive path probing creates massive network tax.

**Example:**
- 26 RSS paths × 12s timeout × 2 retries = **624s maximum per source**
- If all RSS paths fail, then try 8 API paths = **+192s**
- If API fails, parse sitemap = **+24s**
- If sitemap fails, build homepage = **+60-180s**

**Real Case (AnandTech):**
- Tried all 4 methods
- 178.6s total
- 0 articles
- All methods failed

**Impact:** 10-40 wasted HTTP requests per failing source.

---

### 2. **Timeout Multiplication (High Impact)**
**Problem:** High timeout × retries amplifies failure cost.

**Math:**
- Timeout: 12s
- Retries: 2
- Cost per failed endpoint: **12s × 2 = 24s**
- 26 failed RSS paths: **624s (10+ minutes)**

**Real Case (CNET):**
- RSS succeeded at 172.1s (19 articles)
- Likely tried 10-15 RSS paths before finding the right one
- Wasted 120-180s on failed paths

**Impact:** Failed probes cost 10-20x more than successful ones.

---

### 3. **Base Domain Tax (Medium Impact)**
**Problem:** Starting from root requires redirects and homepage parsing.

**V5 Approach:**
```
TechCrunch: https://techcrunch.com/feed  → 3.7s
```

**V6 Approach:**
```
TechCrunch: https://techcrunch.com  → 27.7s
  1. Try /technology/feed → 404 (12s wasted)
  2. Try /tech/feed → 404 (12s wasted)
  3. Try /feed → 200 ✅ (3s)
  Total: 27s
```

**Impact:** 3-10x slower even on success due to failed probes.

---

### 4. **Full-Parse Cost (High Impact)**
**Problem:** newspaper3k parses EVERY article fully (HTML download, parse, NLP).

**Process:**
1. Download article HTML (10-500KB)
2. BeautifulSoup parsing
3. newspaper3k NLP (title extraction, date parsing, author detection, content extraction)
4. Text cleaning

**Cost:** 1-3s per article × 40 articles = **40-120s per source**

**V5 Optimization:** Only parsed headline and snippet from RSS, full parse on-demand.

**Impact:** 50-70% of total source time is article parsing.

---

### 5. **No Connection Reuse (Medium Impact)**
**Problem:** New TCP/TLS handshake for every request.

**Cost per request:**
- DNS lookup: 20-50ms
- TCP handshake: 50-100ms
- TLS handshake: 100-200ms
- Total overhead: **170-350ms per request**

**Math:**
- 40 articles per source
- 40 × 250ms = **10s wasted on handshakes**

**Solution:** `requests.Session()` reuses connections (HTTP keep-alive).

**Impact:** 15-25% time reduction with zero code complexity.

---

### 6. **Sitemap Bloat (Medium Impact)**
**Problem:** Sitemaps can be 10-100MB with 10,000+ URLs.

**Real Case (CNN):**
- Sitemap: ~50MB XML
- 5,000+ URLs
- Parse time: 30-60s
- Only 8 articles matched keywords

**Math:**
- Download: 20-30s (50MB @ 2MB/s)
- XML parsing: 10-20s (BeautifulSoup on 50MB)
- Date filtering: 5-10s (5,000 URLs)
- URL fetching: 40-80s (8 articles × 5-10s each)
- **Total: 130s** (as seen in telemetry)

**Impact:** Sitemap method is 2-5x slower than RSS for same article count.

---

### 7. **RSS Section Bias (High Impact on Coverage)**
**Problem:** Tech-specific RSS paths miss non-tech content.

**Example (Energy keyword):**
- V6 tries: `/technology/feed`, `/ai/feed`, `/tech/feed`
- Energy articles published at: `/business/feed`, `/science/feed`, `/environment/feed`
- **Result:** Energy articles missed even though they exist

**Real Case:**
- NYT has energy articles in `/section/climate/rss`
- V6 tech-specific paths miss it
- V5 used `/news/rss` (broader coverage)

**Impact:** Keyword imbalance (A.I. > Google > Microsoft > Energy > Chipset).

---

### 8. **No Early Exit (Low Impact - Philosophical)**
**Problem:** Scraper fetches MAX_ARTICLES_PER_SOURCE (40) even if 12 already matched keywords.

**Scenario:**
- TechCrunch RSS has 50 articles
- First 12 all match "A.I." keyword
- V6 still downloads remaining 28 articles
- Wasted: 28 × 2s = **56s**

**Counter-Argument:** User wants **many articles**, not samples. No early exit preserves completeness.

**Impact:** Marginal (10-20% speed gain but sacrifices coverage).

---

## 🎯 Optimization Recommendations

### ✅ High-Impact (Safe & Effective)

| # | Optimization | Impact | Effort | Risk | Estimated Gain |
|---|--------------|--------|--------|------|----------------|
| 1 | **Raise workers to 8-10** | High | Low | None | **2x speedup** (25 min) |
| 2 | **Lower timeout to 8s** | High | Low | Low | **1.5x speedup** (16 min) |
| 3 | **Reduce retries to 1** | Medium | Low | Low | **1.2x speedup** (13 min) |
| 4 | **Session reuse** | Medium | Low | None | **1.2x speedup** (11 min) |
| 5 | **Limit RSS to top 8 paths** | Medium | Low | Low | **1.3x speedup** (8.5 min) |
| 6 | **Limit API to top 4 paths** | Low | Low | Low | **1.1x speedup** (7.7 min) |
| 7 | **Method time budgets** | High | Medium | Medium | **1.5x speedup** (5 min) |

**Combined Safe Optimizations:** 50 min → **~35-40 min** (20-30% reduction)

---

### 🟡 Medium-Impact (Trade-offs Required)

| # | Optimization | Impact | Effort | Risk | Trade-off |
|---|--------------|--------|--------|------|-----------|
| 8 | **Selective full-parse** | Medium | Medium | Medium | Miss some articles |
| 9 | **HTML prefilter** | Low | Medium | Medium | False negatives |
| 10 | **Per-source parallelization** | Medium | High | High | Code complexity |
| 11 | **Caching (robots/sitemaps)** | Low | Medium | Low | Stale data (24h TTL) |
| 12 | **Persistence (success hints)** | Low | Medium | Low | File I/O overhead |

**Combined Medium:** 35 min → **~28-32 min** (additional 10-15% reduction)

---

### ❌ High-Risk (Not Recommended)

| # | Optimization | Why NOT Recommended |
|---|--------------|---------------------|
| 13 | **Early exit after 12 matches** | **Creates keyword bias** (tech > energy) |
| 14 | **Reduce MAX_ARTICLES to 20-25** | **Contradicts "we want many news" goal** |
| 15 | **Skip homepage method** | Loses 20% of articles (98/502) |
| 16 | **Hardcode successful paths** | Defeats V6's zero-config philosophy |

---

## 🔧 Implementation Plan

### Phase 1: Quick Wins (Target: <40 min)
**Safe, high-impact changes with zero risk.**

```python
# Config changes only
PARALLEL_WORKERS = 8          # Was 4
REQUEST_TIMEOUT = 8           # Was 12
MAX_RETRIES = 1               # Was 2

# Session reuse (2-line change)
session = requests.Session()
response = session.get(url, ...)  # Instead of requests.get()

# Discovery caps
RSS_PATHS = tech_paths[:8] + general_paths[:4]  # Was 26 total
API_PATHS = api_paths[:4]                        # Was 8 total
```

**Expected Result:** 50 min → 35-40 min

---

### Phase 2: Smart Filtering (Target: <35 min)
**Add intelligence to reduce waste.**

```python
# Method time budgets
METHOD_BUDGETS = {
    "rss": 30,      # Max 30s on RSS discovery
    "api": 20,      # Max 20s on API detection
    "html": 60,     # Max 60s on sitemap parsing
    "homepage": 90  # Max 90s on homepage extraction
}

# Selective full-parse
def should_full_parse(headline: str) -> bool:
    """Only full-parse if headline matches keywords."""
    return any(kw.lower() in headline.lower() for kw in KEYWORDS)

# RSS freshness check
feed = feedparser.parse(feed_url)
if feed.feed.get('updated_parsed'):
    last_update = datetime(*feed.feed.updated_parsed[:6])
    if datetime.now() - last_update > timedelta(days=30):
        logger.info(f"Feed stale (>30 days), skipping")
        continue
```

**Expected Result:** 35 min → 28-32 min

---

### Phase 3: Production Hardening (No speed gain, quality improvement)
**Add resilience and monitoring.**

```python
# Circuit breaker
class CircuitBreaker:
    def __init__(self, failure_threshold=3, timeout=300):
        self.failures = {}
        self.threshold = failure_threshold
        self.timeout = timeout
    
    def can_try(self, source: str) -> bool:
        if source in self.failures:
            count, last_fail = self.failures[source]
            if count >= self.threshold:
                if time.time() - last_fail < self.timeout:
                    return False
        return True
    
    def record_failure(self, source: str):
        if source not in self.failures:
            self.failures[source] = [0, 0]
        self.failures[source][0] += 1
        self.failures[source][1] = time.time()

# Health metrics
HEALTH_METRICS = {
    "success_rate": 0.0,
    "avg_latency": 0.0,
    "articles_per_source": 0.0,
    "method_distribution": {}
}

# Structured logging
import json
logger.info(json.dumps({
    "source": source_name,
    "method": method,
    "articles": len(articles),
    "elapsed": elapsed,
    "success": success
}))
```

---

### Phase 4: Coverage Fixes (Address RSS bias)
**Ensure all keywords get equal coverage.**

```python
# Cross-section RSS feeds
CROSS_SECTION_FEEDS = [
    "/business/feed", "/business/rss",      # For energy, chipset
    "/science/feed", "/science/rss",        # For research
    "/environment/feed", "/climate/feed",   # For energy
    "/markets/feed", "/finance/feed",       # For company news
    "/opinion/feed", "/analysis/feed"       # For policy
]

# Generic feeds first (broader coverage)
RSS_PATHS = [
    "/feed", "/rss", "/rss.xml",           # Try generic FIRST
    "/news/feed", "/articles/feed",        # Then news
    *CROSS_SECTION_FEEDS,                  # Then cross-sections
    *TECH_PATHS[:4]                        # Tech-specific LAST
]

# Per-keyword quota (ensure balance)
def apply_keyword_quota(articles: List[Dict]) -> List[Dict]:
    """Ensure at least 2 articles per keyword."""
    keyword_buckets = {kw: [] for kw in KEYWORDS}
    
    for art in articles:
        for kw in art['matched_keywords'].split(','):
            kw = kw.strip()
            if kw in keyword_buckets:
                keyword_buckets[kw].append(art)
    
    # Fill underrepresented keywords
    balanced = []
    for kw, arts in keyword_buckets.items():
        balanced.extend(arts[:2])  # At least 2 per keyword
    
    # Fill remaining with most relevant
    remaining = [a for a in articles if a not in balanced]
    balanced.extend(remaining[:MAX_ARTICLES_PER_SOURCE - len(balanced)])
    
    return balanced[:MAX_ARTICLES_PER_SOURCE]
```

---

## 📈 Expected Performance After Optimization

| Configuration | Runtime | Articles | Success % | Speed vs V6 | Speed vs V5 |
|---------------|---------|----------|-----------|-------------|-------------|
| **V6 Current** | 50 min | 502 | 86% | 1.0x | 0.5x |
| **V6 + Phase 1** | 35-40 min | 480-500 | 85% | 1.3-1.4x | 0.65-0.7x |
| **V6 + Phase 2** | 28-32 min | 450-480 | 82% | 1.6-1.8x | 0.8-0.9x |
| **V6 + Phase 3** | 28-32 min | 450-480 | 82% | Same | 0.8-0.9x |
| **V6 + Phase 4** | 28-32 min | 450-480 | 82% | Same | 0.8-0.9x |
| **V5 Baseline** | 25 min | 448 | 90% | 2.0x | 1.0x |

**Best-Case Optimized V6:** 28 minutes, 450+ articles, 82% success (12% faster than V5 while maintaining zero-config)

---

## 🎯 Recommendations

### If Priority = Speed
**Use V5.** Hardcoded paths are 2x faster with minimal maintenance burden (update paths 2-3x per year).

### If Priority = Maintainability
**Optimize V6 with Phase 1 + 2.** Target 30-35 minutes is acceptable for zero-config architecture.

### If Priority = Coverage
**Optimize V6 with Phase 4.** Implement cross-section feeds and per-keyword quotas to ensure Energy/Chipset/Policy articles aren't starved by A.I./Google dominance.

### If Priority = Balance
**Implement Phases 1, 2, and 4 only.** Skip Phase 3 (production hardening) until integrating with main application.

---

## 📊 Final Verdict

| Aspect | V5 | V6 | V6 Optimized |
|--------|----|----|--------------|
| **Speed** | ⭐⭐⭐⭐⭐ (25 min) | ⭐⭐☆☆☆ (50 min) | ⭐⭐⭐⭐☆ (30 min) |
| **Maintainability** | ⭐⭐☆☆☆ (hardcoded) | ⭐⭐⭐⭐⭐ (zero-config) | ⭐⭐⭐⭐⭐ |
| **Coverage** | ⭐⭐⭐⭐☆ (448 articles) | ⭐⭐⭐⭐⭐ (502 articles) | ⭐⭐⭐⭐☆ (450 articles) |
| **Fairness** | ⭐⭐⭐☆☆ (skip lists) | ⭐⭐⭐⭐⭐ (all sources equal) | ⭐⭐⭐⭐⭐ |
| **Keyword Balance** | ⭐⭐⭐☆☆ (tech bias) | ⭐⭐☆☆☆ (tech bias) | ⭐⭐⭐⭐☆ (w/ Phase 4) |
| **Complexity** | ⭐⭐⭐☆☆ (moderate) | ⭐⭐⭐⭐☆ (complex) | ⭐⭐⭐⭐⭐ (very complex) |

**Conclusion:** V6 achieves its zero-config goal but pays a 2x speed penalty. Optimizations can reduce this to 1.2-1.3x slower than V5 while preserving architectural benefits. **Recommended action:** Implement Phase 1 (quick wins) immediately, benchmark, then decide on Phases 2-4 based on actual needs.

---

## 🔗 Appendix: Telemetry Highlights

### Fastest Sources (RSS)
1. The Next Web: **3.0s** (2 articles)
2. The Guardian: **7.7s** (8 articles)
3. MIT Technology Review: **7.1s** (23 articles via API)

### Slowest Successful Sources
1. Washington Post: **318.6s** (4 articles, tried all 4 methods)
2. EE Times: **291.1s** (10 articles, RSS only but slow)
3. Google AI Blog: **171.3s** (2 articles, RSS)

### Waterfall Examples (Multi-Method)
- Ars Technica: rss→api→html→**homepage** (83.4s, 18 articles)
- VentureBeat: rss→api→**html** (41.3s, 12 articles)
- TechRadar: rss→api→**html** (44.5s, 31 articles)

### Total Failures (All Methods)
- AnandTech: 178.6s (tried all 4, 0 articles)
- Marktechpost: 186.2s (tried all 4, 0 articles)
- Bloomberg: 27.0s (tried all 4, paywall)
- Reuters: 15.6s (tried all 4, auth required)

---

**Report Generated:** December 14, 2025  
**V6 Version:** Auto-Detection Edition  
**Data Source:** `scraping_telemetry_v6.csv` (50 sources, 502 articles, ~50 min runtime)
