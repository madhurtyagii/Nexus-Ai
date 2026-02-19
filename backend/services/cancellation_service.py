"""Nexus AI - Cancellation Service.

Provides a simple registry for tracking and signaling request cancellation
across the backend, especially for long-running GPU tasks.
"""

import threading
from redis_client import redis_client


class CancellationService:
    """Registry for cancelled request and task IDs using Redis for cross-process sync."""
    
    _instance = None
    _lock = threading.Lock()
    PREFIX = "nexus:cancellation:"
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(CancellationService, cls).__new__(cls)
                cls._instance.redis = redis_client
        return cls._instance

    def _get_key(self, request_id: str) -> str:
        return f"{self.PREFIX}{request_id}"

    def cancel(self, request_id: str):
        """Mark a request ID as cancelled in Redis."""
        if not request_id:
            return
        key = self._get_key(request_id)
        # Mark as cancelled with a 5-minute expiry
        self.redis.setex(key, 300, "1")
        print(f"🛑 [CancellationService] ID marked for cancellation (Redis): {request_id}")

    def is_cancelled(self, request_id: str) -> bool:
        """Check if a request ID has been marked for cancellation in Redis."""
        if not request_id:
            return False
        return self.redis.exists(self._get_key(request_id)) > 0

    def clear(self, request_id: str):
        """Remove a request ID from the cancellation registry (cleanup)."""
        if not request_id:
            return
        self.redis.delete(self._get_key(request_id))
        print(f"🧹 [CancellationService] ID cleared (Redis): {request_id}")


# Global singleton instance
cancellation_service = CancellationService()
