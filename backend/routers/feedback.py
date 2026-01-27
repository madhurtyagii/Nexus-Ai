"""
Nexus AI - Feedback Router
API endpoints for task feedback and preference learning
"""

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from typing import Dict, Optional

from database import get_db
from models.user import User
from models.task import Task
from dependencies import get_current_user
from memory.preference_learner import get_preference_learner
from logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/tasks", tags=["Feedback"])


# Pydantic models
class FeedbackCreate(BaseModel):
    rating: int = Field(..., ge=1, le=5, description="Rating from 1-5")
    feedback: Optional[str] = Field(None, description="Optional text feedback")
    aspects: Optional[Dict[str, bool]] = Field(
        None, 
        description="Aspects liked/disliked, e.g. {'accuracy': true, 'speed': false}"
    )


class FeedbackResponse(BaseModel):
    task_id: int
    rating: int
    feedback: Optional[str]
    learned_preferences: Dict


@router.post("/{task_id}/feedback", response_model=FeedbackResponse)
async def submit_feedback(
    task_id: int,
    feedback_data: FeedbackCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Submit feedback for a completed task.
    
    - Rating: 1-5 stars
    - Feedback: Optional text feedback
    - Aspects: Optional dict of liked/disliked aspects
    
    This helps the system learn your preferences.
    """
    # Get task
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.user_id == current_user.id
    ).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Update task with feedback (if columns exist)
    try:
        task.user_rating = feedback_data.rating
        task.user_feedback = feedback_data.feedback
        task.feedback_timestamp = datetime.utcnow()
        db.commit()
    except Exception as e:
        logger.warning(f"Could not save feedback to task: {e}")
        # Continue anyway - we'll still learn from the feedback
    
    # Learn from feedback
    learner = get_preference_learner()
    
    learned = learner.learn_from_feedback(
        user_id=current_user.id,
        task_id=task_id,
        feedback={
            "rating": feedback_data.rating,
            "feedback": feedback_data.feedback or "",
            "aspects": feedback_data.aspects or {}
        }
    )
    
    logger.info(f"Feedback received for task {task_id}: rating={feedback_data.rating}")
    
    return FeedbackResponse(
        task_id=task_id,
        rating=feedback_data.rating,
        feedback=feedback_data.feedback,
        learned_preferences=learned
    )


@router.get("/{task_id}/feedback")
async def get_task_feedback(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get feedback for a specific task.
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
    
    # Try to get feedback from task
    rating = getattr(task, 'user_rating', None)
    feedback = getattr(task, 'user_feedback', None)
    timestamp = getattr(task, 'feedback_timestamp', None)
    
    if rating is None:
        return {
            "task_id": task_id,
            "has_feedback": False,
            "message": "No feedback submitted for this task"
        }
    
    return {
        "task_id": task_id,
        "has_feedback": True,
        "rating": rating,
        "feedback": feedback,
        "submitted_at": timestamp.isoformat() if timestamp else None
    }
