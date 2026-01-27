"""
Nexus AI - Context Manager
Handles task context, references, and continuity between related tasks
"""

import re
from typing import Dict, List, Any, Optional
from datetime import datetime

from sqlalchemy.orm import Session

from memory.vector_store import VectorStore, get_vector_store
from memory.embeddings import get_embedding_manager
from llm.llm_manager import llm_manager
from logging_config import get_logger

logger = get_logger(__name__)


# Reference patterns to detect
REFERENCE_PATTERNS = [
    r"that code we wrote",
    r"the previous analysis",
    r"what you just",
    r"the (last|previous) (task|result|output)",
    r"(that|the) (blog post|article|content) (from before|we created)",
    r"like we did (before|earlier|last time)",
    r"(similar|same) (to|as) (before|last time)",
    r"based on (that|what you just)",
    r"continue (from|with) (that|where we left)",
    r"(expand|elaborate) on (that|the previous)",
    r"(that|the) function (we|you) (wrote|created)",
    r"(the|that) research (from|we did)",
]


class ContextManager:
    """
    Manages task context and reference resolution.
    
    Features:
    - Detect references to previous work
    - Resolve references to actual content
    - Find related tasks
    - Inject context into prompts
    """
    
    def __init__(
        self,
        vector_store: VectorStore = None,
        db: Session = None
    ):
        """Initialize context manager."""
        self.vector_store = vector_store or get_vector_store()
        self.embedding_manager = get_embedding_manager()
        self.db = db
    
    def get_related_tasks(
        self,
        current_task_prompt: str,
        user_id: int,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Find similar past tasks using semantic search.
        
        Args:
            current_task_prompt: Current task description
            user_id: User ID to filter by
            limit: Max results
            
        Returns:
            List of related tasks with similarity scores
        """
        # Generate embedding for current task
        embedding = self.embedding_manager.generate_embedding(current_task_prompt)
        
        # Search conversation history
        similar = self.vector_store.search_memory(
            collection_name=VectorStore.CONVERSATION_HISTORY,
            query=current_task_prompt,
            query_embedding=embedding,
            filters={"user_id": user_id},
            limit=limit
        )
        
        # Add similarity score (convert distance)
        import math
        for item in similar:
            distance = item.get("distance", 1.0)
            item["similarity"] = math.exp(-distance)
        
        return similar
    
    def load_task_context(self, task_id: int) -> Dict[str, Any]:
        """
        Load full context for a task.
        
        Args:
            task_id: Task ID
            
        Returns:
            Context dict with prompt, history, outputs, related tasks
        """
        # Get conversation history for task
        history = self.vector_store.get_all_memories(
            collection_name=VectorStore.CONVERSATION_HISTORY,
            filters={"task_id": task_id},
            limit=20
        )
        
        # Get agent outputs for task
        outputs = self.vector_store.get_all_memories(
            collection_name=VectorStore.AGENT_OUTPUTS,
            filters={"task_id": task_id},
            limit=20
        )
        
        # Sort chronologically
        history.sort(key=lambda x: x.get("metadata", {}).get("timestamp", ""))
        outputs.sort(key=lambda x: x.get("metadata", {}).get("timestamp", ""))
        
        # Get task prompt (first user message)
        task_prompt = ""
        user_id = None
        if history:
            for msg in history:
                if msg.get("metadata", {}).get("role") == "user":
                    task_prompt = msg.get("content", "")
                    user_id = msg.get("metadata", {}).get("user_id")
                    break
        
        # Find related tasks
        related_tasks = []
        if task_prompt and user_id:
            related_tasks = self.get_related_tasks(task_prompt, user_id, limit=3)
            # Exclude current task
            related_tasks = [t for t in related_tasks if t.get("metadata", {}).get("task_id") != task_id]
        
        # Generate context summary
        context_summary = self._generate_context_summary(history, outputs)
        
        return {
            "task_id": task_id,
            "task_prompt": task_prompt,
            "conversation": history,
            "outputs": outputs,
            "related_tasks": related_tasks,
            "context_summary": context_summary
        }
    
    def inject_context_into_prompt(
        self,
        prompt: str,
        context: Dict[str, Any]
    ) -> str:
        """
        Prepend relevant context to a prompt.
        
        Args:
            prompt: Original prompt
            context: Context dict from load_task_context or similar
            
        Returns:
            Augmented prompt with context prefix
        """
        parts = []
        
        # Add context summary
        summary = context.get("context_summary")
        if summary:
            parts.append(f"**Previous Context:**\n{summary}")
        
        # Add relevant outputs
        outputs = context.get("outputs", [])[:2]
        if outputs:
            output_text = "\n".join([
                f"- {o.get('metadata', {}).get('agent_name', 'Agent')}: {o.get('content', '')[:200]}..."
                for o in outputs
            ])
            parts.append(f"**Recent Agent Outputs:**\n{output_text}")
        
        # Build augmented prompt
        if parts:
            context_prefix = "\n\n".join(parts)
            return f"{context_prefix}\n\n**Current Task:**\n{prompt}"
        
        return prompt
    
    def detect_references(self, prompt: str) -> Dict[str, Any]:
        """
        Detect references to previous work in a prompt.
        
        Args:
            prompt: User prompt to analyze
            
        Returns:
            Dict with has_references, referenced_items, retrieval_queries
        """
        prompt_lower = prompt.lower()
        found_patterns = []
        
        # Check for reference patterns
        for pattern in REFERENCE_PATTERNS:
            matches = re.findall(pattern, prompt_lower)
            if matches:
                found_patterns.append(pattern)
        
        # Also check for common reference words
        reference_words = ["that", "previous", "last", "before", "earlier", "above"]
        has_reference_words = any(word in prompt_lower for word in reference_words)
        
        has_references = len(found_patterns) > 0 or (
            has_reference_words and 
            any(word in prompt_lower for word in ["code", "analysis", "content", "research", "task"])
        )
        
        # Generate retrieval queries
        retrieval_queries = []
        if has_references:
            # Try to identify what's being referenced
            if "code" in prompt_lower:
                retrieval_queries.append("code function implementation")
            if "analysis" in prompt_lower or "research" in prompt_lower:
                retrieval_queries.append("research analysis findings")
            if "content" in prompt_lower or "blog" in prompt_lower or "article" in prompt_lower:
                retrieval_queries.append("content article blog post")
            if "task" in prompt_lower or "result" in prompt_lower:
                retrieval_queries.append("task result output")
            
            # Add the original prompt as a query too
            if not retrieval_queries:
                retrieval_queries.append(prompt)
        
        return {
            "has_references": has_references,
            "referenced_items": found_patterns,
            "retrieval_queries": retrieval_queries
        }
    
    def resolve_references(
        self,
        references: Dict[str, Any],
        user_id: int
    ) -> Dict[str, Any]:
        """
        Resolve detected references to actual content.
        
        Args:
            references: Output from detect_references()
            user_id: User ID to filter by
            
        Returns:
            Dict with resolved and unresolved references
        """
        if not references.get("has_references"):
            return {"resolved": {}, "unresolved": []}
        
        resolved = {}
        unresolved = []
        
        for query in references.get("retrieval_queries", []):
            # Search conversation history
            history_results = self.vector_store.search_memory(
                collection_name=VectorStore.CONVERSATION_HISTORY,
                query=query,
                filters={"user_id": user_id},
                limit=2
            )
            
            # Search agent outputs
            output_results = self.vector_store.search_memory(
                collection_name=VectorStore.AGENT_OUTPUTS,
                query=query,
                filters={"user_id": user_id},
                limit=2
            )
            
            # Combine and find best match
            all_results = history_results + output_results
            
            if all_results:
                # Sort by distance (relevance)
                all_results.sort(key=lambda x: x.get("distance", 1.0))
                best_match = all_results[0]
                resolved[query] = {
                    "content": best_match.get("content", ""),
                    "metadata": best_match.get("metadata", {}),
                    "distance": best_match.get("distance", 0)
                }
            else:
                unresolved.append(query)
        
        return {
            "resolved": resolved,
            "unresolved": unresolved
        }
    
    def _generate_context_summary(
        self,
        history: List[Dict[str, Any]],
        outputs: List[Dict[str, Any]]
    ) -> Optional[str]:
        """Generate a brief summary of context."""
        if not history and not outputs:
            return None
        
        # Try to use LLM for summary
        try:
            context_parts = []
            
            for msg in history[:3]:
                role = msg.get("metadata", {}).get("role", "user")
                content = msg.get("content", "")[:200]
                context_parts.append(f"{role}: {content}")
            
            for out in outputs[:2]:
                agent = out.get("metadata", {}).get("agent_name", "Agent")
                content = out.get("content", "")[:200]
                context_parts.append(f"{agent} output: {content}")
            
            full_context = "\n".join(context_parts)
            
            summary_prompt = f"""Summarize this conversation context in 1-2 sentences:

{full_context}

Brief summary:"""
            
            summary = llm_manager.generate(
                prompt=summary_prompt,
                system="You are a concise summarizer.",
                max_tokens=100
            )
            
            return summary
            
        except Exception as e:
            logger.debug(f"Could not generate context summary: {e}")
            # Fallback: return first message
            if history:
                return f"Previous task: {history[0].get('content', '')[:100]}..."
            return None


# Global context manager instance
_context_manager: Optional[ContextManager] = None


def get_context_manager() -> ContextManager:
    """Get or create the global ContextManager instance."""
    global _context_manager
    if _context_manager is None:
        _context_manager = ContextManager()
    return _context_manager
