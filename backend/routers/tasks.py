"""Nexus AI - Tasks Router.

This module provides API endpoints for managing tasks, including creation, 
listing, status tracking, and background orchestrator integration.
"""

import asyncio
from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional

from database import get_db
from models.user import User
from models.task import Task, Subtask, TaskStatus
from schemas.task import TaskCreate, TaskResponse, TaskWithSubtasksResponse
from dependencies import get_current_user
from services.task_service import TaskService
from orchestrator.queue import task_queue
from cache.redis_cache import cached
from utils.audit import audit_log

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post(
    "/", 
    response_model=TaskResponse, 
    status_code=status.HTTP_201_CREATED,
    summary="Create a new AI task",
    description="Submits a natural language prompt to the AI orchestrator. The task is queued and processed in the background."
)
async def create_task(
    task_data: TaskCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new task and start processing in background.
    
    - Creates task with status 'queued'
    - Starts orchestrator processing asynchronously
    - Returns immediately (non-blocking)
    """
    service = TaskService(db)
    
    # Create task
    new_task = service.create_task(
        user_id=current_user.id,
        user_prompt=task_data.user_prompt,
        project_id=task_data.project_id
    )
    
    # Track user prompt in memory system
    try:
        from memory.conversation_tracker import get_conversation_tracker
        tracker = get_conversation_tracker()
        tracker.track_user_message(
            user_id=current_user.id,
            task_id=new_task.id,
            message=task_data.user_prompt
        )
    except Exception as e:
        # Memory tracking is optional, don't fail the request
        pass
    
    # Process in background (non-blocking)
    background_tasks.add_task(service.process_task, new_task.id)
    
    return new_task


@router.get(
    "/", 
    response_model=List[TaskResponse],
    summary="List user tasks",
    description="Retrieves a paginated list of tasks belong to the authenticated user, optionally filtered by status."
)
async def list_tasks(
    task_status: Optional[str] = Query(None, alias="status", description="Filter by status"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all tasks for the current user.
    """
    return await _list_tasks_internal(task_status, limit, offset, db, current_user.id)

@cached(ttl=60, key_prefix="tasks_list")
async def _list_tasks_internal(task_status, limit, offset, db, user_id):
    query = db.query(Task).filter(Task.user_id == user_id)
    
    if task_status:
        query = query.filter(Task.status == task_status)
    
    tasks = query.order_by(Task.created_at.desc()).offset(offset).limit(limit).all()
    
    return tasks


@router.get(
    "/queue",
    summary="Get queue status",
    description="Returns global and user-specific queue statistics, including pending and active task counts."
)
async def get_queue_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get current queue status and statistics.
    """
    service = TaskService(db)
    
    # Get user's task counts
    total_tasks = db.query(Task).filter(Task.user_id == current_user.id).count()
    completed_tasks = db.query(Task).filter(
        Task.user_id == current_user.id,
        Task.status == TaskStatus.COMPLETED.value
    ).count()
    
    queue_stats = service.get_queue_stats()
    
    return {
        **queue_stats,
        "user_total_tasks": total_tasks,
        "user_completed_tasks": completed_tasks
    }


@router.get(
    "/{task_id}", 
    response_model=TaskWithSubtasksResponse,
    summary="Get task details",
    description="Retrieves full information for a specific task, including all associated agent subtasks."
)
async def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await _get_task_internal(task_id, db, current_user.id)

@cached(ttl=300, key_prefix="task_detail")
async def _get_task_internal(task_id, db, user_id):
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.user_id == user_id
    ).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    return task


@router.get("/{task_id}/status")
async def get_task_status(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get detailed progress of a task.
    """
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.user_id == current_user.id
    ).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    service = TaskService(db)
    return service.get_task_progress(task_id)


@router.get("/{task_id}/subtasks")
async def get_task_subtasks(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all subtasks for a task.
    """
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.user_id == current_user.id
    ).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    service = TaskService(db)
    return service.get_subtasks(task_id)


@router.post("/{task_id}/retry")
async def retry_task(
    task_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retry a failed task.
    """
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.user_id == current_user.id
    ).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    service = TaskService(db)
    
    # Process retry in background
    background_tasks.add_task(service.retry_task, task_id)
    
    return {"message": "Task queued for retry", "task_id": task_id}


@router.post("/{task_id}/cancel")
async def cancel_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Cancel a running task.
    """
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.user_id == current_user.id
    ).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    service = TaskService(db)
    success = service.cancel_task(task_id)
    
    if success:
        return {"message": "Task cancelled", "task_id": task_id}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to cancel task"
        )


@router.delete("/{task_id}")
@audit_log("task_delete")
async def delete_task_router(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a task by ID.
    
    - Verifies ownership
    - Cascades delete to subtasks
    """
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.user_id == current_user.id
    ).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    db.delete(task)
    db.commit()
    
    return {"message": "Task deleted successfully"}
