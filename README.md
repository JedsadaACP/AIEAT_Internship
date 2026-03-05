# AIEAT News Dashboard

A powerful, local-first news curation and translation application built by the Artificial Intelligence Entrepreneur Association of Thailand (AIEAT). Designed specifically for content writers and social media managers to aggregate, score, and translate AI and Tech news using automated web scraping and localized LLMs.

## 🚀 Features

- **Automated Scraping**: Aggregates RSS feeds and sitemaps from 74+ global technology news sources.
- **Content Extraction**: Advanced HTML parsing using `trafilatura` and `newspaper` to bypass paywalls and cookie banners.
- **Local AI Engine**: Full integration with `Ollama` running quantized models (e.g., Typhoon 2.5 4B, TranslateGemma) for 100% private, offline inference.
- **Smart Scoring**: Automatically scores articles from 1-10 based on customized relevance to defined User Profiles and domain keywords.
- **Automated Translation**: Translates English tech journalism into fluent Thai, customized with system prompts matching your organization's tone.
- **User Profiles**: Create distinct intelligence profiles (e.g. "Tech Team", "Finance Dept") with separate monitored keywords and organization names.
- **Desktop UI**: A fast, responsive frontend built with Flet/Flutter for cross-platform ease.

## 📦 Installation (End Users)
1. Download `AIEAT_Distribution.zip`
2. Run `AIEAT_Setup.exe` to install the UI
3. Run `Install_AI_Engine.bat` to install Ollama and the Typhoon LLM
4. Launch the application from the Desktop shortcut

## 🛠️ Tech Stack
- **Frontend**: Python + Flet (Flutter)
- **Backend Core**: Python 3.13
- **Scraping**: `aiohttp`, `trafilatura`, `feedparser`, `beautifulsoup4`
- **Database**: SQLite3
- **AI Backend**: Ollama HTTP API

## 🏃‍♀️ Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/JedsadaACP/AIEAT_Internship.git
   cd AIEAT_Internship
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python -m app.ui.main
   ```

## 🏗️ Building the Executable

This project uses `PyInstaller` and `Inno Setup 6` for distribution. Since the project uses specialized NLP scraping dependencies, you must use the custom `.spec` file.

```bash
# Clean previous builds
rmdir /s /q dist build

# Build standalone executable (bundles missing NLP data files)
python -m PyInstaller build_app.spec --clean --noconfirm

# Compile installer (Requires Inno Setup installed)
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer.iss
```

## 📄 License
This project is open-source under the MIT License.
