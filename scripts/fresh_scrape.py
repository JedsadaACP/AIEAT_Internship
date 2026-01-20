"""Run fresh scrape with refactored backend"""
import sys
import os
import io
import asyncio

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from app.services.scraper_service import ScraperService
from app.services.database_manager import DatabaseManager

async def main():
    print("=" * 60)
    print("FRESH SCRAPE - DB Configured Backend")
    print("=" * 60)
    
    db = DatabaseManager()
    scraper = ScraperService(db=db)
    
    print(f"\nKeywords: {scraper.config.keywords}")
    print(f"Sources: {len(scraper.config.sources)}")
    
    # Run scrape on first 10 sources for quick test
    print("\n--- Running scrape on 10 sources ---")
    stats = await scraper.run(sources=scraper.config.sources[:10])
    
    print(f"\n--- Results ---")
    print(f"Processed: {stats.get('sources_processed', 0)} sources")
    print(f"New articles: {stats.get('articles_saved', 0)}")
    print(f"Errors: {stats.get('errors', 0)}")
    
    # Check DB
    counts = db.get_article_count()
    print(f"\nDB State: {counts}")

if __name__ == "__main__":
    asyncio.run(main())
