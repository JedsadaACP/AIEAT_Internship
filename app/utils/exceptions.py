"""
AIEAT Custom Exceptions - Structured error handling.
"""

class AIEATError(Exception):
    """Base exception for all AIEAT errors."""
    pass


# Database Exceptions
class DatabaseError(AIEATError):
    """Base exception for database operations."""
    pass

class DatabaseConnectionError(DatabaseError):
    """Failed to connect to database."""
    pass

class ArticleExistsError(DatabaseError):
    """Article already exists in database."""
    pass

class ArticleNotFoundError(DatabaseError):
    """Article not found in database."""
    pass


# Scraper Exceptions
class ScraperError(AIEATError):
    """Base exception for scraper operations."""
    pass

class SourceNotReachableError(ScraperError):
    """Failed to reach news source."""
    pass

class ContentExtractionError(ScraperError):
    """Failed to extract content from page."""
    pass

class RSSParseError(ScraperError):
    """Failed to parse RSS feed."""
    pass


# AI Engine Exceptions
class AIEngineError(AIEATError):
    """Base exception for AI operations."""
    pass

class ModelLoadError(AIEngineError):
    """Failed to load LLM model."""
    pass

class ScoringError(AIEngineError):
    """Failed to score article."""
    pass

class InferenceError(AIEngineError):
    """General inference error (model not loaded, etc.)."""
    pass

class TranslationError(AIEngineError):
    """Failed to translate article."""
    pass

class JSONParseError(AIEngineError):
    """Failed to parse LLM JSON output."""
    pass


# Config Exceptions
class ConfigError(AIEATError):
    """Configuration error."""
    pass

class ConfigNotFoundError(ConfigError):
    """Config file not found."""
    pass
