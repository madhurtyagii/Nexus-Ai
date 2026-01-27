"""
Nexus AI - Agent Schemas
Pydantic models for agent-related responses
"""

from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class AgentResponse(BaseModel):
    """Schema for agent response"""
    id: int
    name: str
    role: str
    description: Optional[str] = None
    is_active: bool
    
    class Config:
        from_attributes = True


class AgentDetailResponse(AgentResponse):
    """Schema for detailed agent response with tools and prompt"""
    system_prompt: Optional[str] = None
    available_tools: List[str] = []
    created_at: datetime


class AgentMessageResponse(BaseModel):
    """Schema for agent message response"""
    id: int
    task_id: int
    sender_agent: str
    receiver_agent: Optional[str] = None
    message_content: str
    timestamp: datetime
    
    class Config:
        from_attributes = True
