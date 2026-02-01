"""
Nexus AI - Agent Schemas
Pydantic models for agent-related responses
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


class AgentResponse(BaseModel):
    """Schema for agent response"""
    id: int = Field(..., example=1)
    name: str = Field(..., example="ResearcherAgent")
    role: str = Field(..., example="Researcher")
    description: Optional[str] = Field(None, example="Specializes in web research and data gathering.")
    is_active: bool = Field(..., example=True)
    
    class Config:
        from_attributes = True


class AgentDetailResponse(AgentResponse):
    """Schema for detailed agent response with tools and prompt"""
    system_prompt: Optional[str] = None
    available_tools: List[str] = []
    created_at: datetime


class AgentMessageResponse(BaseModel):
    """Schema for agent message response"""
    id: int = Field(..., example=501)
    task_id: int = Field(..., example=10)
    sender_agent: str = Field(..., example="ManagerAgent")
    receiver_agent: Optional[str] = Field(None, example="CodeAgent")
    message_content: str = Field(..., example="Please implement the authentication logic for the API.")
    timestamp: datetime
    
    class Config:
        from_attributes = True
