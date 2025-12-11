# News Scraping Analysis: What We Can & Cannot Scrape

## Executive Summary
Your current scraper can extract articles from **~80% of news sites** (those with RSS feeds). After upgrades, you can add **metadata from paywalled sites** (+10-15%), but **fully blocked sites require Playwright** (expensive upgrade, +5-10%).

---

## 1. CURRENT CODE - WHAT WE CAN SCRAPE ✅

### **Can Scrape (TODAY)**

#### **Category A: RSS-Available Sites (80% success rate)**
- **TechCrunch, The Verge, Ars Technica, Engadget** → RSS feed direct
- **Reuters, AP News, The Guardian** → Reliable RSS feeds
- **Wired, MIT Tech Review, VentureBeat, Protocol** → RSS with HTML fallback
- **Blognone, BearTai** (Thai sources) → RSS feeds available

**Method:** `feedparser` library auto-discovers `/feed`, `/rss.xml`, `/atom.xml` patterns  
**Speed:** 1-2 seconds per source  
**Content Retrieved:** Full article text (headline, author, body, publish date)  
**Current Results:** 27 sources = 200-500 articles in 5-10 minutes

---

## 2. CURRENT CODE - WHAT WE CANNOT SCRAPE ❌

### **Category B: Paywalled Sites (Lost Revenue Opportunity)**
Sites with soft paywalls where metadata IS visible in plain HTML but full text is blocked:

- **Financial Times** (Business news)
- **Wall Street Journal** (if added)
- **The Economist** (if added)
- **Some Bloomberg content** (subscription walls)

**Current Behavior:**
```python
# Line 347: MIN_CONTENT_LENGTH = 300  ← Too strict!
if not article.text or len(article.text) < MIN_CONTENT_LENGTH:
    continue  # ← Discards valuable partial content
```

**What's Lost:**
- **Headlines** ✅ Can extract
- **Published date** ✅ Can extract
- **Author/source** ✅ Can extract
- **Preview text** (100-200 chars) ✅ Can extract but SKIPPED
- **Full article body** ❌ Hidden behind paywall

**Example (Financial Times):**
```html
<h1>Apple's AI Strategy Faces Regulatory Scrutiny</h1>
<p>Apple's plans to integrate AI into its product line have drawn attention from...</p>
<!-- Full article blocked by paywall -->
```

**Potential Recovery:** +50-100 articles from paywalled sites (headlines + previews)

---

### **Category C: JavaScript-Rendered Sites (Hard to Scrape)**
Sites that load content dynamically (not in initial HTML):

- **BBC News** (Heavy JavaScript)
- **CNBC** (Dynamic loading)
- **Mashable** (Progressive loading)
- **Medium** (if added)
- **Twitter/X feeds** (if attempted)

**Current Behavior:**
```python
# Line 512: SKIP_HTML_SOURCES = {"BBC", "CNBC", "Financial Times"}
# These hang on HTML scraping, so completely skipped
```

**Why It Fails:**
1. Your HTML scraper (`newspaper` library) fetches raw HTML
2. JS-heavy sites serve minimal text in initial HTML
3. Full article loads via JavaScript AFTER page renders
4. `newspaper` can't execute JavaScript (headless browser needed)

**What's Needed:** Playwright (headless browser) to render JS, THEN extract text  
**Current Result:** 0 articles from BBC, CNBC, Mashable

---

### **Category D: Anti-Scraping Protected Sites**
Sites with aggressive bot detection:

- **Some financial data sites** (stricter user-agent checks)
- **Real-time sports data** (rate limiting)
- **LinkedIn** (explicit robots.txt ban)
- **Reddit** (API-only recommended)

**Current Behavior:**
```python
# Line 231: REQUEST_TIMEOUT = 5  ← Hard timeout, no retry
# If request fails → article skipped forever
```

**Why It Fails:**
- HTTP 429 (Too Many Requests) → No retry logic
- HTTP 403 (Forbidden) → Blocked immediately
- Connection timeout → No exponential backoff

---

## 3. FAILURE CLASSIFICATION (6 Status Types)

Based on the conversation history, here's how failures break down:

| Status | Detection | Currently Handled? | Can Extract? | Fix Required |
|--------|-----------|-------------------|--------------|--------------|
| **success** | Full text >300 chars | ✅ Yes | ✅ Full | None |
| **partial** | 100-300 chars (paywall preview) | ❌ No (skipped) | ⚠️ Partial | Lower threshold to 100 chars |
| **blocked** | HTTP 403 Forbidden | ❌ No (skipped) | ❌ No | Accept as unfetchable |
| **rate_limited** | HTTP 429 Too Many Requests | ❌ No (no retry) | ⚠️ Yes (with delay) | Add backoff + retry |
| **timeout** | Connection timeout >5s | ❌ No (no retry) | ⚠️ Yes (with longer timeout) | Increase timeout + retry |
| **dynamic** | JS-rendered content | ❌ No (SKIP_HTML_SOURCES) | ✅ Full (needs Playwright) | **Playwright Phase 2** |

---

