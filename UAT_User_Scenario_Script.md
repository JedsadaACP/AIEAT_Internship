# AIEAT - User Acceptance Testing (UAT) Scenario Script

**Tester Goal**: You are an AI Trends Analyst. Your job is to collect the latest AI news from specific technology websites, let the AI score their relevance, and translate the most important ones into Thai to include in your weekly boss's report. 

Please follow this script from **Start to Stop**. If you get confused, click the wrong thing, or feel something is "clunky", **PLEASE NOTE IT DOWN**. We are testing the *User Experience (UX)*, not your computer skills!

---

### Phase 1: Setup & Import
1. **Open the Application**: Double-click the `AIEAT` shortcut on the desktop. 
2. **First Impressions**: Look at the main dashboard. *Feedback check: Is it clear what the app does?*
3. **Configuration**: Navigate to the **Style / Config** page.
4. **Import Sources**: 
    - You will be provided a file named `UAT_import_template.csv`.
    - Find the "Import" button and upload this file. 
    - *Feedback check: Did the sources load correctly? Was it easy to find?*
5. **Set Keyword**: Type in the keyword `AI` and press Enter/Add. 
6. **Set AI Model**: Select `gemma` (or the default available model) from the drop-down and click **Save**.

### Phase 2: Action - Scraping News
1. **Start the Scraper**: Go to the main scraping/news page and click **Start Scraper**.
2. **Observe**: Watch the progress. 
    - *Feedback check: Do you know what the application is doing? Is the progress clear?*
3. **Stop the Scraper**: Wait for about 10-15 articles to appear, then click **Stop**.

### Phase 3: AI Analysis & Translation (The Core Value)
1. **Auto-Score**: Enable the auto-scoring feature (if not already enabled) and wait for the AI to assign scores based on the keyword `AI`.
2. **Filter by Score**: Find the filter options and select to view only "High Score" articles.
3. **Read & Translate**: 
    - Click on the headline of the top-scored article.
    - Click the **Translate (Thai)** button and wait for the output.
    - *Feedback check: Did it take too long? Was the formatting readable?*
4. **Copy & Paste**: Use the copy button to copy the Thai text and paste it into a blank Notepad or Word document.

### Phase 4: Final Export
1. **Export Data**: Go back to the main list (still filtered by High Score).
2. **Download**: Click **Export to Excel / CSV** and save it to your documents.
3. **Verification**: Open the exported file to ensure your data is there.

---

### 🛑 STOP HERE - Feedback Time
Now that you have completed the flow, please answer:
1. What was the *most confusing* part of the application?
2. Did any buttons or menus feel "hidden" or hard to use?
3. If you could change *one thing* about the interface, what would it be?
