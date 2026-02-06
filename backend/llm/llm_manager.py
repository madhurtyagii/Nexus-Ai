"""Nexus AI - LLM Manager.

This module provides a unified interface for interacting with various 
LLM providers (Ollama, Groq, etc.). It handles prompt templating, 
response generation, and optional caching.
"""

import hashlib
import json
from typing import Optional, List, Dict, Any

from llm.ollama_client import OllamaClient
from llm.groq_client import GroqClient
from redis_client import redis_client, set_cache, get_cache
from config import get_settings

# settings = get_settings() # Removed global settings to avoid stale cache


class LLMManager:
    """Standardized interface for interacting with Large Language Models.
    
    The LLMManager abstracts the complexities of different LLM providers, 
    providing a consistent `generate` method for text creation. It manages 
    connection settings and supports response caching to improve performance.
    
    Attributes:
        ollama: Client for local LLM execution.
        groq: Client for high-speed cloud LLMs.
        prefer_local (bool): If True, defaults to Ollama.
        cache_expiry (int): TTL for cached responses.
    """
    
    def __init__(
        self,
        prefer_local: bool = False,
        cache_expiry: int = 3600
    ):
        """
        Initialize LLM Manager.
        
        Args:
            prefer_local: If True, try Ollama before Groq
            cache_expiry: Cache TTL in seconds (default 1 hour)
        """
        self.prefer_local = prefer_local
        self.cache_expiry = cache_expiry
        
        # Initialize clients dynamically using fresh settings
        self.refresh_clients()
        
    def refresh_clients(self):
        """Re-initialize clients with fresh settings."""
        from config import get_settings
        settings = get_settings()
        self.ollama = OllamaClient(base_url=settings.ollama_base_url)
        self.groq = GroqClient(api_key=settings.groq_api_key)
        
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
        """Generates a text response from the configured LLM.
        
        Args:
            prompt: The user query or instruction.
            system: Optional instructions to set the AI's behavior.
            model: Specific model alias to use.
            use_cache: If True, returns cached results for identical prompts.
            provider: Explicitly select 'ollama' or 'groq'.
            temperature: Creativity parameter (0.0 to 1.0).
            
        Returns:
            Optional[str]: The generated response text, or None if failed.
        """
        # Always refresh clients before generation to ensure fresh API keys
        self.refresh_clients()
        
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
