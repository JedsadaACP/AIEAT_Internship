"""Score 50 most recent articles by date"""
import sys
import os
import io
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stdout.reconfigure(line_buffering=True)

from app.services.database_manager import DatabaseManager
from app.services.ai_engine import InferenceController

def main():
    print("=" * 60, flush=True)
    print("SCORE 50 MOST RECENT ARTICLES", flush=True)
    print("=" * 60, flush=True)
    
    db = DatabaseManager()
    engine = InferenceController()
    
    # Get 50 most recent unscored articles by date
    with db.get_connection() as conn:
        cursor = conn.execute("""
            SELECT m.article_id, m.headline, m.published_at, m.author_name, 
                   m.article_url, c.original_content
            FROM articles_meta m
            JOIN article_content c ON m.article_id = c.article_id
            WHERE (m.ai_score IS NULL OR m.ai_score = 0)
            ORDER BY m.published_at DESC NULLS LAST
            LIMIT 50
        """)
        articles = [dict(row) for row in cursor]
    
    print(f"\nFound {len(articles)} articles to score", flush=True)
    
    if not articles:
        print("No articles to score!")
        return
    
    # Load model
    print("\nLoading model...", flush=True)
    engine.load_model()
    
    scored = 0
    failed = 0
    start_time = time.time()
    
    for i, art in enumerate(articles, 1):
        try:
            result = engine.score_article(
                article_id=art['article_id'],
                url=art.get('article_url', ''),
                author=art.get('author_name', ''),
                date=art.get('published_at', ''),
                content=art.get('original_content', '')[:2000]
            )
            
            if result and result.get('total_score', 0) >= 0:
                db.update_article_score(art['article_id'], result['total_score'])
                scored += 1
                print(f"[{i}/50] Score: {result['total_score']} | {art['headline'][:40]}...", flush=True)
            else:
                failed += 1
                print(f"[{i}/50] FAILED | {art['headline'][:40]}...", flush=True)
                
        except Exception as e:
            failed += 1
            print(f"[{i}/50] ERROR: {str(e)[:50]}", flush=True)
    
    engine.unload_model()
    
    elapsed = time.time() - start_time
    
    print("\n" + "=" * 60, flush=True)
    print("DONE", flush=True)
    print("=" * 60, flush=True)
    print(f"Scored: {scored}/50", flush=True)
    print(f"Failed: {failed}", flush=True)
    print(f"Time: {elapsed/60:.1f} min", flush=True)
    print(f"Speed: {elapsed/max(scored,1):.1f}s per article", flush=True)

if __name__ == "__main__":
    main()
