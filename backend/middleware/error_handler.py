import logging
import traceback
import uuid
from datetime import datetime
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.exc import SQLAlchemyError
from exceptions.custom_exceptions import NexusBaseException, DatabaseError

logger = logging.getLogger(__name__)

async def global_exception_handler(request: Request, exc: Exception):
    """Catch-all for any unhandled exceptions."""
    request_id = str(uuid.uuid4())
    logger.error(f"Unhandled exception: {str(exc)}\nTraceback: {traceback.format_exc()}", 
                 extra={"request_id": request_id})
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": True,
            "error_code": "SYS_500",
            "message": "An unexpected server error occurred.",
            "details": {},
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "request_id": request_id
        }
    )

async def nexus_exception_handler(request: Request, exc: NexusBaseException):
    """Handle custom Nexus exceptions."""
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    
    # Map exception types to status codes if needed, default to 400
    status_code = status.HTTP_400_BAD_REQUEST
    if exc.error_code == "AUTH_001":
        status_code = status.HTTP_401_UNAUTHORIZED
    elif exc.error_code == "QUOTA_001":
        status_code = status.HTTP_429_TOO_MANY_REQUESTS
    elif exc.error_code == "DB_001":
        status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return JSONResponse(
        status_code=status_code,
        content={
            "error": True,
            "error_code": exc.error_code,
            "message": exc.message,
            "details": exc.details,
            "timestamp": exc.timestamp,
            "request_id": request_id
        }
    )

async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle standard FastAPI/Starlette HTTP exceptions."""
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "error_code": f"HTTP_{exc.status_code}",
            "message": exc.detail,
            "details": {},
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "request_id": request_id
        }
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors."""
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": True,
            "error_code": "VAL_422",
            "message": "Input validation failed",
            "details": {"errors": exc.errors()},
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "request_id": request_id
        }
    )

async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    """Handle SQLAlchemy database errors."""
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    logger.error(f"Database error: {str(exc)}", extra={"request_id": request_id})
    
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={
            "error": True,
            "error_code": "DB_001",
            "message": "Database service is temporarily unavailable.",
            "details": {}, # Don't leak SQL details
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "request_id": request_id
        }
    )

def setup_exception_handlers(app):
    """Register all exception handlers to the FastAPI app."""
    app.add_exception_handler(Exception, global_exception_handler)
    app.add_exception_handler(NexusBaseException, nexus_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
