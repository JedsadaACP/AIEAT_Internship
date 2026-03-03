"""
pytest configuration and fixtures for AIEAT integration tests.

These fixtures provide real database connections and mocked UI components
for comprehensive testing of all 211 checklist items.
"""
import os
import sys
import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from app.services.database_manager import DatabaseManager
from app.services.backend_api import BackendAPI


@pytest.fixture(scope="function")
def real_db():
    """
    Create a fresh SQLite in-memory database for each test.
    
    This fixture creates a real DatabaseManager instance with an in-memory
    database and initializes the schema from data/schema.sql.
    
    Returns:
        DatabaseManager: Configured with :memory: database
    """
    import sqlite3
    
    # Create in-memory database
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    
    # Load and execute schema
    schema_path = os.path.join(project_root, "data", "schema.sql")
    if os.path.exists(schema_path):
        with open(schema_path, 'r') as f:
            schema = f.read()
        conn.executescript(schema)
        conn.commit()
    
    # Seed master_status table with initial data
    conn.execute("""
        INSERT INTO master_status (status_name, status_group, description) VALUES
        ('New', 'Article', 'Unprocessed article'),
        ('Scored', 'Article', 'Article with relevance score'),
        ('Translated', 'Article', 'Article translated to Thai'),
        ('Active', 'Source', 'Active news source'),
        ('Inactive', 'Source', 'Disabled news source'),
        ('Online', 'System', 'System online'),
        ('Offline', 'System', 'System offline');
    """)
    conn.commit()
    
    # Create DatabaseManager and set persistent connection
    db = DatabaseManager(":memory:")
    db.set_persistent_connection(conn)
    
    # Load status cache
    db._load_status_cache()
    
    yield db
    
    # Cleanup
    conn.close()


@pytest.fixture(scope="function")
def mock_page():
    """
    Create a mocked Flet page for UI testing.
    
    This fixture creates a MagicMock that simulates a Flet page without
    requiring the actual Flet rendering loop. It includes all common
    page attributes and methods used by UI components.
    
    Returns:
        MagicMock: Mocked Flet page object
    """
    page = MagicMock()
    page.overlay = []
    page.controls = []
    
    # Mock async methods
    async def mock_run_task(coro):
        """Execute coroutine immediately in test context."""
        if callable(coro):
            if hasattr(coro, '__await__'):
                await coro
            else:
                coro()
        return None
    
    page.run_task = MagicMock(side_effect=mock_run_task)
    
    # Mock update methods
    page.update = MagicMock()
    page.set_clipboard = MagicMock()
    
    # Mock snackbar
    page.snack_bar = None
    
    return page


@pytest.fixture(scope="function")
def api(real_db):
    """
    Create a BackendAPI instance with mocked Ollama.
    
    This fixture creates a BackendAPI without calling __init__ to avoid
    the automatic Ollama startup. It provides a real database connection
    with a mocked AI engine for testing.
    
    Args:
        real_db: Fixture providing DatabaseManager instance
        
    Returns:
        BackendAPI: Configured with real DB, mocked AI engine
    """
    # Create instance without calling __init__ (avoids Ollama auto-start)
    api = BackendAPI.__new__(BackendAPI)
    api.db = real_db
    api._engine = MagicMock()
    api._scraper = None
    api._config = None
    
    yield api


