"""
Nexus AI - Groq Client
Client for Groq cloud LLM API
"""

import httpx
import json
from typing import Optional, List, Dict, Any
from config import get_settings

settings = get_settings()


class GroqClient:
    """Client for interacting with Groq cloud LLM API."""
    
    GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
    
    def __init__(
        self, 
        api_key: str = None, 
        default_model: str = "llama-3.3-70b-versatile",
        timeout: float = 60.0
    ):
        """
        Initialize Groq client.
        
        Args:
            api_key: Groq API key (default from settings)
            default_model: Default model to use
            timeout: Request timeout in seconds
        """
        self.api_key = api_key or settings.groq_api_key
        self.default_model = default_model
        self.timeout = timeout
        
        if not self.api_key:
            print("⚠️ Groq API key not configured")
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with authorization."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def generate(
        self, 
        prompt: str, 
        model: str = None, 
        stream: bool = False,
        system: str = None,
        temperature: float = 0.7,
        max_tokens: int = 4096
    ) -> Optional[str]:
        """
        Generate text completion from Groq.
        
        Args:
            prompt: User prompt
            model: Model to use (defaults to default_model)
            stream: Whether to stream response (not implemented for simplicity)
            system: Optional system prompt
            temperature: Creativity parameter (0-1)
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated text or None on failure
        """
        model = model or self.default_model
        
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        
        return self.chat(messages, model, temperature, max_tokens)
    
    def chat(
        self, 
        messages: List[Dict[str, str]], 
        model: str = None,
        temperature: float = 0.7,
        max_tokens: int = 4096
    ) -> Optional[str]:
        """
        Chat completion with message history.
        
        Args:
            messages: List of {"role": "user/assistant/system", "content": "..."}
            model: Model to use
            temperature: Creativity parameter (0-1)
            max_tokens: Maximum tokens to generate
            
        Returns:
            Assistant's response or None on failure
        """
        if not self.api_key:
            print("⚠️ Groq API key not configured")
            return None
            
        model = model or self.default_model
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(
                    self.GROQ_API_URL,
                    headers=self._get_headers(),
                    json=payload
                )
                
                if response.status_code == 401:
                    print("⚠️ Groq API key is invalid")
                    return None
                    
                if response.status_code == 429:
                    print("⚠️ Groq rate limit exceeded")
                    return None
                
                response.raise_for_status()
                data = response.json()
                
                choices = data.get("choices", [])
                if choices:
                    return choices[0].get("message", {}).get("content", "")
                return None
                
        except httpx.ConnectError:
            print("⚠️ Failed to connect to Groq API")
            return None
        except httpx.TimeoutException:
            print("⚠️ Groq request timed out")
            return None
        except Exception as e:
            print(f"⚠️ Groq error: {e}")
            return None
    
    def count_tokens(self, text: str) -> int:
        """
        Rough estimate of token count.
        
        Args:
            text: Text to count tokens for
            
        Returns:
            Estimated token count
        """
        # Rough estimate: ~1.3 tokens per word
        words = len(text.split())
        return int(words * 1.3)
    
    def check_health(self) -> bool:
        """
        Check if Groq API is accessible.
        
        Returns:
            True if API is available, False otherwise
        """
        if not self.api_key:
            return False
            
        # Try a minimal request to verify API key
        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.post(
                    self.GROQ_API_URL,
                    headers=self._get_headers(),
                    json={
                        "model": self.default_model,
                        "messages": [{"role": "user", "content": "hi"}],
                        "max_tokens": 1
                    }
                )
                return response.status_code == 200
        except Exception:
            return False
    
    def list_models(self) -> List[str]:
        """
        List available Groq models.
        
        Returns:
            List of available model names
        """
        # Groq's available models (as of 2026)
        return [
            "llama-3.3-70b-versatile",
            "llama-3.1-8b-instant",
            "llama3-groq-70b-8192-tool-use-preview",
            "mixtral-8x7b-32768",
            "gemma2-9b-it"
        ]
