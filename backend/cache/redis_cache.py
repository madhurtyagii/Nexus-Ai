import json
import logging
import functools
from typing import Any, Optional, Callable
from redis_client import redis_client # Assuming this exists from Phase 2/4

logger = logging.getLogger(__name__)

def cache_get(key: str) -> Optional[Any]:
    """Retrieve value from Redis cache."""
    try:
        data = redis_client.get(key)
        if data:
            return json.loads(data)
    except Exception as e:
        logger.error(f"Cache get error for key {key}: {e}")
    return None

def cache_set(key: str, value: Any, ttl: int = 300):
    """Store value in Redis cache with TTL."""
    try:
        redis_client.setex(key, ttl, json.dumps(value))
    except Exception as e:
        logger.error(f"Cache set error for key {key}: {e}")

def cache_delete(key: str):
    """Invalidate cache key."""
    try:
        redis_client.delete(key)
    except Exception as e:
        logger.error(f"Cache delete error for key {key}: {e}")

def cache_clear_pattern(pattern: str):
    """Clear keys matching pattern."""
    try:
        keys = redis_client.keys(pattern)
        if keys:
            redis_client.delete(*keys)
    except Exception as e:
        logger.error(f"Cache clear pattern error for {pattern}: {e}")

def cached(ttl: int = 300, key_prefix: str = "nexus_cache"):
    """Decorator to cache function results."""
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key from function name and args
            key_parts = [key_prefix, func.__name__]
            if args:
                key_parts.append(str(args))
            if kwargs:
                key_parts.append(str(sorted(kwargs.items())))
            
            cache_key = ":".join(key_parts)
            
            # Check cache
            cached_val = cache_get(cache_key)
            if cached_val is not None:
                logger.debug(f"Cache hit: {cache_key}")
                return cached_val
            
            # Execute function
            result = func(*args, **kwargs)
            
            # Store in cache
            cache_set(cache_key, result, ttl)
            return result
        return wrapper
    return decorator
