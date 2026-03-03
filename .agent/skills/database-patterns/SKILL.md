---
name: database-patterns
description: SQLite database patterns and optimization
---

# Database Patterns Skill

## 🛠️ Level 3 Resources
- **Schema Snapshot**: `python .agent/skills/database-patterns/resources/snapshot_schema.py`
  - *Use this instead of reading table_info manually.*

## Schema Design

### 1. Use Meaningful Primary Keys
```sql
CREATE TABLE articles_meta (
    article_id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id INTEGER NOT NULL,
    headline TEXT NOT NULL,
    -- Always include created_at for debugging
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### 2. Composite Unique Constraints
```sql
-- When same value can exist with different types
CREATE TABLE tags (
    tag_id INTEGER PRIMARY KEY AUTOINCREMENT,
    tag_name TEXT NOT NULL,
    tag_type TEXT NOT NULL,  -- 'Keyword' or 'Domain'
    UNIQUE(tag_name, tag_type)  -- Composite unique!
);
```

### 3. Foreign Keys with ON DELETE
```sql
CREATE TABLE article_tag_map (
    article_id INTEGER,
    tag_id INTEGER,
    FOREIGN KEY (article_id) REFERENCES articles_meta(article_id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(tag_id) ON DELETE CASCADE
);
```

## Query Optimization

### 1. Always Handle NULL
```sql
-- Bad: Breaks if ai_score is NULL
WHERE ai_score >= 5

-- Good: Handle NULL explicitly
WHERE COALESCE(ai_score, 0) >= 5
```

### 2. Use Indexes for Frequent Queries
```sql
CREATE INDEX idx_articles_source ON articles_meta(source_id);
CREATE INDEX idx_articles_date ON articles_meta(published_at);
```

### 3. Efficient Pagination
```sql
-- For large tables, use keyset pagination
SELECT * FROM articles_meta
WHERE article_id > :last_id
ORDER BY article_id
LIMIT 20;
```

### 4. Batch Operations
```python
# Good: Single transaction for multiple inserts
with conn:
    conn.executemany(
        "INSERT INTO tags (tag_name, tag_type) VALUES (?, ?)",
        [("AI", "Keyword"), ("Tech", "Keyword")]
    )

# Bad: Individual commits
for tag in tags:
    conn.execute("INSERT INTO tags ...")
    conn.commit()  # Slow!
```

## Common Patterns

### Get or Create
```python
def get_or_create_tag(self, name: str, tag_type: str) -> int:
    with self.get_connection() as conn:
        # Try to get existing
        row = conn.execute(
            "SELECT tag_id FROM tags WHERE tag_name = ? AND tag_type = ?",
            (name, tag_type)
        ).fetchone()
        
        if row:
            return row['tag_id']
        
        # Create new
        cursor = conn.execute(
            "INSERT INTO tags (tag_name, tag_type) VALUES (?, ?)",
            (name, tag_type)
        )
        return cursor.lastrowid
```

### Upsert (SQLite 3.24+)
```sql
INSERT INTO config (key, value)
VALUES ('model_name', 'typhoon')
ON CONFLICT(key) DO UPDATE SET value = excluded.value;
```

## Migration Scripts

When changing schema on existing database:

```python
def migrate():
    # 1. Check current schema
    # 2. Create backup
    # 3. Apply changes in transaction
    # 4. Verify migration
    with conn:
        # Drop and recreate with new constraint
        conn.execute("ALTER TABLE tags RENAME TO tags_old")
        conn.execute("""
            CREATE TABLE tags (
                tag_id INTEGER PRIMARY KEY,
                tag_name TEXT NOT NULL,
                tag_type TEXT NOT NULL,
                UNIQUE(tag_name, tag_type)
            )
        """)
        conn.execute("INSERT INTO tags SELECT * FROM tags_old")
        conn.execute("DROP TABLE tags_old")
```
