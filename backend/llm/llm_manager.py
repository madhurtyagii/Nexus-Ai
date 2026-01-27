"""
Nexus AI - LLM Manager
Unified interface for multiple LLM providers with fallback and caching
"""

import hashlib
import json
from typing import Optional, List, Dict, Any

from llm.ollama_client import OllamaClient
from llm.groq_client import GroqClient
from redis_client import redis_client, set_cache, get_cache
from config import get_settings

settings = get_settings()


class LLMManager:
    """
    Unified LLM interface with automatic fallback and response caching.
    
    Default behavior:
    - Try Ollama first (local, free, private)
    - Fall back to Groq if Ollama fails
    - Cache responses in Redis to avoid duplicate API calls
    """
    
    def __init__(
        self,
        prefer_local: bool = True,
        cache_expiry: int = 3600
    ):
        """
        Initialize LLM Manager.
        
        Args:
            prefer_local: If True, try Ollama before Groq
            cache_expiry: Cache TTL in seconds (default 1 hour)
        """
        self.ollama = OllamaClient()
        self.groq = GroqClient()
        self.prefer_local = prefer_local
        self.cache_expiry = cache_expiry
        
        # Track provider status
        self._ollama_available = None
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
        provider: str = "auto",
        temperature: float = 0.7
    ) -> Optional[str]:
        """
        Generate text completion with automatic fallback.
        
        Args:
            prompt: User prompt
            system: Optional system prompt
            model: Specific model to use (provider-dependent)
            use_cache: Whether to use cached responses
            provider: "auto", "ollama", or "groq"
            temperature: Creativity parameter
            
        Returns:
            Generated text or None if all providers fail
        """
        # Check cache first
        if use_cache:
            cache_key = self._cache_key(prompt, system)
            cached = get_cache(cache_key)
            if cached:
                print("📦 Using cached LLM response")
                return cached
        
        response = None
        used_provider = None
        
        # Determine provider order
        if provider == "ollama":
            response = self._try_ollama(prompt, system, model)
            used_provider = "ollama"
        elif provider == "groq":
            response = self._try_groq(prompt, system, model, temperature)
            used_provider = "groq"
        else:  # auto
            if self.prefer_local:
                # Try Ollama first
                response = self._try_ollama(prompt, system, model)
                used_provider = "ollama"
                
                if response is None:
                    print("⚠️ Ollama unavailable, falling back to Groq")
                    response = self._try_groq(prompt, system, model, temperature)
                    used_provider = "groq"
            else:
                # Try Groq first
                response = self._try_groq(prompt, system, model, temperature)
                used_provider = "groq"
                
                if response is None:
                    print("⚠️ Groq unavailable, falling back to Ollama")
                    response = self._try_ollama(prompt, system, model)
                    used_provider = "ollama"
        
        # Cache successful response
        if response and use_cache:
            cache_key = self._cache_key(prompt, system)
            set_cache(cache_key, response, self.cache_expiry)
            print(f"✅ LLM response from {used_provider} (cached)")
        
        return response
    
    def _try_ollama(
        self, 
        prompt: str, 
        system: str = None, 
        model: str = None
    ) -> Optional[str]:
        """Try to get response from Ollama."""
        try:
            return self.ollama.generate(prompt, model=model, system=system)
        except Exception as e:
            print(f"⚠️ Ollama error: {e}")
            return None
    
    def _try_groq(
        self, 
        prompt: str, 
        system: str = None, 
        model: str = None,
        temperature: float = 0.7
    ) -> Optional[str]:
        """Try to get response from Groq."""
        try:
            return self.groq.generate(
                prompt, 
                model=model, 
                system=system, 
                temperature=temperature
            )
        except Exception as e:
            print(f"⚠️ Groq error: {e}")
            return None
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        model: str = None,
        provider: str = "auto"
    ) -> Optional[str]:
        """
        Chat completion with message history.
        
        Args:
            messages: List of {"role": "user/assistant/system", "content": "..."}
            model: Specific model to use
            provider: "auto", "ollama", or "groq"
            
        Returns:
            Assistant's response or None if all providers fail
        """
        if provider == "ollama":
            return self.ollama.chat(messages, model)
        elif provider == "groq":
            return self.groq.chat(messages, model)
        else:  # auto
            if self.prefer_local:
                response = self.ollama.chat(messages, model)
                if response is None:
                    response = self.groq.chat(messages, model)
                return response
            else:
                response = self.groq.chat(messages, model)
                if response is None:
                    response = self.ollama.chat(messages, model)
                return response
    
    def get_provider_status(self) -> Dict[str, bool]:
        """
        Check health of all providers.
        
        Returns:
            Dictionary with provider availability status
        """
        return {
            "ollama": self.ollama.check_health(),
            "groq": self.groq.check_health()
        }
    
    def estimate_cost(self, prompt: str, response: str) -> Dict[str, Any]:
        """
        Estimate token usage and cost.
        
        Args:
            prompt: Input prompt
            response: Generated response
            
        Returns:
            Dictionary with token counts and estimated cost
        """
        prompt_tokens = self.groq.count_tokens(prompt)
        response_tokens = self.groq.count_tokens(response)
        total_tokens = prompt_tokens + response_tokens
        
        # Groq pricing (approximate, as of 2024)
        # llama-3.1-70b: ~$0.59 per million input, ~$0.79 per million output
        input_cost = (prompt_tokens / 1_000_000) * 0.59
        output_cost = (response_tokens / 1_000_000) * 0.79
        
        return {
            "prompt_tokens": prompt_tokens,
            "response_tokens": response_tokens,
            "total_tokens": total_tokens,
            "estimated_cost_usd": round(input_cost + output_cost, 6)
        }
    
    def clear_cache(self) -> bool:
        """
        Clear all cached LLM responses.
        
        Returns:
            True if successful
        """
        try:
            # Delete all keys matching llm_cache:*
            keys = redis_client.keys("llm_cache:*")
            if keys:
                redis_client.delete(*keys)
            print(f"🗑️ Cleared {len(keys)} cached LLM responses")
            return True
        except Exception as e:
            print(f"⚠️ Failed to clear cache: {e}")
            return False
    
    def list_available_models(self) -> Dict[str, List[str]]:
        """
        List available models from all providers.
        
        Returns:
            Dictionary with provider -> model list mapping
        """
        return {
            "ollama": self.ollama.list_models(),
            "groq": self.groq.list_models()
        }


# Global LLM manager instance
llm_manager = LLMManager()
