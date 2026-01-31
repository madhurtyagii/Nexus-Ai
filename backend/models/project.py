"""
Nexus AI - Project Model
Database model for projects with workflow management (Phase 6)
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class Project(Base):
    """
    Project model for complex multi-phase projects.
    
    Projects can contain multiple tasks organized by phases.
    Managed by the ManagerAgent.
    """
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Project info
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Status: planning, in_progress, completed, failed, cancelled
    status = Column(String(50), default="planning", index=True)
    
    # Project plan (JSON from ManagerAgent)
    project_plan = Column(JSON, nullable=True)
    
    # Workflow definition
    workflow = Column(JSON, nullable=True)
    
    # Agent that created/manages this project
    created_by_agent = Column(String(100), default="ManagerAgent")
    
    # Metrics
    total_tasks = Column(Integer, default=0)
    completed_tasks = Column(Integer, default=0)
    total_phases = Column(Integer, default=0)
    current_phase = Column(Integer, default=0)
    
    # Estimates
    estimated_minutes = Column(Integer, nullable=True)
    actual_minutes = Column(Integer, nullable=True)
    
    # Risk assessment
    risk_level = Column(String(20), nullable=True)  # low, medium, high
    complexity_score = Column(Float, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Metadata & Organization
    is_archived = Column(Integer, default=0) # 0=active, 1=archived
    is_pinned = Column(Integer, default=0) # 0=normal, 1=pinned
    tags = Column(JSON, nullable=True, default=[])

    # Final output/summary
    output = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="projects")
    tasks = relationship("Task", back_populates="project", cascade="all, delete-orphan")
    files = relationship("File", back_populates="project")
    
    def __repr__(self):
        return f"<Project(id={self.id}, name='{self.name}', status='{self.status}')>"
    
    @property
    def progress_percentage(self):
        """Calculate progress as percentage."""
        if self.total_tasks == 0:
            return 0
        return round((self.completed_tasks / self.total_tasks) * 100, 1)
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "description": self.description,
            "status": self.status,
            "project_plan": self.project_plan,
            "total_tasks": self.total_tasks,
            "completed_tasks": self.completed_tasks,
            "progress": self.progress_percentage,
            "total_phases": self.total_phases,
            "current_phase": self.current_phase,
            "estimated_minutes": self.estimated_minutes,
            "risk_level": self.risk_level,
            "is_archived": bool(self.is_archived),
            "is_pinned": bool(self.is_pinned),
            "tags": self.tags or [],
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }
