# AIEAT News Dashboard — User Manual

**Version:** 1.0.0 | **Last Updated:** March 2026

> AIEAT (AI-Enhanced Article Tool) is a local-first news intelligence dashboard. All AI processing runs on your own machine — no data is sent to the cloud.

---

## Table of Contents
1. [System Requirements](#system-requirements)
2. [Installation](#installation)
3. [Understanding Profiles](#understanding-profiles)
4. [Quick-Start Scenario: The Finance Analyst](#quick-start-scenario-the-finance-analyst)
   - Step 1: Launch & Select Your Profile
   - Step 2: Add News Sources
   - Step 3: Set Your Keywords
   - Step 4: Run the Scraper
   - Step 5: AI Scoring
   - Step 6: Read & Translate
5. [Advanced Tips](#advanced-tips)
6. [Troubleshooting](#troubleshooting)

---

## System Requirements

| Item | Requirement |
|------|-------------|
| Operating System | Windows 10 / 11 (64-bit) |
| RAM | 8 GB minimum (16 GB recommended for AI scoring) |
| Disk Space | 5 GB free (for app + AI model) |
| Internet | Required for scraping news sources |
| Ollama | Installed automatically if you check the box during setup |

---

## Installation

### Standard Installation
1. Double-click **`AIEAT_Setup.exe`**.
2. Follow the on-screen wizard — accept the default install path unless you have a reason to change it.
3. On the **"AI Engine"** screen, you will see:

   > ☐ **Install Ollama AI Engine + Typhoon 2.5 Model**

   **Check this box.** This downloads the local AI model (~3–4 GB) that powers scoring and translation. Without it, those features will not work.

4. Wait for both the app and the model to finish installing. The "Installing Typhoon 2.5…" step can take 5–10 minutes depending on your internet speed.
5. Click **Finish**. AIEAT is now ready.

> **Note:** If you skipped the Ollama checkbox and want to install it later, run `Install_AI_Engine.bat` in the AIEAT installation folder.

---

## Understanding Profiles

AIEAT uses **Profiles** to keep your news completely separated. Each profile has:
- Its own set of **News Sources** (URLs)
- Its own **Keywords** (used to filter scraped articles)
- Its own **Article database** (articles from Profile A never mix with Profile B)

**Default profiles include:** Finance & Markets, Technology, Health, and General News.

You can switch profiles at any time from the top-right Profile button. The dashboard refreshes immediately to show only that profile's articles.

---

## Quick-Start Scenario: The Finance Analyst

> *Imagine you are a Finance Analyst. Every morning you need the top 5 most relevant business articles, scored for importance, and ready to read in Thai. Here is how AIEAT automates that routine.*

---

### Step 1: Launch & Select Your Profile

1. Open **AIEAT** from your desktop shortcut.
2. In the **top-right corner**, click the **Profile** button.
3. Select **Profile 2: Finance & Markets** from the dropdown.
4. The dashboard will reload — you are now working entirely within the Finance profile. All scrapes, scores, and articles are stored separately for this profile.

---

### Step 2: Add News Sources

> ⚠️ **Do this BEFORE running the scraper.** The scraper only visits sources you have added.

1. Click **User Config** in the left sidebar.
2. Scroll to the **"News Sources"** section.
3. To add a single source, type or paste the URL into the input field, then click **Add Source**.
   - Example: `https://www.reuters.com/business`
4. To add many sources at once, click **Import File** and select a `.txt` or `.csv` file where:
   - Each line contains exactly **one URL**
   - Lines starting with `#` are treated as comments and ignored

   **Example file content:**
   ```
   # Finance sources
   https://www.reuters.com/business
   https://www.bloomberg.com/markets
   https://finance.yahoo.com
   ```

5. To remove a source, click the **trash icon** next to it.

> **Pro-tip:** Quality matters more than quantity. 10 focused sources give better results than 50 random ones.

---

### Step 3: Set Your Keywords

> ⚠️ **Critical prerequisite — do this before scraping.** Keywords are the filter the scraper uses to decide which articles to keep. If your keyword list is empty, **zero articles will be saved**.

1. While still in **User Config**, scroll down to the **"Keywords"** section.
2. Add keywords relevant to your profile. For Finance, examples include:
   - `Stock Market`, `Revenue`, `Acquisition`, `GDP`, `Interest Rate`, `Earnings`
3. Each keyword you add acts as an OR filter — an article is saved if it contains **any** of your keywords.
4. Click **Save** to confirm your keywords.

> **Tip:** Start with 5–10 broad keywords, then refine based on what articles you actually get.

---

### Step 4: Run the Scraper

1. Click **Dashboard** in the left sidebar to return to the main screen.
2. Click the blue **Start Scraping** button in the left sidebar.
3. The scraper will visit each of your news sources and attempt to extract article text.
4. Watch the **progress bar** at the bottom-left of the screen — it updates as each source is processed.

**What happens during scraping:**
- The scraper fetches each article's full text
- It checks whether the article contains at least one of your profile's keywords
- Only matching articles are saved to your profile's database
- Sources that are unreachable are skipped silently (check `logs/app.log` if you suspect a source is always failing)

> **Note:** Some websites have strict access restrictions. If a source consistently yields 0 articles, it may require login credentials or have bot-detection that prevents scraping.

---

### Step 5: AI Scoring

After scraping, you may have 20–100+ articles. The AI scoring step ranks them by relevance so you only read what matters.

1. At the top of the **Dashboard**, click **Batch Score**.
2. The local Typhoon 2.5 AI will read each article and assign a **relevance score from 1–10**.
   - Scoring takes roughly 5–30 seconds per article, depending on article length and your hardware.
   - A progress indicator will update as each article is scored.
3. Once scoring is complete, click **Filter** in the sidebar.
4. Set the filter to **"High Relevance (5+)"** to show only the most important articles.

**Score guide:**
| Score | Meaning |
|-------|---------|
| 8–10 | Highly relevant — read immediately |
| 5–7 | Relevant — read if you have time |
| 1–4 | Low relevance — safe to skip |

---

### Step 6: Read & Translate

1. In the filtered dashboard, click **View Detail** on the article you want to read.
2. The detail page shows the full article text, source, and its AI score.
3. Click the **Translate** button at the top of the detail page.
4. The Typhoon AI will translate the full article into professional Thai.
5. The translated text appears below the original — both are shown together for reference.

> ✅ **You have now gone from 0 to a scored, translated, daily briefing — fully local and private.**

---

## Advanced Tips

### Creating & Customizing Profiles
1. Go to **User Config → Profiles** (or **Settings → Database Operations** on some builds).
2. Under **"Manage Profiles"**, you can rename a profile or edit its keywords.
3. To start fresh with any profile, use **Clear Profile Data** — this removes all articles for that profile but keeps your sources and keywords.

> **Important:** Matching your sources to your keywords is essential.  
> If your keywords are `"Finance"` but your only source is `techcrunch.com`, you will get very few or zero articles because TechCrunch mostly writes about technology, not finance.

### Changing the AI Style
1. Click **Style Settings** in the sidebar.
2. You can adjust how the AI writes its scores and translations — e.g., formal vs. conversational, detailed vs. concise.
3. Changes take effect on the next Batch Score or Translate operation.

### Exporting Data
- Scored articles can be exported from **Dashboard → Export** (if available in your version).
- For bulk data analysis, the raw database is located at `data/aieat.db` in your installation folder. It is a standard SQLite file readable by any SQL browser.

---

## Troubleshooting

### "Ollama not running" error
**Cause:** The Ollama AI engine did not start automatically with Windows.  
**Fix:**
1. Open your **Start Menu** and search for `Ollama`.
2. Click it — a small llama 🦙 icon will appear in your **system tray** (bottom-right corner of the screen).
3. Wait 10–15 seconds, then try the operation in AIEAT again.

> If Ollama is not installed at all, run **`Install_AI_Engine.bat`** from the AIEAT installation folder.

---

### "0 articles passed filters"
**Cause:** Your scraper ran, but no saved articles matched your profile's keyword list.  
**Fix:**
1. Go to **User Config → Keywords** and verify you have at least one keyword set.
2. Make sure the keywords are broad enough. `"S&P 500"` is very specific; `"stock"` will match far more articles.
3. Check that your sources are actually publishing articles about your keywords.

---

### Progress Bar Freezes
**Cause:** The visual progress bar sometimes pauses during long operations, but the underlying process is still running.  
**Fix:**
1. Wait 2–3 minutes before assuming it has truly frozen.
2. Watch the **on-screen progress text** next to the bar — if the article count or URL is changing, the scraper is still working.
3. If the app is genuinely frozen, close it and check **`logs/app.log`** in the AIEAT installation folder for the last error.

> **Note:** To find the `logs` folder, open File Explorer and navigate to:  
> `C:\Program Files\AIEAT\logs\app.log` (or wherever you chose to install AIEAT)  
> There is no terminal window in the installed version — all errors go to `app.log`.

---

### Scraper Gets 0 Articles from a Specific Source
**Cause:** The website may require login, use heavy JavaScript rendering, or block automated access.  
**Fix:**
1. Try opening the source URL in your browser to confirm it is accessible.
2. Some news sites offer a public RSS feed — use the RSS URL instead of the homepage.
3. If the site consistently fails, remove it and replace it with an alternative source.

---

### AI Scoring Seems Inaccurate
**Cause:** The Typhoon 2.5 model scores based on how well the article content matches your declared keywords. If your keywords are too generic or your sources are off-topic, scores will feel random.  
**Fix:**
1. Go to **User Config → Keywords** and make your keywords more specific and domain-focused.
2. Consider adjusting the **Style Settings** to give the AI more context about your role (e.g., "Finance analyst at an investment bank").
3. Re-run **Batch Score** after updating settings.

---

## Quick Reference

| Action | Where to click |
|--------|---------------|
| Switch profile | Top-right Profile button |
| Add news sources | User Config → News Sources |
| Set keywords | User Config → Keywords |
| Start scraping | Dashboard → Start Scraping (left sidebar) |
| Score articles | Dashboard → Batch Score (top bar) |
| Filter by score | Dashboard → Filter → High Relevance (5+) |
| Read full article | Dashboard → View Detail |
| Translate article | Detail page → Translate button |
| Change AI style | Style Settings (left sidebar) |
| Check error logs | `logs/app.log` in installation folder |

---

*AIEAT is an open-source project. For the latest version and release notes, visit the GitHub repository.*
