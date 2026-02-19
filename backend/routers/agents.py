"""
Nexus AI - Agents Router
Agent information endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
import json

from database import get_db
from models.agent import Agent
from models.chat import Conversation, ChatMessage as ChatMessageDB
from schemas.agent import AgentResponse, AgentDetailResponse
from agents.agent_factory import AgentFactory
from llm.llm_manager import llm_manager
from sqlalchemy import func

router = APIRouter(prefix="/agents", tags=["Agents"])


class ChatHistoryMessage(BaseModel):
    role: str  # 'user' or 'agent'
    content: str


class ChatRequest(BaseModel):
    agent_name: str
    message: str
    history: Optional[List[ChatHistoryMessage]] = []  # Conversation history for context
    request_id: Optional[str] = None  # Unique ID for cancellation tracking
    file_id: Optional[int] = None  # File attachment for multimodal agents (VisualAgent)
    style: Optional[str] = None  # Style preset for VisualAgent
    conversation_id: Optional[int] = None  # Existing conversation ID


class StopRequest(BaseModel):
    request_id: str


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


@router.get("/conversations/chat/{conversation_id}", response_model=List[dict])
async def get_conversation_history(
    conversation_id: int,
    db: Session = Depends(get_db)
):
    """Fetch the full message sequence for a conversation"""
    messages = db.query(ChatMessageDB).filter(
        ChatMessageDB.conversation_id == conversation_id
    ).order_by(ChatMessageDB.timestamp.asc()).all()
    
    return [
        {
            "role": m.role,
            "content": m.content,
            "timestamp": m.timestamp.isoformat()
        } for m in messages
    ]


@router.get("/conversations/{agent_name}", response_model=List[dict])
async def list_agent_conversations(
    agent_name: str,
    db: Session = Depends(get_db)
):
    """List all previous conversations with a specific agent"""
    conversations = db.query(Conversation).filter(
        Conversation.agent_name == agent_name
    ).order_by(Conversation.updated_at.desc()).all()
    
    return [
        {
            "id": c.id,
            "title": c.title,
            "updated_at": c.updated_at.isoformat()
        } for c in conversations
    ]


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
    Now persists to database.
    """
    try:
        factory = AgentFactory(db_session=db, llm=llm_manager)
        agent = factory.create_agent(request.agent_name)
        
        # 1. Handle Conversation Persistence
        conv_id = request.conversation_id
        if not conv_id:
            # Create a new conversation if none provided
            title = request.message[:50] + "..." if len(request.message) > 50 else request.message
            new_conv = Conversation(
                user_id=1, # TODO: Get from auth
                agent_name=request.agent_name,
                title=title
            )
            db.add(new_conv)
            db.commit()
            db.refresh(new_conv)
            conv_id = new_conv.id
        
        # Save user message
        user_msg_db = ChatMessageDB(
            conversation_id=conv_id,
            role="user",
            content=request.message
        )
        db.add(user_msg_db)
        db.commit()

        # 2. Build Context for LLM
        current_msg_lower = request.message.lower()
        
        # Detect explicit language request
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
        
        is_language_switch = language_request and any(word in current_msg_lower for word in ['same', 'that in', 'it in', 'convert', 'rewrite', 'now in', 'now write'])
        
        # If no history provided but we have a conversation, fetch from DB
        history = request.history or []
        if not history and conv_id:
            past_msgs = db.query(ChatMessageDB).filter(
                ChatMessageDB.conversation_id == conv_id,
                ChatMessageDB.id < user_msg_db.id # Don't include the current message
            ).order_by(ChatMessageDB.timestamp.desc()).limit(10).all()
            history = [ChatHistoryMessage(role=m.role, content=m.content) for m in reversed(past_msgs)]

        conversation_context = ""
        task_description = ""
        
        if history and is_language_switch:
            for msg in history:
                if msg.role == "user":
                    task_description = msg.content
                    break
            if task_description:
                conversation_context = f"Previously discussed: {task_description}"
        elif history:
            context_parts = []
            for msg in history[-6:]:
                role_label = "User" if msg.role == "user" else "Assistant"
                content = msg.content
                if msg.role == "agent" and "```" in content:
                    content = "[Previously provided code implementation]"
                context_parts.append(f"{role_label}: {content}")
            if context_parts:
                conversation_context = "\n".join(context_parts)
        
        # Build prompt
        if is_language_switch and task_description:
            full_prompt = f"Write {task_description} in {language_request}.\n\nIMPORTANT: Generate ONLY {language_request} code."
        elif conversation_context:
            full_prompt = f"Previous conversation:\n{conversation_context}\n\nCurrent request: {request.message}\n\nNote: Respond to the current request, using history for context."
        else:
            full_prompt = request.message
        
        # 3. Execute Agent
        result = await agent.execute({
            "prompt": full_prompt,
            "original_prompt": full_prompt,
            "mode": "chat",
            "has_history": bool(history),
            "requested_language": language_request,
            "request_id": request.request_id,
            "file_id": request.file_id
        })
        
        # 4. Process Output and Persist Agent Response
        if request.request_id:
            from services.cancellation_service import cancellation_service
            cancellation_service.clear(request.request_id)
        
        output = result.get("output")
        if result.get("status") == "error" or output is None:
            output = result.get("error") or result.get("response") or result.get("text") or "I couldn't process that request."
        
        # Handle structured outputs (abbreviated for internal saving, full formatting happens later)
        raw_output = str(output)
        
        # Save agent response to DB
        agent_msg_db = ChatMessageDB(
            conversation_id=conv_id,
            role="agent",
            content=raw_output
        )
        db.add(agent_msg_db)
        
        # Update conversation timestamp
        conv = db.query(Conversation).get(conv_id)
        if conv:
            conv.updated_at = func.now()
        
        db.commit()

        # Formatting for response (re-using existing formatting logic)
        if isinstance(output, dict):
             # [Existing formatting logic here]
             if any(output.get(k) is not None for k in ["results", "content", "response", "text", "message"]):
                main_val = output.get("results") or output.get("content") or output.get("response") or output.get("text") or output.get("message")
                if isinstance(main_val, str) and len(output.keys()) <= 3:
                     output = main_val
             if isinstance(output, dict):
                # Apply specialized formatting (CodeAgent, ResearchAgent, etc.)
                if any(k in output for k in ["code", "original_code", "generated_code"]):
                    code = output.get("code") or output.get("original_code") or output.get("generated_code") or ""
                    lang = output.get("language", "python")
                    explanation = output.get("explanation") or output.get("description") or output.get("summary")
                    if code and isinstance(code, str) and len(code) > 10:
                        output = f"{explanation}\n\n```{lang}\n{code}\n```" if explanation else f"```{lang}\n{code}\n```"
                elif (output.get("summary") or output.get("description")) and (output.get("key_findings") or output.get("findings")):
                    summary = output.get("summary") or output.get("description")
                    findings = output.get("key_findings") or output.get("findings")
                    findings_list = "\n".join([f"- {f}" for f in findings])
                    output = f"### Summary\n{summary}\n\n### Key Findings\n{findings_list}"
                else:
                    formatted_parts = []
                    for key, value in output.items():
                        if key in ["status", "agent_name", "execution_time_seconds", "tokens_used", "timestamp"]: continue
                        clean_key = key.replace("_", " ").title()
                        formatted_parts.append(f"**{clean_key}:** {value}")
                    output = "\n\n".join(formatted_parts) if formatted_parts else str(output)

        return ChatResponse(
            agent_name=request.agent_name,
            response=str(output),
            status="success",
            conversation_id=conv_id
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent '{request.agent_name}' not found"
        )
    except Exception as e:
        if request.request_id:
            from services.cancellation_service import cancellation_service
            cancellation_service.clear(request.request_id)
        return ChatResponse(
            agent_name=request.agent_name,
            response=f"I encountered an error: {str(e)}",
            status="error"
        )


@router.post("/stop")
async def stop_agent_request(request: StopRequest):
    """
    Signal an ongoing agent request to stop.
    """
    from services.cancellation_service import cancellation_service
    cancellation_service.cancel(request.request_id)
    return {"status": "success", "message": f"Cancellation signal sent for {request.request_id}"}
