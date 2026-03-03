============================================
  AIEAT News Dashboard v1.0 - Setup Guide
============================================
>> SYSTEM REQUIREMENTS
- Windows 10/11 (64-bit)
- Microsoft Edge WebView2 Runtime
  (pre-installed on most Windows 10/11 machines)

>> FOR AI FEATURES (Scoring & Translation)
The app works without Ollama for basic scraping.
To enable AI-powered scoring and translation:

1. Install Ollama:
   Download from https://ollama.com and install

2. Pull the Typhoon model (open Terminal/PowerShell):
   ollama pull scb10x/typhoon2.5-qwen3-4b:latest

3. Ollama starts automatically after install.
   If not, run: ollama serve

>> WITHOUT OLLAMA
These features work without Ollama:
- Import news sources from CSV
- Scrape articles from 74+ sources
- Filter, search, and browse articles
- Export data

>> TROUBLESHOOTING
- App won't start:
  Install WebView2 from https://go.microsoft.com/fwlink/p/?LinkId=2124703
- "No models found" in config:
  Make sure Ollama is running (ollama serve)
- Check logs\app.log for error details
