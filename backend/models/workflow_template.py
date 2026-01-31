"""
Nexus AI - Workflow Template Model
Database model for pre-defined project structures
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON
from sqlalchemy.sql import func
from database import Base


class WorkflowTemplate(Base):
    """
    WorkflowTemplate model for reusable project structures.
    """
    __tablename__ = "workflow_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=True, index=True)
    
    # The actual workflow structure [phases with tasks]
    # Format: [{"name": "Phase 1", "tasks": [{"description": "...", "agent": "..."}]}]
    structure = Column(JSON, nullable=False)
    
    # Metadata
    is_built_in = Column(Boolean, default=True)
    icon = Column(String(50), nullable=True)  # Emoji or icon name
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<WorkflowTemplate(id={self.id}, name='{self.name}', category='{self.category}')>"
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "structure": self.structure,
            "is_built_in": self.is_built_in,
            "icon": self.icon,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
