"""
Normalize date formats in database.
Converts all dates to ISO 8601 format: YYYY-MM-DD HH:MM:SS
"""
import sqlite3
from datetime import datetime
from dateutil import parser

def normalize_date(date_str: str) -> str:
    """Convert various date formats to ISO 8601."""
    if not date_str or date_str.strip() == '':
        return None
    
    try:
        # Parse using dateutil (handles RFC 2822, ISO 8601, etc.)
        dt = parser.parse(date_str)
        # Return ISO format without timezone: YYYY-MM-DD HH:MM:SS
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except Exception as e:
        print(f"  Failed to parse: {date_str[:30]}... ({e})")
        return None

def main():
    conn = sqlite3.connect('data/aieat_news.db')
    conn.row_factory = sqlite3.Row
    
    # Get all articles with dates
    cursor = conn.execute('SELECT article_id, published_at FROM articles_meta WHERE published_at IS NOT NULL AND published_at != ""')
    articles = list(cursor)
    
    print(f'=== Date Normalization ===')
    print(f'Found {len(articles)} articles with dates')
    print()
    
    # Show sample formats before
    print('Before (sample):')
    for row in articles[:5]:
        print(f'  {row["published_at"]}')
    print()
    
    # Normalize all dates
    updated = 0
    failed = 0
    
    for row in articles:
        article_id = row['article_id']
        old_date = row['published_at']
        new_date = normalize_date(old_date)
        
        if new_date:
            conn.execute('UPDATE articles_meta SET published_at = ? WHERE article_id = ?', 
                        (new_date, article_id))
            updated += 1
        else:
            failed += 1
    
    conn.commit()
    
    print(f'Updated: {updated}')
    print(f'Failed: {failed}')
    print()
    
    # Show sample after
    print('After (sample):')
    cursor = conn.execute('SELECT published_at FROM articles_meta WHERE published_at IS NOT NULL LIMIT 5')
    for row in cursor:
        print(f'  {row[0]}')
    
    conn.close()
    print('\nDone!')

if __name__ == '__main__':
    main()
