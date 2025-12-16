# V8 News Scraper - Parallel Processing Architecture

## 🚀 Overview

V8 is a complete rewrite of the news scraper with **parallel source processing** as the primary optimization. This version is designed for scalability - whether you're scraping 50 or 500 sources.

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| **Parallel Processing** | Sources scraped concurrently using ThreadPoolExecutor |
| **JSON Configuration** | Sources loaded from `sources.json` file |
| **Silent Fail** | Errors logged but don't crash execution |
| **Progress Tracking** | tqdm progress bars for all operations |
| **Clean Architecture** | Modular design with separation of concerns |
| **Auto-Detection** | Optimal worker count based on CPU cores |

## 📁 File Structure

```
v8_Scraper_Parallel/
├── Scraper_v8_Parallel.ipynb   # Main notebook
├── sources.json                 # Source configuration
├── scraped_news_v8.csv         # Output articles (after run)
├── scraping_telemetry_v8.csv   # Performance telemetry (after run)
├── scraper_v8.log              # Debug log file
└── README_V8.md                # This file
```

## 🔧 Configuration

Edit Cell 2 to customize:

```python
CONFIG = {
    "date_range_days": 7,        # Only articles from last N days
    "timeout_seconds": 10,       # Request timeout
    "max_workers": None,         # None = auto-detect (2x CPU cores)
    "article_workers": 8,        # Workers for article content
    "min_content_length": 200,   # Quality threshold
    "output_file": "scraped_news_v8.csv"
}
```

### Adding/Removing Sources

Edit `sources.json`:

```json
{
  "sources": [
    {"name": "TechCrunch", "url": "https://techcrunch.com"},
    {"name": "The Verge", "url": "https://www.theverge.com"}
  ]
}
```

## 📊 Architecture

### Scraping Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│                    PARALLEL SOURCE PROCESSING                    │
│  ThreadPoolExecutor (max_workers = 2x CPU cores, max 16)        │
└───────────────┬─────────────┬─────────────┬─────────────┬───────┘
                │             │             │             │
         ┌──────▼─────┐ ┌─────▼──────┐ ┌────▼─────┐ ┌─────▼──────┐
         │  Source 1  │ │  Source 2  │ │ Source 3 │ │  Source N  │
         └──────┬─────┘ └─────┬──────┘ └────┬─────┘ └─────┬──────┘
                │             │             │             │
                ▼             ▼             ▼             ▼
         ┌────────────────────────────────────────────────────┐
         │              WATERFALL STRATEGY                     │
         │   RSS → API → HTML → Homepage (per source)         │
         └────────────────────────────────────────────────────┘
                               │
                               ▼
         ┌────────────────────────────────────────────────────┐
         │              FILTER PIPELINE                        │
         │   Date → Keywords → Quality → Dedupe               │
         └────────────────────────────────────────────────────┘
                               │
                               ▼
                         CSV OUTPUT
```

### Cell Structure

| Cell | Purpose | Lines |
|------|---------|-------|
| 1 | Imports | ~35 |
| 2 | Configuration | ~75 |
| 3 | Core Utilities | ~115 |
| 4 | Discovery | ~55 |
| 5 | Scrapers | ~190 |
| 6 | Filters | ~65 |
| 7 | Orchestrator | ~115 |
| 8 | Main Execution | ~30 |
| 9 | Export | ~25 |
| 10 | Analytics | ~75 |
| **Total** | | **~780** |

## ⚡ Performance

### Expected Runtime

| Sources | V7 (Sequential) | V8 (8 workers) | V8 (16 workers) |
|---------|-----------------|----------------|-----------------|
| 50 | ~38 min | ~6-8 min | ~4-5 min |
| 100 | ~75 min | ~12-15 min | ~8-10 min |
| 500 | ~6 hours | ~50-60 min | ~30-40 min |

### Why Parallel?

In sequential processing, while waiting for one slow source (e.g., 60s timeout), all other sources wait. With parallel processing:

- 8 workers = 8 sources processed simultaneously
- Network I/O bound, not CPU bound
- Efficient use of connection pool

## 🔇 Silent Fail Design

V8 never crashes on individual source failures:

```python
try:
    articles, result = future.result()
except Exception as e:
    logger.error(f"Failed: {source_name}: {e}")
    # Continue with next source
```

All errors are logged to `scraper_v8.log` for debugging.

## 📈 Output Files

### scraped_news_v8.csv

| Column | Description |
|--------|-------------|
| title | Article headline |
| url | Full article URL |
| published_date | Publication date (ISO format) |
| content | Article text |
| source_name | Source name |
| source_url | Source website |
| method | Scraping method used |
| keywords_matched | Keywords found in article |
| scrape_timestamp | When scraped |

### scraping_telemetry_v8.csv

| Column | Description |
|--------|-------------|
| source_name | Source name |
| source_url | Source website |
| method_used | RSS/API/HTML/Homepage/none |
| articles_found | Before filtering |
| articles_after_filter | After filtering |
| elapsed_seconds | Time taken |
| success | Boolean |
| error | Error message if failed |

## 🛠️ Customization

### Adding New Discovery Paths

Edit CONFIG in Cell 2:

```python
"rss_paths": ["/feed", "/rss", "/custom-feed"],
"api_paths": ["/api/articles", "/custom-api/v1/posts"]
```

### Adjusting Time Budgets

```python
"time_budget_rss": 30,      # seconds per RSS source
"time_budget_html": 60,     # seconds per HTML source
```

### Changing Keywords

Edit the KEYWORDS list in Cell 2 to match your topics.

## 🆚 V8 vs V7 Comparison

| Aspect | V7 | V8 |
|--------|----|----|
| Source Processing | Sequential | Parallel |
| Code Lines | ~1700 | ~780 |
| Config Location | Embedded | JSON file |
| Error Handling | Mixed | Silent fail |
| Progress Display | Basic | tqdm bars |
| Architecture | Evolved patches | Clean rewrite |

## 📝 License

Open source - use freely for corporate or personal projects.
