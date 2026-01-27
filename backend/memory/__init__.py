# Nexus AI - Memory Package
# Handles vector storage, embeddings, and context management

"""
Core Components:
- VectorStore: ChromaDB wrapper for embedding storage
- EmbeddingManager: Generate embeddings for text
- RAGEngine: Retrieval Augmented Generation
- ConversationTracker: Track all interactions
- PreferenceLearner: Learn user preferences
- ContextManager: Handle task context and references
"""

from memory.vector_store import VectorStore, get_vector_store
from memory.embeddings import EmbeddingManager, get_embedding_manager
from memory.rag import RAGEngine, get_rag_engine
from memory.conversation_tracker import ConversationTracker, get_conversation_tracker
from memory.preference_learner import PreferenceLearner, get_preference_learner
from memory.context_manager import ContextManager, get_context_manager

__all__ = [
    "VectorStore",
    "get_vector_store",
    "EmbeddingManager", 
    "get_embedding_manager",
    "RAGEngine",
    "get_rag_engine",
    "ConversationTracker",
    "get_conversation_tracker",
    "PreferenceLearner",
    "get_preference_learner",
    "ContextManager",
    "get_context_manager",
]

