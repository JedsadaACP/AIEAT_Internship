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
            db_name: Database filename in data/ directory OR ':memory:'
        """
        # Calculate paths using centralized path utility
        from app.utils.paths import get_data_dir
        data_dir = get_data_dir()
        
        if db_name == ":memory:":
            self.db_path = ":memory:"
            self.schema_path = os.path.join(data_dir, "schema.sql")
        else:
            db_filename = os.path.basename(db_name)
            self.db_path = os.path.join(data_dir, db_filename)
            self.schema_path = os.path.join(data_dir, "schema.sql")
            
            # Initialize DB if needed
            if not os.path.exists(self.db_path):
                logger.warning(f"Database not found at: {self.db_path}")
                logger.info("Initializing database from schema...")
                self._initialize_db()
            else:
                logger.info(f"Database connected: {self.db_path}")
        
        # Cache status IDs for performance
        # For :memory:, this will fail if schema not loaded first, 
        # so we wrap in try-except or handle in caller
        self._status_cache: Dict[str, int] = {}
        self._persistent_conn = None
        
        try:
            self._load_status_cache()
            self.ensure_profiles_table()  # <-- ADD THIS LINE
        except Exception as e:
            logger.warning(f"Status cache load failed (normal for new :memory: DB): {e}")
    
    def set_persistent_connection(self, conn: sqlite3.Connection):
        """Set a persistent connection for testing (e.g. :memory:)."""
        self._persistent_conn = conn
    
    @contextmanager
    def get_connection(self):
        """
        Context manager for database connections.
        
        Usage:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                ...
        """
        # If persistent connection is set (for tests), use it directly
        if self._persistent_conn:
            # We don't close persistent connections automatically
            # The caller (conftest.py) must close it.
            # We also don't commit automatically here to allow transaction control?
            # Actually, we should probably yield it but NOT close it in finally.
            try:
                yield self._persistent_conn
                self._persistent_conn.commit()
            except sqlite3.Error as e:
                self._persistent_conn.rollback()
                logger.error(f"Persistent DB error: {e}")
                raise DatabaseConnectionError(f"Failed persistent op: {e}")
            return

        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute("PRAGMA synchronous=NORMAL;")
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
        """Get active keywords for the current profile."""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT tag_name FROM tags
                WHERE tag_type = 'Keyword' AND status_id = ?
                AND profile_id = (SELECT profile_id FROM user_profiles WHERE is_active = 1)
                ORDER BY tag_id
            """, (self.get_status_id('Active'),))
            return [row['tag_name'] for row in cursor]
    
    def get_domains(self) -> List[str]:
        """Get active domains for the current profile."""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT tag_name FROM tags
                WHERE tag_type = 'Domain' AND status_id = ?
                AND profile_id = (SELECT profile_id FROM user_profiles WHERE is_active = 1)
                ORDER BY tag_id
            """, (self.get_status_id('Active'),))
            return [row['tag_name'] for row in cursor]
    
    def add_keyword(self, keyword: str, profile_id: int = None) -> int:
        """Add a keyword to specific profile. Returns tag_id."""
        if profile_id is None:
            profile_id = self._get_active_profile_id()
        with self.get_connection() as conn:
            existing = conn.execute(
                "SELECT tag_id FROM tags WHERE tag_name = ? AND tag_type = 'Keyword' AND profile_id = ?",
                (keyword, profile_id)
            ).fetchone()
            if existing:
                return existing['tag_id']
            try:
                cursor = conn.execute("""
                    INSERT INTO tags (tag_name, tag_type, weight_score, status_id, profile_id)
                    VALUES (?, 'Keyword', 1, ?, ?)
                """, (keyword, self.get_status_id('Active'), profile_id))
                return cursor.lastrowid
            except sqlite3.IntegrityError:
                # Race condition fallback — re-check
                row = conn.execute(
                    "SELECT tag_id FROM tags WHERE tag_name = ? AND tag_type = 'Keyword' AND profile_id = ?",
                    (keyword, profile_id)
                ).fetchone()
                return row['tag_id'] if row else 0
    
    def add_domain(self, domain: str, profile_id: int = None) -> int:
        """Add a domain to specific profile. Returns tag_id."""
        if profile_id is None:
            profile_id = self._get_active_profile_id()
        with self.get_connection() as conn:
            existing = conn.execute(
                "SELECT tag_id FROM tags WHERE tag_name = ? AND tag_type = 'Domain' AND profile_id = ?",
                (domain, profile_id)
            ).fetchone()
            if existing:
                return existing['tag_id']
            try:
                cursor = conn.execute("""
                    INSERT INTO tags (tag_name, tag_type, weight_score, status_id, profile_id)
                    VALUES (?, 'Domain', 1, ?, ?)
                """, (domain, self.get_status_id('Active'), profile_id))
                return cursor.lastrowid
            except sqlite3.IntegrityError:
                # Race condition fallback — re-check
                row = conn.execute(
                    "SELECT tag_id FROM tags WHERE tag_name = ? AND tag_type = 'Domain' AND profile_id = ?",
                    (domain, profile_id)
                ).fetchone()
                return row['tag_id'] if row else 0
    
    def remove_tag(self, tag_id: int):
        """Remove a tag by ID."""
        with self.get_connection() as conn:
            conn.execute("DELETE FROM tags WHERE tag_id = ?", (tag_id,))
    
    def delete_keyword(self, keyword: str, profile_id: int = None):
        """Delete a keyword from specific profile."""
        if profile_id is None:
            profile_id = self._get_active_profile_id()
        with self.get_connection() as conn:
            conn.execute("DELETE FROM tags WHERE tag_name = ? AND tag_type = 'Keyword' AND profile_id = ?", (keyword, profile_id))
    
    def delete_domain(self, domain: str, profile_id: int = None):
        """Delete a domain from specific profile."""
        if profile_id is None:
            profile_id = self._get_active_profile_id()
        with self.get_connection() as conn:
            conn.execute("DELETE FROM tags WHERE tag_name = ? AND tag_type = 'Domain' AND profile_id = ?", (domain, profile_id))

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

    # ==================== USER PROFILES ====================
    def ensure_profiles_table(self):
        """Create user_profiles table if missing and migrate tags for profile_id."""
        with self.get_connection() as conn:
            # Create table (execute, NOT executescript — executescript auto-commits and breaks context)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS user_profiles (
                    profile_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    profile_name TEXT NOT NULL UNIQUE,
                    description TEXT,
                    active_style_id INTEGER DEFAULT 1,
                    is_active INTEGER DEFAULT 0,
                    is_system INTEGER DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Migrate: add is_system column if missing
            try:
                cursor = conn.execute("PRAGMA table_info(user_profiles)")
                columns = [row[1] for row in cursor]
                if 'is_system' not in columns:
                    conn.execute("ALTER TABLE user_profiles ADD COLUMN is_system INTEGER DEFAULT 0")
            except Exception:
                pass
            
            # Add org_name column if it doesn't exist
            cursor = conn.execute("PRAGMA table_info(user_profiles)")
            columns = [info[1] for info in cursor.fetchall()]
            if 'org_name' not in columns:
                conn.execute("ALTER TABLE user_profiles ADD COLUMN org_name TEXT DEFAULT ''")
            
            # Migrate tags: add profile_id and fix UNIQUE constraint
            try:
                cursor = conn.execute("PRAGMA table_info(tags)")
                columns = [row[1] for row in cursor]
                
                if 'profile_id' not in columns:
                    # Step 1: Add profile_id column
                    conn.execute("ALTER TABLE tags ADD COLUMN profile_id INTEGER DEFAULT 1")
                    logger.info("Added profile_id column to tags table")
                
                # Step 2: Check if UNIQUE constraint includes profile_id
                # Get current table schema to check constraint
                schema_row = conn.execute(
                    "SELECT sql FROM sqlite_master WHERE type='table' AND name='tags'"
                ).fetchone()
                
                if schema_row and 'profile_id' not in (schema_row[0] or '').split('UNIQUE')[1] if 'UNIQUE' in (schema_row[0] or '') else True:
                    # Rebuild table with correct UNIQUE constraint
                    logger.info("Rebuilding tags table with profile-scoped UNIQUE constraint...")
                    
                    conn.execute("PRAGMA foreign_keys=OFF")
                    
                    conn.execute("""
                        CREATE TABLE IF NOT EXISTS tags_new (
                            tag_id INTEGER PRIMARY KEY AUTOINCREMENT,
                            tag_name TEXT NOT NULL,
                            tag_type TEXT DEFAULT 'Keyword',
                            weight_score INTEGER DEFAULT 1,
                            status_id INTEGER,
                            profile_id INTEGER DEFAULT 1,
                            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                            updated_by TEXT,
                            UNIQUE(tag_name, tag_type, profile_id),
                            FOREIGN KEY (status_id) REFERENCES master_status(status_id)
                        )
                    """)
                    
                    # Copy all existing data
                    conn.execute("""
                        INSERT OR IGNORE INTO tags_new 
                            (tag_id, tag_name, tag_type, weight_score, status_id, profile_id, created_at, updated_at, updated_by)
                        SELECT tag_id, tag_name, tag_type, weight_score, status_id, 
                               COALESCE(profile_id, 1), created_at, updated_at, updated_by
                        FROM tags
                    """)
                    
                    conn.execute("DROP TABLE tags")
                    conn.execute("ALTER TABLE tags_new RENAME TO tags")
                    conn.execute("PRAGMA foreign_keys=ON")
                    
                    logger.info("Tags table rebuilt with UNIQUE(tag_name, tag_type, profile_id)")
                    
            except Exception as e:
                logger.warning(f"Tags migration: {e}")
            
            # Seed default profiles if empty
            count = conn.execute("SELECT COUNT(*) FROM user_profiles").fetchone()[0]
            if count == 0:
                first_style = conn.execute("SELECT style_id FROM styles ORDER BY style_id LIMIT 1").fetchone()
                safe_style = first_style[0] if first_style else 1
                conn.execute("INSERT OR IGNORE INTO user_profiles (profile_id, profile_name, description, active_style_id, is_active, is_system) VALUES (1, 'Technology & AI', 'AI, software, chips, cloud computing', ?, 1, 1)", (safe_style,))
                conn.execute("INSERT OR IGNORE INTO user_profiles (profile_id, profile_name, description, active_style_id, is_active, is_system) VALUES (2, 'Finance & Markets', 'Stock markets, banking, fintech, crypto', ?, 0, 1)", (safe_style,))
                conn.execute("INSERT OR IGNORE INTO user_profiles (profile_id, profile_name, description, active_style_id, is_active, is_system) VALUES (3, 'Politics & Policy', 'Government policy, regulation, geopolitics', ?, 0, 1)", (safe_style,))
            
            conn.execute("UPDATE user_profiles SET is_system = 1 WHERE profile_id IN (1, 2, 3)")
            logger.info("User profiles table ensured")
    
    def get_all_profiles(self):
        """Get all user profiles."""
        with self.get_connection() as conn:
            cursor = conn.execute("SELECT * FROM user_profiles ORDER BY profile_id")
            return [dict(row) for row in cursor]
    
    def get_active_profile(self):
        """Get the currently active profile."""
        with self.get_connection() as conn:
            row = conn.execute("SELECT * FROM user_profiles WHERE is_active = 1").fetchone()
            return dict(row) if row else None
    
    def _get_active_profile_id(self):
        """Get the ID of the currently active profile."""
        profile = self.get_active_profile()
        return profile['profile_id'] if profile else 1
    def switch_active_profile(self, new_profile_id: int):
        """Switch active profile."""
        with self.get_connection() as conn:
            conn.execute("UPDATE user_profiles SET is_active = 0")
            conn.execute("UPDATE user_profiles SET is_active = 1 WHERE profile_id = ?", (new_profile_id,))
            row = conn.execute("SELECT active_style_id FROM user_profiles WHERE profile_id = ?", (new_profile_id,)).fetchone()
            if row and row['active_style_id']:
                conn.execute("UPDATE styles SET is_active = 0")
                conn.execute("UPDATE styles SET is_active = 1 WHERE style_id = ?", (row['active_style_id'],))
        logger.info(f"Switched to profile {new_profile_id}")
    def add_profile(self, profile_name: str, description: str = "", style_id: int = None, org_name: str = "") -> int:
        """Add a new profile. Returns new profile_id."""
        with self.get_connection() as conn:
            if style_id is None:
                style_row = conn.execute("SELECT style_id FROM styles LIMIT 1").fetchone()
                style_id = style_row['style_id'] if style_row else 1
            cursor = conn.execute("""
                INSERT INTO user_profiles (profile_name, description, active_style_id, is_active, is_system, org_name)
                VALUES (?, ?, ?, 0, 0, ?)
            """, (profile_name, description, style_id, org_name))
            new_id = cursor.lastrowid
            logger.info(f"Created new profile: {profile_name} (ID: {new_id})")
            return new_id

    def update_profile_org(self, profile_id: int, org_name: str) -> bool:
        with self.get_connection() as conn:
            conn.execute("UPDATE user_profiles SET org_name = ? WHERE profile_id = ?", (org_name, profile_id))
            return True
    def rename_profile(self, profile_id: int, new_name: str) -> bool:
        """Rename a profile. Returns False if system profile."""
        with self.get_connection() as conn:
            row = conn.execute("SELECT is_system FROM user_profiles WHERE profile_id = ?", (profile_id,)).fetchone()
            if not row or row['is_system'] == 1:
                logger.warning(f"Cannot rename system profile {profile_id}")
                return False
            conn.execute("UPDATE user_profiles SET profile_name = ? WHERE profile_id = ?", (new_name, profile_id))
            return True
    def delete_profile(self, profile_id: int) -> bool:
        """Delete a profile. Returns False if system. Switches to profile 1 if deleting active."""
        with self.get_connection() as conn:
            row = conn.execute("SELECT is_system, is_active FROM user_profiles WHERE profile_id = ?", (profile_id,)).fetchone()
            if not row or row['is_system'] == 1:
                logger.warning(f"Cannot delete system profile {profile_id}")
                return False
            if row['is_active'] == 1:
                conn.execute("UPDATE user_profiles SET is_active = 1 WHERE profile_id = 1")
            conn.execute("DELETE FROM tags WHERE profile_id = ?", (profile_id,))
            conn.execute("DELETE FROM user_profiles WHERE profile_id = ?", (profile_id,))
            logger.info(f"Deleted profile {profile_id}")
            return True

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
                sql += f" AND COALESCE(m.published_at, m.scraped_at, m.created_at) >= '{cutoff_utc}'"
            elif date_range == "week":
                cutoff_local = now_local - timedelta(days=7)
                cutoff_utc = cutoff_local.astimezone(pytz.UTC).strftime('%Y-%m-%d %H:%M:%S')
                sql += f" AND COALESCE(m.published_at, m.scraped_at, m.created_at) >= '{cutoff_utc}'"
            elif date_range == "month":
                cutoff_local = now_local - timedelta(days=28)
                cutoff_utc = cutoff_local.astimezone(pytz.UTC).strftime('%Y-%m-%d %H:%M:%S')
                sql += f" AND COALESCE(m.published_at, m.scraped_at, m.created_at) >= '{cutoff_utc}'"
            elif date_range and date_range.startswith("custom_"):
                days = int(date_range.split("_")[1])
                cutoff_local = now_local - timedelta(days=days)
                cutoff_utc = cutoff_local.astimezone(pytz.UTC).strftime('%Y-%m-%d %H:%M:%S')
                sql += f" AND COALESCE(m.published_at, m.scraped_at, m.created_at) >= '{cutoff_utc}'"

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
        """Add a new style matching schema.sql."""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO styles (
                    name, output_type, tone, headline_length, 
                    lead_length, body_length, analysis_length, 
                    include_keywords, include_hashtags, custom_instructions
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                name,
                kwargs.get('output_type', 'article'),
                kwargs.get('tone', 'professional'),
                kwargs.get('headline_length', 'medium'),
                kwargs.get('lead_length', 'medium'),
                kwargs.get('body_length', 'medium'),
                kwargs.get('analysis_length', 'medium'),
                kwargs.get('include_keywords', 1),
                kwargs.get('include_hashtags', 0),
                kwargs.get('custom_instructions', ''),
            ))
            return cursor.lastrowid
    
    def update_style(self, style_id: int, **kwargs):
        """Update a style matching schema.sql."""
        if not kwargs:
            return
        with self.get_connection() as conn:
            set_clause = ", ".join(f"{k} = ?" for k in kwargs.keys())
            values = list(kwargs.values()) + [style_id]
            conn.execute(f"""
                UPDATE styles 
                SET {set_clause}
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