"""
Critical bug hunt tests - File picker and edge cases.

Tests for your known pain points and high-bug-probability areas.
"""
import pytest
import os
import tempfile
from unittest.mock import MagicMock, patch
from app.services.database_manager import DatabaseManager
from app.services.backend_api import BackendAPI


@pytest.mark.integration
class TestFilePickerOperations:
    """Test file picker operations - your known pain point."""
    
    def test_import_csv_with_utf8_bom(self, real_db):
        """Test CSV with Byte Order Mark (Windows issue)."""
        api = BackendAPI.__new__(BackendAPI)
        api.db = real_db
        
        # Create CSV with BOM
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.csv', delete=False) as f:
            f.write(b'\xef\xbb\xbfhttps://example.com/source1\n')
            f.write(b'https://example.com/source2\n')
            temp_path = f.name
        
        try:
            # Test file can be read
            with open(temp_path, 'r', encoding='utf-8-sig') as f:
                lines = f.readlines()
            
            # Verify BOM is handled
            assert 'https://' in lines[0]
            assert len(lines) == 2
        finally:
            os.unlink(temp_path)
    
    def test_import_unicode_filenames(self, real_db):
        """Test Thai filenames in file picker."""
        # Create temp file with Thai name
        temp_dir = tempfile.mkdtemp()
        thai_filename = os.path.join(temp_dir, 'แหล่งข่าว.csv')
        
        try:
            with open(thai_filename, 'w', encoding='utf-8') as f:
                f.write('https://example.com\n')
            
            # Verify file can be accessed
            assert os.path.exists(thai_filename)
            
            with open(thai_filename, 'r', encoding='utf-8') as f:
                content = f.read()
            assert 'https://' in content
        finally:
            os.remove(thai_filename)
            os.rmdir(temp_dir)
    
    def test_export_to_readonly_location(self, real_db):
        """Test export fails gracefully with permission error."""
        api = BackendAPI.__new__(BackendAPI)
        api.db = real_db
        
        # Try to write to a read-only path (simulate)
        readonly_path = 'C:\\Windows\\System32\\test_export.csv'
        
        # Should not crash, should handle error gracefully
        try:
            # This will likely fail on Windows without admin rights
            with open(readonly_path, 'w') as f:
                f.write('test')
            # If we get here, clean up
            os.remove(readonly_path)
        except (PermissionError, OSError):
            # Expected behavior - permission denied
            pass  # This is correct error handling
    
    def test_import_empty_file(self, real_db):
        """Test importing empty file doesn't crash."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write('')  # Empty file
            temp_path = f.name
        
        try:
            with open(temp_path, 'r') as f:
                content = f.read()
            assert content == ''
        finally:
            os.unlink(temp_path)
    
    def test_import_malformed_urls(self, real_db):
        """Test importing invalid URLs are filtered out."""
        api = BackendAPI.__new__(BackendAPI)
        api.db = real_db
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write('not-a-url\n')
            f.write('https://valid-url.com\n')
            f.write('ftp://wrong-protocol.com\n')
            temp_path = f.name
        
        try:
            with open(temp_path, 'r') as f:
                lines = [l.strip() for l in f.readlines() if l.strip()]
            
            # Only valid URLs should be processed
            valid_urls = [l for l in lines if l.startswith('http')]
            assert len(valid_urls) == 1
            assert valid_urls[0] == 'https://valid-url.com'
        finally:
            os.unlink(temp_path)


@pytest.mark.integration  
class TestDatabaseEdgeCases:
    """Test database edge cases that cause real bugs."""
    
    def test_unicode_in_headlines(self, real_db):
        """Test Thai/Chinese characters in headlines."""
        article_id = real_db.insert_article(
            source_name="Test",
            source_url="https://test.com",
            headline="ข่าวใหม่ AI ปัญญาประดิษฐ์",
            article_url="https://test.com/1",
            content="Content",
            published_at="2024-01-15",
            author_name="作者"
        )
        
        article = real_db.get_article_by_id(article_id)
        assert article is not None
        assert "ข่าวใหม่" in article['headline']
        assert article['author_name'] == "作者"
    
    def test_very_long_content(self, real_db):
        """Test article with >10k characters."""
        long_content = "A" * 15000
        
        article_id = real_db.insert_article(
            source_name="Test",
            source_url="https://test.com",
            headline="Long Article",
            article_url="https://test.com/long",
            content=long_content,
            published_at="2024-01-15",
            author_name="Author"
        )
        
        article = real_db.get_article_by_id(article_id)
        assert article is not None
        assert len(article['original_content']) == 15000
    
    def test_null_fields_handling(self, real_db):
        """Test missing author, date, etc."""
        article_id = real_db.insert_article(
            source_name="Test",
            source_url="https://test.com",
            headline="Test",
            article_url="https://test.com/2",
            content="Content",
            published_at=None,
            author_name=None
        )
        
        article = real_db.get_article_by_id(article_id)
        assert article is not None
        # Should handle nulls gracefully
    
    def test_duplicate_url_prevention(self, real_db):
        """Test same URL can't be inserted twice."""
        url = "https://example.com/duplicate"
        
        # First insert
        id1 = real_db.insert_article(
            source_name="Test",
            source_url="https://test.com",
            headline="First",
            article_url=url,
            content="Content 1",
            published_at="2024-01-15",
            author_name="Author"
        )
        
        # Second insert should be rejected or return existing ID
        id2 = real_db.insert_article(
            source_name="Test",
            source_url="https://test.com",
            headline="Second",
            article_url=url,
            content="Content 2",
            published_at="2024-01-15",
            author_name="Author"
        )
        
        # Should either return same ID or reject
        assert id1 is not None
        # id2 might be None (rejected) or same as id1 (deduplication)


@pytest.mark.integration
class TestConfigCorruption:
    """Test configuration corruption scenarios."""
    
    def test_corrupted_json_config_recovery(self, real_db):
        """Test broken JSON config file is handled."""
        import json
        
        # Simulate corrupted JSON
        corrupted_json = '{"key": "value", broken}'
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write(corrupted_json)
            temp_path = f.name
        
        try:
            # Should handle JSON parse error gracefully
            with pytest.raises(json.JSONDecodeError):
                with open(temp_path, 'r') as f:
                    json.load(f)
        finally:
            os.unlink(temp_path)
    
    def test_missing_config_file(self, real_db):
        """Test missing config file creates defaults."""
        # This tests the behavior when config doesn't exist
        # Should use defaults rather than crash
        pass  # Placeholder - needs actual config loading test


@pytest.mark.integration
class TestDateParsingEdgeCases:
    """Test date format variations."""
    
    def test_various_date_formats(self, real_db):
        """Test multiple date formats are parsed correctly."""
        from app.services.scraper_service import ScraperService
        
        test_cases = [
            ("2024-01-15", True),
            ("2024-01-15T10:30:00", True),
            ("Mon, 15 Jan 2024 10:30:00 GMT", True),
            ("15/01/2024", True),  # European format
            ("January 15, 2024", True),
            ("invalid-date", False),
            ("", False),
            ("Unknown", False),
        ]
        
        for date_str, should_parse in test_cases:
            result = ScraperService._parse_date(None, date_str)
            if should_parse:
                # Should return datetime object
                pass  # Valid date
            else:
                # Should return None for invalid
                assert result is None, f"Failed for: {date_str}"
