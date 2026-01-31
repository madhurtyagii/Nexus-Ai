"""
Nexus AI - Projects Router (Phase 6)
Project management with ManagerAgent integration and workflow execution
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime
import uuid

from database import get_db
from models.user import User
from models.project import Project
from models.task import Task
from models.workflow_template import WorkflowTemplate
from schemas.project_schemas import (
    ProjectCreate, ProjectUpdate, ProjectResponse, ProjectDetail,
    ProjectProgress, ProjectExecuteRequest, ProjectExecuteResponse,
    ProjectPlanResponse
)
from dependencies import get_current_user

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.post("/", status_code=status.HTTP_201_CREATED)  # Returns dict directly for reliability
async def create_project(
    project_data: ProjectCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new project.
    
    Project is created immediately with a default plan.
    AI-powered planning runs in the background and updates the project.
    """
    try:
        print(f"📝 Creating project: {project_data.name} for user {current_user.id}")
        
        # Handle Workflow Template if provided
        template_id = project_data.template_id
        if template_id:
            template = db.query(WorkflowTemplate).filter(WorkflowTemplate.id == template_id).first()
            if template:
                print(f"📋 Using template: {template.name}")
                project_plan = []
                total_tasks = 0
                
                # Convert template structure to project plan format
                for i, phase in enumerate(template.structure):
                    phase_tasks = []
                    for j, task_data in enumerate(phase.get("tasks", [])):
                        task_id = f"{i+1}.{j+1}"
                        total_tasks += 1
                        phase_tasks.append({
                            "task_id": task_id,
                            "description": task_data["description"],
                            "assigned_agent": task_data["agent"],
                            "estimated_time": "10 minutes",
                            "status": "pending"
                        })
                    
                    project_plan.append({
                        "phase_number": i + 1,
                        "phase_name": phase["name"],
                        "tasks": phase_tasks
                    })
                
                # Update initial project values
                new_project = Project(
                    user_id=current_user.id,
                    name=project_data.name,
                    description=project_data.description or template.description,
                    status="planning",
                    project_plan=project_plan,
                    workflow={"type": "sequential", "phases": project_plan},
                    total_phases=len(project_plan),
                    total_tasks=total_tasks,
                    estimated_minutes=total_tasks * 10,
                    risk_level="low",
                    complexity_score=3.0
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Template with ID {template_id} not found"
                )
        else:
            # Create default plan structure
            default_plan = [
                {
                    "phase_number": 1,
                    "phase_name": "Planning & Analysis",
                    "tasks": [
                        {
                            "task_id": "1.1",
                            "description": "Analyze project requirements",
                            "assigned_agent": "ManagerAgent",
                            "estimated_time": "5 minutes",
                            "status": "pending"
                        }
                    ]
                },
                {
                    "phase_number": 2,
                    "phase_name": "Execution",
                    "tasks": [
                        {
                            "task_id": "2.1",
                            "description": "Execute main task",
                            "assigned_agent": "ContentAgent",
                            "estimated_time": "15 minutes",
                            "status": "pending"
                        }
                    ]
                },
                {
                    "phase_number": 3,
                    "phase_name": "Review & Delivery",
                    "tasks": [
                        {
                            "task_id": "3.1",
                            "description": "Quality review",
                            "assigned_agent": "QAAgent",
                            "estimated_time": "5 minutes",
                            "status": "pending"
                        }
                    ]
                }
            ]
            
            # Create project record IMMEDIATELY
            new_project = Project(
                user_id=current_user.id,
                name=project_data.name,
                description=project_data.description,
                status="planning",
                project_plan=default_plan,
                workflow={"type": "sequential"},
                total_phases=3,
                total_tasks=3,
                estimated_minutes=25,
                risk_level="low",
                complexity_score=3.0
            )
        
        db.add(new_project)
        db.commit()
        db.refresh(new_project)
        
        print(f"✅ Project {new_project.id} created instantly: {new_project.name}")
        
        # Only run AI planning if NOT using a template and complexity is high/auto
        if not template_id:
            complexity = project_data.complexity or "auto"
            if complexity in ["auto", "high", "medium"]:
                background_tasks.add_task(
                    _run_ai_planning,
                    new_project.id,
                    project_data.description or project_data.name,
                    current_user.id
                )
                print(f"AI planning scheduled in background for project {new_project.id}")
        
        # Return dict directly (avoids Pydantic response_model validation issues)
        print(f"Project {new_project.id} created successfully: {new_project.name}")
        return {
            "id": new_project.id,
            "name": new_project.name,
            "description": new_project.description,
            "status": new_project.status,
            "progress": 0,
            "total_tasks": new_project.total_tasks,
            "completed_tasks": new_project.completed_tasks,
            "total_phases": new_project.total_phases,
            "current_phase": new_project.current_phase,
            "estimated_minutes": new_project.estimated_minutes,
            "risk_level": new_project.risk_level,
            "created_at": new_project.created_at.isoformat() if new_project.created_at else None,
            "started_at": None,
            "completed_at": None,
            "project_plan": new_project.project_plan,
            "workflow": new_project.workflow,
        }
        
    except Exception as e:
        import traceback
        print(f"ERROR in create_project: {str(e)}")
        traceback.print_exc()
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create project: {str(e)}"
        )


