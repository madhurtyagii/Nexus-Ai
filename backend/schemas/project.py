"""
Nexus AI - Project Schemas
Pydantic models for project-related requests and responses
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


class ProjectCreate(BaseModel):
    """Schema for creating a new project"""
    name: str = Field(
        ..., 
        min_length=1, 
        max_length=255,
        example="E-commerce Platform Launch"
    )
    description: Optional[str] = Field(
        None, 
        example="A comprehensive project to design, develop, and deploy a new Shopify-based store."
    )


class ProjectUpdate(BaseModel):
    """Schema for updating a project"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None


class ProjectResponse(BaseModel):
    """Schema for project response"""
    id: int = Field(..., example=1)
    user_id: int = Field(..., example=123)
    name: str = Field(..., example="E-commerce Platform Launch")
    description: Optional[str] = Field(None, example="Designing and deploying a new store")
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() + "Z" if v else None
        }


class ProjectWithTaskCountResponse(ProjectResponse):
    """Schema for project response with task count"""
    task_count: int = 0
