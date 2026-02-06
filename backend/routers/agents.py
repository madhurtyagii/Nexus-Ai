"""
Nexus AI - Agents Router
Agent information endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from database import get_db
from models.agent import Agent
from schemas.agent import AgentResponse, AgentDetailResponse
from agents.agent_factory import AgentFactory
from llm.llm_manager import llm_manager

router = APIRouter(prefix="/agents", tags=["Agents"])


class ChatMessage(BaseModel):
    role: str  # 'user' or 'agent'
    content: str


class ChatRequest(BaseModel):
    agent_name: str
    message: str
    history: Optional[List[ChatMessage]] = []  # Conversation history for context


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
        
        current_msg_lower = request.message.lower()
        
        # Detect explicit language request in current message
        language_request = None
        language_patterns = [
            ('c++', 'C++'), ('cpp', 'C++'), (' c++ ', 'C++'),
            ('python', 'Python'), (' py ', 'Python'),
            ('javascript', 'JavaScript'), (' js ', 'JavaScript'),
            ('typescript', 'TypeScript'), (' ts ', 'TypeScript'),
            ('java ', 'Java'), (' java', 'Java'),
            ('rust', 'Rust'), (' go ', 'Go'), ('golang', 'Go'),
        ]
        for pattern, lang in language_patterns:
            if pattern in current_msg_lower:
                language_request = lang
                break
        
        # Check if this is a "same in X" type request
        is_language_switch = language_request and any(word in current_msg_lower for word in ['same', 'that in', 'it in', 'convert', 'rewrite', 'now in', 'now write'])
        
        # Build conversation context from history
        conversation_context = ""
        task_description = ""
        
        if request.history and is_language_switch:
            # Language switch detected - extract only the TASK, not the code
            for msg in request.history:
                if msg.role == "user":
                    # Get the original task description (first user message usually)
                    task_description = msg.content
                    break
            # Don't include code in context - just reference the task
            if task_description:
                conversation_context = f"Previously discussed: {task_description}"
        elif request.history:
            # Normal context building
            context_parts = []
            for msg in request.history[-6:]:  # Last 6 messages for context
                role_label = "User" if msg.role == "user" else "Assistant"
                # Strip code blocks from assistant responses to keep context clean
                content = msg.content
                if msg.role == "agent" and "```" in content:
                    # Just say "provided code" instead of the actual code
                    content = "[Previously provided code implementation]"
                context_parts.append(f"{role_label}: {content}")
            if context_parts:
                conversation_context = "\n".join(context_parts)
        
        # Build the full prompt with context
        if is_language_switch and task_description:
            # Explicit language switch - make it crystal clear
            full_prompt = f"""Write {task_description} in {language_request}.

IMPORTANT: Generate ONLY {language_request} code. Do NOT generate Python or any other language."""
            print(f"🚀 Language switch detected! Generating {language_request} for task: {task_description[:50]}")
        elif conversation_context:
            full_prompt = f"""Previous conversation:
{conversation_context}

Current request: {request.message}

Note: Respond to the current request, using the conversation history for context."""
        else:
            full_prompt = request.message
        
        # Execute with conversation-aware input
        result = await agent.execute({
            "original_prompt": full_prompt,
            "mode": "chat",
            "has_history": bool(request.history),
            "requested_language": language_request
        })
        
        print(f"🤖 [AgentsRouter] Result from {request.agent_name}: {result}")
        
        # Ensure we get a valid output, prioritizing errors if status is error
        output = result.get("output")
        if result.get("status") == "error" or output is None:
            output = result.get("error") or result.get("response") or result.get("text") or "I couldn't process that request."
        
        # Handle structured outputs (like CodeAgent, ResearchAgent)
        if isinstance(output, dict):
            # 1. First, try to extract the main content if it's wrapped
            if any(output.get(k) is not None for k in ["results", "content", "response", "text", "message"]):
                main_val = (
                    output.get("results") or 
                    output.get("content") or 
                    output.get("response") or 
                    output.get("text") or 
                    output.get("message")
                )
                # if the extracted value is a string, and there's nothing else important in the dict, use it
                if isinstance(main_val, str) and len(output.keys()) <= 3:
                     output = main_val

            # 2. If it's still a dict, apply specialized or universal formatting
            if isinstance(output, dict):
                findings = output.get("key_findings") or output.get("findings")
                summary = output.get("summary") or output.get("description")
                
                # CodeAgent format
                if any(k in output for k in ["code", "original_code", "generated_code"]):
                    code = output.get("code") or output.get("original_code") or output.get("generated_code") or ""
                    lang = output.get("language", "python")
                    explanation = output.get("explanation") or output.get("description") or output.get("summary")
                    
                    if isinstance(explanation, dict):
                        explanation = explanation.get("summary") or explanation.get("text") or str(explanation)
                    
                    if code and isinstance(code, str) and len(code) > 10:
                        output = f"{explanation}\n\n```{lang}\n{code}\n```" if explanation else f"```{lang}\n{code}\n```"
                    else:
                        output = explanation or str(output)
                
                # ResearchAgent format
                elif summary and findings and isinstance(findings, list):
                    if isinstance(summary, dict):
                        summary = summary.get("summary") or summary.get("text") or str(summary)
                    findings_list = "\n".join([f"- {f}" for f in findings])
                    output = f"### Summary\n{summary}\n\n### Key Findings\n{findings_list}"
                
                # Universal Fallback
                else:
                    formatted_parts = []
                    for key, value in output.items():
                        if key in ["status", "agent_name", "execution_time_seconds", "tokens_used", "timestamp"]:
                            continue
                        clean_key = key.replace("_", " ").title()
                        if isinstance(value, list):
                            items = "\n".join([f"  - {i}" for i in value])
                            formatted_parts.append(f"**{clean_key}:**\n{items}")
                        elif isinstance(value, dict):
                            formatted_parts.append(f"**{clean_key}:**\n```json\n{json.dumps(value, indent=2)}\n```")
                        else:
                            formatted_parts.append(f"**{clean_key}:** {value}")
                    
                    output = "\n\n".join(formatted_parts) if formatted_parts else str(output)
        
        # Final safety check
        if output is None or output == "None":
            output = "The agent returned an empty response. This might be due to a technical error with the LLM provider."
            
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
