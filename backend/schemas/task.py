"""
Nexus AI - Task Schemas
Pydantic models for task-related requests and responses
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from models.task import TaskStatus


class TaskCreate(BaseModel):
    """Schema for creating a new task"""
    user_prompt: str = Field(..., min_length=1, max_length=10000)
    project_id: Optional[int] = None


class TaskUpdate(BaseModel):
    """Schema for updating a task"""
    status: Optional[str] = None
    output: Optional[str] = None


class SubtaskResponse(BaseModel):
    """Schema for subtask response"""
    id: int
    task_id: int
    assigned_agent: str
    status: str
    input_data: Optional[dict] = None
    output_data: Optional[dict] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    
    class Config:
        from_attributes = True


class TaskResponse(BaseModel):
    """Schema for task response"""
    id: int
    user_id: int
    project_id: Optional[int] = None
    user_prompt: str
    status: str
    complexity_score: Optional[float] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    output: Optional[str] = None
    
    class Config:
        from_attributes = True


class TaskWithSubtasksResponse(TaskResponse):
    """Schema for task response with subtasks included"""
    subtasks: List[SubtaskResponse] = []
