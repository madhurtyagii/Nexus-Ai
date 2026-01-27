"""
Nexus AI - Conversation Tracker
Tracks all user/agent interactions for memory and context
"""

from typing import Dict, List, Any, Optional
from datetime import datetime

from memory.vector_store import VectorStore, get_vector_store
from memory.embeddings import get_embedding_manager
from logging_config import get_logger

logger = get_logger(__name__)


class ConversationTracker:
    """
    Tracks all conversations and agent interactions.
    
    Automatically stores:
    - User messages and task prompts
    - Agent responses and outputs
    - Metadata for filtering and retrieval
    """
    
    def __init__(self, vector_store: VectorStore = None):
        """Initialize conversation tracker."""
        self.vector_store = vector_store or get_vector_store()
        self.embedding_manager = get_embedding_manager()
    
    def track_user_message(
        self,
        user_id: int,
        task_id: int,
        message: str,
        timestamp: datetime = None
    ) -> str:
        """
        Track a user message/prompt.
        
        Args:
            user_id: User ID
            task_id: Associated task ID
            message: User's message content
            timestamp: Message timestamp
            
        Returns:
            Memory ID
        """
        timestamp = timestamp or datetime.utcnow()
        
        # Generate embedding
        embedding = self.embedding_manager.generate_embedding(message)
        
        metadata = {
            "user_id": user_id,
            "task_id": task_id,
            "role": "user",
            "timestamp": timestamp.isoformat(),
            "content_type": "message"
        }
        
        memory_id = self.vector_store.add_memory(
            collection_name=VectorStore.CONVERSATION_HISTORY,
            content=message,
            metadata=metadata,
            embedding=embedding
        )
        
        logger.debug(f"Tracked user message for task {task_id}: {message[:50]}...")
        return memory_id
    
    def track_agent_response(
        self,
        agent_name: str,
        task_id: int,
        response: str,
        metadata: Dict[str, Any] = None,
        user_id: int = None
    ) -> str:
        """
        Track an agent's response/output.
        
        Args:
            agent_name: Name of the agent
            task_id: Associated task ID
            response: Agent's response content
            metadata: Additional metadata (success, execution_time, etc.)
            user_id: Optional user ID
            
        Returns:
            Memory ID
        """
        additional_metadata = metadata or {}
        
        # Generate embedding
        embedding = self.embedding_manager.generate_embedding(response)
        
        stored_metadata = {
            "agent_name": agent_name,
            "task_id": task_id,
            "role": "agent",
            "timestamp": datetime.utcnow().isoformat(),
            "success": additional_metadata.get("success", True),
            "execution_time": additional_metadata.get("execution_time", 0),
            "content_type": "output"
        }
        
        if user_id:
            stored_metadata["user_id"] = user_id
        
        memory_id = self.vector_store.add_memory(
            collection_name=VectorStore.AGENT_OUTPUTS,
            content=response,
            metadata=stored_metadata,
            embedding=embedding
        )
        
        logger.debug(f"Tracked {agent_name} response for task {task_id}")
        return memory_id
    
    def get_conversation_history(
        self,
        task_id: int,
        include_outputs: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Get full conversation history for a task.
        
        Args:
            task_id: Task ID to get history for
            include_outputs: Whether to include agent outputs
            
        Returns:
            Chronologically ordered list of messages
        """
        # Get user messages
        user_messages = self.vector_store.get_all_memories(
            collection_name=VectorStore.CONVERSATION_HISTORY,
            filters={"task_id": task_id}
        )
        
        history = user_messages.copy()
        
        # Add agent outputs if requested
        if include_outputs:
            agent_outputs = self.vector_store.get_all_memories(
                collection_name=VectorStore.AGENT_OUTPUTS,
                filters={"task_id": task_id}
            )
            history.extend(agent_outputs)
        
        # Sort by timestamp
        history.sort(key=lambda x: x.get("metadata", {}).get("timestamp", ""))
        
        return history
    
    def get_user_history(
        self,
        user_id: int,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get recent conversation history for a user.
        
        Args:
            user_id: User ID
            limit: Maximum entries to return
            
        Returns:
            List of recent interactions
        """
        # Get user's messages
        user_messages = self.vector_store.get_all_memories(
            collection_name=VectorStore.CONVERSATION_HISTORY,
            filters={"user_id": user_id},
            limit=limit
        )
        
        # Sort by timestamp descending
        user_messages.sort(
            key=lambda x: x.get("metadata", {}).get("timestamp", ""),
            reverse=True
        )
        
        return user_messages
    
    def analyze_conversation_patterns(
        self,
        user_id: int
    ) -> Dict[str, Any]:
        """
        Analyze patterns in user's conversation history.
        
        Args:
            user_id: User ID to analyze
            
        Returns:
            Pattern analysis dict
        """
        # Get user's history
        history = self.get_user_history(user_id, limit=100)
        
        if not history:
            return {
                "total_interactions": 0,
                "message": "No history available"
            }
        
        # Count agents used
        agent_counts: Dict[str, int] = {}
        task_ids = set()
        
        # Get agent outputs for this user
        outputs = self.vector_store.get_all_memories(
            collection_name=VectorStore.AGENT_OUTPUTS,
            filters={"user_id": user_id},
            limit=100
        )
        
        for output in outputs:
            agent = output.get("metadata", {}).get("agent_name", "unknown")
            agent_counts[agent] = agent_counts.get(agent, 0) + 1
        
        for msg in history:
            task_id = msg.get("metadata", {}).get("task_id")
            if task_id:
                task_ids.add(task_id)
        
        # Find most used agents
        sorted_agents = sorted(
            agent_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return {
            "total_interactions": len(history),
            "total_tasks": len(task_ids),
            "agent_usage": dict(sorted_agents[:5]),
            "most_used_agent": sorted_agents[0][0] if sorted_agents else None,
        }


# Global tracker instance
_conversation_tracker: Optional[ConversationTracker] = None


def get_conversation_tracker() -> ConversationTracker:
    """Get or create the global ConversationTracker instance."""
    global _conversation_tracker
    if _conversation_tracker is None:
        _conversation_tracker = ConversationTracker()
    return _conversation_tracker
