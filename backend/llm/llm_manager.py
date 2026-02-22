"""Nexus AI - LLM Manager.

This module provides a unified interface for interacting with LLM providers.
Currently consolidated to use Groq for all text and vision tasks.
"""

import hashlib
import json
from typing import Optional, List, Dict, Any

from llm.groq_client import GroqClient
from redis_client import redis_client, set_cache, get_cache
from config import get_settings


class LLMManager:
    """Standardized interface for interacting with Large Language Models via Groq.
    
    Attributes:
        groq: Client for high-speed cloud LLMs and Vision.
        cache_expiry (int): TTL for cached responses.
    """
    
    def __init__(
        self,
        cache_expiry: int = 3600
    ):
        """
        Initialize LLM Manager.
        
        Args:
            cache_expiry: Cache TTL in seconds (default 1 hour)
        """
        self.cache_expiry = cache_expiry
        
        # Initialize clients dynamically using fresh settings
        self.refresh_clients()
        
    def refresh_clients(self):
        """Re-initialize clients with fresh settings."""
        from config import get_settings
        settings = get_settings()
        self.groq = GroqClient(api_key=settings.groq_api_key)
        
        # Track provider status
        self._groq_available = None
    
    def _cache_key(self, prompt: str, system: str = None) -> str:
        """Generate cache key from prompt hash."""
        content = f"{system or ''}::{prompt}"
        return f"llm_cache:{hashlib.md5(content.encode()).hexdigest()}"
    
    def generate(
        self,
        prompt: str,
        system: str = None,
        model: str = None,
        use_cache: bool = True,
        provider: str = "groq",
        temperature: float = 0.7,
        images: List[str] = None
    ) -> Optional[str]:
        """Generates a text response from Groq.
        
        Args:
            prompt: The user query or instruction.
            system: Optional instructions to set the AI's behavior.
            model: Specific model alias to use.
            use_cache: If True, returns cached results for identical prompts.
            provider: Defaults to 'groq'.
            temperature: Creativity parameter (0.0 to 1.0).
            images: List of base64 encoded images (multimodal).
            
        Returns:
            Optional[str]: The generated response text, or None if failed.
        """
        # Always refresh clients before generation to ensure fresh API keys
        self.refresh_clients()
        
        # Check cache first
        if use_cache and not images: # Don't cache image requests for now
            cache_key = self._cache_key(prompt, system)
            cached = get_cache(cache_key)
            if cached:
                print("📦 Using cached LLM response")
                return cached
        
        # Always use Groq
        response = self._try_groq(prompt, system, model, temperature, images)
        used_provider = "groq"
        
        # Cache successful response
        if response and use_cache:
            cache_key = self._cache_key(prompt, system)
            set_cache(cache_key, response, self.cache_expiry)
            print(f"✅ LLM response from {used_provider} (cached)")
        
        return response
    
    def _try_groq(
        self, 
        prompt: str, 
        system: str = None, 
        model: str = None,
        temperature: float = 0.7,
        images: List[str] = None
    ) -> Optional[str]:
        """Try to get response from Groq."""
        try:
            return self.groq.generate(
                prompt, 
                model=model, 
                system=system, 
                temperature=temperature,
                images=images
            )
        except Exception as e:
            print(f"⚠️ Groq error: {e}")
            return None
    
    def chat(
        self,
        messages: List[Dict[str, Any]],
        model: str = None,
        provider: str = "groq"
    ) -> Optional[str]:
        """
        Chat completion with message history via Groq.
        
        Args:
            messages: List of {"role": "...", "content": "..."}
            model: Specific model to use
            provider: Defaults to "groq"
            
        Returns:
            Assistant's response or None on failure
        """
        self.refresh_clients()
        return self.groq.chat(messages, model)
    
    def get_provider_status(self) -> Dict[str, bool]:
        """Check health of Groq API."""
        return {
            "groq": self.groq.check_health()
        }
    
    def estimate_cost(self, prompt: str, response: str) -> Dict[str, Any]:
        """Estimate token usage and cost for Groq."""
        prompt_tokens = self.groq.count_tokens(prompt)
        response_tokens = self.groq.count_tokens(response)
        total_tokens = prompt_tokens + response_tokens
        
        # Groq pricing (approximate)
        input_cost = (prompt_tokens / 1_000_000) * 0.59
        output_cost = (response_tokens / 1_000_000) * 0.79
        
        return {
            "prompt_tokens": prompt_tokens,
            "response_tokens": response_tokens,
            "total_tokens": total_tokens,
            "estimated_cost_usd": round(input_cost + output_cost, 6)
        }
    
    def clear_cache(self) -> bool:
        """Clear all cached LLM responses."""
        try:
            keys = redis_client.keys("llm_cache:*")
            if keys:
                redis_client.delete(*keys)
            print(f"🗑️ Cleared {len(keys)} cached LLM responses")
            return True
        except Exception as e:
            print(f"⚠️ Failed to clear cache: {e}")
            return False
    
    def list_available_models(self) -> Dict[str, List[str]]:
        """List available Groq models."""
        return {
            "groq": self.groq.list_models()
        }


# Global LLM manager instance
llm_manager = LLMManager()