def _run_ai_planning(project_id: int, description: str, user_id: int):
    """Background task to run AI planning and update project."""
    from database import SessionLocal
    
    db = SessionLocal()
    try:
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            print(f"❌ Background planning: Project {project_id} not found")
            return
        
        print(f"🤖 Starting AI planning for project {project_id}...")
        
        from agents.manager_agent import ManagerAgent
        manager = ManagerAgent()
        plan_result = manager.execute({
            "project_description": description,
            "user_id": user_id
        })
        
        # Update project with AI-generated plan
        if plan_result and plan_result.get("phases"):
            project.project_plan = plan_result.get("phases", [])
            project.workflow = plan_result.get("workflow", {})
            project.total_phases = len(plan_result.get("phases", []))
            
            # Calculate total tasks reliably from phases
            total_tasks = 0
            for phase in plan_result.get("phases", []):
                total_tasks += len(phase.get("tasks", []))
            project.total_tasks = total_tasks
            project.estimated_minutes = plan_result.get("estimated_minutes", 30)
            project.risk_level = plan_result.get("risk_assessment", {}).get("risk_level", "medium")
            project.complexity_score = plan_result.get("analysis", {}).get("complexity", 5)
            db.commit()
            print(f"✅ AI planning complete for project {project_id}")
        else:
            print(f"⚠️ AI planning returned empty result for project {project_id}")
            
    except Exception as e:
        print(f"❌ AI planning failed for project {project_id}: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


@router.get("/", response_model=List[ProjectResponse])
async def list_projects(
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    q: Optional[str] = Query(None, description="Search query"),
    tags: Optional[str] = Query(None, description="Comma-separated tags"),
    is_archived: bool = Query(False, description="Show archived projects"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List projects for the user with search and filtering.
    """
    query = db.query(Project).filter(Project.user_id == current_user.id)
    
    # Filter by archived status
    query = query.filter(Project.is_archived == (1 if is_archived else 0))
    
    if status_filter:
        query = query.filter(Project.status == status_filter)
        
    if q:
        query = query.filter(
            (Project.name.ilike(f"%{q}%")) | 
            (Project.description.ilike(f"%{q}%"))
        )
        
    if tags:
        tag_list = [t.strip() for t in tags.split(",") if t.strip()]
        for tag in tag_list:
            # Simple check for tags in JSON array
            query = query.filter(Project.tags.contains([tag]))
            
    # Order by pinned first, then newest
    projects = query.order_by(Project.is_pinned.desc(), Project.created_at.desc()) \
                    .offset(offset).limit(limit).all()
    
    return [_project_to_response(p) for p in projects]


@router.patch("/{project_id}/archive", response_model=ProjectResponse)
async def archive_project(
    project_id: int,
    archive: bool = Query(True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Archive or unarchive a project."""
    project = db.query(Project).filter(Project.id == project_id, Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project.is_archived = 1 if archive else 0
    db.commit()
    db.refresh(project)
    return _project_to_response(project)


@router.patch("/{project_id}/pin", response_model=ProjectResponse)
async def pin_project(
    project_id: int,
    pin: bool = Query(True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Pin or unpin a project."""
    project = db.query(Project).filter(Project.id == project_id, Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project.is_pinned = 1 if pin else 0
    db.commit()
    db.refresh(project)
    return _project_to_response(project)


@router.patch("/{project_id}/tags", response_model=ProjectResponse)
async def update_project_tags(
    project_id: int,
    tags: List[str],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update project tags."""
    project = db.query(Project).filter(Project.id == project_id, Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project.tags = tags
    db.commit()
    db.refresh(project)
    return _project_to_response(project)


@router.post("/{project_id}/duplicate", response_model=ProjectResponse)
async def duplicate_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Duplicate an existing project and its plan."""
    original = db.query(Project).filter(Project.id == project_id, Project.user_id == current_user.id).first()
    if not original:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Create new project copy
    duplicated_project = Project(
        user_id=current_user.id,
        name=f"{original.name} (Copy)",
        description=original.description,
        status="planning",  # Reset status to planning
        project_plan=original.project_plan,
        workflow=original.workflow,
        total_tasks=original.total_tasks,
        completed_tasks=0,
        total_phases=original.total_phases,
        current_phase=0,
        estimated_minutes=original.estimated_minutes,
        risk_level=original.risk_level,
        complexity_score=original.complexity_score,
        tags=original.tags
    )
    
    db.add(duplicated_project)
    db.commit()
    db.refresh(duplicated_project)
    
    return _project_to_response(duplicated_project)


@router.get("/{project_id}")  # Removed response_model to avoid Pydantic validation issues
async def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get full project details including plan and tasks.
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
    
    # Return dict directly (avoids Pydantic response_model validation issues)
    return {
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
        "created_at": project.created_at.isoformat() if project.created_at else None,
        "started_at": project.started_at.isoformat() if project.started_at else None,
        "completed_at": project.completed_at.isoformat() if project.completed_at else None,
        "project_plan": project.project_plan,
        "workflow": project.workflow,
        "output": project.output,
        "summary": project.summary
    }


@router.get("/{project_id}/progress", response_model=ProjectProgress)
async def get_project_progress(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get real-time project progress.
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
    
    # Get task counts
    tasks = db.query(Task).filter(Task.project_id == project_id).all()
    total = len(tasks)
    completed = len([t for t in tasks if t.status == "completed"])
    in_progress = len([t for t in tasks if t.status == "in_progress"])
    failed = len([t for t in tasks if t.status == "failed"])
    
    # Calculate remaining time
    remaining_minutes = None
    if project.estimated_minutes and total > 0:
        progress_ratio = completed / total if total > 0 else 0
        remaining_ratio = 1 - progress_ratio
        remaining_minutes = int(project.estimated_minutes * remaining_ratio)
    
    # Get active agents
    active_agents = []
    for task in tasks:
        if task.status == "in_progress":
            # Try to get agent from subtasks
            if task.subtasks:
                for st in task.subtasks:
                    if st.status == "in_progress" and st.assigned_agent:
                        active_agents.append(st.assigned_agent)
    
    return ProjectProgress(
        project_id=project_id,
        status=project.status,
        progress_percentage=project.progress_percentage,
        total_tasks=total,
        completed_tasks=completed,
        in_progress_tasks=in_progress,
        failed_tasks=failed,
        current_phase=project.current_phase or 0,
        active_agents=list(set(active_agents)),
        estimated_remaining_minutes=remaining_minutes
    )


@router.post("/{project_id}/execute", response_model=ProjectExecuteResponse)
async def execute_project(
    project_id: int,
    request: ProjectExecuteRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Start project execution.
    
    Uses the WorkflowEngine to execute the project plan with all agents.
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
    
    if project.status == "in_progress":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Project is already executing"
        )
    
    if not project.workflow and not project.project_plan:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Project has no execution plan. Create a plan first."
        )
    
    # Generate execution ID
    execution_id = str(uuid.uuid4())[:8]
    
    # Update project status and clear previous output
    project.status = "in_progress"
    project.started_at = datetime.utcnow()
    project.completed_tasks = 0
    project.current_phase = 0
    project.output = None  # Clear previous output
    db.commit()
    
    # Start execution in background
    background_tasks.add_task(
        _execute_project_workflow,
        project_id=project_id,
        execution_id=execution_id,
        add_qa=request.add_qa_checkpoints
    )
    
    return ProjectExecuteResponse(
        project_id=project_id,
        execution_id=execution_id,
        status="started",
        message="Project execution started. Monitor progress via /projects/{id}/progress"
    )


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    project_data: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a project.
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
    
    if project_data.name is not None:
        project.name = project_data.name
    if project_data.description is not None:
        project.description = project_data.description
    if project_data.status is not None:
        project.status = project_data.status.value
    
    db.commit()
    db.refresh(project)
    
    return _project_to_progress(project, db)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a project and all associated tasks.
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
    
    # Delete project (cascade will delete tasks)
    db.delete(project)
    db.commit()
    
    return {"message": "Project deleted successfully"}


@router.post("/{project_id}/replan")
async def replan_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Regenerate project plan using ManagerAgent.
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
    
    try:
        from agents.manager_agent import ManagerAgent
        
        manager = ManagerAgent()
        plan_result = manager.execute({
            "project_description": project.description or project.name,
            "user_id": current_user.id
        })
        
        # Update project with new plan
        project.project_plan = plan_result.get("phases", [])
        project.workflow = plan_result.get("workflow", {})
        project.total_phases = len(plan_result.get("phases", []))
        project.total_tasks = plan_result.get("total_tasks", 0)
        project.estimated_minutes = plan_result.get("estimated_minutes", 30)
        project.risk_level = plan_result.get("risk_assessment", {}).get("risk_level", "medium")
        project.status = "planning"
        
        db.commit()
        db.refresh(project)
        
        return {
            "message": "Project replanned successfully",
            "project": _project_to_detail(project)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to replan project: {str(e)}"
        )


# Helper functions

def _project_to_response(project: Project) -> ProjectResponse:
    """Convert Project model to response schema."""
    return ProjectResponse(
        id=project.id,
        name=project.name,
        description=project.description,
        status=project.status or "planning",
        progress=project.progress_percentage,
        total_tasks=project.total_tasks or 0,
        completed_tasks=project.completed_tasks or 0,
        total_phases=project.total_phases or 0,
        current_phase=project.current_phase or 0,
        estimated_minutes=project.estimated_minutes,
        risk_level=project.risk_level,
        is_archived=bool(project.is_archived),
        is_pinned=bool(project.is_pinned),
        tags=project.tags or [],
        created_at=project.created_at,
        started_at=project.started_at,
        completed_at=project.completed_at
    )


def _project_to_detail(project: Project) -> ProjectDetail:
    """Convert Project model to detailed response schema."""
    return ProjectDetail(
        id=project.id,
        name=project.name,
        description=project.description,
        status=project.status or "planning",
        progress=project.progress_percentage,
        total_tasks=project.total_tasks or 0,
        completed_tasks=project.completed_tasks or 0,
        total_phases=project.total_phases or 0,
        current_phase=project.current_phase or 0,
        estimated_minutes=project.estimated_minutes,
        risk_level=project.risk_level,
        is_archived=bool(project.is_archived),
        is_pinned=bool(project.is_pinned),
        tags=project.tags or [],
        created_at=project.created_at,
        started_at=project.started_at,
        completed_at=project.completed_at,
        project_plan=project.project_plan,
        workflow=project.workflow,
        phases=None,  # Could parse from project_plan
        output=project.output,
        summary=project.summary
    )


def _execute_project_workflow(project_id: int, execution_id: str, add_qa: bool = True):
    """Background task to execute project workflow."""
    from database import SessionLocal
    from orchestrator.workflow_engine import WorkflowEngine
    from orchestrator.qa_feedback_loop import add_qa_checkpoints_v2
    
    db = SessionLocal()
    
    try:
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            return
        
        # Get workflow
        workflow = project.workflow or {"phases": project.project_plan}
        
        # 1. Create a Master Task for this execution
        # This is required because WorkflowEngine/Subtasks depend on a Task row
        master_task = Task(
            user_id=project.user_id,
            project_id=project_id,
            user_prompt=f"Project Execution: {project.name}",
            status="in_progress"
        )
        db.add(master_task)
        db.commit()
        db.refresh(master_task)
        
        # Add QA checkpoints if requested
        # DISABLED: This was causing duplicate/unknown tasks and stuck progress
        # if add_qa:
        #     try:
        #         workflow = add_qa_checkpoints_v2(workflow)
        #     except ImportError:
        #          print("!!! FATAL: add_qa_checkpoints_v2 not found - Code mismatch !!!")
        #          pass
        
        # Execute workflow
        engine = WorkflowEngine(db_session=db)
        result = engine.execute_workflow(
            workflow=workflow,
            task_id=master_task.id,
            user_id=project.user_id
        )
        
        # Update project with results
        project.status = "completed" if result.get("status") == "completed" else "failed"
        project.completed_at = datetime.utcnow()
        project.completed_tasks = result.get("tasks_completed", 0)
        project.output = result.get("combined_output", "")
        
        # KEY FIX: Sync execution results back to project_plan for UI visuals
        # and update total_tasks to reflect actual work done (including added QA)
        
        # 1. Parse phase results
        phase_results = result.get("phase_results", [])
        
        # 2. Reconstruct project plan from execution results to ensure perfect sync
        new_plan = []
        real_total_tasks = 0
        real_completed_tasks = 0
        
        for i, phase_res in enumerate(phase_results):
            phase_name = phase_res.get("phase_name", f"Phase {i+1}")
            phase_tasks = []
            
            task_results = phase_res.get("task_results", [])
            for j, task_res in enumerate(task_results):
                real_total_tasks += 1
                status = task_res.get("status", "pending")
                if status == "completed":
                    real_completed_tasks += 1
                    
                phase_tasks.append({
                    "task_id": task_res.get("task_id", f"{i+1}.{j+1}"),
                    "description": task_res.get("description", "Task execution"),
                    # Try multiple field names for agent assignment
                    "assigned_agent": task_res.get("assigned_agent") or task_res.get("agent") or "ContentAgent",
                    "estimated_time": "10 minutes",
                    "status": status,
                    "output": task_res.get("output", "")
                })
            
            new_plan.append({
                "phase_number": i + 1,
                "phase_name": phase_name,
                "tasks": phase_tasks
            })
            
        # 3. Update Project Model
        if new_plan:
            project.project_plan = new_plan
            project.total_tasks = real_total_tasks
            project.completed_tasks = real_completed_tasks
            project.total_phases = len(new_plan)
        
        # Sync master task status
        master_task.status = project.status
        master_task.completed_at = project.completed_at
        master_task.output = project.output
        
        db.commit()
        
    except Exception as e:
        # Mark project as failed
        import traceback
        traceback.print_exc()
        try:
            # Re-query project to ensure session is valid
            project = db.query(Project).filter(Project.id == project_id).first()
            if project:
                project.status = "failed"
                project.output = f"Execution failed: {str(e)}"
                db.commit()
        except:
            pass
    
    finally:
        db.close()

