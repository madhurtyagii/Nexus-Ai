"""
Nexus AI - Agents Router
Agent information endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel

from database import get_db
from models.agent import Agent
from schemas.agent import AgentResponse, AgentDetailResponse
from agents.agent_factory import AgentFactory
from llm.llm_manager import llm_manager

router = APIRouter(prefix="/agents", tags=["Agents"])


class ChatRequest(BaseModel):
    agent_name: str
    message: str


class ChatResponse(BaseModel):
    agent_name: str
    response: str
    status: str


@router.get("/", response_model=List[AgentResponse])
async def list_agents(
    db: Session = Depends(get_db),
    active_only: bool = True
):
    """
    List all available agents.
    
    - By default, returns only active agents
    - Set active_only=False to include inactive agents
    """
    query = db.query(Agent)
    
    if active_only:
        query = query.filter(Agent.is_active == True)
    
    agents = query.all()
    
    return agents


@router.get("/{agent_id}", response_model=AgentDetailResponse)
async def get_agent(
    agent_id: int,
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific agent.
    
    Includes system prompt and available tools.
    """
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    return agent


@router.get("/name/{agent_name}", response_model=AgentDetailResponse)
async def get_agent_by_name(
    agent_name: str,
    db: Session = Depends(get_db)
):
    """
    Get agent by name (e.g., 'ResearchAgent').
    """
    agent = db.query(Agent).filter(Agent.name == agent_name).first()
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    return agent


@router.post("/chat", response_model=ChatResponse)
async def chat_with_agent(
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    """
    Send a direct message to an agent and receive a response.
    
    This is a synchronous, lightweight chat for quick questions.
    """
    try:
        factory = AgentFactory(db_session=db, llm=llm_manager)
        agent = factory.create_agent(request.agent_name)
        
        # Execute with a simple chat-focused input
        result = agent.execute({
            "original_prompt": request.message,
            "mode": "chat"
        })
        
        output = result.get("output", "I couldn't process that request.")
        if isinstance(output, dict):
            output = output.get("content") or output.get("response") or str(output)
        
        return ChatResponse(
            agent_name=request.agent_name,
            response=str(output),
            status="success"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent '{request.agent_name}' not found"
        )
    except Exception as e:
        return ChatResponse(
            agent_name=request.agent_name,
            response=f"I encountered an error: {str(e)}",
            status="error"
        )
