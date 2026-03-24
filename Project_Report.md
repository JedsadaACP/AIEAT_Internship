# Project Report: AIEAT News Dashboard

**Developer:** Jedsada Artchomphoo (Intern)  
**Project:** AIEAT News Dashboard  
**Duration:** December 2025 — March 2026 (5 months)  
**Status:** v1.0.0

---

## 1. Project Overview

AIEAT News Dashboard is a local-first news intelligence dashboard developed to provide secure, offline-capable news monitoring and analysis. Built using Python and the Flet framework, the application automates the process of gathering news from over 74 configurable sources.

The system differentiates itself through a "zero-cloud" dependency model. All data processing, including relevance scoring and Thai language translation, is performed locally on the user's hardware. This is achieved by integrating the Typhoon 2.5 Large Language Model via Ollama for local inference. By eliminating external API dependencies, AIEAT ensures total data privacy and operational continuity without an active internet connection after the initial scraping phase.

---

## 2. Timeline & Milestones

### December 2025: Initiation and Prototyping
*   Project kickoff and requirements specification.
*   Research into news extraction methodologies.
*   Development of an initial scraper prototype using Jupyter Notebooks to validate extraction logic across diverse news domains.

### January 2026: Core Backend Development
*   **Database Design:** Implementation of a relational SQLite schema consisting of 11 tables to manage metadata, content, and system configurations.
*   **Scraper Production:** Porting the prototype logic into a production-ready asynchronous service.
*   **Extraction Pipeline:** Integration of `trafilatura` and `newspaper3k` to ensure high-fidelity content extraction from varied HTML structures.
*   **AI Integration:** Establishing communication with the Ollama `/api/chat` endpoint for local LLM inference.

### February 2026: UI Development and System Integration
*   **Frontend Construction:** Development of the Flet-based interface, including Dashboard, Configuration, Article Detail, Style Management, and User Profile pages.
*   **Profile System:** Implementation of data isolation using `profile_id` foreign keys to allow multiple independent intelligence "silos" within a single installation.
*   **Packaging:** Initial compilation of the application using PyInstaller.
*   **Deployment:** Development of an InnoSetup script to produce a Windows installer, including logic for an optional Ollama engine download.
*   **Bug Resolution:** Addressed critical SSL certificate verification errors encountered in the frozen executable environment.

### March 2026: Optimization and Standardization
*   **Code Maintenance:** Systematic removal of debugging artifacts and optimization of internal logic.
*   **Concurrency Fixes:** Replaced standard `threading.Thread` implementations with Flet’s `page.run_task()` to resolve UI blocking issues during model preloading.
*   **Open Source Standardization:** Applied community standards including MIT License, Code of Conduct, and Contribution guidelines.
*   **Documentation:** Finalized bilingual (English and Thai) User Manuals and QuickStart guides.
*   **Release:** Final build of the 71.9 MB installer and v0.1.0-beta release for User Acceptance Testing (UAT).

---

## 3. Technical Architecture

### UI Framework
*   **Flet (Python):** Utilized for cross-platform desktop GUI development, enabling a reactive interface using Python-native logic.

### Database Layer
*   **SQLite:** A local relational database managing 11 tables: `master_status`, `models`, `system_profile`, `user_profiles`, `tags`, `sources`, `styles`, `articles_meta`, `article_content`, `article_tag_map`, and `logs`.

### Scraping Engine
*   **Asynchronous I/O:** Powered by `aiohttp` for concurrent network requests.
*   **Waterfall Discovery:** A multi-tiered strategy for identifying content:
    1.  Standard RSS Feeds
    2.  Sitemap XML Parsing
    3.  Heuristic Homepage Link Extraction

### AI Inference
*   **Ollama & Typhoon 2.5:** Local execution of the `scb10x/typhoon2.5-qwen3-4b:latest` model.
*   **Interface:** Communication via the `/api/chat` REST endpoint for optimized conversational responses.

### Prompt Engineering
*   **Customizable Styles:** A modular prompt builder that translates raw content into specific formats:
    *   **News Article:** Professional journalistic tone.
    *   **Social Media Post:** Concise, engagement-focused content.
    *   **Executive Brief:** Formal, high-level summaries.

