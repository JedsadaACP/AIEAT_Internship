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

## 📊 Current Status: Week 4-5 - Component 1: Web Scraping

### ✅ Completed (Week 1-3: System Design Phase)
- [x] **Week 1:** Research and requirements gathering
- [x] **Week 2:** System architecture, database schema (11 tables), UX/UI design
- [x] **Week 3:** Functional design and component planning

### ✅ Completed (Week 4-5: Component 1 - Part 1)
- [x] RSS feed discovery and parsing
- [x] Content extraction with newspaper3k
- [x] Keyword matching and filtering
- [x] Database implementation (11 tables)
- [x] CSV output for validation
- [x] DB-ready fields (url_hash, full_content, matched_tags, status)

### 🎯 This Week (Week 5 - Component 1 Completion)
- [ ] **Complete Scraper Module** — HTML fallback, RSS coverage, all edge cases
- [ ] **Database Integration** — Scraper-to-DB interaction and testing
- [ ] **Knowledge Sharing** — Document pipeline in Colab/Jupyter for team
- [ ] **Data Pipeline** — Scrape → DB → Present workflow
- [ ] **LLM Model Testing** — Test Typhoon-Translate locally
- [ ] **Planning** — Action plan for Component 2-3 (next 2 weeks)

### 🚧 Upcoming Components (Week 6-9)
- **Week 5-6:** Component 2 - Data Processing and Annotation
- **Week 6-8:** Component 3 - Training / Fine Tuning (AI scoring & translation)
- **Week 9:** Component 4 - Merge to Product in Docker
- **Week 10:** Component 5 - GitHub upload + installation guideline


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

## 📖 Development Roadmap (15-Week Timeline)

### ✅ Week 1: System Design - Research
- Project charter and requirements
- Technology stack selection

### ✅ Week 2: System Design - Architecture
- System architecture design
- Database schema (11 tables)
- UX/UI mockups (6 screens)

### ✅ Week 3: System Design - Functional Design
- Component specifications
- Data flow diagrams
- Integration planning

### 🚧 Week 4-5: Component 1 - Web Scraping / Data Crawling
- RSS feed discovery and parsing
- HTML fallback scraper (if needed)
- Content extraction (newspaper3k)
- Database integration
- **Current progress:** 70% complete

### Week 5-6: Component 2 - Data Processing and Annotation
- Clean and normalize scraped data
- Keyword tagging and categorization
- Data quality validation

### Week 6-8: Component 3 - Training / Fine Tuning
- AI scoring engine (Typhoon-Translate)
- Thai translation pipeline
- Model optimization

### Week 9: Component 4 - Merge to Product in Docker
- Containerize application
- Configuration management
- Deployment testing

### Week 10: Component 5 - GitHub Upload + Installation Guideline
- Code documentation
- Installation guide
- Unit testing

### Week 10-11: User Acceptance Testing
- End-to-end testing
- Bug fixes and refinements
- Performance optimization

### Week 12: Documentation - GitHub & Installation
- Complete technical documentation
- User manual
- API documentation

### Week 13-14: Documentation - Study Report
- Project report writing
- Results analysis
- Lessons learned

### Week 14-15: Documentation - Study Presentation
- Presentation preparation
- Demo video
- Final presentation

---

## 🧭 HTML Fallback Scraper Design (Post-RSS)

We already have RSS working. This section defines how we add a careful HTML fallback while staying privacy-first and lightweight.

### What We Will Do
- **Decision flow per source:** RSS → sitemap (from robots.txt) → shallow HTML crawl (front/section pages) → article extraction.
- **Static HTTP only:** Use `requests` + `newspaper3k` (no external APIs; headless only if later approved).
- **Polite, low-volume:** Few pages per domain, short timeouts, backoff on 429/403, normalized URLs for dedup.

### What Usually Works
- Server-rendered news sites (WordPress/typical media).
- Sites exposing `sitemap.xml` via `robots.txt`.
- AMP pages via `<link rel="amphtml">` when main page is noisy.

### Likely Pain / Low ROI (for MVP)
- Hard paywalls/login walls (content not in HTML).
- Cloudflare/JS challenges (403/503 loops) without headless.
- Heavy JS/infinite scroll with no discoverable JSON feed.

### Crawl/Extract Heuristics
- **Link filters:** Same-domain only; allow slugs with dates or `/news/`, `/article/`, `/story/`; block login/subscribe/tag/category/search/pdf/media.
- **Caps:** Max ~5–10 seed pages per domain; max ~20 article links per seed; 3–5s timeout; retries=1.
- **Content checks:** Use newspaper3k readability; if too short, try AMP or canonical `og:url`; keep full text for DB, snippet for preview.
- **Metadata:** title, author(s), published (fallback now), url_hash, full_content, matched tags.

### Logging & Failure Classes
- Fetch error, parse error, paywall/login, JS-required, blocked (429/403), empty/too-short content.
- Per-source stats: pages fetched, links found, articles kept, errors.

### Implementation Plan
1) Add decision flow to scraper: RSS → sitemap → shallow HTML crawl.
2) Add robots.txt parse + sitemap fetch to seed URLs.
3) Add link allow/deny heuristics and caps per domain.
4) Keep politeness defaults (UA, timeout, backoff, low concurrency).
5) Log categorized failures and per-source summary.
6) Pilot on 2–3 non-RSS sources; refine heuristics before broadening.

### Opt-In Headless (Later, if needed)
- Only for specific blocked/JS sites, behind a feature flag, and kept minimal to preserve privacy/offline constraints.

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
