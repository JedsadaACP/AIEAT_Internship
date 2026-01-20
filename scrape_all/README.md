# Bulk News Scraping Pipeline for LLM Benchmarking

## Purpose
Collect ~10,000 diverse news articles to benchmark LLM model sizes:
- **Large LM (>100B params)**: Generate keywords/labels (ground truth)
- **Medium LM**: Create benchmark (target: 70% similarity with Large)
- **Small LM**: Match Medium LM performance (70% similarity)

## Files
| File | Description |
|------|-------------|
| `sources.json` | 30+ RSS feeds across 9 categories |
| `scrapers.py` | Async bulk scraper with progress tracking |
| `benchmark_news.db` | SQLite database (created on first run) |

## Categories
- Technology (TechCrunch, Verge, Wired, Ars Technica)
- Science (Science Daily, Nature, New Scientist)
- Academy (Chronicle of Higher Ed, Inside Higher Ed)
- Culture (Guardian Culture, NPR Arts, BBC Culture)
- Agriculture (AgWeb, Agriculture.com, Farm Progress)
- Economics (Reuters Business, Bloomberg, FT)
- Politics (AP Politics, Reuters Politics, The Hill)
- Health (WHO News, Medical News Today)
- Environment (ENN, TreeHugger, Climate Home)

## Usage

### 1. Run the scraper
```bash
cd scrape_all
python scrapers.py
```

### 2. Check stats
```python
from scrapers import BulkScraper
scraper = BulkScraper()
print(scraper.get_stats())
```

### 3. Benchmark workflow
1. Run scraper until `TOTAL >= 10,000`
2. Use Large LM API (GPT-4, Claude, etc.) to generate keywords
3. Use Medium LM to generate keywords
4. Use Small LM (local) to generate keywords
5. Calculate similarity scores

## Database Schema
```sql
articles (
    article_id INTEGER PRIMARY KEY,
    title TEXT,
    content TEXT,
    url TEXT UNIQUE,
    source_name TEXT,
    category TEXT,
    published_at DATETIME,
    
    -- LLM Benchmark Fields
    large_lm_keywords TEXT,   -- Ground truth from >100B model
    medium_lm_keywords TEXT,  -- From medium model
    small_lm_keywords TEXT,   -- From small/fine-tuned model
    
    -- Similarity Scores
    medium_similarity REAL,   -- Target: 70%
    small_similarity REAL     -- Target: 70%
)
```

## Target Distribution
Each category should have ~1,000-1,500 articles for balanced benchmarking.
