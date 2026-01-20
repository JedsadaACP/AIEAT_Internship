"""
Batch Scoring Script - Score all pending articles
Run in background: python scripts/batch_score.py
"""
import sys
import os
import io
import time
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from app.services.database_manager import DatabaseManager
from app.services.ai_engine import InferenceController

def main():
    print("=" * 60)
    print("AIEAT BATCH SCORING")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    db = DatabaseManager()
    engine = InferenceController()
    
    # Get pending articles
    pending = db.get_new_articles(limit=1000)
    total = len(pending)
    print(f"\nPending articles: {total}")
    
    if total == 0:
        print("No articles to score!")
        return
    
    # Load model
    print("\nLoading model (GPU)...")
    start_load = time.time()
    engine.load_model()
    print(f"Model loaded in {time.time() - start_load:.1f}s")
    
    # Score articles
    scored = 0
    failed = 0
    total_time = 0
    
    print(f"\nScoring {total} articles...\n")
    
    for i, art in enumerate(pending, 1):
        start = time.time()
        
        try:
            result = engine.score_article(
                article_id=art['article_id'],
                url=art.get('article_url', ''),
                author=art.get('author_name', ''),
                date=art.get('published_at', ''),
                content=art.get('original_content', '')[:2000]
            )
            
            elapsed = time.time() - start
            total_time += elapsed
            
            if result and result.get('total_score', 0) >= 0:
                db.update_article_score(art['article_id'], result['total_score'])
                scored += 1
                avg = total_time / scored
                remaining = (total - i) * avg
                
                print(f"[{i}/{total}] Score: {result['total_score']} | {elapsed:.1f}s | ETA: {remaining/60:.0f}min | {art['headline'][:40]}...")
            else:
                failed += 1
                print(f"[{i}/{total}] FAILED | {art['headline'][:40]}...")
                
        except Exception as e:
            failed += 1
            print(f"[{i}/{total}] ERROR: {e}")
        
        # Progress save every 50 articles
        if i % 50 == 0:
            print(f"\n--- Checkpoint: {scored} scored, {failed} failed ---\n")
    
    engine.unload_model()
    
    # Summary
    print("\n" + "=" * 60)
    print("SCORING COMPLETE")
    print("=" * 60)
    print(f"Scored: {scored}")
    print(f"Failed: {failed}")
    print(f"Total time: {total_time/60:.1f} minutes")
    print(f"Average: {total_time/max(scored,1):.1f}s per article")
    print(f"Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
