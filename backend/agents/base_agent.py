"""
Nexus AI - Base Agent
Abstract base class for all AI agents
"""

import time
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from datetime import datetime

from sqlalchemy.orm import Session

from llm.llm_manager import LLMManager


class BaseAgent(ABC):
    """
    Abstract base class for all AI agents.
    
    All specialized agents (Research, Code, Content, etc.)
    must inherit from this class and implement the execute() method.
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
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the agent's main task.
        
        Must be implemented by child classes.
        
        Args:
            input_data: Input data for the agent
            
        Returns:
            Output dictionary with keys: status, output, metadata
        """
        pass
    
    def use_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """
        Use a tool by name.
        
        Args:
            tool_name: Name of the tool to use
            **kwargs: Arguments to pass to the tool
            
        Returns:
            Tool execution result
        """
        if tool_name not in self._tool_map:
            error_msg = f"Tool '{tool_name}' not found. Available: {list(self._tool_map.keys())}"
            self.log_action("tool_error", {"tool": tool_name, "error": error_msg})
            return {"success": False, "error": error_msg}
        
        tool = self._tool_map[tool_name]
        
        try:
            self.log_action("tool_call", {"tool": tool_name, "params": kwargs})
            result = tool.execute(**kwargs)
            self.log_action("tool_result", {"tool": tool_name, "success": result.get("success", False)})
            return result
        except Exception as e:
            error_msg = f"Tool '{tool_name}' failed: {str(e)}"
            self.log_action("tool_error", {"tool": tool_name, "error": error_msg})
            return {"success": False, "error": error_msg}
    
    def generate_response(
        self, 
        prompt: str, 
        context: Dict[str, Any] = None,
        use_cache: bool = True
    ) -> Optional[str]:
        """
        Generate a response using the LLM.
        
        Args:
            prompt: User prompt
            context: Optional context to include
            use_cache: Whether to use cached responses
            
        Returns:
            LLM response or None if failed
        """
        # Build full prompt
        full_prompt = prompt
        
        if context:
            context_str = "\n".join([f"{k}: {v}" for k, v in context.items()])
            full_prompt = f"Context:\n{context_str}\n\nTask: {prompt}"
        
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
        Retrieve relevant memories.
        
        Placeholder for Phase 5 memory system.
        
        Args:
            query: Search query
            limit: Max results
            
        Returns:
            List of relevant memories
        """
        # Placeholder - will implement in Phase 5
        return []
    
    def save_to_memory(self, content: str, metadata: Dict[str, Any] = None):
        """
        Save content to memory.
        
        Placeholder for Phase 5 memory system.
        
        Args:
            content: Content to save
            metadata: Optional metadata
        """
        # Placeholder - will implement in Phase 5
        self.log_action("memory_save_attempt", {"content_length": len(content)})
    
    def validate_input(
        self, 
        input_data: Dict[str, Any], 
        required_fields: List[str]
    ) -> bool:
        """
        Validate that input contains all required fields.
        
        Args:
            input_data: Input dictionary
            required_fields: List of required field names
            
        Returns:
            True if valid
            
        Raises:
            ValueError: If missing required fields
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