## 4. PHASE 1 UPGRADES (Can do NOW, no Playwright) ✅

### **Upgrade 1: Lower MIN_CONTENT_LENGTH Threshold**
```python
# Current (Line 347)
MIN_CONTENT_LENGTH = 300  # Too strict for paywalls
MIN_PREVIEW_LENGTH = 100  # NEW: Accept partial content

# Impact: +50-100 articles from paywalled sites
# Time to implement: 10 minutes
```

**Before & After:**
```
Before: Financial Times article rejected (150 chars of preview)
After:  Financial Times article accepted as "partial" status
```

---

### **Upgrade 2: Add Telemetry Tracking per Source**
```python
# Current (Line 479)
def scrape_with_smart_fallback(source, keywords):
    # Returns: (articles, method)
    # Missing: Why failed? How long? What status?

# Needed
def scrape_with_smart_fallback(source, keywords):
    # Returns: (articles, method, telemetry)
    # telemetry = {
    #   "source_name": "Financial Times",
    #   "status": "partial",  # success / partial / timeout / blocked / none
    #   "method": "html",
    #   "articles_found": 3,
    #   "articles_exported": 1,  # After filtering
    #   "http_code": 200,
    #   "reason": "Content too short (<300 chars)",
    #   "elapsed_time": 2.5
    # }
```

**Impact:** Manager sees WHY sources are failing (transparency)  
**Time to implement:** 30 minutes

---

### **Upgrade 3: Add Retry Logic for Transient Failures**
```python
# Current (Line 231)
def safe_request(url, timeout=REQUEST_TIMEOUT):
    try:
        response = requests.get(url, timeout=timeout)
    except:
        return None  # ← Fails once, skipped forever

# Needed
def safe_request_with_retry(url, timeout=REQUEST_TIMEOUT, max_retries=2):
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=timeout)
            if response.status_code == 429:
                time.sleep(30)  # Backoff on rate limit
                continue
            return response
        except (Timeout, ConnectionError):
            if attempt < max_retries - 1:
                time.sleep(5 * (attempt + 1))  # Exponential backoff
```

**Impact:** Recover 10-20 articles from temporary failures  
**Time to implement:** 20 minutes

---

### **Upgrade 4: Expand to 100 Sources (RSS-heavy)**
```python
# Current: 27 sources
# Target: 100 sources (RSS-preferred)

# Add 70+ high-quality RSS sources:
# - More tech: Hacker News, Dev.to, Indie Hackers
# - More business: Industry Week, Supply Chain Dive
# - International: Nikkei, JinriToutiao (Chinese tech)
# - Thai: Thaidaily, Nationtv, Bangkokbiznews
```

**Impact:** 2-3x more articles (400-1500 per run)  
**Time to implement:** 30 minutes (data entry + validation)

---

## 5. PHASE 2 UPGRADE (Requires Playwright) 🚀

### **If Manager Approves: Add Playwright for JS-Rendered Sites**

**Target Sites:**
- BBC News, CNBC, Mashable (currently skipped)
- Financial Times full text (premium content)
- Bloomberg premium articles

**Cost Analysis:**
```
Current Performance:
- 27 sources × 10 sec/source = ~300 seconds (5 min)
- RSS: 80% success rate
- Memory: 500 MB - 1 GB

With Playwright:
- 27 sources × 45 sec/source = 20-25 minutes (4-5x slower!)
- Success rate: 95% (full JS rendering)
- Memory: 10-15 GB (20x more)

For 100 sources:
- Current (RSS only): 10-15 minutes ✅ VIABLE
- Playwright: 45-60 minutes ❌ SLOW (infeasible locally)
- Playwright + parallelization: Still 10-15x RAM overhead
```

**Recommendation:**
> ❌ **Skip Playwright locally.** If manager needs JS content:
> 1. Show Phase 1 results (telemetry report)
> 2. If "Headlines + previews enough" → DONE ✅
> 3. If "Need FT/WSJ full text" → Deploy on cloud (AWS Lambda, cloud VM)

---

## 6. WHAT'S IMPOSSIBLE (Accept as Limits)

### **Tier 1: No Scraping - HTTP Blocking**
These actively block scraping in `robots.txt` or via 403 responses:
- **LinkedIn** → Explicit `User-agent: * Disallow: /` (respect it)
- **PayPal** → HTTP 403 by default
- **Some banking sites** → Security restriction

**Why:** Legal/contractual restrictions. Don't attempt.

---

### **Tier 2: Difficult Without JS Execution**
- **Twitter/X** → 100% JavaScript rendering
- **Instagram** → JavaScript + OAuth required
- **TikTok** → JavaScript + browser fingerprinting

**Why:** Requires full browser session + auth. Not worth it for news.

---

### **Tier 3: Paywalls That Can't Be Bypassed**
- **New York Times** → Hard paywall, counts articles per month
- **Harvard Business Review** → Requires subscription
- **Gated industry reports** → Pay-per-article

**Reality:** Accept ~200-char preview as "best effort"

---

## 7. CURRENT COVERAGE BY YOUR 27 SOURCES

