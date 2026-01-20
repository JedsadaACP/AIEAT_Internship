"""
Clean articles from DB while keeping config, sources, keywords, domains, and styles.
"""
import sqlite3

conn = sqlite3.connect('data/aieat_news.db')

# Delete only articles data
conn.execute("DELETE FROM article_content")
conn.execute("DELETE FROM articles_meta")

# Reset auto-increment
conn.execute("DELETE FROM sqlite_sequence WHERE name IN ('articles_meta', 'article_content')")

conn.commit()

# Check counts
cursor = conn.execute("SELECT COUNT(*) FROM articles_meta")
count = cursor.fetchone()[0]
print(f"Articles remaining: {count}")

cursor = conn.execute("SELECT COUNT(*) FROM sources")
sources = cursor.fetchone()[0]
print(f"Sources preserved: {sources}")

conn.close()
print("Database cleaned successfully!")
