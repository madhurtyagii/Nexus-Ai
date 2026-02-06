"""Nexus AI - User Model.

This module defines the User model for authentication, profile management, 
and establishing relationships with tasks, projects, and files.
"""

from __future__ import annotations
from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON

from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class User(Base):
    """Represents a registered user in the Nexus AI system.
    
    The User model stores authentication credentials and profile information. 
    It serves as the parent for most other user-generated content like 
    Tasks and Projects.
    
    Attributes:
        id: Primary key identifier.
        email: Unique user email address.
        username: Unique display name.
        hashed_password: Argon2 or BCrypt hashed credential.
        is_active: Flag for account status.
        created_at: Database timestamp of registration.
    """
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    settings = Column(JSON, default=lambda: {})
    
    # Relationships
    tasks = relationship("Task", back_populates="user", cascade="all, delete-orphan")
    projects = relationship("Project", back_populates="user", cascade="all, delete-orphan")
    files = relationship("File", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"
