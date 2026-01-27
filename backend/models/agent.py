"""
Nexus AI - Agent Models
Database models for AI agents and their messages
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class Agent(Base):
    """Agent model - represents an AI agent definition"""
    
    __tablename__ = "agents"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    role = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    system_prompt = Column(Text, nullable=True)
    available_tools = Column(JSON, default=list)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<Agent(id={self.id}, name='{self.name}', role='{self.role}')>"


class AgentMessage(Base):
    """AgentMessage model - logs inter-agent communication"""
    
    __tablename__ = "agent_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, index=True)
    sender_agent = Column(String(100), nullable=False, index=True)
    receiver_agent = Column(String(100), nullable=True)
    message_content = Column(Text, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    task = relationship("Task", back_populates="agent_messages")
    
    def __repr__(self):
        return f"<AgentMessage(id={self.id}, from='{self.sender_agent}', to='{self.receiver_agent}')>"
