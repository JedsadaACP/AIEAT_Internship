# Contributing to AIEAT News Dashboard

Thank you for your interest in contributing to the AIEAT News Dashboard! Whether you're fixing bugs, adding new features, or improving documentation, your help is welcome.

## Architecture Overview

The application follows a clean 3-tier architecture:
1. **Frontend (`app/ui/`)**: Built entirely in Python using Flet. Handles purely UI state.
2. **Services (`app/services/`)**: 
   - `scraper_service.py`: High-concurrency async web scraping
   - `ai_engine.py`: Manages Ollama connection and handles LLM tasks
   - `database_manager.py`: SQLite transactions and schema control
   - `backend_api.py`: Orchestrator linking the UI to backend services
3. **Database (`data/aieat_news.db`)**: Local SQLite storage for articles, user profiles, and logs.

## Setting Up Your Environment

1. Fork and clone the repository.
2. Use Python 3.11 - 3.13.
3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. If working on scraping features, ensure `trafilatura` and `justext` are correctly parsing content. 
5. If working on AI, install [Ollama](https://ollama.com) locally and run the `typhoon2.5` model.

## Adding Features

**1. Database Changes:**
If you need to change the schema, modify `ensure_tables()` in `database_manager.py`. Use SQLite `ALTER TABLE` commands gracefully so existing users do not lose data on update.

**2. UI Changes:**
Flet components are strictly modularized under `app/ui/components` and `app/ui/pages`. 
- State should be passed locally within the classes. 
- Avoid using global `page.session` unless absolutely necessary (the app is single-user desktop).

## Submitting Pull Requests

1. **Branch cleanly**: Create a feature branch (`git checkout -b feature/your-feature-name`).
2. **Test your code**: Ensure the `pytest` suite passes.
3. **No secrets**: Do NOT commit personal Hugging Face tokens, API keys, or large `.gguf` model files. (These are actively `.gitignore`d).
4. **Push & PR**: Submit a pull request to `main` with a clear description of changes.

## Compiling for Distribution
If you change how dependencies are imported (especially NLP or scraping libraries like `newspaper`), you MUST update `build_app.spec` using `collect_data_files()` to ensure PyInstaller bundles the required dictionary lists in the compiled `.exe`.
