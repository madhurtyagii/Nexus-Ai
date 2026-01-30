4"""
Nexus AI - Embedding Manager
Generates and caches text embeddings using sentence-transformers
"""

import os
import hashlib
from typing import List, Optional

from logging_config import get_logger

logger = get_logger(__name__)

# Lazy import for sentence-transformers (heavy dependency)
_model = None
_model_name = None


def _get_model():
    """Lazy load the sentence-transformer model."""
    global _model, _model_name
    
    if _model is None:
        try:
            from sentence_transformers import SentenceTransformer
            
            _model_name = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
            logger.info(f"Loading embedding model: {_model_name}")
            
            _model = SentenceTransformer(_model_name)
            logger.info(f"Embedding model loaded successfully (dim={_model.get_sentence_embedding_dimension()})")
            
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            raise
    
    return _model


class EmbeddingManager:
    """
    Manages text embeddings using sentence-transformers.
    
    Features:
    - Lazy model loading
    - Redis caching for embeddings
    - Batch processing support
    - Similarity calculation
    """
    
    def __init__(self, use_cache: bool = True):
        """
        Initialize embedding manager.
        
        Args:
            use_cache: Whether to use Redis for caching embeddings
        """
        self.use_cache = use_cache
        self._redis_client = None
        self.cache_ttl = int(os.getenv("EMBEDDING_CACHE_TTL", 604800))  # 7 days
        
        if use_cache:
            self._init_redis()
    
    def _init_redis(self):
        """Initialize Redis client for caching."""
        try:
            from redis_client import redis_client
            self._redis_client = redis_client
            logger.debug("Redis cache enabled for embeddings")
        except Exception as e:
            logger.warning(f"Redis not available for embedding cache: {e}")
            self._redis_client = None
    
    def _get_cache_key(self, text: str) -> str:
        """Generate cache key from text hash."""
        text_hash = hashlib.sha256(text.encode()).hexdigest()[:16]
        return f"emb:{text_hash}"
    
    def _get_cached_embedding(self, text: str) -> Optional[List[float]]:
        """Get embedding from cache if available."""
        if not self._redis_client or not self.use_cache:
            return None
        
        try:
            cache_key = self._get_cache_key(text)
            cached = self._redis_client.get(cache_key)
            
            if cached:
                import json
                return json.loads(cached)
            return None
            
        except Exception as e:
            logger.debug(f"Cache read error: {e}")
            return None
    
    def _cache_embedding(self, text: str, embedding: List[float]):
        """Cache embedding in Redis."""
        if not self._redis_client or not self.use_cache:
            return
        
        try:
            import json
            cache_key = self._get_cache_key(text)
            self._redis_client.setex(
                cache_key,
                self.cache_ttl,
                json.dumps(embedding)
            )
        except Exception as e:
            logger.debug(f"Cache write error: {e}")
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Text to embed
            
        Returns:
            List of floats representing the embedding
        """
        # Check cache first
        cached = self._get_cached_embedding(text)
        if cached:
            logger.debug("Embedding cache hit")
            return cached
        
        # Preprocess text
        clean_text = self._preprocess_text(text)
        
        # Generate embedding
        model = _get_model()
        embedding = model.encode(clean_text, convert_to_numpy=True).tolist()
        
        # Cache the result
        self._cache_embedding(text, embedding)
        
        return embedding
    
    def generate_batch_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts efficiently.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embeddings
        """
        if not texts:
            return []
        
        # Check cache for each text
        results = [None] * len(texts)
        texts_to_embed = []
        indices_to_embed = []
        
        for i, text in enumerate(texts):
            cached = self._get_cached_embedding(text)
            if cached:
                results[i] = cached
            else:
                texts_to_embed.append(self._preprocess_text(text))
                indices_to_embed.append(i)
        
        # Generate embeddings for uncached texts
        if texts_to_embed:
            model = _get_model()
            embeddings = model.encode(texts_to_embed, convert_to_numpy=True).tolist()
            
            for idx, embedding in zip(indices_to_embed, embeddings):
                results[idx] = embedding
                # Cache new embeddings
                self._cache_embedding(texts[idx], embedding)
        
        logger.debug(f"Generated {len(texts_to_embed)} embeddings, {len(texts) - len(texts_to_embed)} from cache")
        
        return results
    
    def calculate_similarity(
        self, 
        embedding1: List[float], 
        embedding2: List[float]
    ) -> float:
        """
        Calculate cosine similarity between two embeddings.
        
        Args:
            embedding1: First embedding
            embedding2: Second embedding
            
        Returns:
            Similarity score between 0 and 1
        """
        import numpy as np
        
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)
        
        # Cosine similarity
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        similarity = dot_product / (norm1 * norm2)
        
        # Ensure result is between 0 and 1
        return float(max(0, min(1, (similarity + 1) / 2)))
    
    def _preprocess_text(self, text: str) -> str:
        """
        Preprocess text before embedding.
        
        - Remove extra whitespace
        - Truncate if too long (model max ~512 tokens)
        """
        # Remove extra whitespace
        clean = " ".join(text.split())
        
        # Truncate if too long (rough estimate: 512 tokens ≈ 2000 chars)
        max_chars = 2000
        if len(clean) > max_chars:
            clean = clean[:max_chars]
            logger.debug(f"Truncated text from {len(text)} to {max_chars} chars")
        
        return clean
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings from the model."""
        model = _get_model()
        return model.get_sentence_embedding_dimension()


# Global embedding manager instance
_embedding_manager: Optional[EmbeddingManager] = None


def get_embedding_manager() -> EmbeddingManager:
    """Get or create the global EmbeddingManager instance."""
    global _embedding_manager
    if _embedding_manager is None:
        _embedding_manager = EmbeddingManager()
    return _embedding_manager
