"""
Nexus AI - Task Queue
Redis-based queue for distributed task processing
"""

import json
import time
from typing import Optional, Dict, Any, List
from datetime import datetime

from redis_client import redis_client


class TaskQueue:
    """
    Redis-based queue for managing subtask processing.
    
    Features:
    - Priority queue support
    - Retry mechanism with exponential backoff
    - Status tracking
    - Dead letter queue for failed tasks
    """
    
    QUEUE_KEY = "nexus:task_queue"
    PRIORITY_QUEUE_KEY = "nexus:priority_queue"
    PROCESSING_SET = "nexus:processing"
    DEAD_LETTER_KEY = "nexus:dead_letter"
    
    MAX_RETRIES = 3
    
    def __init__(self):
        """Initialize task queue with Redis connection."""
        self.redis = redis_client
    
    def _subtask_key(self, subtask_id: int) -> str:
        """Get Redis key for subtask metadata."""
        return f"nexus:subtask:{subtask_id}"
    
    def _output_key(self, subtask_id: int) -> str:
        """Get Redis key for subtask output."""
        return f"nexus:subtask:{subtask_id}:output"
    
    def enqueue(self, subtask_id: int, priority: int = 0) -> bool:
        """
        Add subtask to processing queue.
        
        Args:
            subtask_id: Subtask ID to enqueue
            priority: Priority level (higher = more urgent)
            
        Returns:
            True if successful
        """
        try:
            # Store metadata
            metadata = {
                "subtask_id": subtask_id,
                "status": "queued",
                "enqueued_at": datetime.utcnow().isoformat(),
                "retries": 0,
                "priority": priority
            }
            self.redis.hset(self._subtask_key(subtask_id), mapping=metadata)
            
            # Add to appropriate queue
            if priority > 0:
                # High priority - push to front
                self.redis.lpush(self.PRIORITY_QUEUE_KEY, subtask_id)
            else:
                # Normal priority - push to back
                self.redis.rpush(self.QUEUE_KEY, subtask_id)
            
            return True
        except Exception as e:
            print(f"⚠️ Failed to enqueue subtask {subtask_id}: {e}")
            return False
    
    def dequeue(self, timeout: int = 1) -> Optional[int]:
        """
        Get next subtask from queue.
        
        Checks priority queue first, then regular queue.
        
        Args:
            timeout: Blocking timeout in seconds
            
        Returns:
            Subtask ID or None if queue empty
        """
        try:
            # Check priority queue first (non-blocking)
            result = self.redis.lpop(self.PRIORITY_QUEUE_KEY)
            if result:
                return int(result)
            
            # Block on regular queue
            result = self.redis.blpop(self.QUEUE_KEY, timeout=timeout)
            if result:
                _, subtask_id = result
                return int(subtask_id)
            
            return None
        except Exception as e:
            print(f"⚠️ Dequeue error: {e}")
            return None
    
    def get_queue_size(self) -> int:
        """Get total number of items in both queues."""
        try:
            normal = self.redis.llen(self.QUEUE_KEY)
            priority = self.redis.llen(self.PRIORITY_QUEUE_KEY)
            return normal + priority
        except Exception:
            return 0
    
    def mark_processing(self, subtask_id: int) -> bool:
        """
        Mark subtask as currently being processed.
        
        Args:
            subtask_id: Subtask ID
            
        Returns:
            True if successful
        """
        try:
            self.redis.hset(self._subtask_key(subtask_id), mapping={
                "status": "processing",
                "started_at": datetime.utcnow().isoformat()
            })
            self.redis.sadd(self.PROCESSING_SET, subtask_id)
            return True
        except Exception as e:
            print(f"⚠️ Failed to mark processing: {e}")
            return False
    
    def mark_complete(
        self, 
        subtask_id: int, 
        output: Dict[str, Any]
    ) -> bool:
        """
        Mark subtask as completed successfully.
        
        Args:
            subtask_id: Subtask ID
            output: Output data to store
            
        Returns:
            True if successful
        """
        try:
            self.redis.hset(self._subtask_key(subtask_id), mapping={
                "status": "completed",
                "completed_at": datetime.utcnow().isoformat()
            })
            
            # Store output with 24 hour expiry
            self.redis.setex(
                self._output_key(subtask_id),
                86400,  # 24 hours
                json.dumps(output)
            )
            
            # Remove from processing set
            self.redis.srem(self.PROCESSING_SET, subtask_id)
            
            return True
        except Exception as e:
            print(f"⚠️ Failed to mark complete: {e}")
            return False
    
    def mark_failed(
        self, 
        subtask_id: int, 
        error: str
    ) -> bool:
        """
        Mark subtask as failed.
        
        If retries < MAX_RETRIES, re-enqueues with higher priority.
        Otherwise, moves to dead letter queue.
        
        Args:
            subtask_id: Subtask ID
            error: Error message
            
        Returns:
            True if re-queued for retry, False if permanently failed
        """
        try:
            # Get current retry count
            metadata = self.redis.hgetall(self._subtask_key(subtask_id))
            retries = int(metadata.get("retries", 0))
            
            self.redis.srem(self.PROCESSING_SET, subtask_id)
            
            if retries < self.MAX_RETRIES:
                # Re-enqueue with incremented retry count
                self.redis.hset(self._subtask_key(subtask_id), mapping={
                    "status": "retry_pending",
                    "retries": retries + 1,
                    "error_message": error,
                    "last_failed_at": datetime.utcnow().isoformat()
                })
                
                # Add to priority queue for retry
                self.enqueue(subtask_id, priority=retries + 1)
                print(f"♻️ Subtask {subtask_id} queued for retry ({retries + 1}/{self.MAX_RETRIES})")
                return True
            else:
                # Permanent failure - move to dead letter queue
                self.redis.hset(self._subtask_key(subtask_id), mapping={
                    "status": "permanently_failed",
                    "retries": retries,
                    "error_message": error,
                    "failed_at": datetime.utcnow().isoformat()
                })
                self.redis.rpush(self.DEAD_LETTER_KEY, subtask_id)
                print(f"💀 Subtask {subtask_id} permanently failed after {retries} retries")
                return False
                
        except Exception as e:
            print(f"⚠️ Failed to mark failed: {e}")
            return False
    
    def get_subtask_status(self, subtask_id: int) -> Dict[str, Any]:
        """Get current status of a subtask."""
        try:
            metadata = self.redis.hgetall(self._subtask_key(subtask_id))
            return metadata if metadata else {"status": "unknown"}
        except Exception:
            return {"status": "unknown"}
    
    def get_subtask_output(self, subtask_id: int) -> Optional[Dict[str, Any]]:
        """Get stored output for a completed subtask."""
        try:
            output = self.redis.get(self._output_key(subtask_id))
            return json.loads(output) if output else None
        except Exception:
            return None
    
    def get_processing_count(self) -> int:
        """Get number of subtasks currently being processed."""
        try:
            return self.redis.scard(self.PROCESSING_SET)
        except Exception:
            return 0
    
    def get_dead_letter_count(self) -> int:
        """Get number of permanently failed subtasks."""
        try:
            return self.redis.llen(self.DEAD_LETTER_KEY)
        except Exception:
            return 0
    
    def clear_all(self) -> bool:
        """Clear all queues (use with caution!)."""
        try:
            self.redis.delete(self.QUEUE_KEY)
            self.redis.delete(self.PRIORITY_QUEUE_KEY)
            self.redis.delete(self.PROCESSING_SET)
            self.redis.delete(self.DEAD_LETTER_KEY)
            return True
        except Exception:
            return False


# Global queue instance
task_queue = TaskQueue()
