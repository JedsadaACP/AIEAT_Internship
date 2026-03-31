# Changelog

All notable changes to AIEAT are documented here. Format follows [Keep a Changelog](https://keepachangelog.com/).

## [1.0.0] - 2026-03-24

### Added
- Multi-profile intelligence silos (Technology & AI, Finance & Markets, Politics & Policy)
- Bilingual user manuals (English + Thai)
- CHANGELOG.md, SUPPORT.md for OSS compliance
- Download count badge on README
- Software Design Specification document (Thai)
- Project Report document

### Changed
- Fixed version string from "1.0.0-beta" to "1.0.0" in About page
- Removed incorrect "Gemma" model reference from About page
- Upgraded README with system requirements, support section, and SmartScreen instructions

### Security
- Identified and remediated SQL injection risk in `database_manager.py`: converted dynamic f-string date filters to parameterized SQLite queries (`?` placeholders) for defense-in-depth
- Hardened AI translation prompt in `prompt_builder.py` with strict anti-hallucination and anti-transliteration rules to prevent technical term corruption

## [0.1.0-beta] - 2026-03-18

### Added
- Initial beta release
- Async news scraper with RSS/Sitemap/Homepage waterfall discovery
- AI relevance scoring via Typhoon 2.5 (Ollama local inference)
- Thai translation with 3 customizable styles (News Article, Social Media, Executive Brief)
- SQLite database with 11 tables
- Flet-based desktop UI (Dashboard, Config, Detail, Style, Profiles, About)
- Windows installer (PyInstaller + InnoSetup) with optional Ollama download
- 74+ configurable news sources with keyword filtering
- CODE_OF_CONDUCT.md, CONTRIBUTING.md, SECURITY.md, LICENSE (MIT)
- GitHub issue templates (bug report + feature request) and PR template
