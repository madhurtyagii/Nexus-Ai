"""
Nexus AI - Base Tool
Abstract base class for all tools
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List
from datetime import datetime


class BaseTool(ABC):
    """
    Abstract base class for all tools that agents can use.
    
    Tools provide specific capabilities like web search, scraping, etc.
    """
    
    def __init__(
        self,
        name: str,
        description: str,
        parameters: Dict[str, str] = None
    ):
        """
        Initialize base tool.
        
        Args:
            name: Tool name (e.g., "web_search")
            description: Human-readable description
            parameters: Dictionary describing expected parameters
        """
        self.name = name
        self.description = description
        self.parameters = parameters or {}
    
    @abstractmethod
    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Execute the tool.
        
        Must be implemented by child classes.
        
        Returns:
            Dictionary with keys: success (bool), data (any), error (str or None)
        """
        pass
    
    def validate_parameters(self, **kwargs) -> bool:
        """
        Validate that required parameters are provided.
        
        Args:
            **kwargs: Provided parameters
            
        Returns:
            True if valid
            
        Raises:
            ValueError: If missing required parameters
        """
        # Get required parameters (those without defaults)
        required = [
            name for name, desc in self.parameters.items()
            if "(required)" in desc.lower() or "(optional)" not in desc.lower()
        ]
        
        missing = [p for p in required if p not in kwargs or kwargs[p] is None]
        
        if missing:
            raise ValueError(f"Missing required parameters for {self.name}: {missing}")
        
        return True
    
    def log_usage(
        self, 
        agent_name: str, 
        result: Dict[str, Any],
        execution_time_ms: int = 0
    ):
        """
        Log tool usage.
        
        Args:
            agent_name: Name of the agent using this tool
            result: Execution result
            execution_time_ms: Execution time in milliseconds
        """
        log_entry = {
            "tool_name": self.name,
            "agent_name": agent_name,
            "success": result.get("success", False),
            "execution_time_ms": execution_time_ms,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Print for now - can add database logging later
        status = "✅" if result.get("success") else "❌"
        print(f"{status} Tool '{self.name}' used by {agent_name} ({execution_time_ms}ms)")
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert tool info to dictionary.
        
        Returns:
            Tool information dictionary
        """
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters
        }
