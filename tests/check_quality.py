"""
Check data quality of scraped articles.
"""
import sqlite3

conn = sqlite3.connect('data/aieat_news.db')
conn.row_factory = sqlite3.Row

# Check content quality - sample 5 articles
print('=== CONTENT QUALITY CHECK ===')
print()

cursor = conn.execute('''
    SELECT m.article_id, m.headline, m.author_name, c.original_content
    FROM articles_meta m
    JOIN article_content c ON m.article_id = c.article_id
    ORDER BY RANDOM()
    LIMIT 5
''')

for row in cursor:
    content = row['original_content']
    print(f"ID: {row['article_id']}")
    print(f"Headline: {row['headline'][:70]}...")
    print(f"Author: {row['author_name']}")
    print(f"Content Length: {len(content)} chars")
    print(f"First 300 chars:")
    print(content[:300])
    print('-' * 60)
    print()

# Stats
print('=== QUALITY STATS ===')
cursor = conn.execute('SELECT LENGTH(original_content) as len FROM article_content')
lengths = [r['len'] for r in cursor]
print(f'Total articles: {len(lengths)}')
print(f'Avg length: {sum(lengths)//len(lengths)} chars')
print(f'Min length: {min(lengths)} chars')
print(f'Max length: {max(lengths)} chars')
print(f'Short (<500): {len([l for l in lengths if l < 500])}')
print(f'Medium (500-2000): {len([l for l in lengths if 500 <= l < 2000])}')
print(f'Long (>2000): {len([l for l in lengths if l >= 2000])}')

# Check for garbage content
print()
print('=== GARBAGE CHECK ===')
cursor = conn.execute("SELECT COUNT(*) FROM article_content WHERE original_content LIKE '%subscribe%' OR original_content LIKE '%sign in%'")
paywall_count = cursor.fetchone()[0]
print(f'Articles with potential paywall text: {paywall_count}')

cursor = conn.execute("SELECT COUNT(*) FROM article_content WHERE LENGTH(original_content) < 200")
short_count = cursor.fetchone()[0]
print(f'Very short articles (<200 chars): {short_count}')

conn.close()
