"""
Nexus AI - Vector Store
ChromaDB wrapper for storing and retrieving memories using embeddings
"""

import os
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional

import chromadb
from chromadb.config import Settings

from logging_config import get_logger

logger = get_logger(__name__)


class VectorStore:
    """
    ChromaDB-based vector store for semantic memory storage and retrieval.
    
    Collections:
    - conversation_history: user conversations and task prompts
    - agent_outputs: all agent execution results
    - user_preferences: learned user preferences
    - domain_knowledge: pre-loaded expert knowledge per agent
    - task_context: context from related tasks
    """
    
    # Collection names
    CONVERSATION_HISTORY = "conversation_history"
    AGENT_OUTPUTS = "agent_outputs"
    USER_PREFERENCES = "user_preferences"
    DOMAIN_KNOWLEDGE = "domain_knowledge"
    TASK_CONTEXT = "task_context"
    
    def __init__(self, persist_directory: str = None):
        """
        Initialize ChromaDB client in persistent mode.
        
        Args:
            persist_directory: Directory to persist ChromaDB data
        """
        self.persist_directory = persist_directory or os.getenv(
            "CHROMADB_DIR", "./data/chromadb"
        )
        
        # Ensure directory exists
        os.makedirs(self.persist_directory, exist_ok=True)
        
        # Initialize ChromaDB client with persistence
        self.client = chromadb.PersistentClient(
            path=self.persist_directory,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Track initialized collections
        self._collections: Dict[str, chromadb.Collection] = {}
        
        logger.info(f"VectorStore initialized with persist_directory: {self.persist_directory}")
    
    def init_collection(
        self, 
        collection_name: str, 
        metadata: Dict[str, Any] = None
    ) -> chromadb.Collection:
        """
        Initialize or get an existing collection.
        
        Args:
            collection_name: Name of the collection
            metadata: Optional metadata for the collection
            
        Returns:
            ChromaDB Collection object
        """
        if collection_name in self._collections:
            return self._collections[collection_name]
        
        try:
            # Get or create collection
            collection = self.client.get_or_create_collection(
                name=collection_name,
                metadata=metadata or {"created_at": datetime.utcnow().isoformat()}
            )
            
            self._collections[collection_name] = collection
            logger.info(f"Collection '{collection_name}' initialized with {collection.count()} documents")
            
            return collection
            
        except Exception as e:
            logger.error(f"Failed to initialize collection '{collection_name}': {e}")
            raise
    
    def add_memory(
        self,
        collection_name: str,
        content: str,
        metadata: Dict[str, Any],
        memory_id: str = None,
        embedding: List[float] = None
    ) -> str:
        """
        Add a memory to a collection.
        
        Args:
            collection_name: Target collection name
            content: Text content to store
            metadata: Metadata dict (user_id, task_id, timestamp, agent_name, memory_type)
            memory_id: Optional unique ID (generated if not provided)
            embedding: Optional pre-computed embedding
            
        Returns:
            Memory ID
        """
        collection = self.init_collection(collection_name)
        
        # Generate ID if not provided
        if not memory_id:
            memory_id = str(uuid.uuid4())
        
        # Add timestamp if not in metadata
        if "timestamp" not in metadata:
            metadata["timestamp"] = datetime.utcnow().isoformat()
        
        # Ensure all metadata values are valid types (str, int, float, bool)
        clean_metadata = self._clean_metadata(metadata)
        
        try:
            if embedding:
                collection.add(
                    documents=[content],
                    embeddings=[embedding],
                    metadatas=[clean_metadata],
                    ids=[memory_id]
                )
            else:
                # Let ChromaDB generate embedding using default model
                collection.add(
                    documents=[content],
                    metadatas=[clean_metadata],
                    ids=[memory_id]
                )
            
            logger.debug(f"Added memory '{memory_id}' to collection '{collection_name}'")
            return memory_id
            
        except Exception as e:
            logger.error(f"Failed to add memory to '{collection_name}': {e}")
            raise

    def add_memories_batch(
        self,
        collection_name: str,
        contents: List[str],
        metadatas: List[Dict[str, Any]],
        memory_ids: List[str] = None,
        embeddings: List[List[float]] = None
    ) -> List[str]:
        """
        Add multiple memories to a collection in a batch.
        
        Args:
            collection_name: Target collection name
            contents: List of text contents
            metadatas: List of metadata dicts
            memory_ids: Optional list of IDs
            embeddings: Optional list of pre-computed embeddings
            
        Returns:
            List of memory IDs
        """
        collection = self.init_collection(collection_name)
        
        if not memory_ids:
            memory_ids = [str(uuid.uuid4()) for _ in contents]
            
        clean_metadatas = [self._clean_metadata(m) for m in metadatas]
        
        try:
            if embeddings:
                collection.add(
                    documents=contents,
                    embeddings=embeddings,
                    metadatas=clean_metadatas,
                    ids=memory_ids
                )
            else:
                collection.add(
                    documents=contents,
                    metadatas=clean_metadatas,
                    ids=memory_ids
                )
            
            logger.info(f"Added {len(memory_ids)} memories to '{collection_name}' in batch")
            return memory_ids
            
        except Exception as e:
            logger.error(f"Batch add to '{collection_name}' failed: {e}")
            raise
    
    def search_memory(
        self,
        collection_name: str,
        query: str,
        filters: Dict[str, Any] = None,
        limit: int = 10,
        query_embedding: List[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar memories in a collection.
        
        Args:
            collection_name: Collection to search
            query: Search query text
            filters: Metadata filters (ChromaDB where clause)
            limit: Maximum results to return
            query_embedding: Optional pre-computed query embedding
            
        Returns:
            List of matching memories with id, content, metadata, distance
        """
        collection = self.init_collection(collection_name)
        
        if collection.count() == 0:
            return []
        
        try:
            if query_embedding:
                results = collection.query(
                    query_embeddings=[query_embedding],
                    n_results=min(limit, collection.count()),
                    where=filters
                )
            else:
                results = collection.query(
                    query_texts=[query],
                    n_results=min(limit, collection.count()),
                    where=filters
                )
            
            # Parse results into structured format
            memories = []
            if results and results['ids'] and len(results['ids']) > 0:
                for i, memory_id in enumerate(results['ids'][0]):
                    memories.append({
                        "id": memory_id,
                        "content": results['documents'][0][i] if results['documents'] else "",
                        "metadata": results['metadatas'][0][i] if results['metadatas'] else {},
                        "distance": results['distances'][0][i] if results['distances'] else 0.0
                    })
            
            logger.debug(f"Found {len(memories)} memories in '{collection_name}' for query")
            return memories
            
        except Exception as e:
            logger.error(f"Search failed in '{collection_name}': {e}")
            return []
    
    def delete_memory(self, collection_name: str, memory_id: str) -> bool:
        """
        Delete a memory by ID.
        
        Args:
            collection_name: Collection containing the memory
            memory_id: ID of memory to delete
            
        Returns:
            True if successful
        """
        collection = self.init_collection(collection_name)
        
        try:
            collection.delete(ids=[memory_id])
            logger.debug(f"Deleted memory '{memory_id}' from '{collection_name}'")
            return True
        except Exception as e:
            logger.error(f"Failed to delete memory '{memory_id}': {e}")
            return False
    
    def update_memory(
        self,
        collection_name: str,
        memory_id: str,
        content: str = None,
        metadata: Dict[str, Any] = None,
        embedding: List[float] = None
    ) -> bool:
        """
        Update a memory's content and/or metadata.
        
        Args:
            collection_name: Collection containing the memory
            memory_id: ID of memory to update
            content: New content (optional)
            metadata: New metadata (optional)
            embedding: New embedding (optional, required if content changes)
            
        Returns:
            True if successful
        """
        collection = self.init_collection(collection_name)
        
        try:
            update_kwargs = {"ids": [memory_id]}
            
            if content:
                update_kwargs["documents"] = [content]
            if metadata:
                update_kwargs["metadatas"] = [self._clean_metadata(metadata)]
            if embedding:
                update_kwargs["embeddings"] = [embedding]
            
            collection.update(**update_kwargs)
            logger.debug(f"Updated memory '{memory_id}' in '{collection_name}'")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update memory '{memory_id}': {e}")
            return False
    
    def get_memory(self, collection_name: str, memory_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific memory by ID.
        
        Args:
            collection_name: Collection containing the memory
            memory_id: ID of memory to retrieve
            
        Returns:
            Memory dict or None if not found
        """
        collection = self.init_collection(collection_name)
        
        try:
            results = collection.get(ids=[memory_id])
            
            if results and results['ids'] and len(results['ids']) > 0:
                return {
                    "id": results['ids'][0],
                    "content": results['documents'][0] if results['documents'] else "",
                    "metadata": results['metadatas'][0] if results['metadatas'] else {}
                }
            return None
            
        except Exception as e:
            logger.error(f"Failed to get memory '{memory_id}': {e}")
            return None
    
    def get_collection_stats(self, collection_name: str) -> Dict[str, Any]:
        """
        Get statistics for a collection.
        
        Args:
            collection_name: Collection name
            
        Returns:
            Stats dict with total_memories, collection_name, last_updated
        """
        collection = self.init_collection(collection_name)
        
        return {
            "total_memories": collection.count(),
            "collection_name": collection_name,
            "last_updated": datetime.utcnow().isoformat()
        }
    
    def clear_collection(self, collection_name: str) -> bool:
        """
        Clear all documents in a collection.
        
        Args:
            collection_name: Collection to clear
            
        Returns:
            True if successful
        """
        try:
            # Delete and recreate collection
            self.client.delete_collection(collection_name)
            
            # Remove from cache
            if collection_name in self._collections:
                del self._collections[collection_name]
            
            # Recreate empty collection
            self.init_collection(collection_name)
            
            logger.info(f"Cleared collection '{collection_name}'")
            return True
            
        except Exception as e:
            logger.error(f"Failed to clear collection '{collection_name}': {e}")
            return False
    
    def get_all_memories(
        self, 
        collection_name: str, 
        filters: Dict[str, Any] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get all memories from a collection with optional filters.
        
        Args:
            collection_name: Collection to query
            filters: Optional metadata filters
            limit: Maximum results
            
        Returns:
            List of memory dicts
        """
        collection = self.init_collection(collection_name)
        
        try:
            results = collection.get(
                where=filters,
                limit=limit
            )
            
            memories = []
            if results and results['ids']:
                for i, memory_id in enumerate(results['ids']):
                    memories.append({
                        "id": memory_id,
                        "content": results['documents'][i] if results['documents'] else "",
                        "metadata": results['metadatas'][i] if results['metadatas'] else {}
                    })
            
            return memories
            
        except Exception as e:
            logger.error(f"Failed to get all memories from '{collection_name}': {e}")
            return []
    
    def _clean_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Clean metadata to ensure all values are valid ChromaDB types.
        ChromaDB only supports str, int, float, bool for metadata values.
        """
        clean = {}
        for key, value in metadata.items():
            if value is None:
                continue
            elif isinstance(value, (str, int, float, bool)):
                clean[key] = value
            elif isinstance(value, datetime):
                clean[key] = value.isoformat()
            else:
                # Convert to string
                clean[key] = str(value)
        return clean


# Global vector store instance
_vector_store: Optional[VectorStore] = None


def get_vector_store() -> VectorStore:
    """Get or create the global VectorStore instance."""
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStore()
    return _vector_store
