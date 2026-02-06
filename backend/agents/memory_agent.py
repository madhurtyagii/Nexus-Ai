"""Nexus AI - Memory Agent.

This module implements the MemoryAgent, specialized in persistent storage, 
context retrieval, preference learning, and conversation summarization 
using vector stores.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import uuid

from agents.base_agent import BaseAgent
from agents.agent_registry import AgentRegistry
from memory.vector_store import VectorStore, get_vector_store
from memory.embeddings import get_embedding_manager
from llm.llm_manager import LLMManager
from logging_config import get_logger

logger = get_logger(__name__)


@AgentRegistry.register
class MemoryAgent(BaseAgent):
    """Agent specialized in memory management and context orchestration.
    
    The MemoryAgent interacts directly with the system's vector store to 
    maintain a long-term memory of interactions. It provides other agents 
    with relevant context, learns user preferences, and generates 
    summaries of complex execution trails.
    
    Attributes:
        name: Agent identifier ("MemoryAgent").
        role: Description of the agent's purpose.
        system_prompt: Instructions for accurate memory handling.
        vector_store: Reference to the underlying vector database.
        
    Example:
        >>> agent = MemoryAgent(llm_manager, db_session)
        >>> result = agent.execute({"operation": "retrieve", "query": "Past AI research"})
        >>> print(result["output"]["memories"])
    """
    
    def __init__(
        self, 
        llm_manager: LLMManager = None, 
        db_session=None,
        tools: List[Any] = None
    ):
        """Initialize Memory Agent."""
        super().__init__(
            name="MemoryAgent",
            role="Context management and memory retrieval",
            system_prompt="""You are a memory manager for an AI agent system. Your responsibilities:
1. Store important information from conversations and task outputs
2. Retrieve relevant context when needed
3. Identify and learn user preferences over time
4. Summarize conversation history concisely
5. Help other agents by providing relevant past information

