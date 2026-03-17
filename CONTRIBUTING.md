# Contributing to AIEAT

Thank you for your interest in contributing to AIEAT! This document provides guidelines for contributing to the project.

## Getting Started

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
   python run_ui.py
   ```

## Prerequisites

- **Python 3.10+** with type hints
- **Ollama** installed and running locally
- **Typhoon 2.5** model pulled (`ollama pull scb10x/typhoon2.5-qwen3-4b:latest`)

## Architecture Overview

AIEAT is a local-first news intelligence dashboard with the following architecture:

- **Flet** - UI framework for the desktop application
- **SQLite** - Local data storage
- **Ollama** - Local AI engine (Typhoon 2.5 model) for AI scoring and translation
- **74+ configurable news sources**

### Key Directories

| Directory | Purpose |
|-----------|---------|
| `app/ui/` | UI components (pages, components, theme) |
| `app/services/` | Backend logic (database, AI engine, scraper) |
| `data/` | Database schema and SQLite files |
| `scripts/` | Utility scripts for data management |

## Submitting Changes

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/your-feature-name`)
3. **Make** your changes with proper type hints
4. **Verify** changes compile correctly:
   ```bash
   python -m py_compile app/ui/main.py
   python -m py_compile app/services/backend_api.py
   # ... on other edited files
   ```
5. **Submit** a Pull Request

## Code Style

- **Python 3.10+** with type hints required
- Use `page.run_task()` for async operations
- **NEVER** use raw `threading.Thread` with Flet UI (causes deadlocks)
- Follow existing code conventions in the project
- Add logging instead of print statements

## Coding Rules

- Always use `page.run_task()` for async operations in Flet
- Use `logger.error()` or `logger.debug()` instead of `print()` for errors
- Avoid hardcoding text in prompts - use Style settings
- Never commit secrets or API keys

## Questions?

- Open an issue for bugs or feature requests
- Check the [User Manual](./User_Manual.md) for usage instructions
- Review existing issues before creating new ones

We appreciate your contributions!
