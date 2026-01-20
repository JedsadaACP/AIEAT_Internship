"""
AIEAT AI Engine - Scoring and Translation using LLM.

Ported from V11_Score.ipynb and V11_Translate.ipynb.
Uses llama-cpp-python with Typhoon2.5 model.
"""
import json
import re
import os
from typing import Dict, Any, Optional, List
from datetime import datetime

from app.utils.logger import get_app_logger
from app.utils.exceptions import AIEngineError, ModelLoadError, InferenceError
from app.services.database_manager import DatabaseManager

logger = get_app_logger(__name__)


class PromptBuilder:
    """Builds prompts for scoring and translation."""
    
    def __init__(self, config: Dict):
        self.system_prompt = config.get('system_prompt', '')
        self.user_template = config.get('user_prompt_template', '')
        self.max_chars = config.get('content_max_chars', 2000)
    
    def build_messages(self, **kwargs) -> List[Dict]:
        """Build chat messages for instruct model."""
        content = kwargs.get('content', '')
        content_truncated = content[:self.max_chars] if content else ''
        kwargs['content'] = content_truncated
        
        user_message = self.user_template.format(**kwargs)
        
        return [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_message}
        ]


class InferenceController:
    """
    Manages LLM model loading and inference.
    
    Handles:
    - Model loading/unloading
    - Scoring articles (7 binary fields + keywords + lead)
    - Translating articles to Thai
    """
    
    def __init__(self, db: DatabaseManager = None):
        self.db = db or DatabaseManager()
        self.llm = None
        self.scoring_config = None
        self.translation_config = None
        self.scoring_prompt_builder = None
        self.translation_prompt_builder = None
        
        self._load_configs()
    
    def _load_configs(self):
        """Load scoring and translation configs."""
        base_dir = os.path.dirname(os.path.abspath(__file__))
        config_dir = os.path.join(os.path.dirname(base_dir), 'config')
        
        # Load scoring config
        scoring_path = os.path.join(config_dir, 'llm_scoring_config.json')
        with open(scoring_path, 'r', encoding='utf-8') as f:
            self.scoring_config = json.load(f)
        self.scoring_prompt_builder = PromptBuilder(self.scoring_config)
        
        # Load keywords from DB first, fallback to JSON
        try:
            self.keywords = self.db.get_keywords()
            if not self.keywords:
                raise ValueError("No keywords in DB")
            logger.info(f"Loaded {len(self.keywords)} keywords from DB")
        except Exception as e:
            logger.warning(f"DB keywords failed ({e}), using JSON fallback")
            keywords_file = self.scoring_config.get('keywords_file', 'keywords.json')
            keywords_path = os.path.join(config_dir, keywords_file)
            try:
                with open(keywords_path, 'r', encoding='utf-8') as f:
                    self.keywords = json.load(f)
            except FileNotFoundError:
                self.keywords = ['A.I.', 'Technology', 'Business']
        
        # Load domains from DB, fallback to config
        try:
            domains = self.db.get_domains()
            if domains:
                self.domain = ', '.join(domains)
                logger.info(f"Loaded {len(domains)} domains from DB")
            else:
                raise ValueError("No domains in DB")
        except Exception as e:
            logger.warning(f"DB domains failed ({e}), using config fallback")
            self.domain = self.scoring_config.get('domain', 'Technology and AI Business')
        
        # Load translation config
        translation_path = os.path.join(config_dir, 'llm_translation_config.json')
        with open(translation_path, 'r', encoding='utf-8') as f:
            self.translation_config = json.load(f)
        self.translation_prompt_builder = PromptBuilder(self.translation_config)
        
        logger.info(f"AI Engine ready: {len(self.keywords)} keywords, domain='{self.domain[:30]}...')")
    
    def load_model(self, model_path: str = None, n_ctx: int = None):
        """
        Load GGUF model using llama-cpp-python.
        
        Args:
            model_path: Path to GGUF file (default from config)
            n_ctx: Context window size (default from config)
        """
        try:
            from llama_cpp import Llama
        except ImportError:
            raise ModelLoadError("llama-cpp-python not installed. Run: pip install llama-cpp-python")
        
        if model_path is None:
            # Get from config, fix relative path
            base_dir = os.path.dirname(os.path.abspath(__file__))
            config_path = self.scoring_config['model']['path']
            # Convert ../data/models/... to absolute path
            model_path = os.path.normpath(os.path.join(base_dir, '..', '..', 'data', 'models', 
                                                        os.path.basename(config_path)))
        
        if n_ctx is None:
            n_ctx = self.scoring_config['model'].get('n_ctx', 4096)
        
        # Get device preference from database
        device_pref = self._get_device_preference()
        n_gpu_layers = self._get_gpu_layers(device_pref)
        
        # Get optimal thread count
        import multiprocessing
        n_threads = min(multiprocessing.cpu_count(), 8)
        
        logger.info(f"Loading model: {model_path}")
        logger.info(f"  Context: {n_ctx}, GPU layers: {n_gpu_layers}, Threads: {n_threads}, Device: {device_pref}")
        
        try:
            self.llm = Llama(
                model_path=model_path,
                n_ctx=n_ctx,
                n_gpu_layers=n_gpu_layers,
                n_threads=n_threads,
                chat_format="chatml",
                verbose=False
            )
            logger.info("Model loaded successfully")
        except Exception as e:
            raise ModelLoadError(f"Failed to load model: {e}")
    
    def _get_device_preference(self) -> str:
        """Get device preference from database."""
        try:
            profile = self.db.get_system_profile()
            return profile.get('inference_device', 'auto')
        except:
            return 'auto'
    
    def _get_gpu_layers(self, device: str) -> int:
        """Get n_gpu_layers based on device preference."""
        if device == 'cpu':
            logger.info("Using CPU mode (user selected)")
            return 0
        elif device == 'gpu':
            logger.info("Using GPU mode (user selected)")
            return 35
        else:  # auto
            return self._detect_gpu_layers()
    
    def _detect_gpu_layers(self) -> int:
        """Auto-detect optimal GPU layers."""
        try:
            import torch
            if torch.cuda.is_available():
                logger.info(f"CUDA available: {torch.cuda.get_device_name(0)}")
                return 35  # Use GPU for most layers
        except ImportError:
            pass
        
        # Check for llama-cpp CUDA support
        try:
            from llama_cpp import llama_supports_gpu_offload
            if llama_supports_gpu_offload():
                return 35
        except:
            pass
            
        logger.info("Using CPU mode")
        return 0  # CPU only
    
    def unload_model(self):
        """Free GPU memory."""
        if self.llm:
            del self.llm
            self.llm = None
            logger.info("Model unloaded")
    
    def _extract_json(self, text: str) -> Dict:
        """Extract JSON from LLM response."""
        # Try to find JSON block
        json_match = re.search(r'```json\s*([\s\S]*?)```', text)
        if json_match:
            text = json_match.group(1)
        else:
            # Try to find raw JSON
            json_match = re.search(r'\{[\s\S]*\}', text)
            if json_match:
                text = json_match.group()
        
        return json.loads(text.strip())
    
    def _check_freshness(self, date_str: str, days: int = 7) -> int:
        """
        Check if article is fresh (< N days old).
        
        Returns:
            1 if article is new (< days old), 0 otherwise
        """
        if not date_str or date_str == 'Unknown':
            return 0
        
        try:
            from dateutil import parser as date_parser
            from datetime import datetime, timezone
            
            article_date = date_parser.parse(date_str)
            
            # Make both timezone-aware or naive for comparison
            now = datetime.now()
            if article_date.tzinfo is not None:
                now = datetime.now(timezone.utc)
            
            age = (now - article_date.replace(tzinfo=now.tzinfo if article_date.tzinfo else None)).days
            
            return 1 if age <= days else 0
        except Exception as e:
            logger.warning(f"Could not parse date '{date_str}': {e}")
            return 0
    
    def score_article(self, article_id: int = None, url: str = '', author: str = '', 
                      date: str = '', content: str = '') -> Dict:
        """
        Score article using LLM + freshness check.
        
        Scoring formula:
        - Keyword matches: 1 point per keyword found (max = num keywords)
        - Is new news: 1 point if article < 7 days old
        - Relate to domain: 1 point if article relates to user domains
        
        Total max = num_keywords + 1 + 1 (e.g., 5+1+1=7)
        """
        if not self.llm:
            raise InferenceError("Model not loaded. Call load_model() first.")
        
        messages = self.scoring_prompt_builder.build_messages(
            url=url,
            author=author or 'Unknown',
            date=date or 'Unknown',
            content=content,
            keywords=', '.join(self.keywords),
            domain=self.domain
        )
        
        try:
            response = self.llm.create_chat_completion(
                messages=messages,
                max_tokens=self.scoring_config['model'].get('max_tokens', 300),
                temperature=self.scoring_config['model'].get('temperature', 0.1)
            )
            
            text = response['choices'][0]['message']['content'].strip()
            result = self._extract_json(text)
            
            # 1. Count keyword matches
            keyword_score = 0
            for key, value in result.items():
                if key not in ('relate', 'raw_response', 'success', 'is_new', 'keyword_score', 'total_score'):
                    try:
                        keyword_score += int(value)
                    except (ValueError, TypeError):
                        pass
            
            # 2. Check "Is New News" (article < 7 days old)
            is_new_score = self._check_freshness(date)
            
            # 3. Get relate score from LLM response
            relate_score = int(result.get('relate', 0))
            
            # Calculate total: keywords + is_new + relate
            total = keyword_score + is_new_score + relate_score
            
            result['keyword_score'] = keyword_score
            result['is_new'] = is_new_score
            result['relate'] = relate_score
            result['total_score'] = total
            result['raw_response'] = text
            result['success'] = True
            
            logger.debug(f"Scored article {article_id}: {total} (kw={keyword_score}, new={is_new_score}, relate={relate_score})")
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error for article {article_id}: {e}")
            return self._empty_score_result(f"JSON parse error: {e}")
        except Exception as e:
            logger.error(f"Scoring error for article {article_id}: {e}")
            return self._empty_score_result(str(e))
    
    def _empty_score_result(self, error: str = '') -> Dict:
        """Return empty score result on error."""
        return {
            'Author': '',
            'Is_fresh': 0,
            'Relevance': 0,
            'AI_News': 0,
            'Social_Impact': 0,
            'Economic_Impact': 0,
            'No_ads': 0,
            'Is_reference': 0,
            'Keywords': [],
            'Lead': '',
            'total_score': 0,
            'raw_response': f'ERROR: {error}',
            'success': False
        }
    
    def translate_article(self, article_id: int = None, url: str = '', author: str = '',
                          date: str = '', publisher: str = '', content: str = '') -> Dict:
        """
        Translate article to Thai.
        
        Returns dict with:
        - Keywords (English | Thai)
        - Headline (Thai)
        - Lead (Thai)
        - Body (Thai)
        - Analysis (Thai)
        - Source
        """
        if not self.llm:
            raise InferenceError("Model not loaded. Call load_model() first.")
        
        messages = self.translation_prompt_builder.build_messages(
            url=url,
            author=author or 'Unknown',
            date=date or 'Unknown',
            publisher=publisher or 'Unknown',
            content=content
        )
        
        try:
            response = self.llm.create_chat_completion(
                messages=messages,
                max_tokens=self.translation_config['model'].get('max_tokens', 3000),
                temperature=self.translation_config['model'].get('temperature', 0.4)
            )
            
            text = response['choices'][0]['message']['content'].strip()
            result = self._parse_translation(text)
            result['raw_response'] = text
            result['success'] = True
            
            logger.debug(f"Translated article {article_id}")
            return result
            
        except Exception as e:
            logger.error(f"Translation error for article {article_id}: {e}")
            return {
                'Keywords': '',
                'Headline': '',
                'Lead': '',
                'Body': '',
                'Analysis': '',
                'Source': '',
                'raw_response': f'ERROR: {e}',
                'success': False
            }
    
    def _parse_translation(self, text: str) -> Dict:
        """Parse translation output with separators."""
        separator = '-####################-'
        parts = text.split(separator)
        
        result = {
            'Keywords': '',
            'Headline': '',
            'Lead': '',
            'Body': '',
            'Analysis': '',
            'Source': ''
        }
        
        # Parse each section
        for part in parts:
            part = part.strip()
            if part.startswith('Keywords:'):
                result['Keywords'] = part.replace('Keywords:', '').strip()
            elif part.startswith('Headline:'):
                result['Headline'] = part.replace('Headline:', '').strip()
            elif part.startswith('Lead:'):
                result['Lead'] = part.replace('Lead:', '').strip()
            elif part.startswith('Body:'):
                result['Body'] = part.replace('Body:', '').strip()
            elif part.startswith('Analysis:'):
                result['Analysis'] = part.replace('Analysis:', '').strip()
            elif part.startswith('Source:') or part.startswith('ที่มา:'):
                result['Source'] = part.strip()
        
        return result
    
    def process_new_articles(self, limit: int = 100, translate_threshold: int = 7,
                             progress_callback = None) -> Dict:
        """
        Process new articles: score all, translate high-score ones.
        
        Args:
            limit: Max articles to process
            translate_threshold: Score needed for translation (default 7 = max)
            progress_callback: Optional callback(current, total, article_headline)
        
        Returns:
            Stats dict
        """
        if not self.llm:
            self.load_model()
        
        # Get new articles
        articles = self.db.get_new_articles(limit=limit)
        total = len(articles)
        
        # Check system profile for auto-translate
        profile = self.db.get_system_profile()
        auto_translate = profile.get('auto_translate_status', 0) == 1
        
        logger.info(f"Processing {total} new articles (translate threshold: {translate_threshold}/7, auto-translate: {auto_translate})")
        
        stats = {
            'total': total,
            'scored': 0,
            'translated': 0,
            'errors': 0
        }
        
        for i, article in enumerate(articles):
            article_id = article['article_id']
            headline = article.get('headline', '')[:50]
            
            if progress_callback:
                progress_callback(i + 1, total, headline)
            
            # Get full content
            full_article = self.db.get_article_by_id(article_id)
            if not full_article:
                stats['errors'] += 1
                continue
            
            content = full_article.get('original_content', '')
            url = full_article.get('article_url', '')
            author = full_article.get('author_name', '')
            date = full_article.get('published_at', '')
            
            # Score article
            score_result = self.score_article(
                article_id=article_id,
                url=url,
                author=author,
                date=date,
                content=content
            )
            
            if score_result.get('success'):
                # Save score to DB
                self.db.update_article_score(article_id, score_result['total_score'])
                stats['scored'] += 1
                
                # Translate if high score AND auto-translate is ON
                if auto_translate and score_result['total_score'] >= translate_threshold:
                    trans_result = self.translate_article(
                        article_id=article_id,
                        url=url,
                        author=author,
                        date=date,
                        content=content
                    )
                    
                    if trans_result.get('success'):
                        # Combine all Thai content
                        thai_content = f"""หัวข้อ: {trans_result.get('Headline', '')}

นำเรื่อง: {trans_result.get('Lead', '')}

{trans_result.get('Body', '')}

## วิเคราะห์
{trans_result.get('Analysis', '')}

{trans_result.get('Source', '')}"""
                        
                        self.db.update_thai_content(article_id, thai_content)
                        stats['translated'] += 1
                        logger.info(f"Translated: {headline}...")
            else:
                stats['errors'] += 1
        
        logger.info(f"Processing complete: {stats}")
        return stats


# CLI entry point
if __name__ == "__main__":
    print("AIEAT AI Engine")
    print("=" * 40)
    
    engine = InferenceController()
    print("Loading model...")
    engine.load_model()
    
    print("\nProcessing articles...")
    stats = engine.process_new_articles(limit=5, translate_threshold=7)
    
    print(f"\nResults: {stats}")
    engine.unload_model()
