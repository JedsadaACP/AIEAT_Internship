"""
AIEAT Database Manager - Data Access Object for SQLite operations.
"""
import sqlite3
import os
import hashlib
from typing import List, Dict, Optional, Any
from contextlib import contextmanager
from datetime import datetime

from app.utils.logger import get_app_logger
from app.utils.exceptions import (
    DatabaseError,
    DatabaseConnectionError,
    ArticleExistsError,
    ArticleNotFoundError,
)

logger = get_app_logger(__name__)


class DatabaseManager:
    """
    Data Access Object for AIEAT SQLite database.
    
    Handles all database operations: INSERT, SELECT, UPDATE for
    sources, articles, tags, and system configuration.
    """
    
    def __init__(self, db_name: str = "aieat_news.db"):
        """
        Initialize database connection.
        
        Args:
            db_name: Database filename in data/ directory
        """
        # Calculate paths relative to project root
        base_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(base_dir))
        
        self.db_path = os.path.join(project_root, "data", db_name)
        self.schema_path = os.path.join(project_root, "data", "schema.sql")
        
        # Initialize DB if needed
        if not os.path.exists(self.db_path):
            logger.warning(f"Database not found at: {self.db_path}")
            logger.info("Initializing database from schema...")
            self._initialize_db()
        else:
            logger.info(f"Database connected: {self.db_path}")
        
        # Cache status IDs for performance
        self._status_cache: Dict[str, int] = {}
        self._load_status_cache()
    
    @contextmanager
    def get_connection(self):
        """
        Context manager for database connections.
        
        Usage:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                ...
        """
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = ON")
            yield conn
            conn.commit()
        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            logger.error(f"Database connection error: {e}")
            raise DatabaseConnectionError(f"Failed to connect: {e}")
        finally:
            if conn:
                conn.close()
    
    def _initialize_db(self) -> None:
        """Create database from schema.sql."""
        if not os.path.exists(self.schema_path):
            raise FileNotFoundError(f"Schema not found: {self.schema_path}")
        
        with open(self.schema_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        try:
            conn = sqlite3.connect(self.db_path)
            conn.executescript(schema_sql)
            conn.commit()
            conn.close()
            logger.info("Database initialized successfully")
        except sqlite3.Error as e:
            logger.error(f"Failed to initialize database: {e}")
            raise DatabaseError(f"Schema execution failed: {e}")
    
    def _load_status_cache(self) -> None:
        """Load status IDs into memory cache."""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("SELECT status_id, status_name FROM master_status")
                for row in cursor:
                    self._status_cache[row['status_name']] = row['status_id']
            logger.debug(f"Loaded {len(self._status_cache)} status codes")
        except Exception as e:
            logger.warning(f"Could not load status cache: {e}")
    
    # ==================== STATUS ====================
    
    def get_status_id(self, status_name: str) -> Optional[int]:
        """
        Get status ID by name.
        
        Args:
            status_name: e.g., 'New', 'Scored', 'Translated'
        
        Returns:
            Status ID or None if not found
        """
        return self._status_cache.get(status_name)
    
    # ==================== SOURCES ====================
    
    def get_all_sources(self) -> List[Dict]:
        """Get all news sources."""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT source_id, domain_name, base_url, scraper_type, 
                       status_id, last_checked_at
                FROM sources
            """)
            return [dict(row) for row in cursor]
    
    def get_source_by_url(self, base_url: str) -> Optional[Dict]:
        """Get source by base URL."""
        with self.get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM sources WHERE base_url = ?",
                (base_url,)
            )
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def insert_source(self, domain_name: str, base_url: str, 
                      scraper_type: str = 'RSS') -> int:
        """
        Insert a new source.
        
        Returns:
            source_id of inserted source
        """
        status_id = self.get_status_id('Online') or 6
        
        with self.get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO sources (domain_name, base_url, scraper_type, status_id)
                VALUES (?, ?, ?, ?)
            """, (domain_name, base_url, scraper_type, status_id))
            conn.commit()
            logger.info(f"Inserted source: {domain_name}")
            return cursor.lastrowid
    
    def get_or_create_source(self, domain_name: str, base_url: str) -> int:
        """Get source ID or create if not exists."""
        source = self.get_source_by_url(base_url)
        if source:
            return source['source_id']
        return self.insert_source(domain_name, base_url)
    
    def delete_source(self, source_id: int):
        """Delete a source by ID. Articles are kept but source_id becomes orphaned."""
        with self.get_connection() as conn:
            conn.execute("DELETE FROM sources WHERE source_id = ?", (source_id,))
            logger.info(f"Deleted source ID: {source_id}")
    
    # ==================== ARTICLES ====================
    
    @staticmethod
    def generate_url_hash(url: str) -> str:
        """Generate SHA256 hash of URL for deduplication."""
        return hashlib.sha256(url.encode('utf-8')).hexdigest()
    
    def article_exists(self, url_hash: str) -> bool:
        """Check if article exists by URL hash."""
        with self.get_connection() as conn:
            cursor = conn.execute(
                "SELECT 1 FROM articles_meta WHERE url_hash = ?",
                (url_hash,)
            )
            return cursor.fetchone() is not None
    
    def _normalize_date(self, date_str: Optional[str]) -> Optional[str]:
        """
        Normalize any date format to ISO 8601 UTC format.
        Returns: '2026-01-12 16:30:00' or None if unparseable.
        """
        if not date_str:
            return None
        
        from dateutil import parser
        import pytz
        
        try:
            # Parse with dateutil (handles RFC 2822, ISO, etc.)
            dt = parser.parse(date_str, fuzzy=True)
            
            # Convert to UTC if timezone-aware
            if dt.tzinfo:
                dt = dt.astimezone(pytz.UTC).replace(tzinfo=None)
            
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        except Exception:
            return None
    
    def insert_article_meta(
        self,
        source_id: int,
        url_hash: str,
        headline: str,
        article_url: str,
        published_at: Optional[str] = None,
        author_name: Optional[str] = None
    ) -> int:
        """
        Insert article metadata.
        
        Returns:
            article_id of inserted article
        
        Raises:
            ArticleExistsError: If article already exists
        """
        if self.article_exists(url_hash):
            raise ArticleExistsError(f"Article exists: {url_hash[:16]}...")
        
        status_id = self.get_status_id('New') or 3
        
        # Normalize date to ISO format for reliable comparison
        normalized_date = self._normalize_date(published_at)
        
        with self.get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO articles_meta 
                (source_id, url_hash, headline, article_url, published_at, author_name, status_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (source_id, url_hash, headline, article_url, normalized_date, author_name, status_id))
            conn.commit()
            logger.debug(f"Inserted article: {headline[:50]}...")
            return cursor.lastrowid
    
    def insert_article_content(
        self,
        article_id: int,
        original_content: str,
        thai_content: Optional[str] = None,
        ai_reasoning: Optional[str] = None
    ) -> None:
        """Insert article full content."""
        with self.get_connection() as conn:
            conn.execute("""
                INSERT INTO article_content (article_id, original_content, thai_content, ai_reasoning)
                VALUES (?, ?, ?, ?)
            """, (article_id, original_content, thai_content, ai_reasoning))
            conn.commit()
            logger.debug(f"Inserted content for article_id: {article_id}")
    
    def insert_article(
        self,
        source_name: str,
        source_url: str,
        headline: str,
        article_url: str,
        content: str,
        published_at: Optional[str] = None,
        author_name: Optional[str] = None
    ) -> Optional[int]:
        """
        Insert complete article (meta + content) in one call.
        
        Returns:
            article_id or None if duplicate
        """
        url_hash = self.generate_url_hash(article_url)
        
        if self.article_exists(url_hash):
            logger.debug(f"Skipping duplicate: {headline[:40]}...")
            return None
        
        try:
            source_id = self.get_or_create_source(source_name, source_url)
            article_id = self.insert_article_meta(
                source_id=source_id,
                url_hash=url_hash,
                headline=headline,
                article_url=article_url,
                published_at=published_at,
                author_name=author_name
            )
            self.insert_article_content(article_id, content)
            return article_id
        except ArticleExistsError:
            return None
    
    def get_new_articles(self, limit: int = 100) -> List[Dict]:
        """Get articles with 'New' status (not yet scored)."""
        status_id = self.get_status_id('New') or 3
        
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT m.article_id, m.headline, m.article_url, m.published_at, m.author_name,
                       c.original_content
                FROM articles_meta m
                JOIN article_content c ON m.article_id = c.article_id
                WHERE m.status_id = ?
                ORDER BY m.created_at DESC
                LIMIT ?
            """, (status_id, limit))
            return [dict(row) for row in cursor]
    
    def get_article_by_id(self, article_id: int) -> Optional[Dict]:
        """Get article by ID with content."""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT m.*, c.original_content, c.thai_content, c.ai_reasoning
                FROM articles_meta m
                LEFT JOIN article_content c ON m.article_id = c.article_id
                WHERE m.article_id = ?
            """, (article_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def update_article_score(self, article_id: int, score: int) -> None:
        """Update article AI score and status to 'Scored'."""
        status_id = self.get_status_id('Scored') or 4
        
        with self.get_connection() as conn:
            conn.execute("""
                UPDATE articles_meta 
                SET ai_score = ?, status_id = ?, updated_at = CURRENT_TIMESTAMP
                WHERE article_id = ?
            """, (score, status_id, article_id))
            conn.commit()
            logger.debug(f"Updated score for article {article_id}: {score}")
    
    def update_thai_content(self, article_id: int, thai_content: str) -> None:
        """Update article Thai translation and status."""
        status_id = self.get_status_id('Translated') or 5
        
        with self.get_connection() as conn:
            conn.execute("""
                UPDATE article_content 
                SET thai_content = ?, updated_at = CURRENT_TIMESTAMP
                WHERE article_id = ?
            """, (thai_content, article_id))
            conn.execute("""
                UPDATE articles_meta 
                SET status_id = ?, updated_at = CURRENT_TIMESTAMP
                WHERE article_id = ?
            """, (status_id, article_id))
            conn.commit()
            logger.debug(f"Updated translation for article {article_id}")
    
    # ==================== STATS ====================
    
    def get_article_count(self) -> Dict[str, int]:
        """Get article counts by status."""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT ms.status_name, COUNT(m.article_id) as count
                FROM articles_meta m
                JOIN master_status ms ON m.status_id = ms.status_id
                GROUP BY ms.status_name
            """)
            return {row['status_name']: row['count'] for row in cursor}
    
    # ==================== TAGS (Keywords & Domains) ====================
    
    def get_keywords(self) -> List[str]:
        """Get all active keywords from tags table."""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT tag_name FROM tags 
                WHERE tag_type = 'Keyword' AND status_id = ?
                ORDER BY tag_id
            """, (self.get_status_id('Active'),))
            return [row['tag_name'] for row in cursor]
    
    def get_domains(self) -> List[str]:
        """Get all active domains from tags table."""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT tag_name FROM tags 
                WHERE tag_type = 'Domain' AND status_id = ?
                ORDER BY tag_id
            """, (self.get_status_id('Active'),))
            return [row['tag_name'] for row in cursor]
    
    def add_keyword(self, keyword: str) -> int:
        """Add a new keyword. Returns tag_id."""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO tags (tag_name, tag_type, weight_score, status_id)
                VALUES (?, 'Keyword', 1, ?)
            """, (keyword, self.get_status_id('Active')))
            return cursor.lastrowid
    
    def add_domain(self, domain: str) -> int:
        """Add a new domain. Returns tag_id."""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO tags (tag_name, tag_type, weight_score, status_id)
                VALUES (?, 'Domain', 1, ?)
            """, (domain, self.get_status_id('Active')))
            return cursor.lastrowid
    
    def remove_tag(self, tag_id: int):
        """Remove a tag by ID."""
        with self.get_connection() as conn:
            conn.execute("DELETE FROM tags WHERE tag_id = ?", (tag_id,))
    
    def delete_keyword(self, keyword: str):
        """Delete a keyword by name."""
        with self.get_connection() as conn:
            conn.execute("DELETE FROM tags WHERE tag_name = ? AND tag_type = 'Keyword'", (keyword,))
    
    def delete_domain(self, domain: str):
        """Delete a domain by name."""
        with self.get_connection() as conn:
            conn.execute("DELETE FROM tags WHERE tag_name = ? AND tag_type = 'Domain'", (domain,))

    def add_article_tags(self, article_id: int, tag_names: List[str]):
        """Link an article to tags (keywords)."""
        if not tag_names:
            return
            
        with self.get_connection() as conn:
            for tag in tag_names:
                # Find tag_id first (case-insensitive)
                cursor = conn.execute(
                    "SELECT tag_id FROM tags WHERE LOWER(tag_name) = LOWER(?)", 
                    (tag,)
                )
                row = cursor.fetchone()
                if row:
                    tag_id = row['tag_id']
                    # Insert mapping, ignore if exists
                    try:
                        conn.execute("""
                            INSERT OR IGNORE INTO article_tag_map (article_id, tag_id)
                            VALUES (?, ?)
                        """, (article_id, tag_id))
                    except Exception:
                        pass
            conn.commit()

    
    # ==================== SYSTEM PROFILE ====================
    
    def get_system_profile(self) -> Dict[str, Any]:
        """Get system configuration."""
        with self.get_connection() as conn:
            row = conn.execute("SELECT * FROM system_profile WHERE profile_id = 1").fetchone()
            if row:
                return dict(row)
            return {}
    
    def update_system_profile(self, **kwargs):
        """Update system profile settings."""
        with self.get_connection() as conn:
            # Build SET clause from kwargs
            set_clause = ", ".join(f"{k} = ?" for k in kwargs.keys())
            values = list(kwargs.values())
            conn.execute(f"""
                UPDATE system_profile 
                SET {set_clause}, updated_at = CURRENT_TIMESTAMP
                WHERE profile_id = 1
            """, values)

    # ==================== BATCH QUERIES ====================

    def get_article_ids_by_filter(self, 
                                date_range: str, 
                                keyword: Optional[str] = None, 
                                min_score: int = 0,
                                target_status: Optional[str] = None) -> List[int]:
        """
        Get article IDs matching criteria.
        date_range: 'today', 'week', 'month', 'custom_X' (days)
        keyword: specific keyword or None/all
        min_score: minimum score filter
        target_status: 'New' (for scoring), 'Scored' (for translating)
        """
        with self.get_connection() as conn:
            sql = """
                SELECT DISTINCT m.article_id
                FROM articles_meta m
                JOIN master_status ms ON m.status_id = ms.status_id
                LEFT JOIN article_tag_map atm ON m.article_id = atm.article_id
                LEFT JOIN tags t ON atm.tag_id = t.tag_id
                WHERE 1=1
            """
            params = []

            # Status Filter
            if target_status:
                sql += " AND ms.status_name = ?"
                params.append(target_status)

            # Date Filter (using published_at - now normalized to ISO format)
            from datetime import datetime, timedelta
            import pytz
            
            local_tz = pytz.timezone('Asia/Bangkok')
            now_local = datetime.now(local_tz)
            
            if date_range == "today":
                # Get start of today in local time, then convert to UTC
                start_of_today_local = now_local.replace(hour=0, minute=0, second=0, microsecond=0)
                cutoff_utc = start_of_today_local.astimezone(pytz.UTC).strftime('%Y-%m-%d %H:%M:%S')
                sql += f" AND m.published_at >= '{cutoff_utc}'"
            elif date_range == "week":
                cutoff_local = now_local - timedelta(days=7)
                cutoff_utc = cutoff_local.astimezone(pytz.UTC).strftime('%Y-%m-%d %H:%M:%S')
                sql += f" AND m.published_at >= '{cutoff_utc}'"
            elif date_range == "month":
                cutoff_local = now_local - timedelta(days=28)
                cutoff_utc = cutoff_local.astimezone(pytz.UTC).strftime('%Y-%m-%d %H:%M:%S')
                sql += f" AND m.published_at >= '{cutoff_utc}'"
            elif date_range and date_range.startswith("custom_"):
                days = int(date_range.split("_")[1])
                cutoff_local = now_local - timedelta(days=days)
                cutoff_utc = cutoff_local.astimezone(pytz.UTC).strftime('%Y-%m-%d %H:%M:%S')
                sql += f" AND m.published_at >= '{cutoff_utc}'"

            # Keyword Filter (case-insensitive)
            if keyword and keyword.lower() != "all":
                sql += " AND LOWER(t.tag_name) = LOWER(?)"
                params.append(keyword)

            # Score Filter (for Translation)
            if min_score > 0:
                sql += " AND COALESCE(m.ai_score, 0) >= ?"
                params.append(min_score)

            cursor = conn.execute(sql, params)
            return [row['article_id'] for row in cursor]

    # ==================== STYLES ====================
    
    def get_styles(self) -> List[Dict]:
        """Get all styles."""
        with self.get_connection() as conn:
            rows = conn.execute("SELECT * FROM styles ORDER BY is_default DESC, name").fetchall()
            return [dict(row) for row in rows]
    
    def get_style(self, style_id: int) -> Optional[Dict]:
        """Get a single style by ID."""
        with self.get_connection() as conn:
            row = conn.execute("SELECT * FROM styles WHERE style_id = ?", (style_id,)).fetchone()
            return dict(row) if row else None
    
    def add_style(self, name: str, **kwargs) -> int:
        """Add a new style. Returns style_id."""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO styles (name, output_type, persona, structure_headline, 
                                   structure_lead, structure_body, structure_analysis, content_order)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                name,
                kwargs.get('output_type', 'Translation & Rewrite'),
                kwargs.get('persona', ''),
                kwargs.get('structure_headline', ''),
                kwargs.get('structure_lead', ''),
                kwargs.get('structure_body', ''),
                kwargs.get('structure_analysis', ''),
                kwargs.get('content_order', 'headline,lead,body,analysis'),
            ))
            return cursor.lastrowid
    
    def update_style(self, style_id: int, **kwargs):
        """Update a style."""
        with self.get_connection() as conn:
            set_clause = ", ".join(f"{k} = ?" for k in kwargs.keys())
            values = list(kwargs.values()) + [style_id]
            conn.execute(f"""
                UPDATE styles 
                SET {set_clause}, updated_at = CURRENT_TIMESTAMP
                WHERE style_id = ?
            """, values)
    
    def delete_style(self, style_id: int):
        """Delete a style."""
        with self.get_connection() as conn:
            conn.execute("DELETE FROM styles WHERE style_id = ? AND is_default = 0", (style_id,))
    
    def get_active_style(self) -> Optional[Dict]:
        """Get the currently active style settings."""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT * FROM styles WHERE is_active = 1 LIMIT 1
            """)
            row = cursor.fetchone()
            if row:
                columns = [desc[0] for desc in cursor.description]
                return dict(zip(columns, row))
            return None
    
    def set_active_style(self, style_id: int):
        """Set a style as active (deactivates others)."""
        with self.get_connection() as conn:
            # Deactivate all styles
            conn.execute("UPDATE styles SET is_active = 0")
            # Activate selected style
            conn.execute("UPDATE styles SET is_active = 1 WHERE style_id = ?", (style_id,))


# Test when run directly
if __name__ == "__main__":
    db = DatabaseManager()
    print(f"Status cache: {db._status_cache}")
    print(f"Article counts: {db.get_article_count()}")