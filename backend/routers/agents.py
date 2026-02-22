"""
Nexus AI - Agents Router
Agent information endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional, Any
from pydantic import BaseModel
import json
import ast
import re

from database import get_db
from models.agent import Agent
from models.chat import Conversation, ChatMessage as ChatMessageDB
from schemas.agent import AgentResponse, AgentDetailResponse
from agents.agent_factory import AgentFactory
from llm.llm_manager import llm_manager
from sqlalchemy import func


def format_agent_output(output: Any) -> str:
    """Converts any agent output (dict, list, string, etc.) into clean readable text.
    
    This function is the LAST LINE OF DEFENSE against raw JSON/dict leaks in the chat.
    It must NEVER return anything that looks like a Python dict or JSON object.
    """
    # Simple cases
    if output is None:
        return ""
    if isinstance(output, str):
        s = output.strip()
        # If it's a string that LOOKS like a dict/json, try to parse and re-format
        if (s.startswith("{") and s.endswith("}")) or (s.startswith("[") and s.endswith("]")):
            try:
                parsed = json.loads(s)
                return format_agent_output(parsed)
            except:
                try:
                    parsed = ast.literal_eval(s)
                    return format_agent_output(parsed)
                except:
                    pass
        return s
    if isinstance(output, (int, float, bool)):
        return str(output)
    if isinstance(output, list):
        return "\n".join([f"- {format_agent_output(item)}" for item in output if item])

    if not isinstance(output, dict):
        return str(output)

    # --- It's a dict. Extract meaningful content. ---
    
    # Keys we should NEVER show to the user
    JUNK_KEYS = {
        "status", "agent_name", "execution_time_seconds", "tokens_used",
        "timestamp", "chat_friendly", "original_prompt", "history",
        "prompt", "request_id", "file_id", "has_history", "mode",
        "requested_language", "original_code", "tested", "test_output",
    }
    
    # 1. If it has an "output" key (BaseAgent wrapper), unwrap it
    if "output" in output:
        inner = output["output"]
        if inner is not None:
            return format_agent_output(inner)
        # output was None, check for error
        if output.get("error"):
            return str(output["error"])
        return ""
    
    # 2. If it has "code" or "fixed_code" — format as a code block
    code = output.get("code") or output.get("fixed_code")
    if code and isinstance(code, str) and len(code) > 10:
        lang = output.get("language") or "python"
        explanation = output.get("explanation") or output.get("summary") or ""
        parts = []
        if explanation:
            parts.append(str(explanation))
        parts.append(f"```{lang}\n{code}\n```")
        return "\n\n".join(parts)
    
    # 3. Check for a single "response"/"content"/"text"/"message"/"results"/"summary"/"findings" key
    CONTENT_KEYS = ["response", "content", "text", "message", "results", "summary", "findings", "explanation", "details"]
    for key in CONTENT_KEYS:
        val = output.get(key)
        if val and isinstance(val, str) and len(val) > 5:
            return val
        if val and isinstance(val, dict):
            return format_agent_output(val)
        if val and isinstance(val, list):
            return "\n".join([f"- {format_agent_output(item)}" for item in val if item])
    
    # 4. Generic: format remaining keys as bold labels, skipping junk
    formatted_parts = []
    for key, value in output.items():
        if key in JUNK_KEYS:
            continue
        if value is None or value == [] or value == "" or value is False:
            continue
        
        clean_key = key.replace("_", " ").title()
        if isinstance(value, str):
            formatted_parts.append(f"**{clean_key}:** {value}")
        elif isinstance(value, list):
            items = "\n".join([f"- {format_agent_output(item)}" for item in value if item])
            formatted_parts.append(f"**{clean_key}:**\n{items}")
        elif isinstance(value, dict):
            inner_formatted = format_agent_output(value)
            formatted_parts.append(f"**{clean_key}:**\n{inner_formatted}")
        else:
            formatted_parts.append(f"**{clean_key}:** {value}")
    
    if formatted_parts:
        return "\n\n".join(formatted_parts)
    
    # 5. Absolute last resort — return empty rather than str(dict)
    return ""


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


class UpdateConversationRequest(BaseModel):
    title: str

class ChatResponse(BaseModel):
    # Existing ChatResponse...
    agent_name: str
    response: str
    status: str
    conversation_id: Optional[int] = None


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
    
    formatted_messages = []
    for m in messages:
        content = m.content
        # Retroactive fix: if the content looks like a raw JSON/Python dict string, try to parse and format it
        cleaned_content = content.strip()
        
        # Aggressive check for JSON-like content
        if m.role == "agent" and (cleaned_content.startswith("{") or cleaned_content.startswith("[") or "': '" in cleaned_content):
            try:
                # Try JSON first
                data = json.loads(cleaned_content)
                content = format_agent_output(data)
            except:
                try:
                    # Fallback for Python-style dict strings
                    data = ast.literal_eval(cleaned_content)
                    if isinstance(data, (dict, list)):
                        content = format_agent_output(data)
                except:
                    # If it contains "status": "success" or "output": ... as text, it's definitely a leak
                    if '"status":' in cleaned_content or "'status':" in cleaned_content:
                        # Very aggressive last-ditch effort: try to regex out the response
                        resp_match = re.search(r'["\']response["\']:\s*["\'](.*?)["\']', cleaned_content, re.DOTALL)
                        if resp_match:
                            content = resp_match.group(1).replace("\\n", "\n")
                    
        formatted_messages.append({
            "role": m.role,
            "content": content,
            "timestamp": m.timestamp.isoformat()
        })
    
    return formatted_messages


@router.patch("/conversations/{conversation_id:int}", response_model=dict)
async def update_conversation(
    conversation_id: int,
    title: Optional[str] = None,
    request: Optional[UpdateConversationRequest] = None,
    db: Session = Depends(get_db)
):
    """Rename a conversation title (supports body or query param)"""
    conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    new_title = (request.title if request else None) or title
    if not new_title:
        raise HTTPException(status_code=400, detail="Title is required")
        
    conv.title = new_title
    db.commit()
    return {"status": "success", "title": new_title}


@router.delete("/conversations/{conversation_id:int}", response_model=dict)
async def delete_conversation(
    conversation_id: int,
    db: Session = Depends(get_db)
):
    """Delete a conversation and all its messages"""
    # Delete messages first
    db.query(ChatMessageDB).filter(ChatMessageDB.conversation_id == conversation_id).delete()
    # Delete conversation
    conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conv:
         raise HTTPException(status_code=404, detail="Conversation not found")
    
    db.delete(conv)
    db.commit()
    return {"status": "success", "message": "Conversation deleted"}


@router.delete("/conversations/clear/{agent_name}", response_model=dict)
async def clear_agent_conversations(
    agent_name: str,
    db: Session = Depends(get_db)
):
    """Clear all conversations for a specific agent"""
    db.query(Conversation).filter(Conversation.agent_name == agent_name).delete()
    db.commit()
    return {"status": "success", "message": f"All history for {agent_name} cleared"}


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
            
            # Formatted history for context
            history = []
            for m in reversed(past_msgs):
                content = m.content
                # Fix for context corruption: ensure agent messages in history are formatted for context
                if m.role == "agent" and content.strip().startswith("{"):
                    try:
                        # Attempt to parse and re-format if it's a raw dict string
                        data = json.loads(content)
                        if isinstance(data, dict):
                            content = format_agent_output(data)
                    except:
                        try:
                            data = ast.literal_eval(content)
                            if isinstance(data, dict):
                                content = format_agent_output(data)
                        except:
                            pass
                history.append(ChatHistoryMessage(role=m.role, content=content))

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
            "user_message": request.message,
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
            error_msg = result.get("error") or ""
            # Clean up internal error messages so user doesn't see stack traces
            if error_msg:
                # Strip internal AttributeErrors / tracebacks
                if "object has no attribute" in error_msg or "Traceback" in error_msg:
                    output = "Sorry, I ran into a temporary issue. Please try again."
                else:
                    output = f"I encountered an issue: {error_msg}"
            else:
                output = result.get("response") or result.get("text") or "I couldn't process that request. Please try again."
        
        # 5. Formatting for response & Persistence (ensure we save Markdown, not JSON)
        formatted_output = format_agent_output(output)
        
        # Safety: never save empty content
        if not formatted_output or not formatted_output.strip():
            formatted_output = "I processed your request but couldn't generate a meaningful response. Please try rephrasing."

        # Save agent response to DB (Saving the formatted Markdown version)
        agent_msg_db = ChatMessageDB(
            conversation_id=conv_id,
            role="agent",
            content=formatted_output
        )
        db.add(agent_msg_db)
        
        # Update conversation timestamp
        conv = db.query(Conversation).get(conv_id)
        if conv:
            conv.updated_at = func.now()
        db.commit()

        return ChatResponse(
            agent_name=request.agent_name,
            response=formatted_output,
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
        
        # Log the real error server-side
        print(f"❌ Agent chat error: {type(e).__name__}: {str(e)}")
        
        # Give user a clean message, not internal Python errors
        error_str = str(e)
        if "object has no attribute" in error_str or "Traceback" in error_str:
            user_msg = "Sorry, I ran into a temporary issue. Please try again."
        elif "rate limit" in error_str.lower() or "429" in error_str:
            user_msg = "I'm being rate limited right now. Please wait a moment and try again."
        else:
            user_msg = f"I encountered an issue processing your request. Please try again."
        
        return ChatResponse(
            agent_name=request.agent_name,
            response=user_msg,
            status="error",
            conversation_id=conv_id if 'conv_id' in locals() else None
        )


@router.post("/stop")
async def stop_agent_request(request: StopRequest):
    """
    Signal an ongoing agent request to stop.
    """
    from services.cancellation_service import cancellation_service
    cancellation_service.cancel(request.request_id)
    return {"status": "success", "message": f"Cancellation signal sent for {request.request_id}"}
