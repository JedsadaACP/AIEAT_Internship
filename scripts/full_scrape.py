"""Run full scrape on all 74 sources"""
import sys
import os
import io
import asyncio

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stdout.reconfigure(line_buffering=True)

from app.services.scraper_service import ScraperService
from app.services.database_manager import DatabaseManager

async def main():
    print("=" * 60, flush=True)
    print("FULL SCRAPE - All 74 Sources", flush=True)
    print("=" * 60, flush=True)
    
    db = DatabaseManager()
    scraper = ScraperService(db=db)
    
    sources = scraper.config.sources
    print(f"\nSources: {len(sources)}", flush=True)
    print(f"Keywords: {scraper.config.keywords}", flush=True)
    
    # Progress callback
    def progress(current, total, name):
        print(f"[{current}/{total}] {name}", flush=True)
    
    print("\n--- Starting full scrape ---", flush=True)
    stats = await scraper.run(sources=sources, progress_callback=progress)
    
    print(f"\n--- Results ---", flush=True)
    print(f"Sources processed: {stats.get('sources_processed', 0)}", flush=True)
    print(f"New articles: {stats.get('articles_saved', 0)}", flush=True)
    print(f"Errors: {stats.get('errors', 0)}", flush=True)
    
    # Check DB
    counts = db.get_article_count()
    total = sum(counts.values()) if counts else 0
    print(f"\nDB Total: {total} articles", flush=True)

if __name__ == "__main__":
    asyncio.run(main())
