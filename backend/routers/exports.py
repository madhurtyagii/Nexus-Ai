"""
Nexus AI - Exports Router
API endpoints for exporting project data
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Response
from sqlalchemy.orm import Session
import io
from typing import Optional

from database import get_db
from models.project import Project
from dependencies import get_current_user
from models.user import User
from services.export_service import ExportService
from routers.projects import _project_to_detail

router = APIRouter(prefix="/exports", tags=["Exports"])

@router.get("/project/{project_id}")
async def export_project(
    project_id: int,
    format: str = Query("markdown", regex="^(markdown|pdf|json|docx)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Export project data in the specified format.
    """
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Get project data as dict (reusing project router helper)
    # We need a proper dict, _project_to_detail returns ProjectDetail schema
    project_data = {
        "id": project.id,
        "name": project.name,
        "description": project.description,
        "status": project.status or "planning",
        "progress": project.progress_percentage,
        "total_tasks": project.total_tasks or 0,
        "completed_tasks": project.completed_tasks or 0,
        "total_phases": project.total_phases or 0,
        "current_phase": project.current_phase or 0,
        "estimated_minutes": project.estimated_minutes,
        "risk_level": project.risk_level,
        "project_plan": project.project_plan,
        "output": project.output,
        "summary": project.summary
    }
    
    if format == "markdown":
        content = ExportService.to_markdown(project_data)
        return Response(
            content=content,
            media_type="text/markdown",
            headers={"Content-Disposition": f"attachment; filename=project_{project_id}.md"}
        )
    
    elif format == "json":
        content = ExportService.to_json(project_data)
        return Response(
            content=content,
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename=project_{project_id}.json"}
        )
    
    elif format == "pdf":
        content = ExportService.to_pdf(project_data)
        return Response(
            content=content,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=project_{project_id}.pdf"}
        )
    
    elif format == "docx":
        content = ExportService.to_docx(project_data)
        return Response(
            content=content,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": f"attachment; filename=project_{project_id}.docx"}
        )
    
    raise HTTPException(status_code=400, detail="Invalid format")
