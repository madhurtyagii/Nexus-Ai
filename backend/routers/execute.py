"""Nexus AI - Code Execution Router.

This router provides endpoints for executing code snippets directly from the UI,
facilitating the 'Live Code Sandbox' functionality.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
from tools.code_executor import CodeExecutorTool
from dependencies import get_current_user
from models.user import User

router = APIRouter(
    prefix="/sandbox",
    tags=["Code Execution"]
)

class CodeExecutionRequest(BaseModel):
    language: str
    code: str
    timeout: Optional[int] = 10

class CodeExecutionResponse(BaseModel):
    success: bool
    stdout: Optional[str] = None
    stderr: Optional[str] = None
    error: Optional[str] = None
    execution_time: Optional[float] = None

@router.post("/python", response_model=CodeExecutionResponse)
async def execute_python(
    request: CodeExecutionRequest,
    current_user: User = Depends(get_current_user)
):
    """Executes Python code in a secure sandbox."""
    if request.language.lower() != "python":
        raise HTTPException(status_code=400, detail="Only Python execution is supported via this endpoint.")
    
    executor = CodeExecutorTool()
    result = executor.execute(code=request.code, timeout=request.timeout)
    
    return CodeExecutionResponse(
        success=result.get("success", False),
        stdout=result.get("stdout"),
        stderr=result.get("stderr"),
        error=result.get("error"),
        execution_time=result.get("execution_time")
    )
