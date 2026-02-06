"""Nexus AI - Retry Utilities.

This module provides a decorator for retrying asynchronous operations 
with exponential backoff, useful for handling transient network issues.
"""
import asyncio
import functools
import logging
import time
from typing import Type, Union, Tuple, Callable, Any

logger = logging.getLogger(__name__)

def retry(
    exceptions: Union[Type[Exception], Tuple[Type[Exception], ...]] = Exception,
    tries: int = 3,
    delay: float = 1,
    backoff: float = 2,
    max_delay: float = 60,
    logger: logging.Logger = logger
) -> Callable:
    """Decorator for retrying a function with exponential backoff.
    
    Args:
        exceptions: The exception type(s) that should trigger a retry.
        tries: The maximum number of attempts before giving up.
        delay: The initial delay between retries in seconds.
        backoff: The multiplier for increasing delay after each attempt.
        max_delay: The maximum allowable delay in seconds.
        logger: Logger instance to record retry attempts.
        
    Returns:
        Callable: The decorated function with retry logic injected.
    """
    def decorator(func: Callable):
        if asyncio.iscoroutinefunction(func):
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                _tries, _delay = tries, delay
                while _tries > 1:
                    try:
                        return await func(*args, **kwargs)
                    except exceptions as e:
                        _tries -= 1
                        logger.warning(
                            f"Retry: {func.__name__} failed with {type(e).__name__}: {e}. "
                            f"Retrying in {_delay}s... ({_tries} tries left)"
                        )
                        await asyncio.sleep(_delay)
                        _delay = min(_delay * backoff, max_delay)
                return await func(*args, **kwargs)
            return async_wrapper
        else:
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                _tries, _delay = tries, delay
                while _tries > 1:
                    try:
                        return func(*args, **kwargs)
                    except exceptions as e:
                        _tries -= 1
                        logger.warning(
                            f"Retry: {func.__name__} failed with {type(e).__name__}: {e}. "
                            f"Retrying in {_delay}s... ({_tries} tries left)"
                        )
                        time.sleep(_delay)
                        _delay = min(_delay * backoff, max_delay)
                return func(*args, **kwargs)
            return sync_wrapper
    return decorator
