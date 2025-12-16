# V6 Scraper Configuration - At a Glance

## 50 News Sources - Base Domains Only (NO HARDCODED PATHS)

### MAJOR TECH NEWS (15 sources)
```
✅ https://techcrunch.com
✅ https://www.theverge.com
✅ https://arstechnica.com
✅ https://www.wired.com
✅ https://www.engadget.com
✅ https://www.cnet.com
✅ https://www.zdnet.com
✅ https://mashable.com
✅ https://venturebeat.com
✅ https://thenextweb.com
✅ https://www.techradar.com
✅ https://www.tomshardware.com
✅ https://www.anandtech.com
✅ https://gizmodo.com
✅ https://www.digitaltrends.com
```

### AI & TECH SPECIALIST (10 sources)
```
✅ https://www.technologyreview.com
✅ https://spectrum.ieee.org
✅ https://aibusiness.com
✅ https://analyticsindiamag.com
✅ https://blogs.microsoft.com                  ← Changed from /ai
✅ https://ai.googleblog.com
✅ https://openai.com                           ← Changed from /blog
✅ https://syncedreview.com
✅ https://www.marktechpost.com
✅ https://the-decoder.com
```

### BUSINESS & FINANCE TECH (10 sources)
```
✅ https://www.bloomberg.com                    ← Changed from /technology
✅ https://www.reuters.com                      ← Changed from /technology
✅ https://www.cnbc.com                         ← Changed from /technology
✅ https://www.ft.com                           ← Changed from /technology
✅ https://www.wsj.com                          ← Changed from /tech
✅ https://fortune.com                          ← Changed from /section/tech
✅ https://www.forbes.com                       ← Changed from /technology
✅ https://www.businessinsider.com              ← Changed from /tech
✅ https://finance.yahoo.com                    ← Changed from /tech
✅ https://seekingalpha.com                     ← Changed from /market-news/technology
```

### GENERAL NEWS (10 sources)
```
✅ https://www.bbc.com                          ← Changed from /news/technology
✅ https://www.cnn.com                          ← Changed from /business/tech
✅ https://www.theguardian.com                  ← Changed from /technology
✅ https://www.nytimes.com                      ← Changed from /section/technology
✅ https://www.washingtonpost.com               ← Changed from /technology
✅ https://www.npr.org                          ← Changed from /sections/technology
✅ https://apnews.com                           ← Changed from /technology
✅ https://www.axios.com                        ← Changed from /technology
✅ https://www.theatlantic.com                  ← Changed from /technology
✅ https://www.politico.com                     ← Changed from /technology
```

### CHIP & ENERGY SPECIALIST (5 sources)
```
✅ https://www.semianalysis.com
✅ https://www.eetimes.com
✅ https://semiengineering.com
✅ https://cleantechnica.com
✅ https://electrek.co
```

---

## Auto-Detection Methods (ALL 50 get EQUAL treatment)

### ✅ METHOD 1: RSS FEED
- Auto-finds feed via common paths: `/feed`, `/rss`, `/atom.xml`, etc.
- Falls back to HTML `<link>` tag detection
- **ALL 50 sources** get RSS attempt

### ✅ METHOD 2: WORDPRESS API (AUTO-DETECT)
```python
# V6: Every source tries this
api_path = "/wp-json/wp/v2/posts"
api_url = urljoin(base_url, api_path)

# Previously: Only 6 sources had hardcoded entries
# Now: All 50 sources get fair try!
```

### ✅ METHOD 3: HTML SITEMAP (AUTO-DETECT)
```python
# V6: Every source attempts sitemap discovery
sitemap_url = find_sitemap(base_url)

# Checks:
# • robots.txt (Sitemap: directive)
# • /sitemap.xml, /sitemap_index.xml
# • /news-sitemap.xml, /post-sitemap.xml

# Previously: 6 sources were blacklisted
# Now: All 50 sources get fair try!
```

### ✅ METHOD 4: HOMEPAGE DETECTION
- Uses newspaper3k to build paper from homepage
- Auto-extracts article links
- **ALL 50 sources** get homepage attempt

---

## Execution Flow (STOP ON FIRST SUCCESS)

```
For each source:
  1. Try RSS
     ├─ Found articles + keywords match? → SUCCESS ✅ DONE
     └─ No articles? → Continue to step 2
  
  2. Try API
     ├─ Found articles + keywords match? → SUCCESS ✅ DONE
     └─ No articles? → Continue to step 3
  
  3. Try HTML/Sitemap
     ├─ Found articles + keywords match? → SUCCESS ✅ DONE
     └─ No articles? → Continue to step 4
  
  4. Try Homepage
     ├─ Found articles + keywords match? → SUCCESS ✅ DONE
     └─ No articles? → FAILED ❌
```

**Result:** Only runs slower methods when faster ones fail

---

## Keywords (6 topics)

```
🔑 A.I.      (matches "AI", "A.I.", "a.i.", etc.)
🔑 Google    (case-insensitive)
🔑 Microsoft (case-insensitive)
🔑 Nvidia    (case-insensitive)
🔑 Energy    (case-insensitive)
🔑 Chipset   (case-insensitive)
```

---

## Quality Filters (Applied to all articles)

✅ **Headline Check:**
- Length: 15-500 characters
- Words: 3+ words
- Not all caps (unless short)
- No junk patterns

✅ **Content Check:**
- Length: 200+ characters
- Words: 30+ words
- 2+ sentences
- Not mostly junk/ads/navigation

✅ **Article Check:**
- Valid URL (http/https)
- Publication date within 14 days
- Matches at least one keyword

✅ **Deduplication:**
- URL hash (MD5) to prevent duplicates

---

## Configuration

| Setting | Value |
|---------|-------|
| **Sources** | 50 quality news outlets |
| **Keywords** | 6 topics (A.I., Google, Microsoft, Nvidia, Energy, Chipset) |
| **Lookback** | 14 days |
| **Max Articles** | 40 per source (160-2000 total, after filtering) |
| **Timeout** | 12 seconds per request |
| **Retries** | 2 attempts per failed request |
| **Parallel Workers** | 4 concurrent article downloads |
| **Min Content** | 200 characters |
| **Min Headline** | 15 characters |

---

## Output Files (when run)

```
scraped_news_v6.csv
├─ Columns: source, headline, author, url, published, matched_keywords, 
│           content_snippet, url_hash, full_content, method, scraped_at
└─ Rows: All articles found (quality-filtered, keyword-matched)

scraping_telemetry_v6.csv
├─ Columns: source, success, method_used, articles_count, methods_tried,
│           elapsed_seconds, url
└─ Rows: 50 sources with detailed statistics per source
```

---

## Improvements from V5 to V6

| Issue | V5 | V6 |
|-------|----|----|
| OpenAI Blog articles | 0 articles | ✅ Will find articles |
| URL consistency | 22 with paths, 28 without | ✅ All 50 base domains |
| API detection | Only 6 hardcoded | ✅ All 50 auto-detect |
| HTML detection | 44 not tried, 6 skipped | ✅ All 50 tried |
| Paywall handling | Manual blacklist | ✅ Auto-detect failures |
| Site changes | Manual updates needed | ✅ Auto-adapts |
| Maintenance | High | ✅ None |
| Scalability | Add source + configure | ✅ Just add source |

---

**Ready to run!** 🚀

Execute: `v6_Scraper_Auto_Detection/Scraper_v6_Auto_Detection.ipynb`
