"""
Nexus AI - Vector Store
ChromaDB wrapper for storing and retrieving memories using embeddings
"""

import os
import uuid
import json
import numpy as np
from datetime import datetime
from typing import Dict, List, Any, Optional

from logging_config import get_logger
logger = get_logger(__name__)

# --- modern ChromaDB Handle ---
CHROMADB_AVAILABLE = False
try:
    import chromadb
    from chromadb.config import Settings as ChromaSettings
    CHROMADB_AVAILABLE = True
except Exception as e:
    import traceback
    logger.error(f"❌ Failed to import chromadb:\n{traceback.format_exc()}")
    chromadb = None
    ChromaSettings = None

class ResilientNumpyStore:
    """
    A lightweight, persistent vector store using Numpy for similarity 
    and JSON for storage. Isolated by collection.
    """
    def __init__(self, persist_directory: str):
        self.persist_directory = persist_directory
        self.data_file = os.path.join(persist_directory, "resilient_storage.json")
        self.embeddings_file = os.path.join(persist_directory, "resilient_embeddings.npy")
        self.collections_data = {} # {collection_name: [memories]}
        self.collections_embeddings = {} # {collection_name: [embeddings]}
        self._load()

    def _load(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r") as f:
                    full_data = json.load(f)
                    
                # New format is a dict of collections
                if isinstance(full_data, dict):
                    self.collections_data = full_data
                    
                    # Also load embeddings if dict
                    if os.path.exists(self.embeddings_file):
                        try:
                            raw_emb = np.load(self.embeddings_file, allow_pickle=True).item()
                            if isinstance(raw_emb, dict):
                                self.collections_embeddings = raw_emb
                        except Exception:
                            logger.warning("Could not load embeddings dict, initializing fresh.")
                else:
                    # Legacy format was a list - WIPE IT (it was test data)
                    logger.info("🗑️ Legacy resilient storage detected. Wiping for fresh start.")
                    self.collections_data = {}
                    self.collections_embeddings = {}
                
                logger.info(f"💾 Loaded collections: {list(self.collections_data.keys())}")
            except Exception as e:
                logger.error(f"Failed to load resilient storage: {e}")

    def _save(self):
        try:
            os.makedirs(self.persist_directory, exist_ok=True)
            with open(self.data_file, "w") as f:
                json.dump(self.collections_data, f)
            np.save(self.embeddings_file, np.array(self.collections_embeddings))
        except Exception as e:
            logger.error(f"Failed to save resilient storage: {e}")

    def add(self, collection_name: str, content: str, metadata: dict, memory_id: str, embedding: List[float]):
        if collection_name not in self.collections_data:
            self.collections_data[collection_name] = []
            self.collections_embeddings[collection_name] = []
            
        self.collections_data[collection_name].append({
            "id": memory_id,
            "content": content,
            "metadata": metadata
        })
        self.collections_embeddings[collection_name].append(embedding)
        self._save()

    def search(self, collection_name: str, query_embedding: List[float], limit: int, filters: dict = None) -> List[dict]:
        mems = self.collections_data.get(collection_name, [])
        embs = self.collections_embeddings.get(collection_name, [])
        
        if not embs or not mems:
            return []
        
        embeddings_array = np.array(embs)
        query_array = np.array(query_embedding)
        
        norms = np.linalg.norm(embeddings_array, axis=1)
        query_norm = np.linalg.norm(query_array)
        
        if query_norm == 0: return []
            
        similarities = np.dot(embeddings_array, query_array) / (norms * query_norm + 1e-9)
        indices = np.argsort(similarities)[::-1]
        
        results = []
        for idx in indices:
            memory = mems[idx]
            if filters:
                match = True
                for k, v in filters.items():
                    if isinstance(v, dict) and "$in" in v:
                        if memory["metadata"].get(k) not in v["$in"]:
                            match = False; break
                    elif memory["metadata"].get(k) != v:
                        match = False; break
                if not match: continue

            results.append({
                "id": memory["id"],
                "content": memory["content"],
                "metadata": memory["metadata"],
                "distance": float(1.0 - similarities[idx])
            })
            if len(results) >= limit: break
        return results

class VectorStore:
    """
    ChromaDB-based vector store for semantic memory storage and retrieval.
    (With in-memory fallback if ChromaDB is unavailable)
    """
    
    # Collection names
    CONVERSATION_HISTORY = "conversation_history"
    AGENT_OUTPUTS = "agent_outputs"
    USER_PREFERENCES = "user_preferences"
    DOMAIN_KNOWLEDGE = "domain_knowledge"
    TASK_CONTEXT = "task_context"
    
    def __init__(self, persist_directory: str = None):
        """Initialize ChromaDB client or resilient fallback."""
        raw_dir = persist_directory or os.getenv("CHROMADB_DIR", "./data/chromadb")
        self.persist_directory = os.path.abspath(raw_dir)
        self._collections = {}
        self.resilient_store = ResilientNumpyStore(self.persist_directory)
        
        if CHROMADB_AVAILABLE:
            try:
                os.makedirs(self.persist_directory, exist_ok=True)
                self.client = chromadb.PersistentClient(
                    path=self.persist_directory,
                    settings=ChromaSettings(anonymized_telemetry=False, allow_reset=True)
                )
                logger.info(f"✅ VectorStore initialized with ChromaDB at: {self.persist_directory}")
            except Exception as e:
                logger.warning(f"⚠️ ChromaDB failed to init: {e}. Using Resilient Storage.")
                self.client = None
        else:
            self.client = None
            logger.warning("🛡️ VectorStore using Resilient Numpy Storage (Persistence Active)")
    
    def init_collection(self, collection_name: str, metadata: Dict[str, Any] = None):
        if not self.client: return None
        if collection_name in self._collections: return self._collections[collection_name]
        try:
            collection = self.client.get_or_create_collection(
                name=collection_name,
                metadata=metadata or {"created_at": datetime.utcnow().isoformat()}
            )
            self._collections[collection_name] = collection
            return collection
        except Exception:
            return None

    def _get_embedding(self, text: str) -> List[float]:
        # Simple content-aware fallback embedding logic.
        # Not a real model, but prevents all chunks from being identical.
        import hashlib
        h = hashlib.md5(text.encode()).digest()
        # Convert hash to a 1536-dim vector by repetition and normalization
        vec = []
        for i in range(1536):
            # Use hash bytes and a bit of position-based math
            val = h[i % len(h)] * (1 + (i % 17))
            vec.append(float(val % 100) / 100.0)
        return vec
    
    def add_memory(self, collection_name: str, content: str, metadata: Dict[str, Any], memory_id: str = None, embedding: List[float] = None) -> str:
        memory_id = memory_id or str(uuid.uuid4())
        metadata = self._clean_metadata(metadata)
        if "timestamp" not in metadata:
            metadata["timestamp"] = datetime.utcnow().isoformat()
            
        # 1. Try Resilient Storage (always backup)
        emb = embedding or self._get_embedding(content)
        self.resilient_store.add(collection_name, content, metadata, memory_id, emb)

        # 2. Try ChromaDB
        collection = self.init_collection(collection_name)
        if collection:
            try:
                collection.add(
                    documents=[content], 
                    metadatas=[metadata], 
                    ids=[memory_id], 
                    embeddings=[embedding] if embedding else None
                )
            except Exception as e:
                logger.error(f"ChromaDB add failed: {e}")
        
        return memory_id

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
    
    def search_memory(self, collection_name: str, query: str, filters: Dict[str, Any] = None, limit: int = 10, query_embedding: List[float] = None) -> List[Dict[str, Any]]:
        # 1. Try ChromaDB first if available
        collection = self.init_collection(collection_name)
        if collection:
            try:
                results = collection.query(
                    query_texts=[query] if not query_embedding else None,
                    query_embeddings=[query_embedding] if query_embedding else None,
                    n_results=min(limit, collection.count() or 1),
                    where=filters
                )
                memories = []
                if results and results['ids'] and len(results['ids']) > 0:
                    for i, m_id in enumerate(results['ids'][0]):
                        memories.append({
                            "id": m_id,
                            "content": results['documents'][0][i],
                            "metadata": results['metadatas'][0][i],
                            "distance": results['distances'][0][i] if 'distances' in results else 0.0
                        })
                    if memories:
                        return memories
            except Exception as e:
                logger.error(f"ChromaDB search failed: {e}. Falling back.")

        # 2. Fallback to Resilient Storage
        emb = query_embedding or self._get_embedding(query)
        return self.resilient_store.search(collection_name, emb, limit, filters)
    
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
