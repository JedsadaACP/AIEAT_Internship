"""
Query database to verify stored data.
"""
import sqlite3

db_path = 'data/aieat_news.db'
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row

# Check articles_meta
print('=== ARTICLES_META (First 5) ===')
cursor = conn.execute('SELECT article_id, headline, article_url, published_at, author_name, ai_score, status_id FROM articles_meta LIMIT 5')
for row in cursor:
    print(f"ID: {row['article_id']}")
    headline = row['headline'] or 'N/A'
    print(f"  Headline: {headline[:60]}...")
    url = row['article_url'] or 'N/A'
    print(f"  URL: {url[:50]}...")
    print(f"  Published: {row['published_at']}")
    print(f"  Author: {row['author_name']}")
    print(f"  Score: {row['ai_score']}, Status: {row['status_id']}")
    print()

# Check article_content
print('=== ARTICLE_CONTENT (First 2) ===')
cursor = conn.execute('SELECT article_id, LENGTH(original_content) as content_len, thai_content FROM article_content LIMIT 2')
for row in cursor:
    print(f"ID: {row['article_id']}, Content Length: {row['content_len']} chars, Thai: {row['thai_content']}")

# Check sources
print()
print('=== SOURCES ===')
cursor = conn.execute('SELECT source_id, domain_name, base_url FROM sources')
for row in cursor:
    print(f"{row['source_id']}: {row['domain_name']} - {row['base_url']}")

# Summary
print()
print('=== SUMMARY ===')
meta_count = conn.execute('SELECT COUNT(*) FROM articles_meta').fetchone()[0]
content_count = conn.execute('SELECT COUNT(*) FROM article_content').fetchone()[0]
source_count = conn.execute('SELECT COUNT(*) FROM sources').fetchone()[0]
print(f"Total articles_meta: {meta_count}")
print(f"Total article_content: {content_count}")
print(f"Total sources: {source_count}")

conn.close()
