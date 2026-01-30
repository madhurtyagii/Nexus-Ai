"""
Nexus AI - Project Schemas
Pydantic schemas for project management API
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class ProjectStatus(str, Enum):
    """Project status enum."""
    PLANNING = "planning"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ProjectCreate(BaseModel):
    """Schema for creating a new project."""
    name: str = Field(..., min_length=1, max_length=255, description="Project name")
    description: Optional[str] = Field(None, description="Project description")
    complexity: Optional[str] = Field(None, description="Complexity level: auto, low, medium, high")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "AI-Powered Blog",
                "description": "Create a complete blog post about AI agents with research and images",
                "complexity": "auto"
            }
        }


class ProjectUpdate(BaseModel):
    """Schema for updating a project."""
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    status: Optional[ProjectStatus] = None


class TaskSummary(BaseModel):
    """Summary of a task within a project."""
    task_id: str
    description: str
    assigned_agent: str
    status: str
    dependencies: List[str] = []
    output_preview: Optional[str] = None


class PhaseSummary(BaseModel):
    """Summary of a project phase."""
    phase_number: int
    phase_name: str
    tasks: List[TaskSummary]
    status: str
    progress: float


class ProjectResponse(BaseModel):
    """Schema for project response."""
    id: int
    name: str
    description: Optional[str]
    status: str
    progress: float
    total_tasks: int
    completed_tasks: int
    total_phases: int
    current_phase: int
    estimated_minutes: Optional[int]
    risk_level: Optional[str]
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class ProjectDetail(ProjectResponse):
    """Detailed project response with plan and tasks."""
    project_plan: Optional[List[Any]] = None  # List of phases, not Dict!
    workflow: Optional[Dict[str, Any]] = None
    phases: Optional[List[PhaseSummary]] = None
    output: Optional[str] = None
    summary: Optional[str] = None


class ProjectProgress(BaseModel):
    """Real-time project progress."""
    project_id: int
    status: str
    progress_percentage: float
    total_tasks: int
    completed_tasks: int
    in_progress_tasks: int
    failed_tasks: int
    current_phase: int
    active_agents: List[str] = []
    estimated_remaining_minutes: Optional[int]


class ProjectExecuteRequest(BaseModel):
    """Request to start project execution."""
    add_qa_checkpoints: bool = Field(True, description="Add QA checkpoints to workflow")


class ProjectExecuteResponse(BaseModel):
    """Response after starting project execution."""
    project_id: int
    execution_id: str
    status: str
    message: str


class ProjectPlanResponse(BaseModel):
    """Response with project plan from ManagerAgent."""
    project_id: int
    project_name: str
    phases: List[Dict[str, Any]]
    total_tasks: int
    estimated_duration: str
    estimated_minutes: int
    risk_level: str
    dependency_graph: Optional[Dict[str, Any]]