### Deployment Pipeline
*   **Compilation:** PyInstaller using a custom `.spec` configuration for asset bundling.
*   **Installation:** InnoSetup producing `AIEAT_Setup.exe` (71.9 MB).

---

## 4. Key Challenges & Solutions

### SSL Certificate Errors in Frozen Executables
**Challenge:** Once packaged as an `.exe`, the application failed to verify SSL certificates for news sources because the default certificate store was inaccessible.  
**Solution:** Bundled the `certifi` certificate bundle explicitly within the PyInstaller data files and configured the application to utilize the bundled path at runtime.

### UI Thread Blocking during Startup
**Challenge:** Long-running initialization tasks (such as checking the Ollama engine status) caused the Flet UI to become unresponsive.  
**Solution:** Migrated from raw Python threading to Flet’s asynchronous `page.run_task()` utility, allowing the UI to remain interactive while background services initialized.

### Windows SmartScreen and Security Warnings
**Challenge:** As the installer is not signed with a commercial Code-Signing certificate, Windows SmartScreen flags the application.  
**Solution:** Since a certificate was outside the project budget, detailed "Safe Execution" instructions were added to the user documentation and QuickStart guide to guide users through the bypass process.

### Multi-Profile Data Isolation
**Challenge:** Ensuring that different user profiles (e.g., "Finance" vs. "Technology") did not leak data or keywords into one another.  
**Solution:** Implemented a strict relational mapping using `profile_id` as a mandatory foreign key across all relevant tables (`tags`, `sources`, `articles_meta`), ensuring that queries are always scoped to the active profile.

---

## 5. Final Deliverables

1.  **AIEAT_Setup.exe:** Comprehensive Windows installer (71.9 MB).
2.  **User_Manual.md:** Detailed English documentation covering installation, configuration, and operation.
3.  **User_Manual_TH.md:** Professional Thai translation of the user manual.
4.  **QuickStart_Guide.md:** A one-page guide for rapid deployment and first-run instructions.
5.  **Install_AI_Engine.bat:** A standalone batch script to automate the installation of Ollama and the Typhoon 2.5 model.
6.  **OSS Repository:** A GitHub-compliant repository including `LICENSE`, `CONTRIBUTING.md`, `SECURITY.md`, and issue templates.

---

## 6. Results & Metrics

*   **Codebase:** 31 Python source files organized into 4 core packages (`services`, `ui`, `utils`, `config`).
*   **Data Structure:** 11-table SQLite database populated with comprehensive seed data.
*   **Coverage:** 74+ pre-configured news sources integrated across 3 default profiles.
*   **Extensibility:** 3 fully customizable AI translation styles.
*   **Localization:** Complete bilingual documentation support.

---

## 7. Lessons Learned

### Asynchronous Programming in Python
The transition from synchronous prototypes to an asynchronous production environment highlighted the necessity of non-blocking I/O for desktop applications. Managing the lifecycle of multiple concurrent scrapers alongside a reactive UI requires disciplined use of `asyncio` and framework-specific task runners to avoid race conditions and deadlocks.

### Complexity of Windows Desktop Packaging
Developing the application logic is only half the effort; packaging for distribution on Windows introduces significant overhead. Managing relative paths, bundling external certificates, and ensuring dependency compatibility in a frozen environment (PyInstaller) requires a robust build pipeline and extensive testing on "clean" machines.

### Importance of Documentation for Non-Technical Users
A powerful tool is only effective if it can be installed and operated by its target audience. For a local AI application, documentation must bridge the gap between complex backend requirements (like Ollama and hardware specifications) and a simple user experience. Clear instructions on bypassing OS-level security warnings are as critical as the code itself.

### Local-First AI Tradeoffs
The project validated the "Local-First" approach, demonstrating that privacy and zero-cost inference are achievable with models like Typhoon 2.5. However, this comes at the cost of hardware dependency. Balancing the model size (4B parameters) against inference speed on standard consumer laptops is a critical design decision that determines the overall utility of the application.