@pytest.fixture(scope="function")
def config_page(mock_page, api):
    """
    Create a ConfigPage instance for testing.
    
    Args:
        mock_page: Mocked Flet page
        api: BackendAPI with real DB
        
    Returns:
        ConfigPage: Configured UI component with all controls mocked
    """
    from app.ui.pages.config import ConfigPage
    
    # ConfigPage creates FilePicker in did_mount() - no need to pass it
    page = ConfigPage(mock_page, api)
    
    # Mock the file_picker since did_mount() won't be called in tests
    page.file_picker = MagicMock()
    
    # Initialize config properly (would normally be loaded in refresh_state)
    page.config = api.get_config()
    page.all_sources = api.get_sources()
    
    # Initialize ALL UI references that methods expect
    page.source_list = MagicMock()
    page.source_list.controls = []
    page.keyword_list = MagicMock()
    page.keyword_list.controls = []
    page.source_url_input = MagicMock()
    page.source_url_input.value = "https://test-source.com"
    page.keyword_input = MagicMock()
    page.keyword_input.value = "TestKeyword"
    page.model_dropdown = MagicMock()
    page.model_dropdown.value = "test-model"
    page.threshold_slider = MagicMock()
    page.threshold_slider.value = 4
    page.source_filter = MagicMock()
    page.source_filter.value = ""
    page.refresh_button = MagicMock()
    page.save_button = MagicMock()
    page.automation_switch = MagicMock()
    page.automation_switch.value = False
    page.org_switch = MagicMock()
    page.org_switch.value = False
    page.scoring_switch = MagicMock()
    page.scoring_switch.value = False
    page.org_name_input = MagicMock()
    page.org_name_input.value = "AIEAT"
    page.org_name_input.page = None  # So update() check doesn't fail
    page.date_radio_group = MagicMock()
    page.date_radio_group.value = "all"
    
    return page


@pytest.fixture(scope="function")
def dashboard(mock_page, api):
    """
    Create a DashboardPage instance for testing.
    
    Args:
        mock_page: Mocked Flet page
        api: BackendAPI with real DB
        
    Returns:
        DashboardPage: Configured UI component with all controls mocked
    """
    from app.ui.pages.dashboard import DashboardPage
    
    def on_view_article(article):
        """Dummy callback for article view."""
        pass
    
    dashboard = DashboardPage(mock_page, api, on_view_article)
    
    # Initialize ALL UI references that methods expect
    dashboard.start_button = MagicMock()
    dashboard.start_button.text = "START SCRAPER"
    dashboard.stop_button = MagicMock()
    dashboard.status_badge = MagicMock()
    dashboard.status_badge.content = MagicMock()
    dashboard.status_badge.content.value = "Idle"
    dashboard.search_field = MagicMock()
    dashboard.search_field.value = ""
    dashboard.filter_panel = MagicMock()
    dashboard.filter_panel.visible = False
    dashboard.news_table_container = MagicMock()
    dashboard.page_label = MagicMock()
    dashboard.page_label.value = "Page 1"
    dashboard.model_dropdown = MagicMock()
    dashboard.model_dropdown.value = "test-model"
    dashboard.auto_score_checkbox = MagicMock()
    dashboard.auto_score_checkbox.value = False
    dashboard.table_column = MagicMock()
    dashboard.progress_container = MagicMock()
    dashboard.progress_container.visible = False
    dashboard.news_table = MagicMock()
    dashboard.news_table.rows = []
    dashboard.pagination = MagicMock()
    dashboard.pagination.controls = []
    dashboard.filter_date_dropdown = MagicMock()
    dashboard.filter_date_dropdown.value = "all"
    dashboard.filter_score_dropdown = MagicMock()
    dashboard.filter_score_dropdown.value = "all"
    dashboard.filter_source_dropdown = MagicMock()
    dashboard.filter_source_dropdown.value = "all"
    dashboard.filter_keyword_dropdown = MagicMock()
    dashboard.filter_keyword_dropdown.value = "all"
    dashboard.page_size_dropdown = MagicMock()
    dashboard.page_size_dropdown.value = "20"
    dashboard.goto_page_field = MagicMock()
    dashboard.goto_page_field.value = "1"
    dashboard.batch_dialog = MagicMock()
    dashboard.batch_dialog.open = False
    dashboard.batch_start_button = MagicMock()
    dashboard.batch_start_button.update = MagicMock()  # Prevent "must be added to page" error
    dashboard.progress_text = MagicMock()
    dashboard.progress_text.value = ""
    dashboard.progress_bar = MagicMock()
    dashboard.progress_bar.value = 0
    dashboard.auto_score_switch = MagicMock()
    dashboard.auto_score_switch.value = False
    dashboard.auto_translate_switch = MagicMock()
    dashboard.auto_translate_switch.value = False
    
    return dashboard


