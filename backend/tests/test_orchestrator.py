import pytest
from backend.orchestrator.core import OrchestratorEngine
from backend.models.task import Task, TaskStatus

def test_orchestrator_initialization(db):
    engine = OrchestratorEngine(db)
    assert engine.db == db

def test_analyze_task(db):
    engine = OrchestratorEngine(db)
    # Mocking would be better here, but let's test the interface
    # For integration testing, we'd need to mock LLM calls
    assert hasattr(engine, 'analyze_task')

def test_task_lifecycle(db):
    # Create a task
    task = Task(user_id=1, user_prompt="Test task", status=TaskStatus.QUEUED.value)
    db.add(task)
    db.commit()
    db.refresh(task)
    
    assert task.id is not None
    assert task.status == "queued"
