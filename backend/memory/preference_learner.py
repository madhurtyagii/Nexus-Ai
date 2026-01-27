"""
Nexus AI - Preference Learner
Learns and applies user preferences from interaction patterns
"""

from typing import Dict, List, Any, Optional
from datetime import datetime

from sqlalchemy.orm import Session

from memory.vector_store import VectorStore, get_vector_store
from memory.embeddings import get_embedding_manager
from logging_config import get_logger

logger = get_logger(__name__)


class PreferenceLearner:
    """
    Learns user preferences from interactions and applies them to tasks.
    
    Preferences tracked:
    - Tone: formal vs casual
    - Detail level: concise vs detailed
    - Preferred agents
    - Content length preferences
    - Response speed priority
    """
    
    def __init__(self, vector_store: VectorStore = None, db: Session = None):
        """Initialize preference learner."""
        self.vector_store = vector_store or get_vector_store()
        self.embedding_manager = get_embedding_manager()
        self.db = db
    
    def analyze_user_behavior(self, user_id: int) -> Dict[str, Any]:
        """
        Analyze user's behavior patterns from history.
        
        Args:
            user_id: User ID to analyze
            
        Returns:
            Preference profile dict
        """
        if not user_id:
            return {"error": "user_id required"}
        
        # Get user's conversation history
        conversations = self.vector_store.get_all_memories(
            collection_name=VectorStore.CONVERSATION_HISTORY,
            filters={"user_id": user_id},
            limit=50
        )
        
        # Get agent outputs for user
        outputs = self.vector_store.get_all_memories(
            collection_name=VectorStore.AGENT_OUTPUTS,
            filters={"user_id": user_id},
            limit=50
        )
        
        # Analyze patterns
        agent_counts: Dict[str, int] = {}
        total_content_length = 0
        
        for output in outputs:
            meta = output.get("metadata", {})
            agent = meta.get("agent_name", "unknown")
            agent_counts[agent] = agent_counts.get(agent, 0) + 1
            total_content_length += len(output.get("content", ""))
        
        # Calculate averages
        avg_content_length = total_content_length / len(outputs) if outputs else 0
        
        # Determine preferences
        detail_level = "detailed" if avg_content_length > 1000 else "concise"
        
        # Find preferred agents
        sorted_agents = sorted(
            agent_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )
        preferred_agents = [a[0] for a in sorted_agents[:3]]
        
        profile = {
            "user_id": user_id,
            "interaction_count": len(conversations),
            "detail_level": detail_level,
            "preferred_agents": preferred_agents,
            "agent_usage": agent_counts,
            "avg_output_length": int(avg_content_length),
            "analyzed_at": datetime.utcnow().isoformat()
        }
        
        logger.debug(f"Analyzed preferences for user {user_id}")
        return profile
    
    def learn_from_feedback(
        self,
        user_id: int,
        task_id: int,
        feedback: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Learn preferences from user feedback.
        
        Args:
            user_id: User ID
            task_id: Task that was rated
            feedback: {rating: 1-5, feedback: str, aspects: dict}
            
        Returns:
            Learned preferences
        """
        rating = feedback.get("rating", 3)
        feedback_text = feedback.get("feedback", "")
        aspects = feedback.get("aspects", {})
        
        lessons = []
        
        # Learn from rating
        if rating >= 4:
            lessons.append("positive_experience")
        elif rating <= 2:
            lessons.append("negative_experience")
        
        # Learn from aspects
        for aspect, liked in aspects.items():
            if liked:
                lessons.append(f"prefer_{aspect}")
            else:
                lessons.append(f"avoid_{aspect}")
        
        # Store as preference
        preference_content = f"Rating: {rating}/5. Feedback: {feedback_text}. Aspects: {aspects}"
        
        embedding = self.embedding_manager.generate_embedding(preference_content)
        
        self.vector_store.add_memory(
            collection_name=VectorStore.USER_PREFERENCES,
            content=preference_content,
            metadata={
                "user_id": user_id,
                "task_id": task_id,
                "rating": rating,
                "preference_type": "feedback",
                "timestamp": datetime.utcnow().isoformat()
            },
            embedding=embedding
        )
        
        logger.info(f"Learned from feedback for user {user_id}, task {task_id}")
        
        return {
            "lessons_learned": lessons,
            "stored": True
        }
    
    def get_user_preferences(self, user_id: int) -> Dict[str, Any]:
        """
        Get aggregated user preferences.
        
        Args:
            user_id: User ID
            
        Returns:
            Preferences dict
        """
        # Get stored preferences
        stored_prefs = self.vector_store.get_all_memories(
            collection_name=VectorStore.USER_PREFERENCES,
            filters={"user_id": user_id},
            limit=20
        )
        
        # Analyze behavior
        behavior = self.analyze_user_behavior(user_id)
        
        # Calculate average rating
        ratings = []
        for pref in stored_prefs:
            meta = pref.get("metadata", {})
            if "rating" in meta:
                ratings.append(meta["rating"])
        
        avg_rating = sum(ratings) / len(ratings) if ratings else None
        
        # Default preferences with overrides from analysis
        preferences = {
            "tone": "professional",  # Default
            "detail_level": behavior.get("detail_level", "moderate"),
            "preferred_agents": behavior.get("preferred_agents", []),
            "content_length": "medium",
            "response_speed": "balanced",
            "avg_satisfaction": avg_rating,
            "preference_count": len(stored_prefs)
        }
        
        return preferences
    
    def apply_preferences_to_task(
        self,
        task_prompt: str,
        preferences: Dict[str, Any]
    ) -> str:
        """
        Modify task prompt to incorporate user preferences.
        
        Args:
            task_prompt: Original task prompt
            preferences: User preferences dict
            
        Returns:
            Enhanced prompt with preference hints
        """
        hints = []
        
        # Add tone hint
        tone = preferences.get("tone", "professional")
        if tone == "casual":
            hints.append("Use a friendly, conversational tone.")
        elif tone == "formal":
            hints.append("Use a formal, professional tone.")
        
        # Add detail level hint
        detail = preferences.get("detail_level", "moderate")
        if detail == "concise":
            hints.append("Keep the response brief and to the point.")
        elif detail == "detailed":
            hints.append("Provide comprehensive, detailed information.")
        
        # Add length hint
        length = preferences.get("content_length", "medium")
        if length == "short":
            hints.append("Aim for a short response.")
        elif length == "long":
            hints.append("A longer, thorough response is preferred.")
        
        # Build enhanced prompt
        if hints:
            hints_text = " ".join(hints)
            enhanced = f"{task_prompt}\n\n[User preferences: {hints_text}]"
            return enhanced
        
        return task_prompt


# Global preference learner instance
_preference_learner: Optional[PreferenceLearner] = None


def get_preference_learner() -> PreferenceLearner:
    """Get or create the global PreferenceLearner instance."""
    global _preference_learner
    if _preference_learner is None:
        _preference_learner = PreferenceLearner()
    return _preference_learner