@pytest.fixture(scope="function")
def detail_page(mock_page, api):
    """
    Create a DetailPage instance for testing.
    
    Args:
        mock_page: Mocked Flet page
        api: BackendAPI with real DB
        
    Returns:
        DetailPage: Configured UI component
    """
    from app.ui.pages.detail import DetailPage
    
    # Create a sample article for testing
    article = {
        'article_id': 1,
        'headline': 'Test Article',
        'source_name': 'TestSource',
        'author_name': 'Test Author',
        'published_at': '2024-01-15',
        'ai_score': 5
    }
    
    def on_back():
        """Dummy callback for back navigation."""
        pass
    
    detail = DetailPage(mock_page, api, article, on_back)
    
    # Mock the detail fetch
    detail.detail = {
        'article_id': 1,
        'headline': 'Test Article',
        'original_content': 'Test content',
        'thai_content': '',
        'ai_score': 5
    }
    
    # Initialize essential UI references
    detail.output_container = MagicMock()
    detail.main_column = MagicMock()
    detail.main_column.controls = []
    
    return detail


@pytest.fixture(scope="function")
def style_page(mock_page, api):
    """
    Create a StylePage instance for testing.
    
    Args:
        mock_page: Mocked Flet page
        api: BackendAPI with real DB
        
    Returns:
        StylePage: Configured UI component
    """
    from app.ui.pages.style import StylePage
    
    style = StylePage(mock_page, api)
    
    # Initialize essential UI references
    style.style_list_col = MagicMock()
    style.style_list_col.controls = []
    style.name_field = MagicMock()
    style.name_field.value = ""
    style.output_type_dropdown = MagicMock()
    style.output_type_dropdown.value = "facebook"
    style.tone_dropdown = MagicMock()
    style.tone_dropdown.value = "conversational"
    style.headline_length = MagicMock()
    style.headline_length.value = "medium"
    style.lead_length = MagicMock()
    style.lead_length.value = "medium"
    style.body_length = MagicMock()
    style.body_length.value = "medium"
    style.analysis_length = MagicMock()
    style.analysis_length.value = "short"
    style.include_keywords = MagicMock()
    style.include_keywords.value = True
    style.include_lead = MagicMock()
    style.include_lead.value = True
    style.include_analysis = MagicMock()
    style.include_analysis.value = True
    style.include_source = MagicMock()
    style.include_source.value = True
    style.include_hashtags = MagicMock()
    style.include_hashtags.value = True
    style.analysis_focus = MagicMock()
    style.analysis_focus.value = ""
    style.btn_save = MagicMock()
    style.btn_active = MagicMock()
    style.btn_active.disabled = False
    
    return style


@pytest.fixture(scope="function")
def about_page(mock_page):
    """
    Create an AboutPage instance for testing.
    
    Note: AboutPage only takes 'page' parameter (no API).
    
    Args:
        mock_page: Mocked Flet page
        
    Returns:
        AboutPage: Configured UI component
    """
    from app.ui.pages.about import AboutPage
    
    about = AboutPage(mock_page)
    return about


# Custom markers for checklist tracking
def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line("markers", "unit: Unit tests (pure functions, no deps)")
    config.addinivalue_line("markers", "integration: Integration tests (components with real deps)")
    config.addinivalue_line("markers", "e2e: End-to-end tests (full user workflows)")
    config.addinivalue_line("markers", "slow: Tests taking > 5 seconds")
    config.addinivalue_line(
        "markers", "checklist_item(item_number, module, function): Mark test as covering checklist item"
    )


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Attach checklist_item marker data to each test report."""
    outcome = yield
    report = outcome.get_result()
    marker = item.get_closest_marker("checklist_item")
    if marker:
        report.user_properties.append(("item_number", marker.kwargs.get("item_number", "N/A")))
        report.user_properties.append(("module", marker.kwargs.get("module", "Unknown")))
        report.user_properties.append(("function", marker.kwargs.get("function", "")))
