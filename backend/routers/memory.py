"""Nexus AI - Memory Router.

This module provides API endpoints for interacting with the semantic 
memory system, including conversation history, preferences, and 
analytics.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel

from database import get_db
from models.user import User
from dependencies import get_current_user
from memory.vector_store import get_vector_store, VectorStore
from memory.conversation_tracker import get_conversation_tracker
from memory.preference_learner import get_preference_learner
from memory.context_manager import get_context_manager
from memory.memory_analytics import get_memory_analytics
from logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/memory", tags=["Memory"])


# Pydantic models
class RelatedTasksQuery(BaseModel):
    prompt: str = None
    task_id: int = None


class ClearMemoryRequest(BaseModel):
    confirm: bool = False
    collection: str = None  # If None, clears all


# Endpoints

@router.get(
    "/conversations",
    summary="Get conversation history",
    description="Retrieves a paginated list of past user interactions tracked by the memory system."
)
async def get_conversations(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user)
):
    """
    Get user's conversation history.
    
    Returns paginated list of past conversations.
    """
    tracker = get_conversation_tracker()
    
    history = tracker.get_user_history(
        user_id=current_user.id,
        limit=limit
    )
    
    # Apply offset (simple pagination)
    paginated = history[offset:offset + limit]
    
    return {
        "conversations": paginated,
        "total": len(history),
        "limit": limit,
        "offset": offset
    }


@router.get(
    "/preferences",
    summary="Get user preferences",
    description="Retrieves learned user preferences (tone, detail, etc.) derived from past interactions."
)
async def get_preferences(
    current_user: User = Depends(get_current_user)
):
    """
    Get learned user preferences.
    
    Returns aggregated preferences with confidence scores.
    """
    learner = get_preference_learner()
    
    preferences = learner.get_user_preferences(current_user.id)
    
    return {
        "user_id": current_user.id,
        "preferences": preferences
    }


@router.get(
    "/related",
    summary="Find related tasks",
    description="Searches the semantic memory for tasks similar to a given prompt or ID."
)
async def get_related_tasks(
    prompt: Optional[str] = Query(None, description="Search prompt"),
    task_id: Optional[int] = Query(None, description="Task ID to find related tasks for"),
    limit: int = Query(5, ge=1, le=20),
    current_user: User = Depends(get_current_user)
):
    """
    Find related past tasks.
    
    Provide either a prompt or task_id to find similar tasks.
    """
    context_mgr = get_context_manager()
    
    if not prompt and not task_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must provide either 'prompt' or 'task_id'"
        )
    
    if task_id:
        # Load task context and get related
        context = context_mgr.load_task_context(task_id)
        return {
            "task_id": task_id,
            "related_tasks": context.get("related_tasks", []),
            "context_summary": context.get("context_summary")
        }
    
    # Search by prompt
    related = context_mgr.get_related_tasks(
        current_task_prompt=prompt,
        user_id=current_user.id,
        limit=limit
    )
    
    return {
        "query": prompt,
        "related_tasks": related
    }


@router.get("/stats")
async def get_memory_stats(
    current_user: User = Depends(get_current_user)
):
    """
    Get memory usage statistics.
    
    Returns total memories, breakdown by type, and storage info.
    """
    analytics = get_memory_analytics()
    
    stats = analytics.get_usage_statistics(user_id=current_user.id)
    
    return stats


@router.get("/analytics")
async def get_memory_analytics_endpoint(
    current_user: User = Depends(get_current_user)
):
    """
    Get comprehensive memory analytics.
    
    Includes usage stats, popular topics, quality score, and suggestions.
    """
    analytics = get_memory_analytics()
    
    stats = analytics.get_usage_statistics(user_id=current_user.id)
    topics = analytics.get_popular_topics(user_id=current_user.id, limit=10)
    quality = analytics.get_memory_quality_score(user_id=current_user.id)
    cleanup = analytics.suggest_cleanup(user_id=current_user.id)
    
    return {
        "statistics": stats,
        "popular_topics": topics,
        "quality_score": quality,
        "cleanup_suggestions": cleanup
    }


@router.delete("/{memory_id}")
async def delete_memory(
    memory_id: str,
    collection: str = Query(..., description="Collection name"),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a specific memory.
    
    Requires memory ID and collection name.
    """
    vector_store = get_vector_store()
    
    # Verify collection is valid
    valid_collections = [
        VectorStore.CONVERSATION_HISTORY,
        VectorStore.AGENT_OUTPUTS,
        VectorStore.USER_PREFERENCES,
        VectorStore.TASK_CONTEXT
    ]
    
    if collection not in valid_collections:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid collection. Must be one of: {valid_collections}"
        )
    
    # Get the memory first to verify ownership
    memory = vector_store.get_memory(collection, memory_id)
    
    if not memory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Memory not found"
        )
    
    # Check ownership
    memory_user_id = memory.get("metadata", {}).get("user_id")
    if memory_user_id and memory_user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this memory"
        )
    
    # Delete
    success = vector_store.delete_memory(collection, memory_id)
    
    if success:
        return {"message": "Memory deleted", "memory_id": memory_id}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete memory"
        )


@router.post("/clear")
async def clear_memories(
    request: ClearMemoryRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Clear all user memories. DANGEROUS!
    
    Requires explicit confirmation.
    """
    if not request.confirm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must set confirm=true to clear memories"
        )
    
    vector_store = get_vector_store()
    
    cleared = []
    
    if request.collection:
        # Clear specific collection
        success = vector_store.clear_collection(request.collection)
        if success:
            cleared.append(request.collection)
    else:
        # Clear all user-related collections
        collections = [
            VectorStore.CONVERSATION_HISTORY,
            VectorStore.AGENT_OUTPUTS,
            VectorStore.USER_PREFERENCES,
            VectorStore.TASK_CONTEXT
        ]
        
        for coll in collections:
            success = vector_store.clear_collection(coll)
            if success:
                cleared.append(coll)
    
    logger.warning(f"User {current_user.id} cleared memories: {cleared}")
    
    return {
        "message": "Memories cleared",
        "cleared_collections": cleared
    }


@router.get("/search")
async def search_memories(
    query: str = Query(..., min_length=1),
    collection: Optional[str] = Query(None, description="Specific collection to search"),
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user)
):
    """
    Search memories by content.
    
    Uses semantic search across memories.
    """
    vector_store = get_vector_store()
    
    results = []
    
    if collection:
        # Search specific collection
        results = vector_store.search_memory(
            collection_name=collection,
            query=query,
            filters={"user_id": current_user.id},
            limit=limit
        )
    else:
        # Search across collections
        collections = [
            VectorStore.CONVERSATION_HISTORY,
            VectorStore.AGENT_OUTPUTS,
            VectorStore.USER_PREFERENCES
        ]
        
        for coll in collections:
            coll_results = vector_store.search_memory(
                collection_name=coll,
                query=query,
                filters={"user_id": current_user.id},
                limit=limit // len(collections)
            )
            
            for r in coll_results:
                r["collection"] = coll
            
            results.extend(coll_results)
        
        # Sort by relevance
        results.sort(key=lambda x: x.get("distance", 1.0))
        results = results[:limit]
    
    return {
        "query": query,
        "results": results,
        "total": len(results)
    }
