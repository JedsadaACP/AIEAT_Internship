"""
Unit tests for prompt_builder module.

Tests pure functions for building and parsing translation prompts.
No external dependencies - these are true unit tests.
"""
import pytest
from app.services.prompt_builder import (
    build_translation_prompt,
    parse_translation_response,
    parse_markdown_format
)


@pytest.mark.unit
class TestBuildTranslationPrompt:
    """Test prompt building with various style configurations."""
    
    def test_build_prompt_facebook_style(self):
        """Test building prompt with facebook output type."""
        style = {
            'output_type': 'facebook',
            'tone': 'conversational',
            'headline_length': 'medium',
            'body_length': 'medium',
            'include_lead': 1,
            'include_analysis': 1,
            'include_source': 1,
            'include_keywords': 1,
            'include_hashtags': 0,
            'custom_instructions': ''
        }
        article = {
            'headline': 'AI Breakthrough Announced',
            'content': 'Scientists have made a major discovery in AI research.'
        }
        
        result = build_translation_prompt(style, article)
        
        assert isinstance(result, str)
        assert 'Social Media Content Expert' in result
        assert 'AI Breakthrough Announced' in result
        assert 'Scientists have made a major discovery' in result
        assert 'facebook' in result.lower()
    
    def test_build_prompt_web_article_style(self):
        """Test building prompt with web article output type."""
        style = {
            'output_type': 'web article',
            'tone': 'professional',
            'headline_length': 'long',
            'body_length': 'long',
            'include_lead': 1,
            'include_analysis': 1,
            'include_source': 1,
            'include_keywords': 1,
            'include_hashtags': 1,
            'custom_instructions': 'Focus on technical details'
        }
        article = {
            'headline': 'New GPU Architecture',
            'content': 'Nvidia reveals next-generation GPU specifications.'
        }
        
        result = build_translation_prompt(style, article)
        
        assert isinstance(result, str)
        assert 'Professional Journalist' in result
        assert 'web article' in result.lower()
        assert 'technical details' in result
    
    def test_build_prompt_summary_style(self):
        """Test building prompt with summary output type."""
        style = {
            'output_type': 'summary',
            'tone': 'conversational',
            'headline_length': 'short',
            'body_length': 'short',
            'include_lead': 0,
            'include_analysis': 0,
            'include_source': 0,
            'include_keywords': 0,
            'include_hashtags': 0,
            'custom_instructions': ''
        }
        article = {
            'headline': 'Tech News Roundup',
            'content': 'Weekly summary of technology news.'
        }
        
        result = build_translation_prompt(style, article)
        
        assert isinstance(result, str)
        assert 'Executive Summarizer' in result
    
    def test_build_prompt_empty_style_defaults(self):
        """Test prompt building with empty style uses defaults."""
        style = {}
        article = {
            'headline': 'Test Article',
            'content': 'Test content here.'
        }
        
        result = build_translation_prompt(style, article)
        
        assert isinstance(result, str)
        assert len(result) > 0
        assert 'Test Article' in result
    
    def test_build_prompt_tone_variations(self):
        """Test all tone variations are handled."""
        tones = ['conversational', 'professional', 'academic']
        article = {'headline': 'Test', 'content': 'Test'}
        
        for tone in tones:
            style = {'tone': tone, 'output_type': 'facebook'}
            result = build_translation_prompt(style, article)
            assert tone.lower() in result.lower() or 'Conversational' in result or 'Professional' in result or 'Academic' in result


@pytest.mark.unit
class TestParseMarkdownFormat:
    """Test markdown parsing from LLM responses."""
    
    def test_parse_basic_markdown(self):
        """Test parsing standard markdown format."""
        text = """# Test Headline

> This is the lead paragraph

This is the body content.

## Analysis
Some analysis text here.

---
Keywords: AI, Technology, News
Source: TechDaily
Hashtags: #AI #Tech"""
        
        result = parse_markdown_format(text)
        
        assert result['success'] is True
        assert result['Headline'] == 'Test Headline'
        assert result['Lead'] == 'This is the lead paragraph'
        assert 'This is the body content' in result['Body']
        assert result['Analysis'] == 'Some analysis text here.'
        assert result['Keywords'] == 'AI, Technology, News'
        assert result['Source'] == 'TechDaily'
        assert result['Hashtags'] == '#AI #Tech'
    
    def test_parse_without_analysis(self):
        """Test parsing markdown without analysis section."""
        text = """# Simple Headline

Body content only.

---
Source: NewsSite"""
        
        result = parse_markdown_format(text)
        
        assert result['success'] is True
        assert result['Headline'] == 'Simple Headline'
        assert result['Analysis'] == ''
    
    def test_parse_without_lead(self):
        """Test parsing markdown without lead paragraph."""
        text = """# No Lead Headline

Direct body content.

---
Keywords: test"""
        
        result = parse_markdown_format(text)
        
        assert result['success'] is True
        assert result['Headline'] == 'No Lead Headline'
        assert result['Lead'] == ''
    
    def test_parse_empty_input(self):
        """Test parsing empty string."""
        result = parse_markdown_format('')
        
        assert result['success'] is False
        assert result['Body'] == ''
    
    def test_parse_malformed_markdown(self):
        """Test parsing malformed markdown falls back gracefully."""
        text = "Just plain text without markdown"
        
        result = parse_markdown_format(text)
        
        # Should still succeed with body containing original text
        assert result['success'] is True
        assert result['Body'] == text


@pytest.mark.unit
class TestParseTranslationResponse:
    """Test translation response wrapper function."""
    
    def test_parse_response_delegates_to_markdown_parser(self):
        """Test that parse_translation_response calls parse_markdown_format."""
        text = """# Thai Headline

Thai content here.

---
Source: Original"""
        
        result = parse_translation_response(text)
        
        assert result['success'] is True
        assert result['Headline'] == 'Thai Headline'
    
    def test_parse_empty_response(self):
        """Test parsing empty translation response."""
        result = parse_translation_response('')
        
        assert result['success'] is False
