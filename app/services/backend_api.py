"""
Backend API Facade - Unified interface for UI
Connects: DatabaseManager, ScraperService, AIEngine
"""
import asyncio
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

from app.services.database_manager import DatabaseManager
from app.services.scraper_service import ScraperService
from app.services.ai_engine import InferenceController
from app.utils.logger import get_app_logger
from app.utils.exceptions import ModelLoadError

logger = get_app_logger(__name__)


@dataclass
class Article:
    """Article data model for UI"""
    article_id: int
    headline: str
    source: str
    author: str
    published_at: str
    url: str
    score: int
    status: str
    original_content: str = ""
    thai_content: str = ""


@dataclass
class Source:
    """Source data model for UI"""
    source_id: int
    name: str
    url: str
    status: str


class BackendAPI:
    """
    Unified API for UI to access all backend services.
    
    Usage:
        api = BackendAPI()
        articles = api.get_articles(limit=50)
        api.run_scraper()
        api.score_articles()
    """
    
    def __init__(self):
        self.db = DatabaseManager()
        self._engine = None  # Lazy loaded
        self._scraper = None  # Lazy loaded
        
        # Cache config
        self._config = None
        
        # Try to start Ollama if not running
        self._ensure_ollama_running()
        
        logger.info("BackendAPI initialized")
    
    def _ensure_ollama_running(self):
        """Check if Ollama is running, start it if not."""
        import requests
        import subprocess
        import time
        
        try:
            # Check if Ollama is responding
            r = requests.get("http://localhost:11434/api/tags", timeout=1)
            if r.status_code == 200:
                return  # Already running
        except:
            pass
        
        # Try to start Ollama
        try:
            logger.info("Starting Ollama server...")
            # Start ollama serve in background (Windows)
            subprocess.Popen(
                ["ollama", "serve"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            # Wait for it to start (max 2 seconds, check often)
            for _ in range(10):
                time.sleep(0.2) # Faster check
                try:
                    r = requests.get("http://localhost:11434/api/tags", timeout=0.5)
                    if r.status_code == 200:
                        logger.info("Ollama started successfully")
                        return
                except:
                    continue
            logger.warning("Ollama start timed out (it might still be loading)")
        except Exception as e:
            logger.warning(f"Could not auto-start Ollama: {e}")
    
    def preload_model(self):
        """Preload AI model in background for faster first call."""
        try:
            if self._engine is None:
                logger.info("Preloading AI model...")
                self._engine = InferenceController(db=self.db)
                self._engine.load_model()
                logger.info("AI Model preloaded successfully")
        except Exception as e:
            logger.warning(f"Model preload failed: {e}")
    
    def reload_model(self):
        """Reload AI model with new settings (called after config change)."""
        try:
            logger.info("Reloading AI model...")
            self._engine = InferenceController(db=self.db)
            self._engine.load_model()
            logger.info(f"AI Model reloaded: {self._engine.model_name}")
            return self._engine.model_name
        except Exception as e:
            logger.warning(f"Model reload failed: {e}")
            return None
    
    # ==================== CONFIG ====================
    
    def get_config(self) -> Dict[str, Any]:
        """Get all configuration for UI display."""
        return {
            'keywords': self.db.get_keywords(),
            'domains': self.db.get_domains(),
            'profile': self.db.get_system_profile(),
            'max_score': len(self.db.get_keywords()) + 2,  # keywords + is_new + relate
            'threshold': (len(self.db.get_keywords()) + 2) // 2 + 1
        }
    
    def get_keywords(self) -> List[str]:
        """Get all keywords."""
        return self.db.get_keywords()
    
    def get_domains(self) -> List[str]:
        """Get all domains."""
        return self.db.get_domains()
    
    def update_config(self, updates: Dict[str, Any]):
        """Update system config."""
        self.db.update_system_profile(**updates)
    
    def add_keyword(self, keyword: str) -> int:
        """Add a new keyword. Returns tag_id."""
        return self.db.add_keyword(keyword)
    
    def add_domain(self, domain: str) -> int:
        """Add a new domain. Returns tag_id."""
        return self.db.add_domain(domain)
    
    def remove_keyword(self, tag_id: int):
        """Remove a keyword by tag_id."""
        self.db.remove_tag(tag_id)
    
    def delete_keyword(self, keyword: str):
        """Delete a keyword by name."""
        self.db.delete_keyword(keyword)
    
    def delete_domain(self, domain: str):
        """Delete a domain by name."""
        self.db.delete_domain(domain)
    
    # ==================== STYLES ====================
    
    def get_styles(self) -> List[Dict]:
        """Get all styles."""
        return self.db.get_styles()
    
    def get_style(self, style_id: int) -> Optional[Dict]:
        """Get a single style."""
        return self.db.get_style(style_id)
    
    def add_style(self, name: str, **kwargs) -> int:
        """Add a new style."""
        return self.db.add_style(name, **kwargs)
    
    def update_style(self, style_id: int, **kwargs):
        """Update a style."""
        self.db.update_style(style_id, **kwargs)
    
    def delete_style(self, style_id: int):
        """Delete a style."""
        self.db.delete_style(style_id)
    
    def set_active_style(self, style_id: int):
        """Set a style as the active style for translation."""
        self.db.set_active_style(style_id)
    
    def get_active_style(self) -> Optional[Dict]:
        """Get the currently active style."""
        return self.db.get_active_style()
    
    # ==================== ARTICLES ====================
    
    def get_articles(self, limit: int = 100, offset: int = 0, 
                     min_score: int = 0, translated_only: bool = False) -> List[Dict]:
        """
        Get articles for dashboard display.
        
        Args:
            limit: Max articles to return
            offset: Pagination offset
            min_score: Minimum score filter
            translated_only: Only return articles with Thai translation
        """
        with self.db.get_connection() as conn:
            sql = """
                SELECT m.article_id, m.headline, m.author_name, m.published_at,
                       m.article_url, m.ai_score, ms.status_name,
                       s.domain_name as source_name,
                       CASE WHEN c.thai_content IS NOT NULL AND c.thai_content != '' 
                            THEN 1 ELSE 0 END as has_translation,
                       GROUP_CONCAT(t.tag_name, ',') as tags
                FROM articles_meta m
                JOIN article_content c ON m.article_id = c.article_id
                JOIN sources s ON m.source_id = s.source_id
                JOIN master_status ms ON m.status_id = ms.status_id
                LEFT JOIN article_tag_map atm ON m.article_id = atm.article_id
                LEFT JOIN tags t ON atm.tag_id = t.tag_id
                WHERE m.ai_score >= ?
            """
            
            if translated_only:
                sql += " AND c.thai_content IS NOT NULL AND c.thai_content != ''"
            
            sql += " GROUP BY m.article_id ORDER BY m.published_at DESC LIMIT ? OFFSET ?"
            
            cursor = conn.execute(sql, (min_score, limit, offset))
            return [dict(row) for row in cursor]
    
    def get_article_detail(self, article_id: int) -> Optional[Dict]:
        """Get full article detail including content."""
        with self.db.get_connection() as conn:
            cursor = conn.execute("""
                SELECT m.article_id, m.headline, m.author_name, m.published_at,
                       m.article_url, m.ai_score, ms.status_name,
                       s.domain_name as source_name,
                       c.original_content, c.thai_content
                FROM articles_meta m
                JOIN article_content c ON m.article_id = c.article_id
                JOIN sources s ON m.source_id = s.source_id
                JOIN master_status ms ON m.status_id = ms.status_id
                WHERE m.article_id = ?
            """, (article_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_article_count(self) -> Dict[str, int]:
        """Get article counts by status."""
        counts = self.db.get_article_count()
        # Add total
        counts['total'] = sum(counts.values())
        # Add translated count
        with self.db.get_connection() as conn:
            translated = conn.execute("""
                SELECT COUNT(*) FROM article_content 
                WHERE thai_content IS NOT NULL AND thai_content != ''
            """).fetchone()[0]
            counts['translated'] = translated
        return counts
    
    # ==================== SOURCES ====================
    
    def get_sources(self) -> List[Dict]:
        """Get all sources for config display."""
        return self.db.get_all_sources()
    
    def get_source_count(self) -> int:
        """Get total source count."""
        sources = self.db.get_all_sources()
        return len(sources) if sources else 0
    
    def add_source(self, url: str) -> int:
        """Add a new source from URL. Auto-detects domain name."""
        # 1. Normalize URL to prevent duplicates (http vs https, www vs non-www)
        if not url:
            return 0
            
        url = url.strip()
        if not url.startswith('http'):
            url = 'https://' + url
            
        # Parse for domain
        from urllib.parse import urlparse
        parsed = urlparse(url)
        domain = parsed.netloc or parsed.path.split('/')[0]
        
        # Clean up domain (remove www.)
        if domain.startswith('www.'):
            domain = domain[4:]
            
        # 2. Re-construct standardized URL (https://domain.com)
        # This matches the 'base_url' UNIQUE constraint logic
        clean_url = f"https://{domain}"
            
        return self.db.insert_source(domain, clean_url)
    
    def delete_source(self, source_id: int):
        """Delete a source by ID."""
        self.db.delete_source(source_id)
    
    # ==================== ACTIONS ====================
    
    def run_scraper(self, source_limit: int = None, 
                    progress_callback=None) -> Dict[str, Any]:
        """
        Run scraper to collect new articles.
        
        Args:
            source_limit: Limit number of sources (None = all)
            progress_callback: Function to call with progress updates
        
        Returns:
            Dict with stats: articles_saved, sources_processed, errors
        """
        if self._scraper is None:
            self._scraper = ScraperService(db=self.db)
        
        # Force reload config from DB to catch user additions
        self._scraper.config._load_configs()
        
        sources = self._scraper.config.sources
        if source_limit:
            sources = sources[:source_limit]
        
        # Run async scraper with progress callback
        result = asyncio.run(self._scraper.run(sources=sources, progress_callback=progress_callback))
        
        logger.info(f"Scraper complete: {result}")
        return result
    
    def run_ai_processing(self, progress_callback=None, limit: int = 500) -> Dict[str, Any]:
        """
        Run AI scoring (and auto-translation) on new articles.
        
        Separated from run_scraper() so dashboard can show distinct progress.
        
        Args:
            progress_callback: Function(current, total, message) -> bool
            limit: Max articles to process (default 500)
        
        Returns:
            Dict with stats: total, scored, translated, errors
        """
        try:
            from app.services.ai_engine import InferenceController
            ai = InferenceController(db=self.db)
            
            # Check if auto-scoring is enabled
            profile = self.db.get_system_profile()
            auto_score = profile.get('auto_scoring_status', 0) == 1
            
            if not auto_score:
                logger.info("Auto-scoring is OFF, skipping AI processing")
                return {'total': 0, 'scored': 0, 'translated': 0, 'errors': 0, 'skipped': True}
            
            logger.info(f"Starting AI processing (limit={limit})...")
            ai_stats = ai.process_new_articles(
                limit=limit,
                progress_callback=progress_callback
            )
            logger.info(f"AI Processing stats: {ai_stats}")
            return ai_stats
            
        except Exception as e:
            logger.error(f"AI Processing failed: {e}")
            return {'total': 0, 'scored': 0, 'translated': 0, 'errors': 1, 'error_msg': str(e)}
    
    def score_article(self, article_id: int) -> Dict[str, Any]:
        """Score a single article."""
        if self._engine is None:
            self._engine = InferenceController()
            try:
                self._engine.load_model()
            except ModelLoadError as e:
                return {'success': False, 'error': f'AI Server Offline. Please run "ollama serve".'}
        
        # Get article content
        detail = self.get_article_detail(article_id)
        if not detail:
            return {'success': False, 'error': 'Article not found'}
        
        result = self._engine.score_article(
            article_id=article_id,
            url=detail.get('article_url', ''),
            author=detail.get('author_name', ''),
            date=detail.get('published_at', ''),
            content=detail.get('original_content', '')[:2000]
        )
        
        if result.get('success'):
            self.db.update_article_score(article_id, result['total_score'])
        
        return result
    
    def translate_article(self, article_id: int) -> Dict[str, Any]:
        """Translate a single article to Thai."""
        if self._engine is None:
            self._engine = InferenceController(db=self.db)
            try:
                self._engine.load_model()
            except ModelLoadError as e:
                return {'success': False, 'error': 'AI Server Offline. Please run "ollama serve".'}
        
        detail = self.get_article_detail(article_id)
        if not detail:
            return {'success': False, 'error': 'Article not found'}
        
        result = self._engine.translate_article(
            article_id=article_id,
            url=detail.get('article_url', ''),
            author=detail.get('author_name', ''),
            date=detail.get('published_at', ''),
            publisher=detail.get('source_name', ''),
            content=detail.get('original_content', '')[:4000]
        )
        
        if result and result.get('Body'):
            # Format with markdown sections
            thai_content = f"## หัวข้อ\n{result.get('Headline', '').strip()}\n\n"
            
            if result.get('Lead'):
                thai_content += f"## นำเรื่อง\n{result.get('Lead', '').strip()}\n\n"
            
            thai_content += f"## เนื้อหา\n{result.get('Body', '').strip()}\n\n"
            
            if result.get('Analysis'):
                thai_content += f"## วิเคราะห์\n{result.get('Analysis', '').strip()}\n\n"
                
            if result.get('Source'):
                thai_content += f"**ที่มา:** {result.get('Source', '').strip()}\n\n"
            
            if result.get('Hashtags'):
                thai_content += f"\n{result.get('Hashtags', '').strip()}"
            
            self.db.update_thai_content(article_id, thai_content)
            return {'success': True, 'thai_content': thai_content, 'chars': len(thai_content)}
        
        return {'success': False, 'error': 'Translation failed'}

    def batch_process_articles(self, action: str, date_range: str, keyword: str = None, min_score: int = 0, stop_callback=None):
        """
        Batch process articles (Generator).
        Yields: (processed_count, total_count, current_article_status)
        """
        target_status = 'New' if action == 'score' else 'Scored'
        
        # FIX: If scoring, ignore min_score (New articles have 0 score)
        if action == 'score':
            min_score = 0
        
        # Debug logging
        print(f"\n=== BATCH PROCESS START ===")
        print(f"Action: {action}, Date: {date_range}, Keyword: {keyword}, MinScore: {min_score}")
        print(f"Target Status: {target_status}")
        
        # 1. Get IDs to process
        article_ids = self.db.get_article_ids_by_filter(
            date_range=date_range, 
            keyword=keyword, 
            min_score=min_score,
            target_status=target_status
        )
        
        total = len(article_ids)
        print(f"Found {total} articles to process: {article_ids[:10]}...")
        
        if total == 0:
            print("No articles found!")
            yield (0, 0, "No articles found")
            return

        # 2. Iterate and process
        success_count = 0
        for i, article_id in enumerate(article_ids):
            # CHECK STOP CALLBACK
            if stop_callback and stop_callback():
                print("⚠️ Stop signal received in backend!")
                yield (i, total, "Stopped by user")
                return

            try:
                print(f"Processing {i+1}/{total}: ID {article_id}")
                if action == 'score':
                    res = self.score_article(article_id)
                    score = res.get('total_score', 0)
                    if res.get('success'):
                        success_count += 1
                    status = f"Scored ID {article_id}: {score}"
                    print(f"  Result: {res}")
                elif action == 'translate':
                    res = self.translate_article(article_id)
                    if res.get('success'):
                        success_count += 1
                    status = f"Translated ID {article_id}: {'OK' if res.get('success') else 'Failed'}"
                    print(f"  Result: {res.get('success')}")
                
                yield (i + 1, total, status)
                
            except Exception as e:
                logger.error(f"Batch error on ID {article_id}: {e}")
                print(f"  ERROR: {e}")
                yield (i + 1, total, f"Error ID {article_id}: {e}")
        
        print(f"=== BATCH COMPLETE: {success_count}/{total} successful ===")
    
    def unload_model(self):
        """Unload AI model to free GPU memory."""
        if self._engine:
            self._engine.unload_model()
            self._engine = None
    
    # ==================== STATS ====================
    
    def get_dashboard_stats(self) -> Dict[str, Any]:
        """Get all stats for dashboard display."""
        counts = self.get_article_count()
        config = self.get_config()
        
        return {
            'articles': counts,
            'sources': self.get_source_count(),
            'keywords': config['keywords'],
            'domains': config['domains'],
            'max_score': config['max_score'],
            'threshold': config['threshold']
        }


# Test when run directly
if __name__ == "__main__":
    api = BackendAPI()
    
    print("=== BackendAPI Test ===")
    
    # Test config
    config = api.get_config()
    print(f"\nConfig: {config}")
    
    # Test articles
    articles = api.get_articles(limit=5)
    print(f"\nArticles (first 5): {len(articles)}")
    for a in articles[:3]:
        print(f"  - {a['headline'][:40]}... (score: {a['ai_score']})")
    
    # Test stats
    stats = api.get_dashboard_stats()
    print(f"\nDashboard stats: {stats}")
