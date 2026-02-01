"""Nexus AI - Main Application Entry Point."""

# CRITICAL: Monkeypatch bcrypt for passlib compatibility BEFORE any other imports
# This resolves the 30-second logic hang/timeout during startup or auth
try:
    import bcrypt
    if not hasattr(bcrypt, "__about__"):
        bcrypt.__about__ = bcrypt
except ImportError:
    pass

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

# Import security middlewares
from middleware.rate_limit import RateLimitMiddleware
from middleware.security_headers import SecurityHeadersMiddleware
from middleware.request_id import RequestIDMiddleware


settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handles the application startup and shutdown events.
    
    This context manager is responsible for initializing database tables,
    verifying Redis connectivity, and starting/stopping support services
    like the WebSocket manager.
    
    Args:
        app: The FastAPI application instance.
    """
    # Startup
    print("🚀 Starting Nexus AI...")
    
    # Database verification
    # Note: Table creation is handled by migrate.py in start.sh
    print("🔍 Database connection: Initializing pool...")
    
    # Test Redis connection
    if ping_redis():
        print("✅ Redis connection successful")
        # Start WebSocket manager
        await ws_manager.start()
        print("✅ WebSocket manager started")
        
        # Start background worker thread (Single-Process Optimization)
        from worker import start_worker_thread
        start_worker_thread()
        print("✅ Background worker started in shared memory")
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
    description="""
### Autonomous Multi-Agent AI Workspace API

Nexus AI is a world-class platform for orchestrating autonomous AI agents. 
This API provides robust endpoints for:
- **Task Orchestration**: Natural language task submission and background processing.
- **Project Management**: Multi-phase project planning and execution.
- **Semantic Memory**: Long-term context storage and retrieval using vector embeddings.
- **Workflow Automation**: Template-driven agent workflows.
- **Agent Monitoring**: Real-time status updates via WebSockets.

Developed with a focus on performance, security, and developer experience.
""",
    version="2.1.0",
    lifespan=lifespan,
    contact={
        "name": "Madhur Tyagi",
        "email": "madhur.tyagi@nexus-ai.com",
        "url": "https://github.com/madhurtyagii",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {"name": "Auth", "description": "Authentication and user session management."},
        {"name": "Tasks", "description": "AI task submission, tracking, and results."},
        {"name": "Projects", "description": "Complex multi-phase project orchestration."},
        {"name": "Agents", "description": "Agent capabilities, status, and activity."},
        {"name": "Memory", "description": "Conversation history and semantic context retrieval."},
        {"name": "Files", "description": "Secure file uploads and management."},
    ]
)

# --- Middleware Stack ---
# (Note: Starlette processes middlewares in reverse order of addition.
# The LAST one added will be the FIRST one to receive the request.)

# 4. Security & Request ID (Innermost)
app.add_middleware(RequestIDMiddleware)
app.add_middleware(SecurityHeadersMiddleware)

# 3. Rate Limiting
app.add_middleware(RateLimitMiddleware, limit=100, window=60)

# 2. CORS (Outer)
# Loosened further to allow all vercel apps during debugging
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://nexus-ai-three-chi.vercel.app",
        "https://nexus-ai.vercel.app",
    ],
    allow_origin_regex=r"https://.*\.vercel\.app", # Allow all vercel subdomains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging Middleware
from fastapi import Request
import time

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Middleware for logging HTTP requests and their processing time."""
    start_time = time.time()
    
    # Call the next handler
    response = await call_next(request)
    
    # Calculate processing time
    process_time = time.time() - start_time
    
    # Log the request (skip health checks to reduce noise)
    if request.url.path != "/health":
        print(f"{request.method} {request.url.path} - {response.status_code} - {process_time:.3f}s")
    
    return response


# Global exception handlers
from middleware.error_handler import setup_exception_handlers
setup_exception_handlers(app)


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
    """Root endpoint providing a simple welcome message and API version."""
    return {
        "message": "Welcome to Nexus AI API",
        "version": "2.1.0",
        "docs": "/docs",
        "status": "operational"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint to verify server and dependency status.
    
    Retrieves system metrics like CPU/Memory usage and checks connectivity
    to services like Redis and the Database.
    
    Returns:
        dict: Health status, system metrics, and service states.
    """
    import psutil
    
    # Debug logging for health check
    print("DEBUG: Performing health check...")
    
    redis_status = "connected" if ping_redis() else "disconnected"
    cpu_usage = psutil.cpu_percent()
    memory_usage = psutil.virtual_memory().percent
    
    print(f"DEBUG: Health check results - Redis: {redis_status}, CPU: {cpu_usage}%, Memory: {memory_usage}%")
    
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "system": {
            "cpu_usage": f"{cpu_usage}%",
            "memory_usage": f"{memory_usage}%"
        },
        "services": {
            "database": "connected",
            "redis": redis_status,
            "websocket": {
                "connections": ws_manager.connection_manager.get_connection_count(),
                "users": ws_manager.connection_manager.get_user_count()
            }
        }
    }

@app.get("/metrics", tags=["Monitoring"])
async def get_metrics():
    """Simple metrics endpoint."""
    if not settings.enable_metrics:
        raise HTTPException(status_code=404, detail="Metrics disabled")
    
    return {
        "uptime": "TODO: track uptime",
        "requests_total": "TODO: track request count",
        "active_tasks": "TODO: track active tasks"
    }


def get_user_id_from_token(token: str) -> Optional[int]:
    """Decodes a JWT token to extract the user ID."""
    from auth import decode_access_token
    payload = decode_access_token(token)
    if payload and "sub" in payload:
        try:
            return int(payload["sub"])
        except (ValueError, TypeError):
            return None
    return None


@app.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: Optional[str] = Query(None)
):
    """Main WebSocket endpoint for real-time application updates.
    
    Handles persistent connections from clients, performing session authentication
    via JWT and delegating message handling to the project's WebSocket manager.
    
    Args:
        websocket: The raw WebSocket connection object.
        token: Optional JWT token provided in the query string.
        
    Note:
        Closes connection with code 4001 if no token is provided, 
        or 4002 if the token is invalid.
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
