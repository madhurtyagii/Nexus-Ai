"""Nexus AI - File Management Router.

This module provides API endpoints for securely uploading, downloading, 
listing, and deleting files associated with tasks and projects.
"""

import os
import uuid
import shutil
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from database import get_db
from models.user import User
from models.file import File as FileModel
from dependencies import get_current_user
from config import get_settings
from utils.audit import audit_log

router = APIRouter(prefix="/files", tags=["Files"])
settings = get_settings()

@router.post(
    "/upload", 
    status_code=status.HTTP_201_CREATED,
    summary="Upload a file",
    description="Uploads a file to the server and registers it in the database. Supports optional links to projects or tasks."
)
async def upload_file(
    file: UploadFile = File(...),
    project_id: Optional[int] = Query(None),
    task_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload a file and store its metadata in the database.
    """
    # Validate file size
    file.file.seek(0, os.SEEK_END)
    file_size = file.file.tell()
    file.file.seek(0)
    
    if file_size > settings.max_file_size:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Max size is {settings.max_file_size // (1024*1024)}MB"
        )
    
    # Validate file extension
    ext = os.path.splitext(file.filename)[1].lower().replace(".", "")
    allowed_exts = settings.allowed_extensions.split(",")
    if ext not in allowed_exts:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed: {settings.allowed_extensions}"
        )
    
    # Generate unique filename
    unique_filename = f"{uuid.uuid4()}.{ext}"
    file_path = os.path.join(settings.upload_dir, unique_filename)
    
    # Ensure upload directory exists
    os.makedirs(settings.upload_dir, exist_ok=True)
    
    # Save file to disk
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not save file: {str(e)}"
        )
    
    # Register file in database
    db_file = FileModel(
        user_id=current_user.id,
        project_id=project_id,
        task_id=task_id,
        filename=unique_filename,
        original_filename=file.filename,
        file_path=file_path,
        file_size=file_size,
        mime_type=file.content_type
    )
    
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    
    return db_file.to_dict()

@router.get(
    "/", 
    response_model=List[dict],
    summary="List files",
    description="Retrieves a list of files belonging to the current user, with optional filters for project and task."
)
async def list_files(
    project_id: Optional[int] = None,
    task_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all files belonging to the current user.
    Optional filtering by project_id or task_id.
    """
    query = db.query(FileModel).filter(FileModel.user_id == current_user.id)
    
    if project_id:
        query = query.filter(FileModel.project_id == project_id)
    if task_id:
        query = query.filter(FileModel.task_id == task_id)
        
    files = query.all()
    return [file.to_dict() for file in files]

@router.get("/{file_id}")
async def get_file_metadata(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get file metadata by ID.
    Verify ownership before returning.
    """
    db_file = db.query(FileModel).filter(FileModel.id == file_id).first()
    
    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")
    
    if db_file.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this file")
        
    return db_file.to_dict()

@router.get("/{file_id}/download")
async def download_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Download the actual file content.
    Verify ownership before serving.
    """
    db_file = db.query(FileModel).filter(FileModel.id == file_id).first()
    
    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")
    
    if db_file.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this file")
    
    if not os.path.exists(db_file.file_path):
        raise HTTPException(status_code=404, detail="Physical file missing on server")
        
    return FileResponse(
        path=db_file.file_path,
        filename=db_file.original_filename,
        media_type=db_file.mime_type
    )

@router.delete("/{file_id}")
@audit_log("file_delete")
async def delete_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a file from disk and database.
    """
    db_file = db.query(FileModel).filter(FileModel.id == file_id).first()
    
    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")
    
    if db_file.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this file")
    
    # Remove from disk
    if os.path.exists(db_file.file_path):
        os.remove(db_file.file_path)
    
    # Remove from database
    db.delete(db_file)
    db.commit()
    
    return {"message": f"Successfully deleted file: {db_file.original_filename}"}
