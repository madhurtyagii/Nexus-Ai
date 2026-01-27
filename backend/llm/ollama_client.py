"""
Nexus AI - Ollama Client
Client for local Ollama LLM server
"""

import httpx
import json
from typing import Optional, Generator, List, Dict, Any
from config import get_settings

settings = get_settings()


class OllamaClient:
    """Client for interacting with local Ollama LLM server."""
    
    def __init__(
        self, 
        base_url: str = None, 
        default_model: str = "llama3.1",
        timeout: float = 120.0
    ):
        """
        Initialize Ollama client.
        
        Args:
            base_url: Ollama server URL (default from settings)
            default_model: Default model to use
            timeout: Request timeout in seconds
        """
        self.base_url = base_url or settings.ollama_base_url
        self.default_model = default_model
        self.timeout = timeout
    
    def generate(
        self, 
        prompt: str, 
        model: str = None, 
        stream: bool = False,
        system: str = None
    ) -> Optional[str]:
        """
        Generate text completion from Ollama.
        
        Args:
            prompt: User prompt
            model: Model to use (defaults to default_model)
            stream: Whether to stream response
            system: Optional system prompt
            
        Returns:
            Generated text or None on failure
        """
        model = model or self.default_model
        url = f"{self.base_url}/api/generate"
        
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": stream
        }
        
        if system:
            payload["system"] = system
        
        try:
            with httpx.Client(timeout=self.timeout) as client:
                if stream:
                    return self._stream_generate(client, url, payload)
                else:
                    response = client.post(url, json=payload)
                    response.raise_for_status()
                    data = response.json()
                    return data.get("response", "")
        except httpx.ConnectError:
            print(f"⚠️ Ollama not reachable at {self.base_url}")
            return None
        except httpx.TimeoutException:
            print(f"⚠️ Ollama request timed out")
            return None
        except Exception as e:
            print(f"⚠️ Ollama error: {e}")
            return None
    
    def _stream_generate(
        self, 
        client: httpx.Client, 
        url: str, 
        payload: dict
    ) -> Generator[str, None, None]:
        """Stream response chunks from Ollama."""
        try:
            with client.stream("POST", url, json=payload) as response:
                for line in response.iter_lines():
                    if line:
                        data = json.loads(line)
                        if "response" in data:
                            yield data["response"]
        except Exception as e:
            print(f"⚠️ Ollama stream error: {e}")
            return
    
    def chat(
        self, 
        messages: List[Dict[str, str]], 
        model: str = None
    ) -> Optional[str]:
        """
        Chat completion with message history.
        
        Args:
            messages: List of {"role": "user/assistant/system", "content": "..."}
            model: Model to use
            
        Returns:
            Assistant's response or None on failure
        """
        model = model or self.default_model
        url = f"{self.base_url}/api/chat"
        
        payload = {
            "model": model,
            "messages": messages,
            "stream": False
        }
        
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(url, json=payload)
                response.raise_for_status()
                data = response.json()
                return data.get("message", {}).get("content", "")
        except httpx.ConnectError:
            print(f"⚠️ Ollama not reachable at {self.base_url}")
            return None
        except Exception as e:
            print(f"⚠️ Ollama chat error: {e}")
            return None
    
    def list_models(self) -> List[str]:
        """
        List available models on Ollama server.
        
        Returns:
            List of model names
        """
        url = f"{self.base_url}/api/tags"
        
        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.get(url)
                response.raise_for_status()
                data = response.json()
                models = data.get("models", [])
                return [m.get("name", "") for m in models]
        except Exception as e:
            print(f"⚠️ Failed to list Ollama models: {e}")
            return []
    
    def check_health(self) -> bool:
        """
        Check if Ollama server is reachable.
        
        Returns:
            True if server is available, False otherwise
        """
        try:
            with httpx.Client(timeout=5.0) as client:
                response = client.get(f"{self.base_url}/api/tags")
                return response.status_code == 200
        except Exception:
            return False
    
    def pull_model(self, model: str) -> bool:
        """
        Pull a model from Ollama library.
        
        Args:
            model: Model name to pull
            
        Returns:
            True if successful
        """
        url = f"{self.base_url}/api/pull"
        
        try:
            with httpx.Client(timeout=600.0) as client:  # 10 min timeout for large models
                response = client.post(url, json={"name": model})
                return response.status_code == 200
        except Exception as e:
            print(f"⚠️ Failed to pull model {model}: {e}")
            return False
