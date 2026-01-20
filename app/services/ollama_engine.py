"""
Ollama-based AI Engine for GPU-accelerated inference.

Replaces llama-cpp-python with Ollama for:
- Automatic GPU detection and usage
- Faster inference (10x improvement)
- No need to manage GGUF files manually
"""
import json
import re
import os
import requests
from typing import Dict, Any, Optional, List

from app.utils.logger import get_app_logger
from app.utils.exceptions import AIEngineError, ModelLoadError, InferenceError
from app.services.database_manager import DatabaseManager

logger = get_app_logger(__name__)

OLLAMA_BASE_URL = "http://localhost:11434"


class OllamaController:
    """
    Ollama-based LLM inference controller.
    
    Uses Ollama API for GPU-accelerated inference instead of llama-cpp-python.
    """
    
    def __init__(self, db: DatabaseManager = None, model_name: str = "qwen2.5:1.5b"):
        self.db = db or DatabaseManager()
        self.model_name = model_name
        self.scoring_config = None
        self.translation_config = None
        self.keywords = []
        self.domain = ""
        
        self._load_configs()
    
    def _load_configs(self):
        """Load scoring and translation configs."""
        base_dir = os.path.dirname(os.path.abspath(__file__))
        config_dir = os.path.join(os.path.dirname(base_dir), 'config')
        
        # Load scoring config
        scoring_path = os.path.join(config_dir, 'llm_scoring_config.json')
        with open(scoring_path, 'r', encoding='utf-8') as f:
            self.scoring_config = json.load(f)
        
        # Load keywords from DB first, fallback to JSON
        try:
            self.keywords = self.db.get_keywords()
            if not self.keywords:
                raise ValueError("No keywords in DB")
            logger.info(f"Loaded {len(self.keywords)} keywords from DB")
        except Exception as e:
            logger.warning(f"DB keywords failed ({e}), using JSON fallback")
            keywords_path = os.path.join(config_dir, 'keywords.json')
            if os.path.exists(keywords_path):
                with open(keywords_path, 'r') as f:
                    self.keywords = json.load(f)
        
        # Load domain
        try:
            self.domain = self.db.get_domain()
            if not self.domain:
                raise ValueError("No domain in DB")
        except:
            self.domain = self.scoring_config.get('domain', 'Technology, Economics, and AI Business')
        
        # Load translation config
        translation_path = os.path.join(config_dir, 'llm_translation_config.json')
        with open(translation_path, 'r', encoding='utf-8') as f:
            self.translation_config = json.load(f)
        
        logger.info(f"Ollama Engine ready: model={self.model_name}, {len(self.keywords)} keywords")
    
    def check_ollama_running(self) -> bool:
        """Check if Ollama server is running."""
        try:
            response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def check_model_available(self) -> bool:
        """Check if the configured model is available."""
        try:
            response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                return any(m.get('name', '').startswith(self.model_name.split(':')[0]) for m in models)
        except:
            pass
        return False
    
    def generate(self, prompt: str, system: str = None, max_tokens: int = 200) -> str:
        """Generate text using Ollama API."""
        if not self.check_ollama_running():
            raise InferenceError("Ollama is not running. Start it with: ollama serve")
        
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": self.model_name,
            "messages": messages,
            "stream": False,
            "options": {
                "num_predict": max_tokens,
                "temperature": 0.1
            }
        }
        
        try:
            response = requests.post(
                f"{OLLAMA_BASE_URL}/api/chat",
                json=payload,
                timeout=120
            )
            response.raise_for_status()
            return response.json().get('message', {}).get('content', '')
        except Exception as e:
            raise InferenceError(f"Ollama inference failed: {e}")
    
    def score_article(self, article_id: int = None, headline: str = None, content: str = None) -> Dict[str, Any]:
        """
        Score an article using Ollama.
        
        Returns dict with binary fields for each keyword + 'relate'.
        """
        # Get article from DB if not provided
        if headline is None or content is None:
            if article_id is None:
                raise ValueError("Must provide article_id or headline+content")
            article = self.db.get_article_content(article_id)
            if not article:
                raise ValueError(f"Article {article_id} not found")
            headline = article.get('headline', '')
            content = article.get('original_content', '')
        
        # Build prompt (matching backend config)
        keywords_str = ", ".join(self.keywords)
        content_truncated = content[:2000] if content else ''
        
        system_prompt = self.scoring_config.get('system_prompt', 
            "You are a news relevance analyst. Return ONLY valid JSON.")
        
        user_prompt = self.scoring_config.get('user_prompt_template', '').format(
            content=f"Headline: {headline}\n\n{content_truncated}",
            keywords=keywords_str,
            domain=self.domain
        )
        
        # Generate
        response = self.generate(user_prompt, system=system_prompt)
        
        # Parse JSON
        scores = self._parse_scores(response)
        
        return {
            'article_id': article_id,
            'scores': scores,
            'raw_response': response
        }
    
    def _parse_scores(self, response: str) -> Dict[str, int]:
        """Parse JSON scores from response."""
        # Try to extract JSON
        try:
            # Find JSON in response
            json_match = re.search(r'\{[^{}]+\}', response)
            if json_match:
                scores = json.loads(json_match.group())
                # Normalize to 0/1
                return {k: (1 if v else 0) for k, v in scores.items()}
        except:
            pass
        
        # Return empty scores on failure
        default = {kw: 0 for kw in self.keywords}
        default['relate'] = 0
        return default
    
    def translate_article(self, article_id: int = None, content: str = None) -> str:
        """Translate article content to Thai using Ollama."""
        if content is None:
            if article_id is None:
                raise ValueError("Must provide article_id or content")
            article = self.db.get_article_content(article_id)
            if not article:
                raise ValueError(f"Article {article_id} not found")
            content = article.get('original_content', '')
        
        # Build translation prompt
        system_prompt = self.translation_config.get('system_prompt', 
            "You are a professional translator. Translate to Thai.")
        
        user_prompt = self.translation_config.get('user_prompt_template', 
            "Translate the following text to Thai:\n\n{content}").format(
            content=content[:3000]
        )
        
        # Generate with more tokens for translation
        response = self.generate(user_prompt, system=system_prompt, max_tokens=1000)
        
        return response


def get_ollama_controller(model_name: str = "qwen2.5:1.5b") -> OllamaController:
    """Factory function to get OllamaController instance."""
    return OllamaController(model_name=model_name)


# Quick test
if __name__ == "__main__":
    print("Testing Ollama Controller...")
    
    controller = OllamaController()
    
    if not controller.check_ollama_running():
        print("ERROR: Ollama not running. Start with: ollama serve")
        exit(1)
    
    if not controller.check_model_available():
        print(f"WARNING: Model {controller.model_name} not found. Pull with: ollama pull {controller.model_name}")
    
    # Test simple generation
    response = controller.generate("What is 2+2?", max_tokens=50)
    print(f"Test response: {response[:100]}...")
    
    print("Ollama Controller ready!")
