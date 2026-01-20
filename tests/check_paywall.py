"""
Check potential paywall articles.
"""
import sqlite3

conn = sqlite3.connect('data/aieat_news.db')
conn.row_factory = sqlite3.Row

print('=== POTENTIAL PAYWALL ARTICLES ===')
print('(Shortest articles containing "subscribe" or "sign in")\n')

cursor = conn.execute("""
    SELECT m.headline, LENGTH(c.original_content) as len, 
           SUBSTR(c.original_content, 1, 500) as preview
    FROM articles_meta m 
    JOIN article_content c ON m.article_id = c.article_id 
    WHERE c.original_content LIKE '%subscribe%' 
       OR c.original_content LIKE '%sign in%'
    ORDER BY len ASC 
    LIMIT 8
""")

for row in cursor:
    print(f"Length: {row['len']} chars")
    print(f"Headline: {row['headline'][:60]}...")
    print(f"Preview:")
    print(row['preview'][:400])
    print('-' * 60)
    print()

# Check for actual garbage patterns
print('=== CHECKING FOR REAL GARBAGE ===')
garbage_patterns = [
    "please subscribe to continue",
    "create a free account", 
    "this content is only available",
    "you have reached your limit",
    "member-only content"
]

for pattern in garbage_patterns:
    cursor = conn.execute(
        f"SELECT COUNT(*) FROM article_content WHERE LOWER(original_content) LIKE '%{pattern}%'"
    )
    count = cursor.fetchone()[0]
    print(f"'{pattern}': {count} articles")

conn.close()
