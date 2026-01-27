"""
Nexus AI - Admin Router
Admin endpoints for monitoring and management
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any

from database import get_db
from models.user import User
from models.task import Task, TaskStatus
from models.agent import Agent
from dependencies import get_current_user
from llm.llm_manager import llm_manager
from orchestrator.queue import task_queue
from redis_client import ping_redis
from logging_config import read_recent_logs

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/health")
async def health_check():
    """
    Comprehensive health check for all services.
    """
    # Check LLM providers
    llm_status = llm_manager.get_provider_status()
    
    return {
        "status": "healthy",
        "services": {
            "database": "connected",
            "redis": "connected" if ping_redis() else "disconnected",
            "ollama": "available" if llm_status["ollama"] else "unavailable",
            "groq": "available" if llm_status["groq"] else "unavailable"
        }
    }


@router.get("/metrics")
async def get_metrics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get system metrics and statistics.
    """
    # Task statistics
    total_tasks = db.query(Task).count()
    completed_tasks = db.query(Task).filter(Task.status == TaskStatus.COMPLETED.value).count()
    failed_tasks = db.query(Task).filter(Task.status == TaskStatus.FAILED.value).count()
    in_progress_tasks = db.query(Task).filter(Task.status == TaskStatus.IN_PROGRESS.value).count()
    
    # Queue statistics
    queue_size = task_queue.get_queue_size()
    processing_count = task_queue.get_processing_count()
    dead_letter_count = task_queue.get_dead_letter_count()
    
    # Agent statistics
    active_agents = db.query(Agent).filter(Agent.is_active == True).count()
    
    # Calculate success rate
    success_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    
    return {
        "tasks": {
            "total": total_tasks,
            "completed": completed_tasks,
            "failed": failed_tasks,
            "in_progress": in_progress_tasks,
            "success_rate_percent": round(success_rate, 1)
        },
        "queue": {
            "size": queue_size,
            "processing": processing_count,
            "dead_letter": dead_letter_count
        },
        "agents": {
            "active": active_agents
        }
    }


@router.get("/logs")
async def get_logs(
    lines: int = 100,
    level: str = None,
    current_user: User = Depends(get_current_user)
):
    """
    Get recent log entries.
    
    Args:
        lines: Number of lines to return (max 500)
        level: Filter by log level (INFO, ERROR, etc.)
    """
    lines = min(lines, 500)  # Cap at 500
    
    log_lines = read_recent_logs(lines=lines)
    
    # Filter by level if specified
    if level:
        level_upper = level.upper()
        log_lines = [l for l in log_lines if f"| {level_upper}" in l]
    
    return {
        "count": len(log_lines),
        "logs": log_lines
    }


@router.get("/llm/status")
async def get_llm_status(
    current_user: User = Depends(get_current_user)
):
    """
    Get detailed LLM provider status.
    """
    provider_status = llm_manager.get_provider_status()
    available_models = llm_manager.list_available_models()
    
    return {
        "providers": {
            "ollama": {
                "available": provider_status["ollama"],
                "models": available_models["ollama"]
            },
            "groq": {
                "available": provider_status["groq"],
                "models": available_models["groq"]
            }
        }
    }


@router.post("/cache/clear")
async def clear_cache(
    current_user: User = Depends(get_current_user)
):
    """
    Clear all LLM response caches.
    """
    success = llm_manager.clear_cache()
    
    if success:
        return {"message": "Cache cleared successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to clear cache"
        )


@router.post("/queue/clear")
async def clear_queue(
    current_user: User = Depends(get_current_user)
):
    """
    Clear all queues (WARNING: This will remove all pending tasks!).
    """
    success = task_queue.clear_all()
    
    if success:
        return {"message": "All queues cleared"}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to clear queues"
        )
