"""Nexus AI - Audit Logging.

This module provides a decorator for auditing API operations by logging 
actions performed by users for security and debugging purposes.
"""
import logging
import functools
from datetime import datetime
from typing import Any, Callable

logger = logging.getLogger("audit")

def audit_log(action: str) -> Callable:
    """Decorator to log audited actions in the backend.
    
    Args:
        action: A descriptive string for the activity being logged.
        
    Returns:
        Callable: The decorated function with audit logging logic.
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract user if possible (assuming current_user is a kwarg)
            user = kwargs.get("current_user")
            user_id = user.id if user and hasattr(user, "id") else "unknown"
            
            start_time = datetime.utcnow()
            try:
                result = await func(*args, **kwargs)
                logger.info(
                    f"AUDIT: action={action} user_id={user_id} status=success timestamp={start_time}"
                )
                return result
            except Exception as e:
                logger.error(
                    f"AUDIT: action={action} user_id={user_id} status=failed error='{str(e)}' timestamp={start_time}"
                )
                raise
        return wrapper
    return decorator
