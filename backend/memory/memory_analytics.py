"""
Nexus AI - Memory Analytics
Analytics and insights about memory usage
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from collections import Counter

from memory.vector_store import VectorStore, get_vector_store
from logging_config import get_logger

logger = get_logger(__name__)


class MemoryAnalytics:
    """
    Analytics and insights for memory system.
    
    Provides:
    - Usage statistics
    - Popular topics
    - Memory quality scores
    - Cleanup suggestions
    """
    
    def __init__(self, vector_store: VectorStore = None):
        """Initialize memory analytics."""
        self.vector_store = vector_store or get_vector_store()
    
    def get_usage_statistics(self, user_id: int = None) -> Dict[str, Any]:
        """
        Get comprehensive usage statistics.
        
        Args:
            user_id: Optional user ID to filter by
            
        Returns:
            Statistics dict
        """
        filters = {"user_id": user_id} if user_id else None
        
        # Get counts from each collection
        collections = [
            VectorStore.CONVERSATION_HISTORY,
            VectorStore.AGENT_OUTPUTS,
            VectorStore.USER_PREFERENCES,
            VectorStore.DOMAIN_KNOWLEDGE,
            VectorStore.TASK_CONTEXT
        ]
        
        stats = {
            "total_memories": 0,
            "by_collection": {},
            "by_agent": {},
            "recent_activity": 0
        }
        
        for collection_name in collections:
            collection_stats = self.vector_store.get_collection_stats(collection_name)
            count = collection_stats.get("total_memories", 0)
            stats["by_collection"][collection_name] = count
            stats["total_memories"] += count
            
            # Get memories for agent analysis
            if collection_name == VectorStore.AGENT_OUTPUTS:
                outputs = self.vector_store.get_all_memories(
                    collection_name=collection_name,
                    filters=filters,
                    limit=100
                )
                
                for output in outputs:
                    agent = output.get("metadata", {}).get("agent_name", "unknown")
                    stats["by_agent"][agent] = stats["by_agent"].get(agent, 0) + 1
        
        # Calculate recent activity (last 7 days)
        # Note: This is approximate since we can't easily query by timestamp in ChromaDB
        conversations = self.vector_store.get_all_memories(
            collection_name=VectorStore.CONVERSATION_HISTORY,
            filters=filters,
            limit=50
        )
        stats["recent_activity"] = len(conversations)
        
        stats["generated_at"] = datetime.utcnow().isoformat()
        
        return stats
    
    def get_popular_topics(
        self, 
        user_id: int = None, 
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Extract popular topics from conversation history.
        
        Args:
            user_id: Optional user ID
            limit: Max topics to return
            
        Returns:
            List of topics with frequencies
        """
        filters = {"user_id": user_id} if user_id else None
        
        # Get conversations
        conversations = self.vector_store.get_all_memories(
            collection_name=VectorStore.CONVERSATION_HISTORY,
            filters=filters,
            limit=100
        )
        
        # Simple keyword extraction
        # In production, use NLP for better topic extraction
        all_words = []
        
        stop_words = {
            "the", "a", "an", "is", "are", "was", "were", "be", "been",
            "have", "has", "had", "do", "does", "did", "will", "would",
            "could", "should", "may", "might", "must", "shall", "can",
            "to", "of", "in", "for", "on", "with", "at", "by", "from",
            "up", "about", "into", "through", "during", "before", "after",
            "above", "below", "between", "under", "again", "further",
            "then", "once", "here", "there", "when", "where", "why", "how",
            "all", "each", "few", "more", "most", "other", "some", "such",
            "no", "nor", "not", "only", "own", "same", "so", "than", "too",
            "very", "just", "i", "me", "my", "myself", "we", "our", "you",
            "your", "he", "him", "his", "she", "her", "it", "its", "they",
            "them", "their", "what", "which", "who", "whom", "this", "that",
            "these", "those", "am", "and", "but", "if", "or", "because", "as"
        }
        
        for conv in conversations:
            content = conv.get("content", "").lower()
            words = content.split()
            
            for word in words:
                # Clean word
                clean_word = "".join(c for c in word if c.isalnum())
                if len(clean_word) > 3 and clean_word not in stop_words:
                    all_words.append(clean_word)
        
        # Count frequencies
        word_counts = Counter(all_words)
        
        # Get top topics
        top_topics = [
            {"topic": word, "count": count}
            for word, count in word_counts.most_common(limit)
        ]
        
        return top_topics
    
    def get_memory_quality_score(self, user_id: int = None) -> Dict[str, Any]:
        """
        Calculate memory quality score.
        
        Args:
            user_id: Optional user ID
            
        Returns:
            Quality score and breakdown
        """
        filters = {"user_id": user_id} if user_id else None
        
        scores = {
            "preference_coverage": 0,
            "context_richness": 0,
            "recency": 0
        }
        
        # Check preference coverage
        preferences = self.vector_store.get_all_memories(
            collection_name=VectorStore.USER_PREFERENCES,
            filters=filters,
            limit=20
        )
        scores["preference_coverage"] = min(len(preferences) * 10, 100)
        
        # Check context richness (conversation + outputs)
        conversations = self.vector_store.get_all_memories(
            collection_name=VectorStore.CONVERSATION_HISTORY,
            filters=filters,
            limit=50
        )
        outputs = self.vector_store.get_all_memories(
            collection_name=VectorStore.AGENT_OUTPUTS,
            filters=filters,
            limit=50
        )
        context_count = len(conversations) + len(outputs)
        scores["context_richness"] = min(context_count * 2, 100)
        
        # Recency score (based on recent activity)
        scores["recency"] = min(len(conversations) * 5, 100)
        
        # Overall score
        overall = (
            scores["preference_coverage"] * 0.3 +
            scores["context_richness"] * 0.5 +
            scores["recency"] * 0.2
        )
        
        return {
            "overall_score": round(overall, 1),
            "breakdown": scores,
            "recommendations": self._get_recommendations(scores)
        }
    
    def suggest_cleanup(self, user_id: int = None) -> Dict[str, Any]:
        """
        Suggest memories that could be cleaned up.
        
        Args:
            user_id: Optional user ID
            
        Returns:
            Cleanup suggestions
        """
        suggestions = {
            "old_memories": 0,
            "duplicate_candidates": 0,
            "low_relevance": 0,
            "recommendations": []
        }
        
        # Get all memories
        filters = {"user_id": user_id} if user_id else None
        
        conversations = self.vector_store.get_all_memories(
            collection_name=VectorStore.CONVERSATION_HISTORY,
            filters=filters,
            limit=100
        )
        
        # Check for potential duplicates (very similar content)
        contents = [c.get("content", "") for c in conversations]
        seen = set()
        duplicates = 0
        
        for content in contents:
            # Simple hash-based duplicate detection
            content_hash = hash(content[:100])
            if content_hash in seen:
                duplicates += 1
            seen.add(content_hash)
        
        suggestions["duplicate_candidates"] = duplicates
        
        # Count total memories
        total = len(conversations)
        
        if total > 50:
            suggestions["recommendations"].append(
                "Consider summarizing older conversations to reduce storage"
            )
        
        if duplicates > 5:
            suggestions["recommendations"].append(
                f"Found {duplicates} potential duplicate memories - consider cleanup"
            )
        
        return suggestions
    
    def _get_recommendations(self, scores: Dict[str, int]) -> List[str]:
        """Generate recommendations based on scores."""
        recommendations = []
        
        if scores["preference_coverage"] < 30:
            recommendations.append("Provide feedback on tasks to help learn your preferences")
        
        if scores["context_richness"] < 30:
            recommendations.append("Use the system more to build context for better results")
        
        if scores["recency"] < 30:
            recommendations.append("Recent activity is low - memory may be stale")
        
        return recommendations


# Global analytics instance
_memory_analytics: Optional[MemoryAnalytics] = None


def get_memory_analytics() -> MemoryAnalytics:
    """Get or create the global MemoryAnalytics instance."""
    global _memory_analytics
    if _memory_analytics is None:
        _memory_analytics = MemoryAnalytics()
    return _memory_analytics
