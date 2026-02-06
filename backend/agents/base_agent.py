"""Nexus AI - Base Agent Definition.

This module defines the abstract base class for all specialized AI agents 
in the Nexus AI ecosystem. It provides core functionalities like tool usage, 
LLM interaction, memory retrieval, and state management.

Classes:
    BaseAgent: Abstract base class for all Nexus AI agents.
"""

import time
import os
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from datetime import datetime

from sqlalchemy.orm import Session

from llm.llm_manager import LLMManager
from utils.circuit_breaker import llm_circuit_breaker, search_circuit_breaker
from exceptions.custom_exceptions import AgentError, ToolExecutionError


class BaseAgent(ABC):
    """Abstract base class for specialized AI agents.
    
    All specialized agents (Research, Code, Content, etc.) must inherit 
    from this class and implement the `execute` method to define their 
    unique logic and tool integrations.
    
    Attributes:
        name (str): The unique identifier for the agent.
        role (str): A brief description of the agent's responsibilities.
        system_prompt (str): Instructions provided to the LLM for this agent.
        llm (LLMManager): Utility for generating responses from configured models.
        db (Session): Database session for persistence and context fetching.
        tools (list): A list of tool instances available for the agent to call.
    """
    
    def __init__(
        self,
        name: str,
        role: str,
        system_prompt: str,
        llm_manager: LLMManager = None,
        db_session: Session = None,
        tools: List[Any] = None
    ):
        """
        Initialize base agent.
        
        Args:
            name: Agent name (e.g., "ResearchAgent")
            role: Agent role description
            system_prompt: System prompt for LLM interactions
            llm_manager: LLM manager instance
            db_session: Database session
            tools: List of tool objects available to this agent
        """
        self.name = name
        self.role = role
        self.system_prompt = system_prompt
        self.llm = llm_manager
        self.db = db_session
        self.tools = tools or []
        
        # Execution tracking
        self._start_time = None
        self._tokens_used = 0
        
        # Create tool lookup dictionary
        self._tool_map = {tool.name: tool for tool in self.tools}
    
    @abstractmethod
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Main execution logic to be implemented by subclasses.
        
        Args:
            input_data: A dictionary containing task parameters and context.
            
        Returns:
            dict: The result of agent execution, including status and output.
        """
        pass
    
    async def use_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """Executes a registered tool by name with specified arguments.
        
        Integrates with circuit breakers for external service calls.
        
        Args:
            tool_name: The name of the tool to invoke.
            **kwargs: Arbitrary keyword arguments passed to the tool.
            
        Returns:
            dict: The standardized output from the tool execution.
        """
        if tool_name not in self._tool_map:
            error_msg = f"Tool '{tool_name}' not found. Available: {list(self._tool_map.keys())}"
            self.log_action("tool_error", {"tool": tool_name, "error": error_msg})
            return {"success": False, "error": error_msg}
        
        tool = self._tool_map[tool_name]
        
        try:
            self.log_action("tool_call", {"tool": tool_name, "params": kwargs})
            
            # Apply search circuit breaker for web search tool
            if tool_name in ["WebSearch", "Scraper"]:
                result = await search_circuit_breaker.call(tool.execute_async, **kwargs)
            else:
                if hasattr(tool, 'execute_async'):
                    result = await tool.execute_async(**kwargs)
                else:
                    result = tool.execute(**kwargs)
                
            self.log_action("tool_result", {"tool": tool_name, "success": result.get("success", False)})
            return result
        except Exception as e:
            error_msg = f"Tool '{tool_name}' failed: {str(e)}"
            self.log_action("tool_error", {"tool": tool_name, "error": error_msg})
            if "Circuit Breaker" in str(e):
                return {"success": False, "error": f"Service temporarily unavailable: {str(e)}", "retryable": False}
            return {"success": False, "error": error_msg}
    
    def generate_response(
        self, 
        prompt: str, 
        context: Dict[str, Any] = None,
        use_cache: bool = True
    ) -> Optional[str]:
        """Synthesizes a response from the LLM based on prompt and context.
        
        Args:
            prompt: The specific instruction or query for the LLM.
            context: Optional metadata or data to append to the prompt.
            use_cache: Whether to use recent cached responses for speed.
            
        Returns:
            Optional[str]: The generated text from the LLM, or an error message.
        """
        # Build full prompt
        full_prompt = prompt
        
        if context:
            context_str = "\n".join([f"{k}: {v}" for k, v in context.items()])
            full_prompt = f"Context:\n{context_str}\n\nTask: {prompt}"
        
        # Call LLM directly (circuit breaker was async and caused issues)
        if not self.llm:
            self.log_action("llm_error", {"error": "LLM manager not initialized"})
            return None
        
        try:
            response = self.llm.generate(
                prompt=full_prompt,
                system=self.system_prompt,
                use_cache=use_cache
            )
            
            if response:
                # Estimate tokens (rough)
                self._tokens_used += len(prompt.split()) + len(response.split())
            
            return response
        except Exception as e:
            self.log_action("llm_error", {"error": str(e)})
            return None
    
    def log_action(self, action: str, details: Dict[str, Any] = None):
        """
        Log an agent action.
        
        Args:
            action: Action type
            details: Additional details
        """
        log_entry = {
            "agent": self.name,
            "action": action,
            "details": details or {},
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Print to console for now
        print(f"🤖 [{self.name}] {action}: {details}")
        
        # TODO: Save to database agent_logs table
    
    def get_memory(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve relevant memories using the vector store.
        
        Args:
            query: Search query
            limit: Max results
            
        Returns:
            List of relevant memories
        """
        try:
            from memory.vector_store import get_vector_store, VectorStore
            
            vector_store = get_vector_store()
            
            # Search agent outputs for relevant past work
            memories = vector_store.search_memory(
                collection_name=VectorStore.AGENT_OUTPUTS,
                query=query,
                filters={"agent_name": self.name} if self.name else None,
                limit=limit
            )
            
            self.log_action("memory_retrieved", {"count": len(memories)})
            return memories
            
        except ImportError:
            self.log_action("memory_not_available", {})
            return []
        except Exception as e:
            self.log_action("memory_error", {"error": str(e)})
            return []
    
    def save_to_memory(self, content: str, metadata: Dict[str, Any] = None):
        """
        Save content to memory using the vector store.
        
        Args:
            content: Content to save
            metadata: Optional metadata (user_id, task_id, etc.)
        """
        try:
            from memory.vector_store import get_vector_store, VectorStore
            from memory.embeddings import get_embedding_manager
            
            vector_store = get_vector_store()
            embedding_manager = get_embedding_manager()
            
            # Generate embedding
            embedding = embedding_manager.generate_embedding(content)
            
            # Build metadata
            mem_metadata = metadata or {}
            mem_metadata["agent_name"] = self.name
            
            # Save to agent outputs collection
            memory_id = vector_store.add_memory(
                collection_name=VectorStore.AGENT_OUTPUTS,
                content=content,
                metadata=mem_metadata,
                embedding=embedding
            )
            
            self.log_action("memory_saved", {"memory_id": memory_id, "content_length": len(content)})
            
        except ImportError:
            self.log_action("memory_not_available", {})
        except Exception as e:
            self.log_action("memory_save_error", {"error": str(e)})
    
    
    def validate_input(
        self, 
        input_data: Dict[str, Any], 
        required_fields: List[str]
    ) -> bool:
        """Checks if the input dictionary contains all necessary keys.
        
        Args:
            input_data: The raw input provided to the agent.
            required_fields: A list of keys that must be present.
            
        Returns:
            bool: True if all fields are present.
            
        Raises:
            ValueError: If any required fields are missing.
        """
        missing = [f for f in required_fields if f not in input_data]
        
        if missing:
            raise ValueError(f"Missing required fields: {missing}")
        
        return True
    
    def format_output(
        self, 
        data: Any, 
        status: str = "success",
        error: str = None
    ) -> Dict[str, Any]:
        """
        Format agent output in standard structure.
        
        Args:
            data: Output data
            status: "success" or "error"
            error: Error message if status is "error"
            
        Returns:
            Formatted output dictionary
        """
        execution_time = 0
        if self._start_time:
            execution_time = round(time.time() - self._start_time, 2)
        
        output = {
            "status": status,
            "output": data,
            "agent_name": self.name,
            "execution_time_seconds": execution_time,
            "tokens_used": self._tokens_used,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if error:
            output["error"] = error
        
        return output
    
    def start_execution(self):
        """Mark the start of execution for timing."""
        self._start_time = time.time()
        self._tokens_used = 0
        self.log_action("execution_started", {})
    
    def end_execution(self):
        """Mark the end of execution."""
        self.log_action("execution_completed", {
            "duration_seconds": round(time.time() - self._start_time, 2),
            "tokens_used": self._tokens_used
        })

    def _get_file_path(self, file_id: int) -> Optional[str]:
        """Resolve file_id to physical path using the database."""
        if not self.db:
            return None
        
        from models.file import File
        db_file = self.db.query(File).filter(File.id == file_id).first()
        if db_file and os.path.exists(db_file.file_path):
            return db_file.file_path
        return None

    def _read_file_content(self, file_id: int) -> Dict[str, Any]:
        """Read file content using FileProcessorTool."""
        file_path = self._get_file_path(file_id)
        if not file_path:
            return {"success": False, "error": "File not found"}
        
        tool = self._tool_map.get("FileProcessor")
        if not tool:
            # Fallback to simple text read if tool is missing
            try:
                with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                    return {"success": True, "content": f.read()}
            except Exception as e:
                return {"success": False, "error": str(e)}
        
        # Determine action based on extension
        ext = os.path.splitext(file_path)[1].lower().replace(".", "")
        action = "read_text"
        if ext == "csv": action = "read_csv"
        elif ext == "pdf": action = "read_pdf"
        elif ext in ["xlsx", "xls"]: action = "read_excel"
        elif ext == "json": action = "read_json"
        
        return tool.execute(action=action, file_path=file_path)
