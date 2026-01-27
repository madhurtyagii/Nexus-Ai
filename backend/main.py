"""
Nexus AI - Main Application Entry Point
FastAPI application with all routes and middleware
"""

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

# Include routers
app.include_router(auth_router)
app.include_router(tasks_router)
app.include_router(agents_router)
app.include_router(projects_router)
app.include_router(admin_router)


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint - API welcome message."""
    return {
        "message": "Welcome to Nexus AI API",
        "version": "1.0.0",
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
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
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
