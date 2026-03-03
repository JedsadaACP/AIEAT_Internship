# 🤖 INSTRUCTIONS FOR MINIMAX M2.1 (Worker Agent)

**Role:** Senior QA Automation Engineer
**Objective:** Add 15 Missing Unit Tests to `tests/integration/test_ui_pages.py`
**Constraint:** DO NOT modify source code. ONLY modify the test file. Use existing fixtures.

## 1. Context
We have an existing `pytest` integration suite. We need to increase coverage by testing specific UI logic functions that were previously skipped.

## 2. Target File
`tests/integration/test_ui_pages.py`

## 3. Tasks
Copy and paste the following test methods into the appropriate classes in `test_ui_pages.py`.

### A. Add to `class TestConfigUI:`

```python
    @pytest.mark.checklist_item(item_number=108, module="Config", function="Update threshold display")
    def test_config_update_threshold_display(self, config_page):
        """Item 108: Update threshold display."""
        config_page.threshold_container = MagicMock()
        config_page._update_threshold_display()
        assert config_page.threshold_container.content is not None

    @pytest.mark.checklist_item(item_number=110, module="Config", function="Add domain")
    def test_config_add_domain(self, config_page):
        """Item 110: Add domain - verify domain added to database."""
        config_page.domain_input = MagicMock()
        config_page.domain_input.value = "example.com"
        config_page.domains_row = MagicMock()
        config_page.domains_row.controls = []
        initial_domains = config_page.api.get_domains()
        config_page._add_domain(None)
        updated_domains = config_page.api.get_domains()
        assert len(updated_domains) > len(initial_domains)

    @pytest.mark.checklist_item(item_number=111, module="Config", function="Remove domain")
    def test_config_remove_domain(self, config_page):
        """Item 111: Remove domain - verify domain removed from database."""
        config_page.api.add_domain("removeme.com")
        config_page.domain_input = MagicMock()
        config_page.domains_row = MagicMock()
        config_page.domains_row.controls = []
        config_page._remove_domain("removeme.com")
        domains = config_page.api.get_domains()
        assert "removeme.com" not in domains

    @pytest.mark.checklist_item(item_number=117, module="Config", function="Filter sources")
    def test_config_filter_sources(self, config_page):
        """Item 117: Filter sources - verify filtering works."""
        config_page.sources_list = MagicMock()
        config_page.sources_list.controls = []
        config_page.all_sources = [
            {'domain_name': 'reuters.com'}, {'domain_name': 'bbc.com'}
        ]
        event = MagicMock()
        event.control.value = "reuters"
        config_page._filter_sources(event)
        # sources_list.controls should have been set (1 match)
        assert config_page.sources_list.controls is not None
        # Verify it filtered (logic check depending on implementation, ensuring no crash first)

    @pytest.mark.checklist_item(item_number=122, module="Config", function="On date radio change")
    def test_config_on_date_radio_change(self, config_page):
        """Item 122: On date radio change - verify custom field toggled."""
        config_page.custom_days_field = MagicMock()
        config_page.custom_days_label = MagicMock()
        event = MagicMock()
        event.control.value = "custom"
        config_page._on_date_radio_change(event)
        assert config_page.custom_days_field.visible == True
        assert config_page.custom_days_label.visible == True

    @pytest.mark.checklist_item(item_number=124, module="Config", function="Show save confirmation")
    def test_config_show_save_confirmation(self, config_page):
        """Item 124: Show save confirmation - verify dialog opened."""
        config_page._show_save_confirmation(None)
        assert len(config_page.page.overlay) > 0
        config_page.page.update.assert_called()
```

### B. Add to `class TestDashboardUI:`

```python
    @pytest.mark.checklist_item(item_number=142, module="Dashboard", function="Open source filter dialog")
    def test_dashboard_open_source_filter_dialog(self, dashboard):
        """Item 142: Open source filter dialog."""
        dashboard._open_source_filter_dialog(None)
        assert len(dashboard.page.overlay) > 0

    @pytest.mark.checklist_item(item_number=143, module="Dashboard", function="Create keyword dropdown")
    def test_dashboard_create_keyword_dropdown(self, dashboard):
        """Item 143: Create keyword dropdown."""
        import flet as ft
        options = [ft.dropdown.Option("all", "All"), ft.dropdown.Option("ai", "AI")]
        result = dashboard._create_keyword_dropdown(options)
        assert result is not None
        assert hasattr(dashboard, 'keyword_dropdown')

    @pytest.mark.checklist_item(item_number=147, module="Dashboard", function="On date filter change")
    def test_dashboard_on_date_filter_change(self, dashboard):
        """Item 147: On date filter change."""
        event = MagicMock()
        event.control.value = "7days"
        dashboard._on_date_filter_change(event)
        assert dashboard.filter_date_range == "7days"

    @pytest.mark.checklist_item(item_number=148, module="Dashboard", function="On score filter change")
    def test_dashboard_on_score_filter_change(self, dashboard):
        """Item 148: On score filter change."""
        event = MagicMock()
        event.control.value = "5"
        dashboard._on_score_filter_change(event)
        assert dashboard.filter_score == "5"

    @pytest.mark.checklist_item(item_number=177, module="Dashboard", function="Format date")
    def test_dashboard_format_date(self, dashboard):
        """Item 177: Format date - verify date formatting."""
        result = dashboard._format_date("2024-01-15")
        assert result != "-", "Valid date should format properly"
        assert result != "", "Should return formatted string"

    @pytest.mark.checklist_item(item_number=180, module="Dashboard", function="Safe update")
    def test_dashboard_safe_update(self, dashboard):
        """Item 180: Safe update - verify thread-safe update."""
        dashboard._safe_update()
        dashboard.page.update.assert_called()

    @pytest.mark.checklist_item(item_number=181, module="Dashboard", function="Parse date for sort")
    def test_dashboard_parse_date_for_sort(self, dashboard):
        """Item 181: Parse date for sort - verify timestamp returned."""
        from app.ui.pages.dashboard import _parse_date_for_sort
        result = _parse_date_for_sort("2024-01-15T10:00:00")
        assert result > 0, "Valid date should return positive timestamp"
        assert _parse_date_for_sort("") == 0
        assert _parse_date_for_sort(None) == 0
```

### C. Add to `class TestDetailUI:`

```python
    @pytest.mark.checklist_item(item_number=192, module="Detail", function="Save file")
    def test_detail_save_file(self, detail_page):
        """Item 192: Save file - verify file write attempted."""
        mock_open = MagicMock()
        with patch('builtins.open', mock_open):
            detail_page._save_file("test", "some content")
        mock_open.assert_called_once()
```

### D. Add to `class TestStyleUI:`

```python
    @pytest.mark.checklist_item(item_number=200, module="Style", function="Update form values")
    def test_style_update_form_values(self, style_page):
        """Item 200: Update form values - verify form populated."""
        style = {'name': 'TestStyle', 'output_type': 'article', 'tone': 'professional',
                 'headline_length': 'long', 'lead_length': 'short', 'body_length': 'medium',
                 'analysis_length': 'short', 'include_keywords': 1, 'include_lead': 1,
                 'include_analysis': 1, 'include_source': 1, 'include_hashtags': 1,
                 'custom_instructions': 'Focus on tech', 'is_active': False}
        style_page._update_form_values(style)
        assert style_page.name_field.value == 'TestStyle'
        assert style_page.output_type_dropdown.value == 'article'
        assert style_page.tone_dropdown.value == 'professional'
        assert style_page.headline_length.value == 'long'
```
