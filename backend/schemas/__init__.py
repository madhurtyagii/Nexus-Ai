"""
Nexus AI - Schemas Package
Export all Pydantic schemas
"""

from schemas.user import UserCreate, UserLogin, UserResponse, Token, TokenData
from schemas.task import TaskCreate, TaskUpdate, TaskResponse, TaskWithSubtasksResponse, SubtaskResponse
from schemas.agent import AgentResponse, AgentDetailResponse, AgentMessageResponse
from schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse, ProjectWithTaskCountResponse

__all__ = [
    # User schemas
    "UserCreate",
    "UserLogin", 
    "UserResponse",
    "Token",
    "TokenData",
    # Task schemas
    "TaskCreate",
    "TaskUpdate",
    "TaskResponse",
    "TaskWithSubtasksResponse",
    "SubtaskResponse",
    # Agent schemas
    "AgentResponse",
    "AgentDetailResponse",
    "AgentMessageResponse",
    # Project schemas
    "ProjectCreate",
    "ProjectUpdate",
    "ProjectResponse",
    "ProjectWithTaskCountResponse",
]
