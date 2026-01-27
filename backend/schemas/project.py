"""
Nexus AI - Project Schemas
Pydantic models for project-related requests and responses
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


class ProjectCreate(BaseModel):
    """Schema for creating a new project"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None


class ProjectUpdate(BaseModel):
    """Schema for updating a project"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None


class ProjectResponse(BaseModel):
    """Schema for project response"""
    id: int
    user_id: int
    name: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ProjectWithTaskCountResponse(ProjectResponse):
    """Schema for project response with task count"""
    task_count: int = 0
