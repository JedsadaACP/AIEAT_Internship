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

## 📖 Development Roadmap & Action Plan

### Phase 1: Scraper Module Development ✅ (Current)
**Goal:** Build robust scraper covering all conditions

#### Completed
- [x] RSS feed discovery and parsing
- [x] Content extraction with newspaper3k
- [x] CSV validation output
- [x] DB-ready fields (url_hash, full_content, matched_tags)

#### In Progress
- [ ] **Develop HTML scraper fallback** (when RSS unavailable)
- [ ] **Handle edge cases:**
  - Paywalled content detection
  - Login screen detection
  - Rate limiting / anti-bot measures
  - Timeout handling
  - Malformed RSS feeds
- [ ] **Test coverage:** RSS + HTML scraping across 10+ sources

#### Deliverable
- Working scraper module (RSS + HTML)
- Test results document
- Knowledge sharing session with team

---

### Phase 2: Database Integration & Testing (Next 2 Weeks)
**Goal:** Connect scraper to database and validate end-to-end workflow

#### Week 6 Tasks
- [ ] **Create database interaction layer**
  - Insert articles into `articles_meta` and `article_content`
  - Link tags via `article_tag_map` junction table
  - Implement deduplication using `url_hash`
  - Query sources and keywords from database
- [ ] **Test scraper → database pipeline**
  - Run scraper on 4 test sources
  - Verify data integrity in database
  - Test duplicate handling
- [ ] **Convert notebook to production code**
  - Extract logic to `app/services/scraper_service.py`
  - Add logging and error handling

#### Week 7 Tasks
- [ ] **Present scraped news in database**
  - Query and display articles from DB
  - Show statistics (article count, sources, keywords)
  - Export sample data for review
- [ ] **Prepare for LLM integration**
  - Test Typhoon-Translate 1.5 model locally
  - Design prompt templates for scoring
  - Plan AI engine architecture

#### Knowledge Sharing
- [ ] Weekly presentation of sub-task completion
- [ ] Share Jupyter/Colab notebooks with team
- [ ] Document learnings and challenges
- [ ] 2-week advance action plan for next phase

---

### Phase 3: AI Model Integration (Week 8-9)
**Goal:** Implement local LLM for article scoring and translation

#### Tasks
- [ ] **Try LLM model (Typhoon-Translate 1.5)**
  - Load model using ctransformers
  - Test inference speed and quality
  - Optimize for CPU execution
- [ ] **Implement scoring engine**
  - Design scoring prompt
  - Score articles 1-5 based on significance
  - Store scores in `articles_meta.ai_score`
- [ ] **Implement translation**
  - Translate top-scoring articles to Thai
  - Store in `article_content.thai_content`
  - Quality validation

#### Deliverable
- Working AI engine
- Sample scored and translated articles
- Performance benchmarks

---

### Phase 4: UI Development (Week 10-11)
**Goal:** Build PyQt6 desktop application

#### Tasks
- [ ] Dashboard screen (3-pane layout)
- [ ] Configuration screens (sources, keywords, settings)
- [ ] News reader with Thai translation view
- [ ] Control bar (start/stop scraper, model selection)

---

### Phase 5: Integration & Testing (Week 12)
**Goal:** End-to-end system testing and deployment

#### Tasks
- [ ] Full pipeline integration test
- [ ] User acceptance testing
- [ ] Documentation finalization
- [ ] Packaging with PyInstaller

---

## 🤝 Contributing & Collaboration

This is an internship project for AIEAT. Contributors should follow this workflow:

### Weekly Workflow
1. **Complete assigned sub-task** for the week
2. **Test thoroughly** and document results
3. **Share knowledge** with team via:
   - Jupyter notebooks with explanations
   - Google Colab links for testing
   - Group presentation of completed work
4. **Plan 2 weeks ahead** in each presentation
5. **Commit to repo** with clear messages

### Git Workflow
1. Clone the repo: `git clone https://github.com/YOUR_USERNAME/AIEAT_Internship.git`
2. Create feature branch: `git checkout -b feature/your-feature`
3. Make changes and test locally
4. Commit: `git commit -m "[Phase N] Description of changes"`
5. Push: `git push origin feature/your-feature`
6. Create pull request for team review

### Code Style
- Follow PEP 8
- Use type hints where applicable
- Add docstrings to functions
- Keep functions under 50 lines
- Include unit tests for new features

### Knowledge Sharing
- **After each sub-task:** Share Colab/Jupyter pipeline with team
- **Weekly presentations:** Demo completed work + plan next 2 weeks
- **Documentation:** Update README with learnings and challenges

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
