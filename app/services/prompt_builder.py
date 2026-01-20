"""
AIEAT Prompt Builder - Builds translation prompts from style settings.

Creates optimized prompts for Typhoon model based on user-configured styles.
"""
import json
from typing import Dict, Any, Optional


def build_translation_prompt(style: Dict, article: Dict) -> str:
    """
    Build translation prompt from style settings and article data.
    
    Args:
        style: Style settings dict from database
        article: Article data dict with keys: url, author, date, publisher, content
    
    Returns:
        Formatted prompt string for LLM
    """
    # Extract style settings with defaults
    output_type = style.get('output_type', 'facebook')
    tone = style.get('tone', 'conversational')
    headline_length = style.get('headline_length', 'medium')
    lead_length = style.get('lead_length', 'medium')
    body_length = style.get('body_length', 'medium')
    analysis_length = style.get('analysis_length', 'short')
    include_keywords = style.get('include_keywords', 1)
    include_lead = style.get('include_lead', 1)
    include_analysis = style.get('include_analysis', 1)
    include_source = style.get('include_source', 1)
    include_hashtags = style.get('include_hashtags', 1)
    analysis_focus = style.get('analysis_focus', 'ผลกระทบต่อผู้ใช้และตลาดไทย')
    
    # Build role based on output type
    roles = {
        'facebook': 'Thai content writer for a popular tech Facebook page',
        'article': 'professional Thai news translator and editor',
        'summary': 'Thai news summarizer who creates brief summaries'
    }
    role = roles.get(output_type, roles['facebook'])
    
    # Build tone instruction
    tones = {
        'conversational': 'Write conversational Thai, friendly and easy to read for social media',
        'professional': 'Write professional Thai, suitable for news website',
        'technical': 'Write technical Thai with industry terminology'
    }
    tone_instruction = tones.get(tone, tones['conversational'])
    
    # Build length instructions
    length_map = {
        'short': {'headline': '1 line, max 8 words', 'lead': '1-2 sentences', 'body': '2 paragraphs', 'analysis': '1-2 sentences'},
        'medium': {'headline': '1 line, max 12 words', 'lead': '2-3 sentences', 'body': '3 paragraphs', 'analysis': '1 paragraph'},
        'long': {'headline': '1-2 lines, max 15 words', 'lead': '3-4 sentences', 'body': '4-5 paragraphs', 'analysis': '2 paragraphs'}
    }
    
    headline_desc = length_map.get(headline_length, length_map['medium'])['headline']
    lead_desc = length_map.get(lead_length, length_map['medium'])['lead']
    body_desc = length_map.get(body_length, length_map['medium'])['body']
    analysis_desc = length_map.get(analysis_length, length_map['short'])['analysis']
    
    # Build JSON schema based on enabled sections
    json_fields = {}
    
    if include_keywords:
        json_fields['keywords'] = ['keyword1', 'keyword2', 'keyword3', 'keyword4', 'keyword5']
    
    json_fields['headline'] = f'Thai headline ({headline_desc})'
    
    if include_lead:
        json_fields['lead'] = f'Thai lead paragraph ({lead_desc})'
    
    json_fields['body'] = f'Thai article body ({body_desc})'
    
    if include_analysis:
        json_fields['analysis'] = f'{analysis_focus} ({analysis_desc})'
    
    if include_source:
        source_text = f"ที่มา: {article.get('publisher', 'Unknown')} — {article.get('url', '')}"
        json_fields['source'] = source_text
    
    if include_hashtags:
        json_fields['hashtags'] = ['#Tag1', '#Tag2', '#Tag3', '#Tag4', '#Tag5']
    
    # Build the prompt
    prompt = f"""You are a {role}.

TASK: Rewrite this English news into engaging Thai content.

OUTPUT FORMAT - Return ONLY this JSON:
{json.dumps(json_fields, ensure_ascii=False, indent=2)}

WRITING RULES:
1. {tone_instruction}
2. Keep ALL brand/product names in English: Apple, Google, Siri, Gemini, AI, ChatGPT, Microsoft, etc.
3. Hashtags MUST be in English only for better reach: #Apple #AI #Siri
4. Short sentences, easy to read on mobile
5. Make content engaging and shareable
6. For person names, use format: สตีฟ จ็อบส์ (Steve Jobs)

AVOID:
- Translating brand names to Thai (keep Apple, Google, Siri, Gemini in English)
- Long academic sentences
- Generic phrases like "น่าจับตาดู"

ARTICLE:
URL: {article.get('url', '')}
Author: {article.get('author', 'Unknown')}
Date: {article.get('date', 'Unknown')}
Publisher: {article.get('publisher', 'Unknown')}

{article.get('content', '')}

Return ONLY valid JSON, no other text."""

    return prompt


