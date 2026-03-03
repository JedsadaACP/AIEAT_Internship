# AIEAT Comprehensive Master Test Plan

## 1. Testing Objective
This plan ensures **100% functional coverage** of the AIEAT application. "All means all" — every service, engine, and utility must be verified. We divide testing into three layers:
1.  **Unit Tests (Component Level):** Does this function work in isolation?
2.  **Integration Tests (System Level):** Do modules talk to each other correctly?
3.  **UI/UX Verification (User Level):** Does the app behave correctly for the human?

---

## 2. Unit Test Matrix (The "All Means All" Checklist)

### 2.1 Database Service (`app/services/database_manager.py`)
| Functionality | Test Case Description | Status |
| :--- | :--- | :--- |
| **Connection** | `get_connection()` returns valid sqlite3 object. | |
| **Initialization** | `_initialize_db()` creates all 5 tables if missing. | |
| **Insert Source** | `add_source(url)` saves URL and handles duplicates. | |
| **Insert Article** | `add_article(data)` saves headline, link, date correctly. | |
| **Fetch Articles** | `get_new_articles()` returns only `sc_status='new'`. | |
| **Update Score** | `update_article_score()` updates `ai_score` and sets status. | |
| **System Profile** | `get_system_profile()` returns dict (even if empty). | |

### 2.2 AI Engine (`app/services/ai_engine.py`)
| Functionality | Test Case Description | Status |
| :--- | :--- | :--- |
| **Load Model** | `load_model(name)` connects to Ollama successfully. | |
| **Prompt Gen** | `score_article()` builds prompt with correct keywords. | |
| **Parsing** | `_parse_score_response()` extracts "Score: X" from LLM text. | |
| **Translation** | `translate_article()` returns valid JSON structure. | |
| **Error Handling** | Engine handles timeout or "Ollama not running" gracefully. | |

### 2.3 Scraper Service (`app/services/scraper_service.py`)
| Functionality | Test Case Description | Status |
| :--- | :--- | :--- |
| **Fetch Feed** | `_fetch_rss_feed()` parses valid XML content. | |
| **Browser Init** | Playwright launches successfully (headless). | |
| **Content Ext** | `fetch_article_content()` returns real text (not junk). | |
| **Anti-Bot** | Scraper handles basic headers/user-agent rotation. | |

### 2.4 Backend API (`app/services/backend_api.py`)
| Functionality | Test Case Description | Status |
| :--- | :--- | :--- |
| **Config Facade** | `get_config()` aggregates DB profile + sources list. | |
| **State Sync** | `reload_model()` triggers AI Engine reload logic. | |

---

## 3. Automated Test Scripts
We have a suite of scripts in `tests/` that cover these matricies.

| Script Name | Scope | Expected Duration |
| :--- | :--- | :--- |
| `python tests/test_database.py` | verifies **2.1 Database Service** | < 1 sec |
| `python tests/test_backend_api.py` | verifies **2.4 Backend API** | < 1 sec |
| `python tests/test_e2e.py` | verifies **2.2 AI Engine** (Real workflow) | ~30-60 sec |
| *To Be Created* | `tests/test_scraper.py` (Mocked & Real) | |

---

## 4. Manual UI Verification Checklist

### Phase 1: Configuration Page
- [ ] **Data Sync:** Open Config > Change Model > Verification: Model stays changed after restart.
- [ ] **Source Management:** Add Source > Check list (75+ items visible) > Delete Source.
- [ ] **Toggles:** Turn "Translate New News" OFF > Restart > Verify it is still OFF.

### Phase 2: Dashboard Page
- [ ] **Display:** Table shows columns: Date, Source, Headline, Score, Status.
- [ ] **Interaction:** Click "Score" button > UI shows progress bar > Table updates row color.
- [ ] **Responsiveness:** Resize window > Table adjusts width.

### Phase 3: Style Settings
- [ ] **CRUD:** Create New Style > Save > Select it > Verify form fills with saved data.
- [ ] **Delete:** Delete a style > Dropdown reverts to "Default".

---

## 5. Master Pass/Fail Summary
**Project Status:**
- [ ] Backend Core Logic (100% Pass)
- [ ] UI Functionality (100% Pass)
- [ ] AI Integration (100% Pass)

*Signed:* ____________________ (Tester)
