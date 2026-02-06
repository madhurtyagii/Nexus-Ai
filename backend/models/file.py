"""
Nexus AI - File Model
Database model for tracking user uploads and agent-generated files
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, BigInteger
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class File(Base):
    """
    File model for tracking metadata of uploaded and generated files.
    """
    __tablename__ = "files"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="SET NULL"), nullable=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id", ondelete="SET NULL"), nullable=True, index=True)
    
    filename = Column(String(255), nullable=False)  # Unique/Stored filename
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=False)
    file_size = Column(BigInteger, nullable=False)  # Size in bytes
    mime_type = Column(String(100), nullable=True)
    
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="files")
    project = relationship("Project", back_populates="files")
    task = relationship("Task", back_populates="files") # Note: Need to add relationship to Task model too

    def __repr__(self):
        return f"<File(id={self.id}, filename='{self.original_filename}', user_id={self.user_id})>"

    def to_dict(self):
        """Convert to dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "project_id": self.project_id,
            "task_id": self.task_id,
            "filename": self.original_filename, # Use original name for UI display
            "stored_filename": self.filename,
            "size": self.file_size, # Frontend expects 'size'
            "file_size": self.file_size,
            "mime_type": self.mime_type,
            "uploaded_at": self.uploaded_at.isoformat() if self.uploaded_at else None,
            "created_at": self.uploaded_at.isoformat() if self.uploaded_at else None # Frontend expects 'created_at'
        }
