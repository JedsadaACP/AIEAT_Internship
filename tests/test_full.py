"""
Full 74-source integration test.
"""
import asyncio
import sys
sys.path.insert(0, '.')

from app.services.scraper_service import ScraperService

async def test_full():
    scraper = ScraperService()
    
    print(f"[START] Starting FULL test with {len(scraper.config.sources)} sources...")
    print(f"   Batch size: {scraper.config.settings.get('batch_size', 5)}")
    print(f"   Max articles per source: {scraper.config.settings.get('max_articles_saved_per_source', 30)}")
    print()
    
    def progress(current, total, name):
        pct = (current / total) * 100
        print(f"\r[{current}/{total}] ({pct:.0f}%) {name}...", end="", flush=True)
    
    stats = await scraper.run(progress_callback=progress)
    
    print()
    print()
    print("=" * 50)
    print("[RESULTS] FULL TEST RESULTS")
    print("=" * 50)
    print(f"New articles: {stats['new_articles']}")
    print(f"Sources with articles: {stats['successful_sources']}/{stats['total_sources']}")
    print(f"Duplicates: {stats['duplicates']}")
    print(f"Errors: {stats['errors']}")
    print(f"Time: {stats['elapsed_minutes']:.2f} minutes")
    print()
    
    # Check DB
    counts = scraper.db.get_article_count()
    print(f"DB Article Counts: {counts}")
    
    # Show sources breakdown
    print()
    print("Sources in DB:")
    with scraper.db.get_connection() as conn:
        cursor = conn.execute("SELECT domain_name FROM sources ORDER BY source_id")
        sources = [row['domain_name'] for row in cursor]
        print(f"  Total: {len(sources)}")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    asyncio.run(test_full())
