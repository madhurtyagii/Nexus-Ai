import time
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, limit: int = 100, window: int = 60):
        super().__init__(app)
        self.limit = limit
        self.window = window

    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for health checks and CORS preflight
        if request.url.path == "/health" or request.method == "OPTIONS":
            return await call_next(request)
        
        # Handle case where client might be None (health checks, internal requests)
        if request.client is None:
            return await call_next(request)

        client_ip = request.client.host
        key = f"rate_limit:{client_ip}"

        try:
            # Import redis_client lazily to avoid import issues
            from redis_client import redis_client
            
            current = redis_client.get(key)
            if current and int(current) >= self.limit:
                return JSONResponse(
                    status_code=429,
                    content={"detail": "Too many requests. Please slow down."}
                )

            # Increment and set expiry IF it's a new window (atomically)
            pipe = redis_client.pipeline()
            pipe.incr(key)
            # Only set expiry if it doesn't exist (fixed window)
            pipe.expire(key, self.window, nx=True)
            pipe.execute()
        except Exception as e:
            # Don't block requests if Redis is down
            print(f"Rate limiter error (non-fatal): {e}")

        return await call_next(request)
