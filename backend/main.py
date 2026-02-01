"""Nexus AI - Main Application Entry Point.

This module initializes the FastAPI application, configures middleware (CORS, 
Rate Limiting, Security Headers, etc.), and includes all router modules. 
It also handles the application lifespan events and WebSocket connections.

Features:
    - FastAPI app initialization
    - Global middleware configuration
    - Lifespan management (DB, Redis)
    - WebSocket orchestration
    - Global exception handling
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

# Configure CORS - Allow frontend origins
cors_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "https://nexus-ai.vercel.app",
    "https://*.vercel.app",  # Allow all Vercel preview deployments
]

# Also check for CORS_ORIGINS environment variable
import os
env_cors = os.getenv("CORS_ORIGINS", "")
if env_cors:
    cors_origins.extend([origin.strip() for origin in env_cors.split(",") if origin.strip()])

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Security & Rate Limiting Middlewares
app.add_middleware(RequestIDMiddleware)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RateLimitMiddleware, limit=100, window=60)

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
    """Root endpoint providing a simple welcome message and API version.
    
    Returns:
        dict: A welcome message, version, and documentation link.
    """


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint to verify server and dependency status.
    
    Retrieves system metrics like CPU/Memory usage and checks connectivity
    to services like Redis and the Database.
    
    Returns:
        dict: Health status, system metrics, and service states.
    """
    import psutil
    
    redis_status = "connected" if ping_redis() else "disconnected"
    cpu_usage = psutil.cpu_percent()
    memory_usage = psutil.virtual_memory().percent
    
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
    """Decodes a JWT token to extract the user ID.
    
    Args:
        token: The encoded JWT string.
        
    Returns:
        Optional[int]: The user ID if valid, else None.
    """


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
