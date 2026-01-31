import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request

class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        # Set request_id in state for later use
        request.state.request_id = request_id
        
        response = await call_next(request)
        
        # Return request_id in response headers
        response.headers["X-Request-ID"] = request_id
        return response
