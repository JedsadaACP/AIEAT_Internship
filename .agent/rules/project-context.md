---
description: Project context that loads automatically for AIEAT work
activation: always
---

# AIEAT Project Context

## Core Files
- Entry point: `run_ui.py`
- Current priorities: Read `SESSION_HANDOFF.md`
- Project rules: Read `AGENTS.md`

## Tech Stack
- **UI**: Flet (Python)
- **LLM**: Ollama API (localhost:11434)  
- **Model**: `scb10x/typhoon2.5-qwen3-4b`
- **Database**: SQLite (`data/aieat_news.db`)

## Anti-Patterns
- ❌ NEVER use `api/generate` for Typhoon → Use `api/chat`
- ❌ NEVER use `threading.Thread` + `page.update()` in Flet
- ❌ NEVER hardcode text in prompt builder

## Key Directories
- `app/services/` — Backend logic
- `app/ui/pages/` — Flet UI pages
- `.agent/skills/` — Domain-specific patterns
- `training_data/` — Fine-tuning dataset
