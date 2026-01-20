"""Translate high-score articles (score >= max//2 + 1)"""
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
    print("TRANSLATE HIGH-SCORE ARTICLES", flush=True)
    print("=" * 60, flush=True)
    
    # Threshold: max_score // 2 + 1 = 8 // 2 + 1 = 5
    MAX_SCORE = 8  # 6 keywords + 1 is_new + 1 relate
    THRESHOLD = MAX_SCORE // 2 + 1  # = 5
    
    print(f"Max score: {MAX_SCORE}", flush=True)
    print(f"Threshold formula: max//2 + 1 = {THRESHOLD}", flush=True)
    
    db = DatabaseManager()
    engine = InferenceController()
    
    # Get high-score articles without Thai translation
    with db.get_connection() as conn:
        cursor = conn.execute("""
            SELECT m.article_id, m.headline, m.ai_score, m.published_at, 
                   m.author_name, m.article_url, c.original_content,
                   s.domain_name as publisher
            FROM articles_meta m
            JOIN article_content c ON m.article_id = c.article_id
            JOIN sources s ON m.source_id = s.source_id
            WHERE m.ai_score >= ?
              AND (c.thai_content IS NULL OR c.thai_content = '')
            ORDER BY m.ai_score DESC
        """, (THRESHOLD,))
        articles = [dict(row) for row in cursor]
    
    print(f"Articles with score >= {THRESHOLD}: {len(articles)}", flush=True)
    
    if not articles:
        print("No articles to translate!")
        return
    
    # Load model
    print("\nLoading model...", flush=True)
    engine.load_model()
    
    translated = 0
    failed = 0
    start_time = time.time()
    
    for i, art in enumerate(articles, 1):
        print(f"\n[{i}/{len(articles)}] Score: {art['ai_score']} | {art['headline'][:40]}...", flush=True)
        
        try:
            result = engine.translate_article(
                article_id=art['article_id'],
                url=art.get('article_url', ''),
                author=art.get('author_name', ''),
                date=art.get('published_at', ''),
                publisher=art.get('publisher', ''),
                content=art.get('original_content', '')[:4000]
            )
            
            if result and result.get('Body'):
                # Format for UI display - structured sections
                thai_content = f"## หัวข้อ\n{result.get('Headline', '')}\n\n"
                thai_content += f"## นำเรื่อง\n{result.get('Lead', '')}\n\n"
                thai_content += f"## เนื้อหา\n{result.get('Body', '')}\n\n"
                thai_content += f"## วิเคราะห์\n{result.get('Analysis', '')}"
                
                db.update_thai_content(art['article_id'], thai_content)
                translated += 1
                print(f"  Translated: {len(thai_content)} chars", flush=True)
                
                # Show format preview for first article
                if i == 1:
                    print("\n--- FORMAT PREVIEW ---", flush=True)
                    print(thai_content[:500] + "...", flush=True)
                    print("--- END PREVIEW ---", flush=True)
            else:
                failed += 1
                print(f"  FAILED: No content", flush=True)
                
        except Exception as e:
            failed += 1
            print(f"  ERROR: {str(e)[:50]}", flush=True)
    
    engine.unload_model()
    
    elapsed = time.time() - start_time
    
    print("\n" + "=" * 60, flush=True)
    print("DONE", flush=True)
    print("=" * 60, flush=True)
    print(f"Translated: {translated}/{len(articles)}", flush=True)
    print(f"Failed: {failed}", flush=True)
    print(f"Time: {elapsed/60:.1f} min", flush=True)

if __name__ == "__main__":
    main()
