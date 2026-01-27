"""
Nexus AI - Agents Router
Agent information endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models.agent import Agent
from schemas.agent import AgentResponse, AgentDetailResponse

router = APIRouter(prefix="/agents", tags=["Agents"])


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