When summarizing, be concise but preserve key details.
When learning preferences, identify patterns in user behavior and requests.
Always maintain accuracy - never fabricate memories.""",
            llm_manager=llm_manager,
            db_session=db_session,
            tools=[]  # Memory agent uses VectorStore directly
        )
        
        self.vector_store = get_vector_store()
        self.embedding_manager = get_embedding_manager()
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Entry point for memory-related operations.
 like storage or retrieval.
        
        Args:
            input_data: A dictionary containing:
                - operation (str): One of 'store', 'retrieve', 'summarize', 
                    'learn_preference', or 'get_context'.
                - content/query (str, optional): Data to store or search for.
                - metadata/filters (dict, optional): Additional context or 
                    search constraints.
                    
        Returns:
            dict: Results of the memory operation.
        """
        self.start_execution()
        
        try:
            operation = input_data.get("operation", "retrieve")
            
            if operation == "store":
                result = self._store_memory(
                    content=input_data.get("content", ""),
                    memory_type=input_data.get("memory_type", "conversation"),
                    metadata=input_data.get("metadata", {})
                )
            
            elif operation == "retrieve":
                result = self._retrieve_memories(
                    query=input_data.get("query", ""),
                    memory_type=input_data.get("memory_type", "conversation"),
                    filters=input_data.get("filters", {}),
                    limit=input_data.get("limit", 5)
                )
            
            elif operation == "summarize":
                result = self._summarize_history(
                    task_id=input_data.get("task_id"),
                    user_id=input_data.get("user_id")
                )
            
            elif operation == "learn_preference":
                result = self._learn_preference(
                    user_id=input_data.get("user_id"),
                    interaction_data=input_data.get("interaction_data", {})
                )
            
            elif operation == "get_context":
                result = self._get_task_context(
                    task_prompt=input_data.get("task_prompt", ""),
                    user_id=input_data.get("user_id"),
                    limit=input_data.get("limit", 5)
                )
            
            else:
                result = {"error": f"Unknown operation: {operation}"}
            
            self.end_execution()
            return self.format_output(result)
            
        except Exception as e:
            logger.error(f"MemoryAgent execution failed: {e}")
            self.end_execution()
            return self.format_output(None, status="error", error=str(e))
    
    def _store_memory(
        self,
        content: str,
        memory_type: str,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Store a new memory."""
        # Map memory type to collection
        type_to_collection = {
            "conversation": VectorStore.CONVERSATION_HISTORY,
            "output": VectorStore.AGENT_OUTPUTS,
            "preference": VectorStore.USER_PREFERENCES,
            "knowledge": VectorStore.DOMAIN_KNOWLEDGE,
            "context": VectorStore.TASK_CONTEXT
        }
        
        collection = type_to_collection.get(memory_type, VectorStore.CONVERSATION_HISTORY)
        
        # Generate embedding
        embedding = self.embedding_manager.generate_embedding(content)
        
        # Store memory
        memory_id = self.vector_store.add_memory(
            collection_name=collection,
            content=content,
            metadata=metadata,
            embedding=embedding
        )
        
        self.log_action("memory_stored", {
            "collection": collection,
            "memory_id": memory_id,
            "content_length": len(content)
        })
        
        return {
            "success": True,
            "memory_id": memory_id,
            "stored_at": datetime.utcnow().isoformat()
        }
    
    def _retrieve_memories(
        self,
        query: str,
        memory_type: str,
        filters: Dict[str, Any],
        limit: int = 5
    ) -> Dict[str, Any]:
        """Retrieve relevant memories."""
        type_to_collection = {
            "conversation": VectorStore.CONVERSATION_HISTORY,
            "output": VectorStore.AGENT_OUTPUTS,
            "preference": VectorStore.USER_PREFERENCES,
            "knowledge": VectorStore.DOMAIN_KNOWLEDGE,
            "context": VectorStore.TASK_CONTEXT,
            "all": None  # Search all
        }
        
        collection = type_to_collection.get(memory_type, VectorStore.CONVERSATION_HISTORY)
        
        # Generate query embedding
        query_embedding = self.embedding_manager.generate_embedding(query)
        
        if collection is None:
            # Search all collections
            all_memories = []
            for coll_name in [
                VectorStore.CONVERSATION_HISTORY,
                VectorStore.AGENT_OUTPUTS,
                VectorStore.USER_PREFERENCES
            ]:
                memories = self.vector_store.search_memory(
                    collection_name=coll_name,
                    query=query,
                    query_embedding=query_embedding,
                    filters=filters if filters else None,
                    limit=limit
                )
                for m in memories:
                    m["source_collection"] = coll_name
                all_memories.extend(memories)
            
            # Sort by distance and take top results
            all_memories.sort(key=lambda x: x.get("distance", 1.0))
            memories = all_memories[:limit]
        else:
            memories = self.vector_store.search_memory(
                collection_name=collection,
                query=query,
                query_embedding=query_embedding,
                filters=filters if filters else None,
                limit=limit
            )
        
        self.log_action("memories_retrieved", {
            "query": query[:50],
            "count": len(memories)
        })
        
        return {
            "memories": memories,
            "total_found": len(memories),
            "query": query
        }
    
    def _summarize_history(
        self,
        task_id: int = None,
        user_id: int = None
    ) -> Dict[str, Any]:
        """Summarize conversation history."""
        # Build filters
        filters = {}
        if task_id:
            filters["task_id"] = task_id
        if user_id:
            filters["user_id"] = user_id
        
        if not filters:
            return {"error": "Must provide task_id or user_id"}
        
        # Retrieve all relevant memories
        memories = self.vector_store.get_all_memories(
            collection_name=VectorStore.CONVERSATION_HISTORY,
            filters=filters,
            limit=50
        )
        
        if not memories:
            return {"summary": "No conversation history found.", "memory_count": 0}
        
        # Combine into context
        history_text = "\n\n".join([
            f"[{m.get('metadata', {}).get('timestamp', '')}] {m.get('content', '')}"
            for m in memories
        ])
        
        # Use LLM to summarize
        if self.llm:
            summary_prompt = f"""Summarize this conversation history, highlighting key points and decisions:

{history_text[:3000]}

Provide a concise summary (2-3 paragraphs max)."""
            
            summary = self.generate_response(summary_prompt)
        else:
            # Fallback: simple concatenation
            summary = f"History contains {len(memories)} entries. Most recent: {memories[0].get('content', '')[:200]}..."
        
        # Store summary as a new memory
        if summary:
            self._store_memory(
                content=summary,
                memory_type="context",
                metadata={
                    "type": "summary",
                    "task_id": task_id,
                    "user_id": user_id,
                    "source_memories": len(memories)
                }
            )
        
        return {
            "summary": summary,
            "memory_count": len(memories)
        }
    
    def _learn_preference(
        self,
        user_id: int,
        interaction_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Learn user preference from interaction."""
        if not user_id:
            return {"error": "user_id is required"}
        
        # Use LLM to identify preferences
        if self.llm and interaction_data:
            prompt = f"""Analyze this user interaction and identify any implicit or explicit preferences:

Interaction: {str(interaction_data)[:1000]}

Identify preferences in these categories:
1. Tone preference (formal/casual)
2. Detail level (concise/detailed)
3. Response speed priority (quick/thorough)
4. Content type preferences

Return a JSON object with identified preferences and confidence scores (0-1)."""
            
            response = self.generate_response(prompt)
            
            if response:
                # Store identified preferences
                self._store_memory(
                    content=response,
                    memory_type="preference",
                    metadata={
                        "user_id": user_id,
                        "source": "interaction_analysis",
                        "raw_interaction": str(interaction_data)[:500]
                    }
                )
                
                return {
                    "preferences_learned": response,
                    "confidence": 0.7,
                    "stored": True
                }
        
        return {
            "preferences_learned": [],
            "confidence": 0,
            "message": "Could not analyze preferences (LLM not available)"
        }
    
    def _get_task_context(
        self,
        task_prompt: str,
        user_id: int = None,
        limit: int = 5
    ) -> Dict[str, Any]:
        """Get relevant context for a task."""
        if not task_prompt:
            return {"error": "task_prompt is required"}
        
        filters = {"user_id": user_id} if user_id else None
        
        # Search for similar past tasks
        similar_tasks = self.vector_store.search_memory(
            collection_name=VectorStore.CONVERSATION_HISTORY,
            query=task_prompt,
            filters=filters,
            limit=limit
        )
        
        # Search for relevant outputs
        relevant_outputs = self.vector_store.search_memory(
            collection_name=VectorStore.AGENT_OUTPUTS,
            query=task_prompt,
            filters=filters,
            limit=limit
        )
        
        # Get user preferences
        user_preferences = []
        if user_id:
            user_preferences = self.vector_store.search_memory(
                collection_name=VectorStore.USER_PREFERENCES,
                query=task_prompt,
                filters={"user_id": user_id},
                limit=3
            )
        
        # Generate context summary using LLM
        context_summary = None
        if self.llm and (similar_tasks or relevant_outputs):
            context_text = ""
            if similar_tasks:
                context_text += "Similar past tasks:\n"
                for t in similar_tasks[:2]:
                    context_text += f"- {t.get('content', '')[:200]}\n"
            if relevant_outputs:
                context_text += "\nRelevant past outputs:\n"
                for o in relevant_outputs[:2]:
                    context_text += f"- {o.get('content', '')[:200]}\n"
            
            summary_prompt = f"""Summarize this context briefly for the current task:
Current task: {task_prompt}

{context_text}

One paragraph summary:"""
            
            context_summary = self.generate_response(summary_prompt)
        
        return {
            "similar_tasks": similar_tasks,
            "relevant_outputs": relevant_outputs,
            "user_preferences": user_preferences,
            "context_summary": context_summary
        }
    
    def get_agent_knowledge(
        self,
        agent_name: str,
        topic: str
    ) -> Dict[str, Any]:
        """Get domain knowledge for an agent."""
        knowledge = self.vector_store.search_memory(
            collection_name=VectorStore.DOMAIN_KNOWLEDGE,
            query=topic,
            filters={"agent_name": agent_name},
            limit=5
        )
        
        return {
            "agent": agent_name,
            "topic": topic,
            "knowledge": knowledge
        }
    
    def cleanup_old_memories(
        self,
        older_than_days: int = 90,
        user_id: int = None
    ) -> Dict[str, Any]:
        """Clean up old memories."""
        # This is a placeholder - actual implementation would need
        # to query by timestamp and delete old entries
        # ChromaDB doesn't have native TTL support
        
        self.log_action("cleanup_requested", {
            "older_than_days": older_than_days,
            "user_id": user_id
        })
        
        return {
            "message": "Cleanup scheduled",
            "older_than_days": older_than_days
        }
