"""
Data Standardization Utility
Ensures consistent data formatting across all scrapers before CSV export
"""

import re
from datetime import datetime
from html import unescape
import html.parser

# Standard date format for all output
STANDARD_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def normalize_date(date_input):
    """
    Convert any date format to standardized YYYY-MM-DD HH:MM:SS
    
    Handles:
    - RFC 2822: "Tue, 09 Dec 2025 16:42:57 +0000"
    - ISO datetime: "2025-12-09 00:00:00"
    - ISO 8601: "2025-12-09T09:08:14"
    - datetime objects
    """
    if isinstance(date_input, datetime):
        return date_input.strftime(STANDARD_DATE_FORMAT)
    
    if not isinstance(date_input, str):
        return datetime.now().strftime(STANDARD_DATE_FORMAT)
    
    date_input = date_input.strip()
    
    # Try common formats
    formats = [
        "%a, %d %b %Y %H:%M:%S %z",  # RFC 2822: Tue, 09 Dec 2025 16:42:57 +0000
        "%Y-%m-%d %H:%M:%S",          # ISO: 2025-12-09 00:00:00
        "%Y-%m-%dT%H:%M:%S",          # ISO 8601: 2025-12-09T09:08:14
        "%Y-%m-%d %H:%M:%S.%f",       # With microseconds
        "%Y-%m-%dT%H:%M:%S.%f",       # ISO 8601 with microseconds
        "%Y-%m-%d",                   # Date only
    ]
    
    for fmt in formats:
        try:
            dt = datetime.strptime(date_input.replace('+0000', '').strip(), fmt)
            return dt.strftime(STANDARD_DATE_FORMAT)
        except ValueError:
            continue
    
    # Fallback to today's date
    return datetime.now().strftime(STANDARD_DATE_FORMAT)


def clean_html_content(text):
    """
    Remove HTML entities and decode special characters
    
    Converts: "&#8217;" -> "'", "&nbsp;" -> " ", etc.
    """
    if not text:
        return ""
    
    # Decode HTML entities
    text = unescape(text)
    
    # Fix common encoding issues
    text = text.replace('\u2019', "'")  # Curly apostrophe -> straight apostrophe
    text = text.replace('\u201c', '"')  # Left double quote
    text = text.replace('\u201d', '"')  # Right double quote
    text = text.replace('\u2013', '-')  # En dash
    text = text.replace('\u2014', '-')  # Em dash
    
    # Remove weird whitespace/line breaks
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    
    return text


def normalize_keywords(keywords_input):
    """
    Convert keywords to consistent comma-separated format
    
    Handles:
    - List: ['AI', 'Google'] -> "AI, Google"
    - String: "AI, Google, Meta" -> "AI, Google, Meta"
    - List-like string: "['AI', 'Google']" -> "AI, Google"
    """
    if not keywords_input:
        return ""
    
    # If already a string
    if isinstance(keywords_input, str):
        # Remove Python list brackets if present
        keywords_input = keywords_input.strip()
        if keywords_input.startswith('[') and keywords_input.endswith(']'):
            keywords_input = keywords_input[1:-1]
        
        # Split and clean
        items = [item.strip().strip("'\"") for item in keywords_input.split(',')]
        items = [item for item in items if item]  # Remove empty
        return ", ".join(items)
    
    # If list or tuple
    if isinstance(keywords_input, (list, tuple)):
        items = [str(item).strip().strip("'\"") for item in keywords_input]
        items = [item for item in items if item]
        return ", ".join(items)
    
    return str(keywords_input)


def format_matched_tags(tags_input):
    """
    Format matched tags as comma-separated string (for storage)
    Same as normalize_keywords but kept separate for clarity
    """
    return normalize_keywords(tags_input)


def standardize_row(row):
    """
    Apply all standardization rules to a single data row
    
    Returns: Cleaned and standardized dictionary
    """
    standardized = {}
    
    for key, value in row.items():
        if key == "published":
            standardized[key] = normalize_date(value)
        elif key == "full_content":
            standardized[key] = clean_html_content(value)
        elif key == "content_snippet":
            standardized[key] = clean_html_content(value)
        elif key in ["keywords", "matched_tags"]:
            standardized[key] = normalize_keywords(value)
        else:
            standardized[key] = value
    
    return standardized


def standardize_dataset(data_list):
    """
    Apply standardization to entire dataset
    
    Args:
        data_list: List of dictionaries (rows)
    
    Returns:
        List of standardized dictionaries
    """
    return [standardize_row(row) for row in data_list]


# Test function
if __name__ == "__main__":
    # Test date normalization
    test_dates = [
        "Tue, 09 Dec 2025 16:42:57 +0000",
        "2025-12-09 00:00:00",
        "2025-12-09T09:08:14",
    ]
    
    print("=== DATE NORMALIZATION TEST ===")
    for date_str in test_dates:
        normalized = normalize_date(date_str)
        print(f"{date_str:<35} -> {normalized}")
    
    # Test HTML cleaning
    test_html = "This is &#8217;great&#8217; &amp; fantastic&#8217;"
    print(f"\n=== HTML CLEANING TEST ===")
    print(f"Original: {test_html}")
    print(f"Cleaned:  {clean_html_content(test_html)}")
    
    # Test keyword normalization
    test_keywords = [
        ['AI', 'Google'],
        "AI, Google, Meta",
        "['AI', 'Google']",
    ]
    print(f"\n=== KEYWORD NORMALIZATION TEST ===")
    for kw in test_keywords:
        normalized = normalize_keywords(kw)
        print(f"{str(kw):<30} -> {normalized}")
