# 🚀 V7 News Scraper - Optimized Edition

## Overview
V7 is an optimized version of V6 that maintains the **zero-hardcode** philosophy while significantly improving performance through smarter defaults and reduced overhead.

## Key Optimizations (V6 → V7)

### Performance Parameters

| Parameter | V6 | V7 | Impact |
|-----------|----|----|--------|
| **Parallel Workers** | 4 | 8 | 2x parallel downloading |
| **Request Timeout** | 12s | 8s | 33% faster failure detection |
| **Max Retries** | 2 | 1 | 50% less retry time |
| **RSS Paths** | 26 | 12 | 54% fewer discovery probes |
| **API Paths** | 8 | 4 | 50% fewer API probes |
| **Sitemap Paths** | 15 | 8 | 47% fewer sitemap probes |

### New Features

#### 1. HTTP Session Reuse
```python
HTTP_SESSION = requests.Session()  # Connection keep-alive
response = HTTP_SESSION.get(url)   # Reuses TCP/TLS connections
```
- Eliminates handshake overhead (~250ms per request)
- ~20-30% reduction in network time

#### 2. Method Time Budgets
```python
METHOD_TIME_BUDGETS = {
    "rss": 40,       # Max 40s on RSS discovery
    "api": 25,       # Max 25s on API detection  
    "html": 70,      # Max 70s on sitemap parsing
    "homepage": 100  # Max 100s on homepage extraction
}
```
- Prevents runaway timeouts on failing sources
- Guarantees maximum time per source

#### 3. Cross-Section RSS Feeds
RSS discovery now prioritizes broader feeds for better keyword coverage:
```python
RSS_PATHS_V7 = [
    # Generic first (broadest coverage)
    "/feed", "/rss", "/rss.xml",
    # Cross-section (for Energy/Business)
    "/business/feed", "/science/feed", "/energy/feed",
    # Tech-specific last
    "/technology/feed", "/tech/feed", "/ai/feed"
]
```

#### 4. Progress Tracker with ETA
```
[████████░░░░░░░░░░░░░░░░░░░░░░] 26.0% | 13/50 | ✅10 ❌3 | 12m 45s | ETA 36m 18s
```

## Expected Performance

| Configuration | Runtime | Articles | vs V6 |
|---------------|---------|----------|-------|
| **V6 Baseline** | ~50 min | 502 | 1.0x |
| **V7 Optimized** | ~35-40 min | 450-500 | **1.3-1.4x** |

## What's NOT Changed (Preserved from V6)

✅ **Zero-hardcode philosophy** - No source-specific configs  
✅ **Same 50 sources** - All base domains preserved  
✅ **Same 6 keywords** - A.I., Google, Microsoft, Nvidia, Energy, Chipset  
✅ **Same 14-day lookback**  
✅ **Same 40 max articles per source** - No reduction  
✅ **Same waterfall order** - RSS → API → HTML → Homepage  
✅ **Same quality filters** - Headline, content, date validation  
✅ **Same keyword matching** - Case-insensitive with A.I./AI handling  
✅ **No early exit** - Preserves coverage completeness  
✅ **No article cap reduction** - "We want many articles"  

## Files

| File | Description |
|------|-------------|
| `Scraper_v7_Optimized.ipynb` | Main notebook |
| `scraped_news_v7.csv` | Output articles |
| `scraping_telemetry_v7.csv` | Per-source performance data |
| `scraper_v7.log` | Debug log |

## Quick Comparison

### V5 (Hardcoded)
- ✅ Fast (~25 min)
- ❌ Requires maintenance
- ❌ Biased (skip lists)

### V6 (Zero-Config)
- ❌ Slow (~50 min)
- ✅ Zero maintenance
- ✅ Fair to all sources

### V7 (Optimized Zero-Config)
- ✅ Faster (~35-40 min)
- ✅ Zero maintenance
- ✅ Fair to all sources
- ✅ Better keyword coverage (cross-section feeds)

## Run Instructions

1. Execute cells 1-6 to load libraries and functions
2. Execute cell 7 to run the scraper (watch ETA in progress bar)
3. Execute cell 8 to export results
4. Execute cells 9-10 for analytics (optional)

## Output Schema

```csv
source,headline,author,url,published,matched_keywords,content_snippet,url_hash,full_content,method,scraped_at
```

---
**Version:** 7.0 (Optimized Edition)  
**Based on:** V6 Auto-Detection Edition  
**Target:** ~35-40 min runtime with same article quality
