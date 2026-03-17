"""
AIEAT AI Engine - Scoring and Translation using LLM.

Ported from V11_Score.ipynb and V11_Translate.ipynb.
Uses Ollama for GPU-accelerated inference.
"""
import json
import re
import os
import requests
from typing import Dict, Any, Optional, List
from datetime import datetime

from app.utils.logger import get_app_logger
from app.utils.exceptions import AIEngineError, ModelLoadError, InferenceError
from app.services.database_manager import DatabaseManager
from app.services.prompt_builder import build_translation_prompt, parse_translation_response

logger = get_app_logger(__name__)

# Ollama configuration
OLLAMA_URL = "http://localhost:11434"
DEFAULT_MODEL = "scb10x/typhoon2.5-qwen3-4b:latest"


class PromptBuilder:
    """Builds prompts for scoring and translation."""
    
    def __init__(self, config: Dict, org_name: str = ""):
        self.config = config
        self.org_name = org_name
        self.system_prompt = config.get('system_prompt', '')
        self.user_template = config.get('user_prompt_template', '')
        self.max_chars = config.get('content_max_chars', 2000)
    
    def build_messages(self, **kwargs) -> List[Dict]:
        """Build chat messages for instruct model."""
        kwargs['org_name'] = self.org_name
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
        from app.utils.paths import get_config_dir
        config_dir = get_config_dir()
        
        # Load scoring config
        scoring_path = os.path.join(config_dir, 'llm_scoring_config.json')
        try:
            with open(scoring_path, 'r', encoding='utf-8') as f:
                self.scoring_config = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Scoring config missing or corrupt: {scoring_path} - {e}")
            self.scoring_config = {
                'system_prompt': 'You are a news scoring assistant.',
                'user_prompt_template': 'Score this article: {content}',
                'content_max_chars': 2000
            }
        self.scoring_prompt_builder = PromptBuilder(self.scoring_config)
        
        # Load keywords from DB first, fallback to JSON
        try:
            keywords_rows = self.db.get_keywords()
            if not keywords_rows:
                raise ValueError("No keywords in DB")
            # Extract names from rows if they are dicts or objects with 'tag_name'
            self.keywords = []
            for k in keywords_rows:
                if isinstance(k, dict): self.keywords.append(k.get('tag_name', str(k)))
                elif hasattr(k, 'tag_name'): self.keywords.append(k.tag_name)
                elif hasattr(k, '__getitem__'): # sqlite3.Row or similar
                    try: self.keywords.append(k['tag_name'])
                    except: self.keywords.append(str(k))
                else: self.keywords.append(str(k))
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
            domain_rows = self.db.get_domains()
            if domain_rows:
                domains = []
                for d in domain_rows:
                    if isinstance(d, dict): domains.append(d.get('tag_name', str(d)))
                    elif hasattr(d, 'tag_name'): domains.append(d.tag_name)
                    elif hasattr(d, '__getitem__'):
                        try: domains.append(d['tag_name'])
                        except: domains.append(str(d))
                    else: domains.append(str(d))
                self.domain = ', '.join(domains)
                logger.info(f"Loaded {len(domains)} domains from DB")
            else:
                raise ValueError("No domains in DB")
        except Exception as e:
            logger.warning(f"DB domains failed ({e}), using config fallback")
            self.domain = self.scoring_config.get('domain', 'Technology and AI Business')
        
        # Load translation config
        translation_path = os.path.join(config_dir, 'llm_translation_config.json')
        try:
            with open(translation_path, 'r', encoding='utf-8') as f:
                self.translation_config = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Translation config missing or corrupt: {translation_path} - {e}")
            self.translation_config = {
                'system_prompt': 'You are a Thai translator.',
                'user_prompt_template': 'Translate this article to Thai: {content}',
                'content_max_chars': 3000
            }
        self.translation_prompt_builder = PromptBuilder(self.translation_config)
        
        logger.info(f"AI Engine ready: {len(self.keywords)} keywords, domain='{self.domain[:30]}...')")
    
    def load_model(self, model_name: str = None, n_ctx: int = None):
        """
        Initialize Ollama connection.
        
        Args:
            model_name: Name of Ollama model to use (default: first available)
            n_ctx: Ignored (Ollama manages context)
        """
        # Check Ollama is running
        try:
            r = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
            if r.status_code != 200:
                raise ModelLoadError("Ollama not responding")
            
            models = [m['name'] for m in r.json().get('models', [])]
            if not models:
                raise ModelLoadError("No models available in Ollama. Run: ollama pull scb10x/typhoon2.5-qwen3-4b")
            
            # Check database for saved model preference
            if not model_name:
                try:
                    profile = self.db.get_system_profile()
                    if profile and profile.get('model_name'):
                        model_name = profile['model_name']
                        logger.info(f"Loaded saved model preference: {model_name}")
                except Exception as e:
                    logger.debug(f"Could not load saved model: {e}")
            
            # Use specified model or first available
            if model_name and model_name in models:
                self.model_name = model_name
            elif model_name:
                logger.warning(f"Model '{model_name}' not found, using {models[0]}")
                self.model_name = models[0]
            else:
                self.model_name = models[0]
            
            self.llm = self.model_name  # Store model name for use in translate_article
            logger.info(f"Ollama ready: {self.model_name}")
            
        except requests.exceptions.ConnectionError:
            raise ModelLoadError("Ollama is not running. Start it with: ollama serve")
        except ModelLoadError:
            raise
        except Exception as e:
            raise ModelLoadError(f"Failed to connect to Ollama: {e}")
    
    def _ollama_chat(self, messages: List[Dict], max_tokens: int = 300, temperature: float = 0.1, timeout: int = 180) -> str:
        """Send chat request to Ollama."""
        payload = {
            "model": self.model_name,
            "messages": messages,
            "stream": False,
            "options": {
                "num_predict": max_tokens,
                "temperature": temperature,
                "stop": ["---", "User:", "Observation:", "<|im_end|>", "<|endoftext|>"]
            }
        }
        
        r = requests.post(f"{OLLAMA_URL}/api/chat", json=payload, timeout=timeout)
        r.raise_for_status()
        return r.json().get('message', {}).get('content', '')
    
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
        
        active_prof = self.db.get_active_profile()
        org_name = active_prof.get('org_name', 'AIEAT') if active_prof else 'AIEAT'
        self.scoring_prompt_builder.org_name = org_name
        self.translation_prompt_builder.org_name = org_name

        messages = self.scoring_prompt_builder.build_messages(
            url=url,
            author=author or 'Unknown',
            date=date or 'Unknown',
            content=content,
            keywords=', '.join(self.keywords),
            domain=self.domain
        )
        
        try:
            text = self._ollama_chat(
                messages=messages,
                max_tokens=self.scoring_config['model'].get('max_tokens', 300),
                temperature=self.scoring_config['model'].get('temperature', 0.1)
            )
            
            result = self._extract_json(text)
            
            # 1. Count keyword matches (Strict Whitelist Approach)
            keyword_score = 0
            # Clean normalization of keys for robust matching
            normalized_keywords = [k.lower().strip() for k in self.keywords]
            
            for key, value in result.items():
                # Only score if the key is explicitly in our monitored keywords
                if key.lower().strip() in normalized_keywords:
                    try:
                         # Ensure we only add 1 per keyword if binary, or exact value if weighted
                         # Usually prompts return 0 or 1.
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
                          date: str = '', publisher: str = '', content: str = '',
                          style: Dict = None) -> Dict:
        """
        Translate article to Thai using active style settings.
        
        Args:
            article_id: Article ID (optional)
            url, author, date, publisher, content: Article data
            style: Style settings dict (optional, loads active style if None)
        
        Returns dict with:
        - Keywords, Headline, Lead, Body, Analysis, Source, Hashtags
        """
        if not self.llm:
            raise InferenceError("Model not loaded. Call load_model() first.")
        
        # Load active style if not provided
        if style is None:
            try:
                style = self.db.get_active_style()
                if not style:
                    logger.info("No active style found, using defaults")
                    style = {}
            except Exception as e:
                logger.warning(f"Could not load active style: {e}")
                style = {}
        
        # Build article data dict
        article_data = {
            'url': url,
            'author': author or 'Unknown',
            'date': date or 'Unknown',
            'publisher': publisher or 'Unknown',
            'content': content
        }
        
        # Build prompt using style settings
        prompt = build_translation_prompt(style, article_data)
        
        try:
            # Use Chat API (better for Instruct models like Typhoon/Qwen)
            # Construct messages
            messages = [
                {"role": "user", "content": prompt}
            ]
            
            text = self._ollama_chat(
                messages=messages,
                max_tokens=4000,  # Increased for Web Article style
                temperature=0.2,
                timeout=300  # 5 minutes for longer translations
            )
            
            # Parse using new JSON-based parser
            result = parse_translation_response(text)
            result['raw_response'] = text
            
            # EMERGENCY FALLBACK: If parsing failed or Body is empty, use raw text
            if not result.get('success') or not result.get('Body'):
                logger.warning(f"JSON parsing failed for article {article_id}, using raw text fallback")
                result['Body'] = text
                result['Headline'] = 'Translation (Raw Output)'
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
                'Hashtags': '',
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
                             progress_callback = None, stop_callback = None) -> Dict:
        """
        Process new articles: score all, translate high-score ones.
        
        Args:
            limit: Max articles to process
            translate_threshold: Score needed for translation (default 7 = max)
            progress_callback: Optional callback(current, total, article_headline)
            stop_callback: Optional callback() -> bool to stop execution
        
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
            # Check stop signal
            if stop_callback and stop_callback():
                logger.info("AI processing stopped by user")
                break

            article_id = article['article_id']
            headline = article.get('headline', '')[:50]
            
            if progress_callback:
                # Callback format: (current, total, message)
                # We reuse the scraper's progress bar format
                msg = f"AI Scoring: {headline}"
                should_continue = progress_callback(i + 1, total, msg)
                if should_continue is False:
                    logger.info("AI processing stopped by user via UI")
                    break
            
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
            logger.info(f"Scoring {i+1}/{total}: {headline}")  # VISIBLE IN TERMINAL NOW
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
