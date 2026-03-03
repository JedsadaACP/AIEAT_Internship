# AIEAT Testing Guide

## Architecture Overview

**Application Type**: Desktop Database Application (Flet + SQLite + Ollama)
**Testing Pattern**: Diamond (appropriate for this architecture)
**Total Functions**: ~250

## Testing Levels

### 1. Unit Tests (~35 tests)
**Purpose**: Test pure functions with no external dependencies
**Speed**: < 1 second
**Location**: `tests/unit/`

**Test Files**:
- `test_prompt_builder.py` - Translation prompt building & parsing
- `test_text_processing.py` - Text cleaning, validation, hashing
- `test_parsers.py` - JSON extraction, date parsing, logic

**Coverage**:
- prompt_builder: build_translation_prompt, parse_markdown_format
- scraper_service: clean_text, clean_author, is_paywall, is_same_domain, matches_keywords, parse_date
- database_manager: generate_url_hash
- ai_engine: extract_json, check_freshness, parse_translation
- ollama_engine: parse_scores
- system_check: get_model_recommendations

### 2. Integration Tests (~206 tests)
**Purpose**: Test components with real dependencies (SQLite, mocked APIs)
**Speed**: ~30 seconds
**Location**: `tests/integration/`

**Test Files**:
- `test_database.py` - DatabaseManager CRUD operations
- `test_services.py` - Scraper, AI Engine, BackendAPI
- `test_ui.py` - Flet UI components (mocked)

**Coverage**:
- Database: insert_article, get_article, update_score, sources, keywords, styles
- Services: run_scraper, score_article, translate_article, batch_process
- UI: build_page, add_keyword, export_csv, filters

### 3. E2E Tests (~30 tests)
**Purpose**: Test complete user workflows
**Speed**: ~5 minutes
**Location**: `tests/e2e/`

**Test File**:
- `test_workflows.py` - End-to-end user scenarios

**Coverage**:
- First-time setup
- Add/configure sources
- Run scraper
- Score & translate articles
- Export data
- Manage styles

## Directory Structure

```
tests/
├── __init__.py
├── conftest.py              # Shared fixtures
├── pytest.ini              # pytest configuration
├── checklists/             # Test checklists
│   ├── unit_testing_checklist.csv
│   ├── integration_testing_checklist.csv
│   └── e2e_testing_checklist.csv
├── unit/                   # Unit tests (~35)
│   ├── __init__.py
│   ├── test_prompt_builder.py
│   ├── test_text_processing.py
│   └── test_parsers.py
├── integration/            # Integration tests (~206)
│   ├── __init__.py
│   ├── conftest.py         # Integration fixtures
│   ├── test_database.py
│   ├── test_services.py
│   └── test_ui.py
└── e2e/                    # E2E tests (~30)
    ├── __init__.py
    └── test_workflows.py
```

## Running Tests

### Run All Tests
```bash
pytest
```

### Run by Level
```bash
# Unit tests only (fast)
pytest -m unit

# Integration tests only
pytest -m integration

# E2E tests only
pytest -m e2e
```

### Run with Coverage
```bash
pytest --cov=app --cov-report=html
```

### Run Specific Test File
```bash
pytest tests/unit/test_prompt_builder.py
```

## Test Markers

- `@pytest.mark.unit` - Pure function tests
- `@pytest.mark.integration` - Component tests with dependencies
- `@pytest.mark.e2e` - End-to-end tests
- `@pytest.mark.slow` - Tests taking > 5 seconds

## Fixtures

### Unit Tests
No fixtures needed - pure functions only

### Integration Tests
- `real_db` - SQLite in-memory database with schema
- `mock_page` - Mocked Flet page object
- `api` - BackendAPI with real DB, mocked AI
- `config_page` - ConfigPage with mocked UI
- `dashboard` - DashboardPage with mocked UI
- `detail_page` - DetailPage with mocked UI
- `style_page` - StylePage with mocked UI
- `about_page` - AboutPage with mocked UI

### E2E Tests
- Full application instance (if automated)

## Best Practices

### Unit Tests
- Test pure functions only
- No database, API, or file I/O
- Fast execution (< 1ms per test)
- Descriptive test names
- One assertion per test (ideally)

### Integration Tests
- Use real SQLite (in-memory)
- Mock external APIs (Ollama)
- Mock UI components (Flet)
- Test component interactions
- Clean up after each test

### E2E Tests
- Test complete user flows
- Use real application state
- Clean database before/after
- Focus on critical paths

## Adding New Tests

### 1. Identify Test Type
- Pure function → Unit test
- Component with deps → Integration test  
- User workflow → E2E test

### 2. Check Checklist
Refer to appropriate checklist CSV to see what's already covered

### 3. Write Test
Follow naming convention: `test_<function>_<scenario>`

### 4. Run Test
```bash
pytest tests/<level>/test_<file>.py::Test<Class>::test_<name> -v
```

## Coverage Goals

- **Unit**: 100% of pure functions (~35 functions)
- **Integration**: Critical paths (~206 tests already exist)
- **E2E**: Main workflows (~30 scenarios)

## Continuous Integration

```yaml
# .github/workflows/test.yml
- Run unit tests on every commit
- Run integration tests on PR
- Run E2E tests before release
```

## Troubleshooting

### Tests Failing?
1. Check Ollama is running (for integration)
2. Verify SQLite schema is loaded
3. Check test data exists

### Slow Tests?
1. Use `-m unit` for fast feedback
2. Use `-n auto` for parallel execution
3. Skip slow tests with `--ignore=tests/e2e`

## References

- [pytest documentation](https://docs.pytest.org/)
- [Testing Checklists](checklists/)
- [Source Code](../app/)
