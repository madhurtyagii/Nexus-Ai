"""
Nexus AI - Groq Client
Client for Groq cloud LLM API
"""

import httpx
import json
from typing import Optional, List, Dict, Any
from config import get_settings

class GroqClient:
    """Client for interacting with Groq cloud LLM API."""
    
    GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
    
    def __init__(
        self, 
        api_key: str = None, 
        default_model: str = "meta-llama/llama-4-scout-17b-16e-instruct",
        timeout: float = 60.0
    ):
        """
        Initialize Groq client.
        
        Args:
            api_key: Groq API key (default from settings)
            default_model: Default model to use
            timeout: Request timeout in seconds
        """
        if api_key is None:
            from config import get_settings
            api_key = get_settings().groq_api_key
            
        self.api_key = api_key
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
        max_tokens: int = 4096,
        images: List[str] = None
    ) -> Optional[str]:
        """
        Generate text completion from Groq.
        
        Args:
            prompt: User prompt
            model: Model to use (defaults to default_model)
            stream: Whether to stream response
            system: Optional system prompt
            temperature: Creativity parameter (0-1)
            max_tokens: Maximum tokens to generate
            images: List of base64 encoded images
            
        Returns:
            Generated text or None on failure
        """
        model = model or self.default_model
        
        # Determine if this involves images
        if images:
            content = [{"type": "text", "text": prompt}]
            for img in images:
                # Ensure base64 prefix if missing
                if not img.startswith("data:"):
                    img = f"data:image/jpeg;base64,{img}"
                content.append({
                    "type": "image_url",
                    "image_url": {"url": img}
                })
            
            user_message = {"role": "user", "content": content}
        else:
            user_message = {"role": "user", "content": prompt}

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append(user_message)
        
        return self.chat(messages, model, temperature, max_tokens)
    
    def chat(
        self, 
        messages: List[Dict[str, Any]], 
        model: str = None,
        temperature: float = 0.7,
        max_tokens: int = 4096
    ) -> Optional[str]:
        """
        Chat completion with message history.
        
        Args:
            messages: List of {"role": "...", "content": "..."} or multi-content
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
                
                if response.status_code != 200:
                    print(f"❌ Groq API Error ({response.status_code}): {response.text}")
                    return None
                
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
            if 'response' in locals():
                print(f"Response text: {response.text}")
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
            "meta-llama/llama-4-maverick-17b-128e-instruct",
            "meta-llama/llama-4-scout-17b-16e-instruct",
            "llama-3.3-70b-versatile",
            "llama-3.1-8b-instant",
            "whisper-large-v3-turbo"
        ]
