import pytest
from app.ui.pages.about import AboutPage

class TestAboutUI:
    """
    Covers 3 About Page Items:
    - Build Page
    - Build Layout
    - Refresh State
    """

    @pytest.fixture
    def about_page(self, page, real_db):
        return AboutPage(page, real_db)

    def test_build_page(self, about_page):
        """Test About Page Instantiation and Build."""
        # 1. Build
        content = about_page.build()
        assert content is not None
        
        # 2. Check Layout Sections (Implicitly called by build)
        # We can inspect the returned Column controls
        assert len(content.controls) > 0 # Should have header, content
        
    def test_refresh_state(self, about_page):
        """Test Refresh State (even if empty)."""
        about_page.refresh_state()
        assert True # Just ensure no crash
