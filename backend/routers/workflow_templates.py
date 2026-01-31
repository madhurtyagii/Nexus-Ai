"""
Nexus AI - Workflow Templates Router
API endpoints for managing and retrieving project templates
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from database import get_db
from models.workflow_template import WorkflowTemplate
from dependencies import get_current_user
from models.user import User

router = APIRouter(prefix="/workflow-templates", tags=["Templates"])

@router.get("/", response_model=List[dict])
async def list_templates(
    category: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all available workflow templates.
    """
    query = db.query(WorkflowTemplate)
    if category:
        query = query.filter(WorkflowTemplate.category == category)
    
    templates = query.order_by(WorkflowTemplate.category, WorkflowTemplate.name).all()
    return [template.to_dict() for template in templates]

@router.get("/{template_id}", response_model=dict)
async def get_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get detailed information about a specific template.
    """
    template = db.query(WorkflowTemplate).filter(WorkflowTemplate.id == template_id).first()
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Template with ID {template_id} not found"
        )
    
    return template.to_dict()
