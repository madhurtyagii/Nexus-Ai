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
    user_prompt: str = Field(
        ..., 
        min_length=1, 
        max_length=10000,
        example="Create a Python script that analyzes the sentiment of the latest tweets about SpaceX."
    )
    project_id: Optional[int] = Field(None, example=1)


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
        json_encoders = {
            datetime: lambda v: v.isoformat() + "Z" if v else None
        }



class TaskResponse(BaseModel):
    """Schema for task response"""
    id: int = Field(..., example=1)
    user_id: int = Field(..., example=123)
    project_id: Optional[int] = Field(None, example=1)
    user_prompt: str = Field(..., example="Analyze sentiment of SpaceX tweets")
    status: str = Field(..., example="completed")
    complexity_score: Optional[float] = Field(None, example=0.85)
    created_at: datetime
    completed_at: Optional[datetime] = None
    output: Optional[str] = Field(None, example="The sentiment analysis shows a 75% positive rating...")
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() + "Z" if v else None
        }



class TaskWithSubtasksResponse(TaskResponse):
    """Schema for task response with subtasks included"""
    subtasks: List[SubtaskResponse] = []
