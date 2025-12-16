# V9 Async Scraper: Notebook Design (Cell by Cell)

This document outlines the logical flow of the `Run_V9_Async.ipynb` notebook. This is the "Blueprint" for our modern, industrial-grade scraper.

## ♻️ Migration Strategy: Keep vs. Throw

To build the "No BS" version, we are strictly filtering components from V1-V8.

### ✅ What We KEEP (The Good Parts)
*   **The "Waterfall" Logic:** (From V4/V7) The strategy of "Try RSS first, then fallback to HTML" is efficient. We keep this but make it *Async*.
*   **The Configuration:** (From V8) `sources.json` is excellent. We keep the strict separation of Code vs. Data.
*   **The Output Schema:** (From V8) The CSV columns (`headline`, `url`, `content`, `method`) are perfect for the AIEAT system. We strictly maintain this contract.
*   **The Filters:** (From V4-V8) The Keyword & Date filtering logic works. We keep it.

### 🗑️ What We THROW (The "Bullshit")
*   **`newspaper3k`:** (V1-V8) **THROWN.** It is the #1 cause of "garbage" text (capturing ads/navbars). Replaced by `trafilatura`.
*   **`requests`:** (V1-V8) **THROWN.** Cannot handle JavaScript/React apps. Replaced by `Playwright` + `aiohttp`.
*   **`ThreadPoolExecutor`:** (V8) **THROWN.** Spawning 50 OS threads crashes RAM. Replaced by `AsyncIO` (1 thread, 50 tasks).
*   **"Fast Fail":** (V8) **THROWN.** V8 gave up too quickly on 403s. V9 will "fight back" with browser rotation.

---

## 🧱 The Foundation

### Cell 1: Environment Setup & Imports
**Purpose:** Initialize the modern async environment.
**Logic:**
1.  Import standard async libraries (`asyncio`, `aiohttp`) for non-blocking I/O.
2.  Import `playwright.async_api` for the headless browser engine.
3.  Import `trafilatura` for state-of-the-art text extraction.
4.  **Critical Check:** Verify if `nest_asyncio` is needed (Jupyter notebooks run in an existing event loop, so we need to patch it to allow nested loops).
5.  Setup robust logging that handles async log messages safely.

### Cell 2: Configuration (The Control Center)
**Purpose:** Define *what* to scrape and *how* aggressively.
**Logic:**
1.  **Sources:** Load `sources.json`.
2.  **Concurrency Limits:** Define `MAX_CONCURRENT_TABS` (e.g., 5 or 8). *This is crucial.* In V8, we crashed RAM because we spawned too many browsers. Here, we use a `Semaphore` to strictly limit active tabs.
3.  **Timeouts:** Set strict timeouts for efficient "Fast Failing".
    -   `STATIC_TIMEOUT`: 10s (for RSS/XML).
    -   `BROWSER_TIMEOUT`: 30s (for heavy JS pages).
4.  **Paths:** Define the RSS/Sitemap discovery paths (prioritizing "General" then "Tech" feeds).

---

## ⚙️ The Engine Room

### Cell 3: The `AsyncCleaner` (Extraction)
**Purpose:** Turn raw HTML into clean data (The "Trash Filter").
**Logic:**
1.  Input: Raw HTML string.
2.  **Legacy Check:** Abandon `newspaper3k` entirely.
3.  **Modern Method:** Pass HTML to `trafilatura.extract()`.
    -   Enable `include_comments=False` (remove comment sections).
    -   Enable `include_tables=False` (remove data tables).
4.  **Fallback:** If `trafilatura` returns None (rare), fall back to a simple `BeautifulSoup` text extraction to ensure we get *something*.
5.  Output: Clean, readable text string.

### Cell 4: The `AsyncNavigator` (Core Browser Logic)
**Purpose:** Manage the Playwright Browser safely.
**Logic:**
1.  **Context Isolation:** Define a function `fetch_dynamic_content(url)` that:
    -   Launches a *new* Browser Context (incognito mode equivalent) for **every single source**. This prevents site A from seeing cookies from site B (Anti-detection).
    -   Injects "Stealth" headers (User-Agent spoofing).
2.  **Smart Waiting:** Instead of `time.sleep()`, use `page.wait_for_load_state('networkidle')`. This waits until the spinner stops spinning.
3.  **Action Simulation:** Scroll down 3 times to trigger any "Lazy Loaded" content.
4.  **Cleanup:** Use `try/finally` blocks to **GUARANTEE** the page closes even if the scraper crashes. This fixes the "Memory Leak" issue.

---

## 🧠 The Brain

### Cell 5: The `SourceProcessor` (Waterfall Logic)
**Purpose:** Decide *how* to scrape a specific source (Speed vs. Power).
**Logic:**
1.  **Step 1 (The Sprint):** Try to fetch RSS feeds using `aiohttp` (Static/Fast).
    -   If successful and valid XML: Parse, extract links, and return. **STOP.**
2.  **Step 2 (The Deep Dive):** If RSS fails, perform a "Homepage Scan" using Playwright.
    -   Render the homepage fully.
    -   Extract all `<a>` tags.
    -   Filter links using "Keyword Heuristics" (e.g., url contains `/article`, `/news`, or year `2024` / `2025`).
3.  **Step 3 (The Harvest):** For every article link found:
    -   Check if it's "Static Friendly" (most news sites). Try fast fetch.
    -   If "Access Denied" (403/401), switch to Playwright Dynamic Fetch.
    -   Extract content using `AsyncCleaner`.
4.  **Telemetry:** Record exactly which method worked (RSS vs. HTML vs. Browser) for future optimization.

### Cell 6: The `Orchestrator` (Pipeline Manager)
**Purpose:** Run everything in parallel without melting the CPU.
**Logic:**
1.  Create a `Semaphore(5)` to limit concurrency.
2.  Function `process_safe(source)`:
    -   Acquire Semaphore.
    -   Run `SourceProcessor`.
    -   Release Semaphore.
3.  **The Big Bang:** Use `asyncio.gather(*tasks)` to launch all 50+ sources simultaneously. The Semaphore ensures only 5 run actively at once, while others wait in a queue. This is efficient and keeps RAM usage flat.

---

## 🏁 The Finish Line

### Cell 7: Main Execution & Export
**Purpose:** Run the loop and save data.
**Logic:**
1.  Call `await main()`.
2.  Watch the `tqdm` progress bar (V9 will use an async-compatible progress bar).
3.  **Data Validation:**
    -   Convert results to Pandas DataFrame.
    -   Check for "Empty" rows.
    -   Check for strict keyword matches.
4.  **Export:** Save `scraped_news_v9.csv` and `telemetry_v9.csv`.
5.  **Report:** Print a high-level summary:
    -   "X sources scraped in Y minutes."
    -   "Best performing method: RSS (60%)"
    -   "Top failure reason: Timeout."
