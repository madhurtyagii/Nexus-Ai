"""
Nexus AI - Main Application Entry Point
FastAPI application with all routes and middleware
"""

# Fix Windows console encoding to support Unicode/emoji output
import sys
import os
if sys.platform == 'win32':
    # Force UTF-8 encoding for stdout/stderr on Windows
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except AttributeError:
        # Python < 3.7 fallback
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    # Also set environment variable for subprocesses
    os.environ['PYTHONIOENCODING'] = 'utf-8'

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Optional
import jwt

from database import engine, Base, get_db
from config import get_settings
from redis_client import ping_redis

# Import all models to ensure they're registered with SQLAlchemy
from models import User, Task, Subtask, Agent, AgentMessage, Project

# Import routers
from routers.auth import router as auth_router
from routers.tasks import router as tasks_router
from routers.agents import router as agents_router
from routers.projects import router as projects_router
from routers.admin import router as admin_router
from routers.memory import router as memory_router
from routers.feedback import router as feedback_router
from routers.files import router as files_router
from routers.workflow_templates import router as workflow_templates_router
from routers.exports import router as exports_router

# Import messaging
from messaging import ws_manager


settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler.
    Runs on startup and shutdown.
    """
    # Startup
    print("🚀 Starting Nexus AI...")
    
    # Create database tables
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created/verified")
    
    # Test Redis connection
    if ping_redis():
        print("✅ Redis connection successful")
        # Start WebSocket manager
        await ws_manager.start()
        print("✅ WebSocket manager started")
    else:
        print("⚠️ Redis connection failed - some features may be unavailable")
    
    print("✅ Nexus AI is ready!")
    print(f"📚 API Documentation: http://localhost:{settings.port}/docs")
    print(f"🔌 WebSocket: ws://localhost:{settings.port}/ws")
    
    yield
    
    # Shutdown
    print("👋 Shutting down Nexus AI...")
    await ws_manager.stop()


# Create FastAPI application
app = FastAPI(
    title="Nexus AI API",
    description="Autonomous Multi-Agent AI Workspace API",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS - Allow all origins in development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Logging Middleware
from fastapi import Request
import time

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    log_line = f"\n{datetime.now().isoformat()} 📥 {request.method} {request.url.path}"
    with open("requests.log", "a", encoding="utf-8") as f:
        f.write(log_line)
    
    try:
        response = await call_next(request)
        process_time = (time.time() - start_time) * 1000
        log_line = f"\n{datetime.now().isoformat()} 📤 {request.method} {request.url.path} - {response.status_code} ({process_time:.2f}ms)"
        with open("requests.log", "a", encoding="utf-8") as f:
            f.write(log_line)
        return response
    except Exception as e:
        log_line = f"\n{datetime.now().isoformat()} ❌ Uncaught Exception: {str(e)}"
        with open("requests.log", "a", encoding="utf-8") as f:
            f.write(log_line)
        print(f"ERROR Uncaught Exception: {str(e)}")
        import traceback
        traceback.print_exc()
        raise


# Global exception handler to catch ALL exceptions
from starlette.responses import JSONResponse
from starlette.requests import Request as StarletteRequest
from fastapi import Request as FastAPIRequest

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Catch all exceptions and print detailed traceback"""
    import traceback
    import sys
    print("=" * 50, file=sys.stderr)
    print("GLOBAL EXCEPTION HANDLER TRIGGERED", file=sys.stderr)
    print(f"Request: {request.method} {request.url}", file=sys.stderr)
    print(f"Exception Type: {type(exc).__name__}", file=sys.stderr)
    print(f"Exception: {exc}", file=sys.stderr)
    traceback.print_exc(file=sys.stderr)
    print("=" * 50, file=sys.stderr)
    
    # Force flush to ensure output is visible
    sys.stderr.flush()
    
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal Server Error: {str(exc)}"}
    )


# Include routers
app.include_router(auth_router)
app.include_router(tasks_router)
app.include_router(agents_router)
app.include_router(projects_router)
app.include_router(admin_router)
app.include_router(memory_router)
app.include_router(feedback_router)
app.include_router(files_router)
app.include_router(workflow_templates_router)
app.include_router(exports_router)


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint - API welcome message."""
    return {
        "message": "Welcome to Nexus AI API",
        "version": "2.0.0",
        "docs": "/docs"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint.
    Returns server status and timestamp.
    """
    redis_status = "connected" if ping_redis() else "disconnected"
    
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "database": "connected",
            "redis": redis_status,
            "websocket": {
                "connections": ws_manager.connection_manager.get_connection_count(),
                "users": ws_manager.connection_manager.get_user_count()
            }
        }
    }


def get_user_id_from_token(token: str) -> Optional[int]:
    """Extract user ID from JWT token."""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return payload.get("sub")
    except:
        return None


@app.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: Optional[str] = Query(None)
):
    """
    WebSocket endpoint for real-time updates.
    
    Connect with: ws://localhost:8000/ws?token=<jwt_token>
    
    Client messages:
    - {"action": "subscribe_task", "task_id": 123}
    - {"action": "unsubscribe_task", "task_id": 123}
    - {"action": "ping"}
    """
    # Authenticate
    if not token:
        await websocket.close(code=4001, reason="No token provided")
        return
    
    user_id = get_user_id_from_token(token)
    if not user_id:
        await websocket.close(code=4002, reason="Invalid token")
        return
    
    # Handle connection
    await ws_manager.handle_connection(websocket, user_id)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