### **Breakdown:**
| Difficulty | Sources | Status | Method | Success Rate |
|------------|---------|--------|--------|--------------|
| **Easy (RSS)** | 7 | Fully working | RSS | 95%+ |
| **Medium (RSS + HTML)** | 9 | Mostly working | RSS → HTML fallback | 70-80% |
| **Hard (JS + Paywall)** | 5 | Partially skipped | SKIP_HTML (BBC, CNBC, FT) | 20-30% |
| **Thai** | 4 | Mixed | RSS if available | 60-70% |
| **TOTAL** | 27 | ~70% effective | Hybrid | **~70-75%** |

---

## 8. ACTIONABLE NEXT STEPS

### **Recommended Path: Phase 1 → Manager Review → Phase 2 (if needed)**

#### **STEP 1: Phase 1 Implementation (1.5 hours)**
```
Task 1: Lower threshold (10 min)
  - Change MIN_CONTENT_LENGTH = 300 → 100
  - Add MIN_PREVIEW_LENGTH = 100
  - Mark articles 100-300 chars as status="partial"

Task 2: Add telemetry (30 min)
  - Track per-source: status, method, http_code, reason, elapsed_time
  - Generate summary report: X success, Y partial, Z failed

Task 3: Add retry logic (20 min)
  - safe_request() → safe_request_with_retry()
  - Handle 429 (rate limit) + timeout with backoff

Task 4: Expand to 70+ sources (30 min)
  - Add RSS-heavy tech, business, Thai sources
  - Test 5-10 before full rollout
```

**Result:** 27 sources → 100 sources, 5-10 min → still 5-10 min, articles 200-500 → 400-1500

---

#### **STEP 2: Show Manager Phase 1 Results**
```
"After 1 week of Phase 1:
- Scraped: 1,200 unique articles
- Status breakdown: 950 success (79%), 200 partial (17%), 50 failed (4%)
- Paywall extraction: 150+ headlines from FT/Bloomberg
- Speed: 100 sources in 7 minutes
- Memory: 600 MB

Questions for Phase 2:
1. Is 79% + 17% partial coverage sufficient?
2. If NO → Need Playwright (60+ min execution, 10-15 GB RAM)
"
```

---

#### **STEP 3: Phase 2 Decision (If Needed)**
```
If manager says: "Get more from hard sites" →
  Option A: Deploy Playwright on cloud (AWS EC2, not local PC)
  Option B: Accept partial content from paywalls (headline + preview)
  Option C: Only scrape FT/WSJ periodically (not in main pipeline)
```

---

## 9. CURRENT BUGS/LIMITATIONS IN CODE

### **Bug 1: Silent Failures (No Logging per Source)**
```python
# Line 479: scrape_with_smart_fallback returns (articles, method)
# Issue: No tracking of WHY source failed
# Fix: Add telemetry dict with status + reason
```

### **Bug 2: No Retry on HTTP 429/Timeout**
```python
# Line 231: safe_request() has single try-except
# Issue: Rate limit → permanent skip instead of backoff
# Fix: Add max_retries + exponential backoff
```

### **Bug 3: MIN_CONTENT_LENGTH Too Strict**
```python
# Line 347: MIN_CONTENT_LENGTH = 300
# Issue: Discards paywall previews (100-300 chars)
# Fix: Add MIN_PREVIEW_LENGTH = 100, mark as "partial" status
```

### **Bug 4: SKIP_HTML_SOURCES Hardcoded**
```python
# Line 512: SKIP_HTML_SOURCES = {"BBC", "CNBC", "Financial Times"}
# Issue: Can't override per-source; hard to expand
# Fix: Move to database/config with per-source settings
```

---

## 10. SUMMARY TABLE: Current vs After Upgrades

| Metric | Current | Phase 1 | Phase 2 |
|--------|---------|---------|---------|
| **Sources** | 27 | 100 | 100+ |
| **Success Rate** | 70-75% | 80-85% | 95%+ |
| **Partial (Paywall)** | 0% (skipped) | 10-15% | N/A (full text) |
| **Full Text Rate** | ~70% | ~70% | ~95% |
| **Speed (100 sources)** | N/A | 10-15 min | 50-80 min ❌ |
| **Memory** | <1 GB | <1 GB | 10-15 GB ❌ |
| **Effort** | N/A | 1.5 hours | 8-10 hours + cloud setup |
| **Recommended?** | Current state OK | ✅ YES | ❌ NO (local), only cloud |

---

## Conclusion

**What you CAN scrape today:**
- ✅ 80% of news sites with RSS feeds (fast, reliable)
- ✅ 15-20% more headlines from paywalled sites (after lowering threshold)

**What you CAN'T scrape today:**
- ❌ Full text from JS-rendered sites (BBC, CNBC, Mashable)
- ❌ Premium content behind hard paywalls (NYT, HBR)
- ❌ Sites with anti-bot protection (LinkedIn)

**What you SHOULD do next:**
1. **Phase 1** (1.5 hours): Lower threshold + telemetry + retry logic
2. Show manager the report
3. **Phase 2** (if needed): Only on cloud, not local machine

---
