"""
Nexus AI - RAG Engine
Retrieval Augmented Generation for context-aware agent responses
"""

from typing import Dict, List, Any, Optional
from datetime import datetime

from memory.vector_store import VectorStore, get_vector_store
from memory.embeddings import EmbeddingManager, get_embedding_manager
from logging_config import get_logger

logger = get_logger(__name__)


class RAGEngine:
    """
    Retrieval Augmented Generation engine.
    
    Enhances agent prompts with relevant context retrieved
    from the vector store before sending to LLM.
    """
    
    def __init__(
        self,
        vector_store: VectorStore = None,
        embedding_manager: EmbeddingManager = None,
        retrieval_limit: int = 5,
        similarity_threshold: float = 0.7
    ):
        """
        Initialize RAG engine.
        
        Args:
            vector_store: VectorStore instance
            embedding_manager: EmbeddingManager instance
            retrieval_limit: Max items to retrieve per source
            similarity_threshold: Min similarity score to include
        """
        self.vector_store = vector_store or get_vector_store()
        self.embedding_manager = embedding_manager or get_embedding_manager()
        self.retrieval_limit = retrieval_limit
        self.similarity_threshold = similarity_threshold
    
    def augment_prompt(
        self,
        base_prompt: str,
        context_sources: List[str] = None,
        user_id: int = None,
        task_id: int = None,
        max_context_length: int = 2000
    ) -> str:
        """
        Enhance a prompt with retrieved context.
        
        Args:
            base_prompt: Original user/task prompt
            context_sources: Sources to retrieve from (conversation, outputs, preferences, knowledge)
            user_id: Filter by user ID
            task_id: Filter by task ID
            max_context_length: Max chars for context section
            
        Returns:
            Augmented prompt with context
        """
        if context_sources is None:
            context_sources = ["conversation", "outputs", "preferences"]
        
        # Map source names to collection names
        source_to_collection = {
            "conversation": VectorStore.CONVERSATION_HISTORY,
            "outputs": VectorStore.AGENT_OUTPUTS,
            "preferences": VectorStore.USER_PREFERENCES,
            "knowledge": VectorStore.DOMAIN_KNOWLEDGE,
            "context": VectorStore.TASK_CONTEXT
        }
        
        # Build filters
        filters = {}
        if user_id:
            filters["user_id"] = user_id
        
        # Retrieve context from each source
        context_sections = []
        
        for source in context_sources:
            collection_name = source_to_collection.get(source)
            if not collection_name:
                continue
            
            context = self.retrieve_context(
                query=base_prompt,
                collections=[collection_name],
                filters=filters if source != "knowledge" else None,
                limit=self.retrieval_limit
            )
            
            if context["context_items"]:
                section = self._format_context_section(source, context["context_items"])
                if section:
                    context_sections.append(section)
        
        # Build augmented prompt
        if not context_sections:
            return base_prompt
        
        # Combine and truncate context
        combined_context = "\n\n".join(context_sections)
        if len(combined_context) > max_context_length:
            combined_context = combined_context[:max_context_length] + "..."
        
        augmented = f"""### Relevant Context
{combined_context}

### Current Task
{base_prompt}"""
        
        logger.debug(f"Augmented prompt with {len(context_sections)} context sections")
        return augmented
    
    def retrieve_context(
        self,
        query: str,
        collections: List[str],
        filters: Dict[str, Any] = None,
        limit: int = None
    ) -> Dict[str, Any]:
        """
        Retrieve relevant context from multiple collections.
        
        Args:
            query: Search query
            collections: List of collection names to search
            filters: Metadata filters
            limit: Max results per collection
            
        Returns:
            Dict with context_items, sources, total_items
        """
        limit = limit or self.retrieval_limit
        all_items = []
        sources = []
        
        for collection_name in collections:
            try:
                results = self.vector_store.search_memory(
                    collection_name=collection_name,
                    query=query,
                    filters=filters,
                    limit=limit
                )
                
                for item in results:
                    item["source"] = collection_name
                    all_items.append(item)
                
                if results:
                    sources.append(collection_name)
                    
            except Exception as e:
                logger.warning(f"Failed to search collection '{collection_name}': {e}")
        
        # Rank and filter by relevance
        ranked_items = self.rank_by_relevance(all_items, query)
        
        return {
            "context_items": ranked_items,
            "sources": sources,
            "total_items": len(ranked_items)
        }
    
    def rank_by_relevance(
        self,
        items: List[Dict[str, Any]],
        query: str
    ) -> List[Dict[str, Any]]:
        """
        Rank items by relevance score.
        
        Args:
            items: List of context items with distance scores
            query: Original query
            
        Returns:
            Sorted and filtered list
        """
        if not items:
            return []
        
        # Convert distance to similarity (ChromaDB uses L2 distance)
        # Lower distance = higher similarity
        for item in items:
            distance = item.get("distance", 1.0)
            # Convert L2 distance to similarity score (0-1)
            # Using exponential decay: similarity = exp(-distance)
            import math
            item["similarity"] = math.exp(-distance)
        
        # Sort by similarity descending
        sorted_items = sorted(items, key=lambda x: x["similarity"], reverse=True)
        
        # Filter by threshold
        filtered = [
            item for item in sorted_items 
            if item["similarity"] >= self.similarity_threshold
        ]
        
        # If nothing passes threshold, return top items anyway
        if not filtered and sorted_items:
            filtered = sorted_items[:3]
        
        return filtered
    
    def build_context_string(
        self,
        context_items: List[Dict[str, Any]],
        max_length: int = 2000
    ) -> str:
        """
        Build a formatted context string from items.
        
        Args:
            context_items: List of context items
            max_length: Max output length
            
        Returns:
            Formatted context string
        """
        if not context_items:
            return ""
        
        parts = []
        current_length = 0
        
        for item in context_items:
            content = item.get("content", "")
            metadata = item.get("metadata", {})
            
            # Format item
            source = item.get("source", "memory")
            timestamp = metadata.get("timestamp", "")
            agent = metadata.get("agent_name", "")
            
            header = f"[{source}"
            if agent:
                header += f" - {agent}"
            if timestamp:
                header += f" @ {timestamp[:10]}"
            header += "]"
            
            formatted = f"{header}\n{content}"
            
            # Check length
            if current_length + len(formatted) + 4 > max_length:
                break
            
            parts.append(formatted)
            current_length += len(formatted) + 4  # Account for separator
        
        return "\n---\n".join(parts)
    
    def _format_context_section(
        self,
        source: str,
        items: List[Dict[str, Any]]
    ) -> Optional[str]:
        """Format a context section with header."""
        if not items:
            return None
        
        headers = {
            "conversation": "📝 Past Conversations",
            "outputs": "🤖 Previous Agent Outputs",
            "preferences": "⚙️ User Preferences",
            "knowledge": "📚 Domain Knowledge",
            "context": "🔗 Related Context"
        }
        
        header = headers.get(source, f"📌 {source.title()}")
        content = self.build_context_string(items, max_length=500)
        
        if not content:
            return None
        
        return f"**{header}**\n{content}"
    
    def get_agent_knowledge(
        self,
        agent_name: str,
        topic: str,
        limit: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Retrieve domain knowledge for a specific agent.
        
        Args:
            agent_name: Name of the agent
            topic: Topic to search for
            limit: Max results
            
        Returns:
            List of knowledge items
        """
        return self.vector_store.search_memory(
            collection_name=VectorStore.DOMAIN_KNOWLEDGE,
            query=topic,
            filters={"agent_name": agent_name},
            limit=limit
        )


# Global RAG engine instance
_rag_engine: Optional[RAGEngine] = None


def get_rag_engine() -> RAGEngine:
    """Get or create the global RAGEngine instance."""
    global _rag_engine
    if _rag_engine is None:
        _rag_engine = RAGEngine()
    return _rag_engine
