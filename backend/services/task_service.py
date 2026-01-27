"""
Nexus AI - Task Service
Business logic for task management separated from routes
"""

import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
from sqlalchemy.orm import Session

from models.task import Task, Subtask, TaskStatus
from orchestrator.core import OrchestratorEngine
from orchestrator.queue import task_queue


class TaskService:
    """
    Service layer for task management.
    Handles creation, processing, progress tracking, and cancellation.
    """
    
    def __init__(self, db: Session):
        """Initialize with database session."""
        self.db = db
    
    def create_task(
        self, 
        user_id: int, 
        user_prompt: str, 
        project_id: int = None
    ) -> Task:
        """
        Create a new task record.
        
        Args:
            user_id: Owner user ID
            user_prompt: Task description
            project_id: Optional project ID
            
        Returns:
            Created Task object
        """
        task = Task(
            user_id=user_id,
            user_prompt=user_prompt,
            project_id=project_id,
            status=TaskStatus.QUEUED.value
        )
        
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        
        return task
    
    def process_task(self, task_id: int) -> Dict[str, Any]:
        """
        Process a task using the orchestrator.
        
        This is the synchronous version - for background processing,
        use process_task_async.
        
        Args:
            task_id: Task ID to process
            
        Returns:
            Execution summary
        """
        orchestrator = OrchestratorEngine(self.db)
        return orchestrator.execute_task(task_id)
    
    async def process_task_async(self, task_id: int) -> Dict[str, Any]:
        """
        Process a task asynchronously in background.
        
        Args:
            task_id: Task ID to process
            
        Returns:
            Execution summary
        """
        try:
            # Run orchestrator in thread pool to not block event loop
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, 
                self.process_task, 
                task_id
            )
            return result
        except Exception as e:
            # Update task status to failed
            task = self.db.query(Task).filter(Task.id == task_id).first()
            if task:
                task.status = TaskStatus.FAILED.value
                task.output = f"Error: {str(e)}"
                self.db.commit()
            
            return {"error": str(e), "task_id": task_id}
    
    def get_task_progress(self, task_id: int) -> Dict[str, Any]:
        """
        Get current progress of a task.
        
        Args:
            task_id: Task ID
            
        Returns:
            Progress dictionary
        """
        task = self.db.query(Task).filter(Task.id == task_id).first()
        if not task:
            return {"error": "Task not found"}
        
        subtasks = self.db.query(Subtask).filter(Subtask.task_id == task_id).all()
        
        total = len(subtasks)
        completed = len([s for s in subtasks if s.status == TaskStatus.COMPLETED.value])
        in_progress = len([s for s in subtasks if s.status == TaskStatus.IN_PROGRESS.value])
        failed = len([s for s in subtasks if s.status == TaskStatus.FAILED.value])
        
        progress = (completed / total * 100) if total > 0 else 0
        
        # Find current active agent
        current_agent = None
        for s in subtasks:
            if s.status == TaskStatus.IN_PROGRESS.value:
                current_agent = s.assigned_agent
                break
        
        # Estimate remaining time
        if total > 0 and completed < total:
            remaining_steps = total - completed
            estimated_remaining = remaining_steps * 30  # ~30s per step
        else:
            estimated_remaining = 0
        
        return {
            "task_id": task_id,
            "status": task.status,
            "progress_percentage": round(progress, 1),
            "current_agent": current_agent,
            "subtasks_completed": completed,
            "subtasks_in_progress": in_progress,
            "subtasks_failed": failed,
            "subtasks_total": total,
            "estimated_time_remaining": estimated_remaining,
            "output": task.output
        }
    
    def get_subtasks(self, task_id: int) -> List[Dict[str, Any]]:
        """
        Get all subtasks for a task.
        
        Args:
            task_id: Task ID
            
        Returns:
            List of subtask dictionaries
        """
        subtasks = self.db.query(Subtask).filter(Subtask.task_id == task_id).all()
        
        return [
            {
                "id": s.id,
                "assigned_agent": s.assigned_agent,
                "status": s.status,
                "input_data": s.input_data,
                "output_data": s.output_data,
                "error_message": s.error_message,
                "created_at": s.created_at.isoformat() if s.created_at else None,
                "completed_at": s.completed_at.isoformat() if s.completed_at else None
            }
            for s in subtasks
        ]
    
    def cancel_task(self, task_id: int) -> bool:
        """
        Cancel a task and its pending subtasks.
        
        Args:
            task_id: Task ID to cancel
            
        Returns:
            True if cancelled successfully
        """
        task = self.db.query(Task).filter(Task.id == task_id).first()
        if not task:
            return False
        
        # Update task status
        task.status = "cancelled"
        
        # Cancel pending subtasks
        pending_subtasks = self.db.query(Subtask).filter(
            Subtask.task_id == task_id,
            Subtask.status.in_([TaskStatus.QUEUED.value, TaskStatus.IN_PROGRESS.value])
        ).all()
        
        for subtask in pending_subtasks:
            subtask.status = "cancelled"
        
        self.db.commit()
        return True
    
    def retry_task(self, task_id: int) -> Dict[str, Any]:
        """
        Retry a failed task.
        
        Args:
            task_id: Task ID to retry
            
        Returns:
            Execution summary
        """
        task = self.db.query(Task).filter(Task.id == task_id).first()
        if not task:
            return {"error": "Task not found"}
        
        # Reset task status
        task.status = TaskStatus.QUEUED.value
        task.output = None
        task.completed_at = None
        
        # Delete old subtasks
        self.db.query(Subtask).filter(Subtask.task_id == task_id).delete()
        self.db.commit()
        
        # Process again
        return self.process_task(task_id)
    
    def get_queue_stats(self) -> Dict[str, Any]:
        """
        Get queue statistics.
        
        Returns:
            Queue status dictionary
        """
        return {
            "queue_size": task_queue.get_queue_size(),
            "processing_count": task_queue.get_processing_count(),
            "dead_letter_count": task_queue.get_dead_letter_count()
        }
