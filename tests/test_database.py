"""
Database Manager Tests
"""
import pytest
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.database_manager import DatabaseManager
from app.utils.exceptions import ArticleExistsError


class TestDatabaseManager:
    """Test suite for DatabaseManager."""
    
    @pytest.fixture
    def db(self):
        """Create database manager instance."""
        return DatabaseManager()
    
    def test_connection(self, db):
        """Test database connection works."""
        with db.get_connection() as conn:
            cursor = conn.execute("SELECT 1")
            assert cursor.fetchone()[0] == 1
    
    def test_status_cache_loaded(self, db):
        """Test status cache is populated."""
        assert 'New' in db._status_cache
        assert 'Scored' in db._status_cache
        assert 'Translated' in db._status_cache
    
    def test_get_status_id(self, db):
        """Test getting status ID by name."""
        new_id = db.get_status_id('New')
        assert new_id is not None
        assert isinstance(new_id, int)
    
    def test_generate_url_hash(self):
        """Test URL hash generation."""
        url = "https://example.com/article/123"
        hash1 = DatabaseManager.generate_url_hash(url)
        hash2 = DatabaseManager.generate_url_hash(url)
        
        assert hash1 == hash2  # Same URL = same hash
        assert len(hash1) == 64  # SHA256 = 64 hex chars
    
    def test_article_exists_false(self, db):
        """Test article_exists returns False for non-existent."""
        fake_hash = "0" * 64
        assert db.article_exists(fake_hash) == False
    
    def test_get_article_count(self, db):
        """Test getting article counts."""
        counts = db.get_article_count()
        assert isinstance(counts, dict)


# Run tests directly
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
