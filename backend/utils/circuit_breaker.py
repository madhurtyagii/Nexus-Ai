"""Nexus AI - Circuit Breaker.

This module implements the Circuit Breaker pattern to prevent cascading 
failures by failing fast when a remote service is detected as unhealthy.
"""
import asyncio
import time
import logging
from enum import Enum
from typing import Callable, Any, Optional
from functools import wraps

logger = logging.getLogger(__name__)

class CircuitState(Enum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"

class CircuitBreaker:
    """Implements the Circuit Breaker pattern for asynchronous functions.
    
    The CircuitBreaker monitors for failures and transitions between 
    CLOSED, OPEN, and HALF_OPEN states to protect the system from 
    unresponsive dependencies.
    
    Attributes:
        name: Identifier for the circuit breaker instance.
        failure_threshold: Number of failures before opening the circuit.
        recovery_timeout: Seconds to wait before attempting recovery.
        
    Example:
        >>> breaker = CircuitBreaker("API_ROOT", failure_threshold=3)
        >>> @breaker
        >>> async def call_api():
        >>>     ...
    """
    def __init__(
        self, 
        name: str, 
        failure_threshold: int = 5, 
        recovery_timeout: int = 60,
        expected_exception: type = Exception
    ):
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = 0
        
    def __call__(self, func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            return await self.call(func, *args, **kwargs)
        return wrapper

    async def call(self, func: Callable, *args, **kwargs) -> Any:
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time > self.recovery_timeout:
                logger.info(f"Circuit Breaker [{self.name}]: Transitioning from OPEN to HALF_OPEN")
                self.state = CircuitState.HALF_OPEN
            else:
                logger.warning(f"Circuit Breaker [{self.name}]: State is OPEN, rejecting request")
                raise Exception(f"Circuit Breaker [{self.name}] is OPEN")

        try:
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure()
            raise e

    def _on_success(self):
        if self.state == CircuitState.HALF_OPEN:
            logger.info(f"Circuit Breaker [{self.name}]: Transitioning from HALF_OPEN to CLOSED")
            self.state = CircuitState.CLOSED
            self.failure_count = 0
        elif self.state == CircuitState.CLOSED:
            self.failure_count = 0

    def _on_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.state == CircuitState.CLOSED:
            if self.failure_count >= self.failure_threshold:
                logger.error(f"Circuit Breaker [{self.name}]: Threshold reached. Transitioning to OPEN")
                self.state = CircuitState.OPEN
        elif self.state == CircuitState.HALF_OPEN:
            logger.error(f"Circuit Breaker [{self.name}]: Failure in HALF_OPEN. Transitioning back to OPEN")
            self.state = CircuitState.OPEN

# Pre-defined circuit breakers for common services
llm_circuit_breaker = CircuitBreaker("LLM_API", failure_threshold=5, recovery_timeout=60)
search_circuit_breaker = CircuitBreaker("SEARCH_API", failure_threshold=3, recovery_timeout=30)
