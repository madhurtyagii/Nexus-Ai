"""
Nexus AI - Task Models
Database models for tasks and subtasks
"""

from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum


class TaskStatus(str, enum.Enum):
    """Enum for task status"""
    QUEUED = "queued"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class Task(Base):
    """Main task model - represents a user request"""
    
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="SET NULL"), nullable=True, index=True)
    user_prompt = Column(Text, nullable=False)
    status = Column(String(20), default=TaskStatus.QUEUED.value, index=True)
    complexity_score = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    output = Column(Text, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="tasks")
    project = relationship("Project", back_populates="tasks")
    subtasks = relationship("Subtask", back_populates="task", cascade="all, delete-orphan")
    agent_messages = relationship("AgentMessage", back_populates="task", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Task(id={self.id}, status='{self.status}', user_id={self.user_id})>"


class Subtask(Base):
    """Subtask model - represents work assigned to a specific agent"""
    
    __tablename__ = "subtasks"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, index=True)
    assigned_agent = Column(String(100), nullable=False, index=True)
    input_data = Column(JSON, nullable=True)
    output_data = Column(JSON, nullable=True)
    status = Column(String(20), default=TaskStatus.QUEUED.value, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Relationships
    task = relationship("Task", back_populates="subtasks")
    
    def __repr__(self):
        return f"<Subtask(id={self.id}, agent='{self.assigned_agent}', status='{self.status}')>"
