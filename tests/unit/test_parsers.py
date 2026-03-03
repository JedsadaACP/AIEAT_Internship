"""
Unit tests for parsing and logic functions.

Tests JSON parsing, date checking, and business logic.
No external dependencies - true unit tests.
"""
import pytest
import json
from datetime import datetime, timedelta
from app.services.ai_engine import InferenceController, PromptBuilder
from app.services.ollama_engine import OllamaController
from app.utils.system_check import get_model_recommendations
from app.ui.pages.dashboard import DashboardPage


@pytest.mark.unit
class TestExtractJson:
    """Test JSON extraction from LLM responses."""
    
    def test_extract_json_from_markdown_code_block(self):
        """Test extracting JSON from markdown code blocks."""
        text = 'Some text before ```json\n{"key": "value"}\n``` and after'
        controller = InferenceController.__new__(InferenceController)
        result = controller._extract_json(text)
        assert result == {"key": "value"}
    
    def test_extract_json_raw(self):
        """Test extracting raw JSON without markdown."""
        text = 'Some text {"key": "value", "num": 123} more text'
        controller = InferenceController.__new__(InferenceController)
        result = controller._extract_json(text)
        assert result == {"key": "value", "num": 123}
    
    def test_extract_json_invalid(self):
        """Test handling invalid JSON gracefully."""
        text = 'No JSON here'
        controller = InferenceController.__new__(InferenceController)
        with pytest.raises(json.JSONDecodeError):
            controller._extract_json(text)


@pytest.mark.unit
class TestCheckFreshness:
    """Test article freshness checking."""
    
    def test_fresh_article_returns_1(self):
        """Test recent article is marked fresh."""
        controller = InferenceController.__new__(InferenceController)
        yesterday = (datetime.now() - timedelta(days=1)).isoformat()
        result = controller._check_freshness(yesterday, days=7)
        assert result == 1
    
    def test_old_article_returns_0(self):
        """Test old article is marked not fresh."""
        controller = InferenceController.__new__(InferenceController)
        last_month = (datetime.now() - timedelta(days=30)).isoformat()
        result = controller._check_freshness(last_month, days=7)
        assert result == 0
    
    def test_empty_date_returns_0(self):
        """Test empty date returns 0."""
        controller = InferenceController.__new__(InferenceController)
        result = controller._check_freshness('', days=7)
        assert result == 0
    
    def test_unknown_date_returns_0(self):
        """Test 'Unknown' date returns 0."""
        controller = InferenceController.__new__(InferenceController)
        result = controller._check_freshness('Unknown', days=7)
        assert result == 0
    
    def test_invalid_date_returns_0(self):
        """Test invalid date format returns 0."""
        controller = InferenceController.__new__(InferenceController)
        result = controller._check_freshness('not-a-date', days=7)
        assert result == 0


@pytest.mark.unit
class TestEmptyScoreResult:
    """Test empty score result generation."""
    
    def test_empty_result_structure(self):
        """Test empty result has correct structure."""
        controller = InferenceController.__new__(InferenceController)
        result = controller._empty_score_result()
        
        assert result['total_score'] == 0
        assert result['success'] is False
        assert 'ERROR' in result['raw_response']
        assert 'Author' in result
        assert 'Is_fresh' in result
    
    def test_empty_result_with_error_message(self):
        """Test empty result includes error message."""
        controller = InferenceController.__new__(InferenceController)
        result = controller._empty_score_result("Connection failed")
        
        assert "Connection failed" in result['raw_response']


@pytest.mark.unit
class TestParseTranslation:
    """Test translation parsing."""
    
    def test_parse_translation_sections(self):
        """Test parsing translation with all sections."""
        separator = '-####################-'
        text = f"Headline: Thai Headline{separator}Body: Thai body content{separator}Source: News Source"
        
        controller = InferenceController.__new__(InferenceController)
        result = controller._parse_translation(text)
        
        assert result['Headline'] == 'Thai Headline'
        assert result['Body'] == 'Thai body content'
        assert result['Source'] == 'Source: News Source'


