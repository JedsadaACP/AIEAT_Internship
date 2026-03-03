# AGENTS.md - AIEAT Project

> **Universal agent configuration** for AI coding assistants.

---

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Start the application
python run_ui.py

# Ensure Ollama is running
ollama serve

# Preferred translation model
ollama pull scb10x/typhoon2.5-qwen3-4b:latest
```

---

## 📋 Code Style

- **Python 3.10+** with type hints required
- **Docstrings** for all classes and public methods
- **Flet UI**: Use `page.run_task()` for async operations
- **Error handling**: Log with `logger.error()`, never silent failures
- **After editing**: Run `python -m py_compile <file.py>`

---

## 🔧 Tech Stack (DO NOT CHANGE)

| Component | Technology | Notes |
|-----------|------------|-------|
| **LLM Backend** | Ollama API | localhost:11434 |
| **Primary Model** | `scb10x/typhoon2.5-qwen3-4b` | Best for Thai translation |
| **UI Framework** | Flet | Desktop app |
| **Database** | SQLite | `data/aieat_news.db` |
| **Scraping** | aiohttp + BeautifulSoup | Async |

### BANNED Technologies
- ❌ llama-cpp-python (removed)
- ❌ selenium/playwright for scraping
- ❌ Flask/FastAPI (not needed)

---

## 📁 Project Structure

```
AIEAT_Internship/
├── app/
│   ├── services/           # Backend logic
│   │   ├── ai_engine.py        # LLM via Ollama
│   │   ├── ollama_engine.py    # Alternative Ollama controller
│   │   ├── backend_api.py      # Main API facade
│   │   ├── database_manager.py # SQLite operations
│   │   ├── prompt_builder.py   # Translation prompts (DYNAMIC)
│   │   └── scraper_service.py  # News discovery
│   ├── ui/pages/           # Flet UI pages
│   │   ├── dashboard.py        # Main news list + batch processing
│   │   ├── detail.py           # Article detail + translation
│   │   ├── config.py           # Settings + threshold
│   │   ├── style.py            # Translation style presets
│   │   └── about.py            # About page
│   └── config/             # JSON configs
├── data/
│   ├── aieat_news.db       # Main database
│   └── schema.sql          # Database schema
├── .agent/
│   ├── skills/             # Domain-specific patterns
│   ├── workflows/          # Step-by-step processes
│   └── rules/              # Always-on context rules
└── training_data/          # Fine-tuning dataset
```

---

## 🎯 Key Components

### Prompt Builder (`app/services/prompt_builder.py`)
- Builds translation prompts from **Style UI settings**
- Respects ALL settings: `tone`, `headline_length`, `body_length`, `include_*`
- **NO HARDCODED text** - everything configurable by user

### Style Settings Used
| Setting | Used In Prompt | Effect |
|---------|----------------|--------|
| `tone` | ✅ Yes | Writing style (conversational/professional) |
| `headline_length` | ✅ Yes | Short/Medium/Long |
| `body_length` | ✅ Yes | Short/Medium/Long |
| `include_hashtags` | ✅ Yes | Adds hashtag instruction |
| `include_analysis` | ✅ Yes | Adds analysis section |
| `custom_instructions` | ✅ Yes | User custom context |

---

## 🚫 Anti-Patterns (NEVER DO THESE)

1. ❌ **NEVER** use `api/generate` for Typhoon → Use `api/chat`
2. ❌ **NEVER** assume `published_at` exists → Use `COALESCE()`
3. ❌ **NEVER** put `on_change` inside Dropdown constructor
4. ❌ **NEVER** run long operations on main UI thread
5. ❌ **NEVER** use raw `threading.Thread` + `page.update()` in Flet
6. ❌ **NEVER** hardcode text in prompt builder → Everything from Style settings

---

## 📦 Deployment

To build standalone .exe:
```bash
python -m PyInstaller build_app.spec --noconfirm --clean
```

Output: `dist/AIEAT_News_Analyzer/`

---

## 🔄 Workflows

Use `/switch-task` to change between tasks.
Read `SESSION_HANDOFF.md` for current priorities.
