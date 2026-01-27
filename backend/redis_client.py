"""
Nexus AI - Redis Client
Redis connection and utility functions for caching and messaging
"""

import redis
import json
from typing import Optional, Any, Generator
from config import get_settings

settings = get_settings()

# Create Redis connection pool
pool = redis.ConnectionPool.from_url(settings.redis_url, decode_responses=True)

# Create Redis client
redis_client = redis.Redis(connection_pool=pool)


def ping_redis() -> bool:
    """
    Test Redis connection.
    
    Returns:
        True if connection successful, False otherwise
    """
    try:
        return redis_client.ping()
    except redis.ConnectionError:
        return False


def set_cache(key: str, value: Any, expiry_seconds: int = 3600) -> bool:
    """
    Store data in Redis cache.
    
    Args:
        key: Cache key
        value: Value to store (will be JSON serialized if not string)
        expiry_seconds: TTL in seconds (default 1 hour)
        
    Returns:
        True if successful
    """
    try:
        if not isinstance(value, str):
            value = json.dumps(value)
        redis_client.setex(key, expiry_seconds, value)
        return True
    except redis.RedisError:
        return False


def get_cache(key: str) -> Optional[Any]:
    """
    Retrieve data from Redis cache.
    
    Args:
        key: Cache key
        
    Returns:
        Cached value or None if not found
    """
    try:
        value = redis_client.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        return None
    except redis.RedisError:
        return None


def delete_cache(key: str) -> bool:
    """
    Delete a key from Redis cache.
    
    Args:
        key: Cache key to delete
        
    Returns:
        True if key was deleted
    """
    try:
        redis_client.delete(key)
        return True
    except redis.RedisError:
        return False


def publish_message(channel: str, message: Any) -> bool:
    """
    Publish a message to a Redis channel.
    
    Args:
        channel: Channel name
        message: Message to publish (will be JSON serialized)
        
    Returns:
        True if successful
    """
    try:
        if not isinstance(message, str):
            message = json.dumps(message)
        redis_client.publish(channel, message)
        return True
    except redis.RedisError:
        return False


def subscribe_channel(channel: str) -> Generator:
    """
    Subscribe to a Redis channel and yield messages.
    
    Args:
        channel: Channel name to subscribe to
        
    Yields:
        Messages from the channel
    """
    pubsub = redis_client.pubsub()
    pubsub.subscribe(channel)
    
    for message in pubsub.listen():
        if message["type"] == "message":
            data = message["data"]
            try:
                yield json.loads(data)
            except json.JSONDecodeError:
                yield data


# Task queue functions
TASK_QUEUE_KEY = "nexus:task_queue"


def enqueue_task(task_id: int) -> bool:
    """Add a task ID to the processing queue."""
    try:
        redis_client.rpush(TASK_QUEUE_KEY, task_id)
        return True
    except redis.RedisError:
        return False


def dequeue_task() -> Optional[int]:
    """Remove and return the next task ID from the queue."""
    try:
        task_id = redis_client.lpop(TASK_QUEUE_KEY)
        return int(task_id) if task_id else None
    except redis.RedisError:
        return None


def get_queue_length() -> int:
    """Get the number of tasks in the queue."""
    try:
        return redis_client.llen(TASK_QUEUE_KEY)
    except redis.RedisError:
        return 0
