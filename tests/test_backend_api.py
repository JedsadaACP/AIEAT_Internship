"""Test BackendAPI facade"""
import sys
import os
import io

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from app.services.backend_api import BackendAPI

def main():
    print("=" * 60)
    print("BackendAPI Test")
    print("=" * 60)
    
    api = BackendAPI()
    
    # Test config
    print("\n--- Config ---")
    config = api.get_config()
    print(f"Keywords: {config['keywords']}")
    print(f"Domains: {config['domains']}")
    print(f"Max score: {config['max_score']}")
    print(f"Threshold: {config['threshold']}")
    
    # Test articles
    print("\n--- Articles ---")
    articles = api.get_articles(limit=5)
    print(f"Total returned: {len(articles)}")
    for a in articles[:3]:
        headline = a['headline'][:40] if a['headline'] else 'No headline'
        print(f"  [{a['ai_score']}] {headline}...")
    
    # Test article detail
    if articles:
        print("\n--- Article Detail ---")
        detail = api.get_article_detail(articles[0]['article_id'])
        print(f"ID: {detail['article_id']}")
        print(f"Headline: {detail['headline'][:50]}...")
        print(f"Has Thai: {'Yes' if detail.get('thai_content') else 'No'}")
        print(f"Content length: {len(detail.get('original_content', ''))}")
    
    # Test stats
    print("\n--- Dashboard Stats ---")
    stats = api.get_dashboard_stats()
    print(f"Articles: {stats['articles']}")
    print(f"Sources: {stats['sources']}")
    print(f"Keywords: {stats['keywords']}")
    print(f"Domains: {stats['domains']}")
    
    print("\n" + "=" * 60)
    print("All tests passed!")
    print("=" * 60)

if __name__ == "__main__":
    main()
