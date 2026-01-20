"""
Test translation with 5/7 threshold on already-scored articles.
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, '.')

from app.services.ai_engine import InferenceController

def test_translate():
    engine = InferenceController()
    
    print("Loading model...")
    engine.load_model()
    
    # Get articles with score >= 5
    with engine.db.get_connection() as conn:
        cursor = conn.execute("""
            SELECT m.article_id, m.headline, m.ai_score, c.original_content
            FROM articles_meta m
            JOIN article_content c ON m.article_id = c.article_id
            WHERE m.ai_score >= 5 AND c.thai_content IS NULL
            LIMIT 2
        """)
        articles = [dict(row) for row in cursor]
    
    print(f"Found {len(articles)} articles with score >= 5 to translate")
    
    for article in articles:
        print(f"\nTranslating ID:{article['article_id']} (score:{article['ai_score']})")
        print(f"  Headline: {article['headline'][:50]}...")
        
        result = engine.translate_article(
            article_id=article['article_id'],
            content=article['original_content']
        )
        
        if result.get('success'):
            thai_headline = result.get('Headline', '')
            print(f"  [OK] Translated!")
            print(f"  Thai Headline: {thai_headline[:50] if thai_headline else 'N/A'}...")
            
            # Save to DB
            thai_content = f"""หัวข้อ: {result.get('Headline', '')}

นำเรื่อง: {result.get('Lead', '')}

{result.get('Body', '')}

## วิเคราะห์
{result.get('Analysis', '')}"""
            
            engine.db.update_thai_content(article['article_id'], thai_content)
            print("  Saved to DB!")
        else:
            print(f"  [FAIL]")
    
    engine.unload_model()
    print("\nDone!")

if __name__ == "__main__":
    test_translate()