def parse_translation_response(text: str) -> Dict:
    """
    Parse JSON response from LLM.
    
    Args:
        text: Raw LLM response
    
    Returns:
        Parsed dict with translation fields
    """
    result = {
        'Keywords': '',
        'Headline': '',
        'Lead': '',
        'Body': '',
        'Analysis': '',
        'Source': '',
        'Hashtags': '',
        'success': False
    }
    
    try:
        # Clean potential markdown code blocks
        clean = text.strip()
        if clean.startswith('```'):
            # Remove first line (```json)
            lines = clean.split('\n')
            clean = '\n'.join(lines[1:])
            if clean.endswith('```'):
                clean = clean[:-3]
        
        parsed = json.loads(clean)
        
        # Map JSON fields to result
        if 'keywords' in parsed:
            if isinstance(parsed['keywords'], list):
                result['Keywords'] = ', '.join(parsed['keywords'])
            else:
                result['Keywords'] = parsed['keywords']
        
        result['Headline'] = parsed.get('headline', '')
        result['Lead'] = parsed.get('lead', '')
        result['Body'] = parsed.get('body', '')
        result['Analysis'] = parsed.get('analysis', '')
        result['Source'] = parsed.get('source', '')
        
        if 'hashtags' in parsed:
            if isinstance(parsed['hashtags'], list):
                result['Hashtags'] = ' '.join(parsed['hashtags'])
            else:
                result['Hashtags'] = parsed['hashtags']
        
        result['success'] = True
        
    except json.JSONDecodeError as e:
        # Fallback: try to parse with separator format
        result = _parse_separator_format(text)
    
    return result


def _parse_separator_format(text: str) -> Dict:
    """Fallback parser for separator-based format."""
    separator = '-####################-'
    parts = text.split(separator)
    
    result = {
        'Keywords': '',
        'Headline': '',
        'Lead': '',
        'Body': '',
        'Analysis': '',
        'Source': '',
        'Hashtags': '',
        'success': False
    }
    
    for part in parts:
        part = part.strip()
        if part.startswith('Keywords:'):
            result['Keywords'] = part.replace('Keywords:', '').strip()
        elif part.startswith('Headline:'):
            result['Headline'] = part.replace('Headline:', '').strip()
        elif part.startswith('Lead:'):
            result['Lead'] = part.replace('Lead:', '').strip()
        elif part.startswith('Body:'):
            result['Body'] = part.replace('Body:', '').strip()
        elif part.startswith('Analysis:'):
            result['Analysis'] = part.replace('Analysis:', '').strip()
        elif part.startswith('Source:') or part.startswith('ที่มา:'):
            result['Source'] = part.strip()
        elif part.startswith('Hashtags:'):
            result['Hashtags'] = part.replace('Hashtags:', '').strip()
    
    if result['Headline'] or result['Body']:
        result['success'] = True
    
    return result


# Default style presets
DEFAULT_PRESETS = {
    'facebook': {
        'name': 'Facebook Post',
        'output_type': 'facebook',
        'tone': 'conversational',
        'headline_length': 'short',
        'lead_length': 'short',
        'body_length': 'medium',
        'analysis_length': 'short',
        'include_keywords': 1,
        'include_lead': 1,
        'include_analysis': 1,
        'include_source': 1,
        'include_hashtags': 1,
        'analysis_focus': 'ผลกระทบต่อคนไทยและผู้ใช้งาน',
        'is_active': 1
    },
    'article': {
        'name': 'Web Article',
        'output_type': 'article',
        'tone': 'professional',
        'headline_length': 'medium',
        'lead_length': 'medium',
        'body_length': 'long',
        'analysis_length': 'medium',
        'include_keywords': 1,
        'include_lead': 1,
        'include_analysis': 1,
        'include_source': 1,
        'include_hashtags': 0,
        'analysis_focus': 'วิเคราะห์ผลกระทบทางเศรษฐกิจและสังคมไทย',
        'is_active': 0
    },
    'summary': {
        'name': 'Executive Summary',
        'output_type': 'summary',
        'tone': 'professional',
        'headline_length': 'short',
        'lead_length': 'short',
        'body_length': 'short',
        'analysis_length': 'short',
        'include_keywords': 1,
        'include_lead': 1,
        'include_analysis': 0,
        'include_source': 1,
        'include_hashtags': 0,
        'analysis_focus': '',
        'is_active': 0
    }
}
