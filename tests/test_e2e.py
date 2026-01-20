"""
End-to-End Backend Test
Tests: Scraper → Score → Translate pipeline
"""
import sys
import os
import io

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from app.services.database_manager import DatabaseManager
from app.services.ai_engine import InferenceController

def main():
    print("=" * 60)
    print("AIEAT End-to-End Backend Test")
    print("=" * 60)
    
    # 1. Database Check
    print("\n[1/4] Database Check...")
    db = DatabaseManager()
    counts = db.get_article_count()
    print(f"  Articles: {counts}")
    
    # 2. Get unscored articles
    print("\n[2/4] Getting unscored articles...")
    new_articles = db.get_new_articles(limit=3)
    print(f"  Found {len(new_articles)} articles to process")
    
    if not new_articles:
        print("  No new articles to process!")
        return
    
    for art in new_articles:
        print(f"  - {art['headline'][:50]}...")
    
    # 3. Score articles
    print("\n[3/4] Scoring articles (this may take a minute)...")
    engine = InferenceController()
    engine.load_model()
    
    scored = 0
    for art in new_articles:
        print(f"  Scoring: {art['headline'][:40]}...")
        result = engine.score_article(
            article_id=art['article_id'],
            url=art.get('article_url', ''),
            author=art.get('author_name', ''),
            date=art.get('published_at', ''),
            content=art.get('original_content', '')[:2000]
        )
        
        if result and result.get('total_score', 0) > 0:
            db.update_article_score(art['article_id'], result['total_score'])
            scored += 1
            print(f"    Score: {result.get('total_score', 0)}/7")
        else:
            print(f"    Failed to score")
    
    print(f"  Scored {scored}/{len(new_articles)} articles")
    
    # 4. Translate high-score article
    print("\n[4/4] Translation test...")
    
    # Get a scored article with score >= 3
    with db.get_connection() as conn:
        cursor = conn.execute("""
            SELECT m.article_id, m.headline, m.ai_score, c.original_content
            FROM articles_meta m
            JOIN article_content c ON m.article_id = c.article_id
            WHERE m.ai_score >= 3 AND c.thai_content IS NULL
            LIMIT 1
        """)
        article = cursor.fetchone()
    
    if article:
        print(f"  Translating: {article['headline'][:40]}...")
        result = engine.translate_article(
            article_id=article['article_id'],
            url='',
            author='',
            date='',
            publisher='',
            content=article['original_content'][:3000]
        )
        
        if result and result.get('Body'):
            thai_content = f"หัวข้อ: {result.get('Headline', '')}\n\n"
            thai_content += f"นำเรื่อง: {result.get('Lead', '')}\n\n"
            thai_content += f"{result.get('Body', '')}\n\n"
            thai_content += f"วิเคราะห์: {result.get('Analysis', '')}"
            
            db.update_thai_content(article['article_id'], thai_content)
            print(f"    Translation saved! ({len(thai_content)} chars)")
        else:
            print(f"    Translation failed")
    else:
        print("  No articles with score >= 3 to translate")
    
    engine.unload_model()
    
    # Final summary
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)
    final_counts = db.get_article_count()
    print(f"Final counts: {final_counts}")

if __name__ == "__main__":
    main()
