import time
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from redis_client import redis_client

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, limit: int = 100, window: int = 60):
        super().__init__(app)
        self.limit = limit
        self.window = window

    async def dispatch(self, request: Request, call_next):
        # Skip for health checks or non-API routes
        if not request.url.path.startswith("/"):
            return await call_next(request)

        # Use IP or user_id as key
        client_ip = request.client.host
        key = f"rate_limit:{client_ip}"

        try:
            current = redis_client.get(key)
            if current and int(current) >= self.limit:
                raise HTTPException(status_code=429, detail="Too many requests")

            # Increment and set expiry if new
            pipe = redis_client.pipeline()
            pipe.incr(key)
            pipe.expire(key, self.window)
            pipe.execute()
        except Exception as e:
            # Don't block requests if Redis is down, but log it
            print(f"Rate limiter error: {e}")

        return await call_next(request)
