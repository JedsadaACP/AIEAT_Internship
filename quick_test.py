"""Quick E2E Test for AIEAT"""
import sys
sys.path.insert(0, '.')
from app.services.backend_api import BackendAPI

print('=== QUICK E2E TEST ===')
api = BackendAPI()

# Test 1: Get articles
print('\n[1] Getting articles...')
articles = api.get_articles(limit=3)
print(f'    Found {len(articles)} articles')
if articles:
    art = articles[0]
    headline = art.headline if hasattr(art, 'headline') else art.get('headline', 'Unknown')
    print(f'    First: {headline[:50]}...')

# Test 2: Get active style
print('\n[2] Getting active style...')
style = api.get_active_style()
print(f'    Style: {style.get("name") if style else "None"}')

# Test 3: Quick translate (first article)
if articles:
    print('\n[3] Testing translation (this takes ~20s)...')
    art = articles[0]
    art_id = art.article_id if hasattr(art, 'article_id') else art.get('article_id')
    result = api.translate_article(art_id)
    print(f'    Success: {result.get("success")}')
    if result.get('Headline'):
        print(f'    Headline: {result.get("Headline")[:60]}...')
    if result.get('Body'):
        print(f'    Body length: {len(result.get("Body"))} chars')

print('\n=== TEST COMPLETE ===')

