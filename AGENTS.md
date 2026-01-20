# AGENTS.md - AIEAT Project Codex

> This file defines how AI assistants should work on this project.
> **READ THIS FIRST before making any changes.**

---

## Current Status 🔨

**Phase:** Pre-UAT Bug Fixes
**Deadline:** Friday Jan 23, 2026 (Installer package due)

**Active Tasks:**
- [ ] Fix delete keywords function
- [ ] Fix delete domains function
- [ ] Fix sources add/delete
- [ ] Fix Style Setting (or remove)
- [ ] End-to-end testing
- [ ] Create installer package

**Completed:**
- ✅ Migrated from llama-cpp to Ollama backend
- ✅ GPU acceleration via Ollama
- ✅ Model selection from Ollama models
- ✅ Removed CPU/GPU toggle (obsolete with Ollama)

**Side Tasks (After Installer):**
- ⬜ Training data generation with Qwen3:8b
- ⬜ LoRA fine-tuning
- ⬜ Model evaluation

---

## Quick Start

```bash
# Ensure Ollama is running
ollama serve

# Start the application
python run_ui.py

# List available models
ollama list
```

---

## Architecture

### Backend: Ollama (NOT llama-cpp)

The app uses **Ollama** for LLM inference, NOT llama-cpp-python.

| Component | Details |
|-----------|---------|
| **Ollama URL** | http://localhost:11434 |
| **Default Model** | First available in Ollama |
| **Recommended** | scb10x/typhoon2.5-qwen3-4b |

**Important:** Ollama must be running for the app to work!

---

## Project Structure

```
AIEAT_Internship/
├── app/                    # Main Application
│   ├── config/             # LLM configs (scoring, translation)
│   ├── services/           # Backend Services
│   │   ├── ai_engine.py        # LLM via Ollama API
│   │   ├── backend_api.py      # Main API layer
│   │   ├── database_manager.py # SQLite operations
│   │   └── scraper_service.py  # News scraper
│   ├── ui/                 # Flet UI Pages
│   │   └── pages/
│   │       ├── dashboard.py    # Main news listing
│   │       ├── detail.py       # Article detail view
│   │       ├── config.py       # Settings (keywords, domains, sources)
│   │       └── style.py        # Style presets (NEEDS FIX)
│   └── utils/
│       ├── system_check.py     # Hardware detection
│       └── logger.py           # Logging utility
│
├── data/                   # Data Storage
│   ├── aieat_news.db           # Main SQLite database
│   └── models/                 # (Legacy - models now in Ollama)
│
├── benchmark_test/         # Benchmarking Scripts
│   ├── LoRA/                   # Training data (side project)
│   └── results/                # Benchmark outputs
│
├── scraper_archive/        # Historical Scraper Versions (Reference Only)
└── run_ui.py               # Application entry point
```

---

## Backend Services

| Service | File | Purpose |
|---------|------|---------|
| **BackendAPI** | `backend_api.py` | Main API - orchestrates all operations |
| **DatabaseManager** | `database_manager.py` | SQLite CRUD for articles, sources, config |
| **InferenceController** | `ai_engine.py` | LLM scoring & translation via **Ollama** |
| **ScraperService** | `scraper_service.py` | News discovery (RSS/Sitemap/Homepage) |

---

## Database Schema (aieat_news.db)

**Core Tables:**
- `articles_meta` - Article metadata (headline, source, date, score)
- `article_content` - Full article content
- `article_translated` - Thai translations
- `sources` - News source configuration
- `keywords` - Scoring keywords
- `domains` - Content domain categories
- `system_profile` - App settings
- `styles` - Writing style presets

---

## Known Issues

| Issue | Status |
|-------|--------|
| Can't delete keywords | ❌ Broken |
| Can't delete domains | ❌ Broken |
| Style Setting not working | ❌ Broken |
| Sources CRUD | ⚠️ Untested |
| Ollama not auto-starting | ⚠️ Shows error, manual start needed |

---

## Coding Standards

- **Type hints** required for all functions
- **Docstrings** for classes and public methods
- **UI updates** must call `page.update()` after state changes
- **Ollama calls** use `requests` library to API endpoints
- **Error handling** for Ollama connection failures

---

## Model Configuration

Models are managed by **Ollama**, not local GGUF files.

```bash
# Pull recommended model
ollama pull scb10x/typhoon2.5-qwen3-4b

# Pull translation model (optional)
ollama pull translategemma:4b

# List models
ollama list
```

---

## DO NOT

- ❌ Reference llama-cpp-python (removed)
- ❌ Add CPU/GPU toggles (Ollama handles automatically)
- ❌ Look for GGUF files in data/models (obsolete)
- ❌ Modify scraper_archive/ files (reference only)
