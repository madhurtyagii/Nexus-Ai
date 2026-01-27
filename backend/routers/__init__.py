"""
Nexus AI - Routers Package
Export all API routers
"""

from routers.auth import router as auth_router
from routers.tasks import router as tasks_router
from routers.agents import router as agents_router
from routers.projects import router as projects_router
from routers.admin import router as admin_router

__all__ = [
    "auth_router",
    "tasks_router", 
    "agents_router",
    "projects_router",
    "admin_router",
]
