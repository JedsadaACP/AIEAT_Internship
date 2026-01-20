"""
Sprint 1 Integration Test - Scrape 5 sources and verify DB storage.
"""
import asyncio
import sys
sys.path.insert(0, '.')

from app.services.scraper_service import ScraperService

async def test():
    scraper = ScraperService()
    
    # Test with first 5 sources only
    test_sources = scraper.config.sources[:5]
    print(f"Testing with {len(test_sources)} sources...")
    for s in test_sources:
        print(f"  - {s['name']}")
    print()
    
    stats = await scraper.run(sources=test_sources)
    
    print(f"\n=== RESULTS ===")
    print(f"New articles: {stats['new_articles']}")
    print(f"Sources with articles: {stats['successful_sources']}/{stats['total_sources']}")
    print(f"Duplicates: {stats['duplicates']}")
    print(f"Errors: {stats['errors']}")
    print(f"Time: {stats['elapsed_seconds']}s")
    
    # Check DB
    counts = scraper.db.get_article_count()
    print(f"\nDB Article Counts: {counts}")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    asyncio.run(test())
