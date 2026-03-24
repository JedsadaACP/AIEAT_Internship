# AIEAT News Dashboard v1.0.0

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![Flet](https://img.shields.io/badge/Flet-UI-purple)](https://flet.dev/)
[![Downloads](https://img.shields.io/github/downloads/JedsadaACP/AIEAT_Internship/total)](https://github.com/JedsadaACP/AIEAT_Internship/releases)

A local-first news intelligence dashboard that scrapes, scores, and translates articles using a local AI engine. No cloud dependency — everything runs on your machine.

## 📚 Documentation
For detailed setup instructions, troubleshooting, and best practices, please refer to our comprehensive user manuals:
- 📖 **[English User Manual](./User_Manual.md)**
- 🇹🇭 **[คู่มือการใช้งานภาษาไทย (Thai Manual)](./User_Manual_TH.md)**

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

## System Requirements

- **OS:** Windows 10 / 11 (64-bit)
- **RAM:** Minimum 8 GB (16+ GB recommended for local AI models)
- **Disk Space:** 5 GB minimum (for application and offline AI models)

## Quick Start Installation

1. Download **`AIEAT_Setup.exe`** from the [GitHub Releases](https://github.com/JedsadaACP/AIEAT_Internship/releases) page.
2. Double-click to run the installer.
   > ⚠️ **Note (Windows SmartScreen):** As this is an indie open-source release without a paid code-signing certificate, Windows SmartScreen may show a blue "Windows protected your PC" warning. Click **"More info"**, and then click **"Run anyway"**.
3. Optionally install Ollama during setup (highly recommended for AI scanning and translation).

## Tech Stack

| Component | Technology |
|-----------|------------|
| UI Framework | Python + Flet |
| Database | SQLite |
| AI Engine | Ollama (Typhoon 2.5 local model) |

## Contributing

Contributions are welcome! Please read our [Contributing Guide](./CONTRIBUTING.md) for setup instructions, code standards, and how to verify your changes.

## Support & Contact

- **Issues & Support:** Please open an issue on our [GitHub Issues](https://github.com/JedsadaACP/AIEAT_Internship/issues) page.
- **Security:** If you find a security vulnerability, please refer to our [Security Policy](./SECURITY.md) privately.

## License

This project is licensed under the MIT License — see the [LICENSE](./LICENSE) file for details.
