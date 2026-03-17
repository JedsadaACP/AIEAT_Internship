# AIEAT - AI-Enhanced Article Tracker v1.0.0

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![Flet](https://img.shields.io/badge/Flet-UI-purple)](https://flet.dev/)

A local-first news intelligence dashboard that scrapes, scores, and translates articles using a local AI engine. No cloud dependency — everything runs on your machine.

## What It Is

AIEAT is designed for content writers, social media managers, and news analysts who need to:
- Aggregate news from 74+ configurable sources
- Automatically score article relevance using AI
- Translate English articles to Thai with customizable tones
- Organize content into profile-based silos (Finance, Tech, Politics, etc.)

## Key Features

- **Multi-Profile Article Silos** — Create separate intelligence profiles with custom keywords
- **AI Relevance Scoring** — Uses Typhoon 2.5 model to score articles 1-10
- **Thai Translation** — Localized AI translation with customizable styles
- **74+ Configurable News Sources** — Add or remove sources easily
- **Windows Installer** — Optional Ollama setup during installation

## Installation

1. Download `AIEAT_Setup.exe` from the [GitHub Releases](https://github.com/JedsadaACP/AIEAT_Internship/releases) page
2. Run the installer
3. Optionally install Ollama during setup (recommended for AI features)

## Quick Start

1. Launch the app
2. Select a profile (or create a new one)
3. Add news sources and set keywords
4. Click **Scrape** to fetch articles
5. Click **Batch Score** to run AI scoring
6. Review and translate articles

## Tech Stack

| Component | Technology |
|-----------|------------|
| UI Framework | Python + Flet |
| Database | SQLite |
| AI Engine | Ollama (Typhoon 2.5 model) |

## Contributing

Contributions are welcome! Please read our [Contributing Guide](./CONTRIBUTING.md) for setup instructions and code standards.

## License

This project is licensed under the MIT License — see the [LICENSE](./LICENSE) file for details.
