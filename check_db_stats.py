import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'data', 'aieat_news.db')
conn = sqlite3.connect(db_path)

print("=" * 60)
print("DATABASE STATS")
print("=" * 60)

# Total counts
total = conn.execute('SELECT COUNT(*) FROM articles_meta').fetchone()[0]
with_content = conn.execute('SELECT COUNT(*) FROM article_content WHERE original_content IS NOT NULL').fetchone()[0]
print(f"Total articles: {total}")
print(f"With content: {with_content}")

# Sample keyword analysis - check if articles contain keywords
print("\n=== KEYWORD MENTIONS (in content) ===")
keywords = ['Nvidia', 'Google', 'Microsoft', 'crypto', 'AI', 'chipset']
for kw in keywords:
    count = conn.execute(f"SELECT COUNT(*) FROM article_content WHERE original_content LIKE '%{kw}%'").fetchone()[0]
    print(f"  {kw}: {count} articles")

conn.close()
print("\n" + "=" * 60)