@pytest.mark.unit
class TestBuildMessages:
    """Test prompt message building."""
    
    def test_build_messages_structure(self):
        """Test message list structure."""
        config = {
            'system_prompt': 'You are a helpful assistant',
            'user_prompt_template': 'Process: {content}',
            'content_max_chars': 100
        }
        builder = PromptBuilder(config)
        
        messages = builder.build_messages(content="Test content")
        
        assert len(messages) == 2
        assert messages[0]['role'] == 'system'
        assert messages[1]['role'] == 'user'
        assert 'Test content' in messages[1]['content']
    
    def test_build_messages_truncates_content(self):
        """Test long content is truncated."""
        config = {
            'system_prompt': 'Test',
            'user_prompt_template': '{content}',
            'content_max_chars': 10
        }
        builder = PromptBuilder(config)
        
        long_content = "a" * 100
        messages = builder.build_messages(content=long_content)
        
        assert len(messages[1]['content']) <= 10


@pytest.mark.unit
class TestParseScores:
    """Test score parsing from Ollama responses."""
    
    def test_parse_valid_scores(self):
        """Test parsing valid JSON scores."""
        controller = OllamaController.__new__(OllamaController)
        controller.keywords = ['AI', 'Technology']
        
        response = '{"AI": 1, "Technology": 0, "relate": 1}'
        result = controller._parse_scores(response)
        
        assert result['AI'] == 1
        assert result['Technology'] == 0
        assert result['relate'] == 1
    
    def test_parse_invalid_returns_defaults(self):
        """Test invalid JSON returns default scores."""
        controller = OllamaController.__new__(OllamaController)
        controller.keywords = ['AI']
        
        response = 'Invalid JSON'
        result = controller._parse_scores(response)
        
        assert result['AI'] == 0
        assert result['relate'] == 0


@pytest.mark.unit
class TestGetModelRecommendations:
    """Test model recommendation logic."""
    
    def test_high_vram_recommends_large_models(self):
        """Test 24GB+ VRAM recommends 13B models."""
        system_info = {
            'gpu': {'cuda_available': True, 'memory_mb': 24000},
            'ram': {'total_gb': 32}
        }
        
        result = get_model_recommendations(system_info)
        
        assert result['can_run_local_llm'] is True
        assert result['max_model_size_b'] == 13
        assert result['use_gpu'] is True
    
    def test_low_vram_recommends_small_models(self):
        """Test 8GB VRAM recommends 4B models."""
        system_info = {
            'gpu': {'cuda_available': True, 'memory_mb': 8000},
            'ram': {'total_gb': 16}
        }
        
        result = get_model_recommendations(system_info)
        
        assert result['max_model_size_b'] == 4
    
    def test_no_gpu_checks_ram_fallback(self):
        """Test CPU-only with sufficient RAM."""
        system_info = {
            'gpu': {'cuda_available': False, 'memory_mb': 0},
            'ram': {'total_gb': 16}
        }
        
        result = get_model_recommendations(system_info)
        
        assert result['can_run_local_llm'] is True
        assert 'CPU' in result['recommended_scoring_model']


@pytest.mark.unit
class TestParseDateForSort:
    """Test date parsing for sorting."""
    
    def test_parse_iso_date(self):
        """Test parsing ISO format date."""
        from app.ui.pages.dashboard import _parse_date_for_sort
        result = _parse_date_for_sort('2024-01-15T10:30:00')
        assert isinstance(result, float)
        assert result > 0
    
    def test_parse_rfc_date(self):
        """Test parsing RFC format date."""
        from app.ui.pages.dashboard import _parse_date_for_sort
        result = _parse_date_for_sort('Mon, 15 Jan 2024 10:30:00 GMT')
        assert isinstance(result, float)
    
    def test_parse_invalid_date_returns_zero(self):
        """Test invalid date returns 0."""
        from app.ui.pages.dashboard import _parse_date_for_sort
        result = _parse_date_for_sort('invalid')
        assert result == 0.0
    
    def test_parse_empty_date_returns_zero(self):
        """Test empty date returns 0."""
        from app.ui.pages.dashboard import _parse_date_for_sort
        result = _parse_date_for_sort('')
        assert result == 0.0
