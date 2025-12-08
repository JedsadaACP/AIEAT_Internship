# AIEAT Automated AI News Pipeline

A standalone desktop application that automates the complete workflow of gathering, scoring, and translating global tech news into Thai—with zero external API calls and full data privacy.

## 🎯 Project Overview

**Client:** AI Entrepreneur Association of Thailand (AIEAT)  
**Goal:** Eliminate manual news curation burden through AI-powered automation  
**Approach:** Local LLM (Typhoon-Translate 1.5) for scoring and translation  

### Key Features
- 🔍 **Automated RSS Discovery** — Smart feed detection from generic URLs
- 📰 **Content Extraction** — Clean article text with ad/noise removal
- 🤖 **AI Scoring** — Local LLM assigns significance scores
- 🌏 **Thai Translation** — Professional translation for top-scoring articles
- 🔒 **Privacy-First** — No cloud APIs, fully offline operation
- 💾 **SQLite Database** — 11-table normalized schema

---

## 📊 Current Status: Phase 1 Complete ✅

### ✅ Completed (Week 5)
- [x] RSS feed discovery and parsing
- [x] Content extraction with newspaper3k
- [x] Keyword matching and filtering
- [x] Database schema design (11 tables)
- [x] CSV output for validation
- [x] DB-ready fields (url_hash, full_content, matched_tags, status)

### 🚧 Next Phase (Week 6)
- [ ] Database integration (insert articles)
- [ ] AI scoring engine implementation
- [ ] Convert notebook to production code (`scraper_service.py`)

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Windows/Linux/macOS

### Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/AIEAT_Internship.git
cd AIEAT_Internship

# Install dependencies
pip install -r requirements.txt

# Initialize database
python init_db.py
```

### Run Phase 1 Scraper

```bash
# Open Jupyter Notebook
jupyter notebook News_Scraper.ipynb

# Or run all cells programmatically
jupyter nbconvert --to notebook --execute News_Scraper.ipynb
```

### Test Output

After running, check:
- `scraped_data_from_homepages.csv` — CSV with all scraped articles
- Verify columns: source, headline, author, url, published, keywords, url_hash, full_content, matched_tags, status

---

## 📁 Project Structure

```
AIEAT_Internship/
├── News_Scraper.ipynb          # Phase 1: Scraper prototype
├── main.py                     # Application entry point (TBD)
├── init_db.py                  # Database initialization
├── requirements.txt            # Python dependencies
├── README.md                   # This file
│
├── app/
│   ├── __init__.py
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py         # Configuration management
│   ├── services/
│   │   ├── __init__.py
│   │   ├── database_manager.py # Database operations
│   │   ├── scraper_service.py  # Scraper (TBD Phase 2)
│   │   └── ai_engine.py        # AI scoring/translation (TBD)
│   ├── ui/
│   │   ├── __init__.py
│   │   └── main_window.py      # PyQt6 GUI (TBD)
│   └── utils/
│       └── __init__.py
│
├── data/
│   ├── schema.sql              # Database schema (11 tables)
│   ├── aieat_news.db           # SQLite database (generated)
│   └── models/                 # AI model files (TBD)
│
├── logs/                       # Application logs (generated)
└── notebooks/                  # Experimental notebooks
```

---

## 🗄️ Database Schema

11-table normalized SQLite database:

1. **master_status** — Central status dictionary
2. **models** — AI model registry
3. **system_profile** — System configuration (singleton)
4. **tags** — Keywords and domains
5. **sources** — News sources
6. **styles** — Output style templates
7. **style_params** — Style parameters
8. **articles_meta** — Article metadata (lightweight)
9. **article_content** — Article full text (heavy)
10. **article_tag_map** — Article-to-tag junction table
11. **logs** — System logs

---

## 🔧 Configuration

### Test Sources (Phase 1)
- Blognone (https://www.blognone.com)
- TechCrunch (https://techcrunch.com)
- The Verge (https://www.theverge.com)
- BBC Tech (https://www.bbc.com)

### Keywords
AI, Artificial Intelligence, Machine Learning, Data, Google, Microsoft, Meta, NVIDIA, Crypto

### Settings
- **Lookback window:** 14 days
- **Min content length:** 300 characters
- **User agent:** Chrome 120

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| Language | Python 3.10+ |
| GUI | PyQt6 |
| Database | SQLite3 |
| RSS Parsing | feedparser |
| Content Extraction | newspaper3k |
| AI Model | Typhoon-Translate 1.5 (.gguf) |
| AI Inference | ctransformers (CPU) |
| Packaging | PyInstaller (.exe/.app) |

---

## 📖 Development Roadmap

### Phase 1: Collection (Week 5) ✅
- RSS discovery and parsing
- Content extraction
- CSV validation output

### Phase 2: Database Integration (Week 6)
- Insert articles into database
- Source/tag management
- Deduplication logic

### Phase 3: AI Scoring (Week 7)
- Local LLM integration
- Significance scoring
- Quality filtering

### Phase 4: Translation (Week 8)
- Thai translation
- Output formatting
- Quality validation

### Phase 5: UI (Week 9-10)
- PyQt6 dashboard
- Configuration screens
- Results viewer

---

## 🤝 Contributing

This is an internship project for AIEAT. Contributors should:

1. Clone the repo
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make changes and test
4. Commit with clear messages: `[Phase N] Description`
5. Push and create pull request

### Code Style
- Follow PEP 8
- Use type hints where applicable
- Add docstrings to functions
- Keep functions under 50 lines

---

## 📝 License

This project is developed for AI Entrepreneur Association of Thailand (AIEAT).  
License: TBD

---

## 📧 Contact

**Project Lead:** [Your Name]  
**Organization:** AI Entrepreneur Association of Thailand (AIEAT)  
**Repository:** https://github.com/YOUR_USERNAME/AIEAT_Internship

---

## 🙏 Acknowledgments

- AIEAT community
- Typhoon-Translate team
- Open-source contributors (feedparser, newspaper3k, PyQt6)

---

**Last Updated:** December 9, 2025  
**Phase:** 1 (Scraper Prototype) ✅
