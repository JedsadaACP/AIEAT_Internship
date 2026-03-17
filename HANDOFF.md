# Developer Handoff & Knowledge Transfer

This document serves as the primary technical handoff for future employees and the open-source community taking over the AIEAT News Dashboard project.

## 🧠 Core Architecture Decisions

### 1. Flet for UI
**Why?** The initial UI was complex to build in typical web frameworks while binding to local Python scraping libraries. Flet allowed us to write the entire desktop GUI in Python, compiling down to a standalone cross-platform app while directly invoking our Python classes seamlessly.

### 2. Local LLM Strategy (Ollama)
**Why?** Privacy and cost. Connecting to OpenAI APIs is expensive for continuous scraping. We use **Ollama** running locally on the user's desktop hardware, using `typhoon2.5-qwen3` for native Thai translation and scoring. Our `ai_engine.py` calls localhost `11434`.

### 3. Waterfall Scraping Engine
**Why?** RSS feeds are fast but provide incomplete text. HTML parsing is thorough but brittle.
**Our design in `scraper_service.py`:**
1. Async fetch RSS feeds and sitemaps.
2. Filter URLs against a deduplication table (`sqlite`) and exact date constraints.
3. Fallback extraction chain: `trafilatura` first -> `newspaper` if it fails -> `BeautifulSoup` generic parsing if others fail.

## 🐛 Known Quirks & Fixes

### 1. The `UNIQUE` Constraint Bug in Tags
SQLite does not support altering constraints natively. We handled this by creating separate records per `profile_id`. A profile-aware approach must always be maintained in `backend_api` when updating tag values.

### 2. PyInstaller Missing Assets
If PyInstaller outputs an `.exe` but `trafilatura` crashes in production, it is because PyInstaller doesn't bundle data files naturally. 
*Rule:* Anytime you add a new library with static files (like stoplists or dictionaries), update `build_app.spec` with `collect_data_files('new_package')` and append it into the `datas=` array.

### 3. Flet Navigation Cache
If you re-instantiate a page component (like `DashboardPage`) on route changes, state resets. To maintain fast navigation, we keep `page_cache` in `main.py`. Be careful to wipe `page_cache['dashboard_logic']` when a user switches profiles so they don't see stale data!

## 🔭 Future Ideas for Expansion

1. **Auto-Trigger Scheduler:** Right now scraping is triggered explicitly. Adding an `apscheduler` daemon to auto-scrape at 3 AM local time would improve UX.
2. **LoRA Fine-tuning integration:** Allow the UI to select custom model weights (LoRA adapters) directly for specialized translation tones.
3. **Automated Publish to CMS:** Webhook integration in `app/services` to push a "scored and translated" article directly to a WordPress/Ghost blog.
