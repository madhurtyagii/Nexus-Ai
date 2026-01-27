"""
Nexus AI - Agent Factory
Factory for creating agent instances with proper configuration
"""

from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session

from agents.agent_registry import AgentRegistry
from llm.llm_manager import LLMManager, llm_manager
from tools.tool_registry import ToolRegistry


class AgentFactory:
    """
    Factory for creating configured agent instances.
    
    Handles:
    - Looking up agents in registry
    - Configuring with appropriate tools
    - Injecting dependencies (LLM, DB)
    """
    
    # Map agent names to their required tools
    AGENT_TOOLS = {
        "ResearchAgent": ["web_search", "web_scraper"],
        "CodeAgent": ["code_executor", "file_manager"],
        "ContentAgent": [],  # Uses LLM only
        "DataAgent": ["data_analyzer"],
        "QAAgent": [],  # Uses LLM only
        "MemoryAgent": ["memory_store"],
        "ManagerAgent": [],  # Uses LLM only
    }
    
    def __init__(self, db_session: Session = None, llm: LLMManager = None):
        """
        Initialize factory.
        
        Args:
            db_session: Database session
            llm: LLM manager (defaults to global instance)
        """
        self.db = db_session
        self.llm = llm or llm_manager
        self.tool_registry = ToolRegistry()
    
    def create_agent(
        self, 
        agent_name: str,
        additional_tools: List[str] = None
    ):
        """
        Create a fully configured agent instance.
        
        Args:
            agent_name: Name of the agent to create
            additional_tools: Extra tools to attach
            
        Returns:
            Configured agent instance
        """
        # Get required tools for this agent
        required_tool_names = self.AGENT_TOOLS.get(agent_name, [])
        
        if additional_tools:
            required_tool_names = list(set(required_tool_names + additional_tools))
        
        # Get tool instances
        tools = []
        for tool_name in required_tool_names:
            try:
                tool = self.tool_registry.get_tool(tool_name)
                if tool:
                    tools.append(tool)
            except Exception as e:
                print(f"⚠️ Tool '{tool_name}' not available: {e}")
        
        # Create agent instance
        agent = AgentRegistry.get_agent(
            agent_name=agent_name,
            llm_manager=self.llm,
            db_session=self.db,
            tools=tools
        )
        
        return agent
    
    def create_multiple(
        self, 
        agent_names: List[str]
    ) -> Dict[str, Any]:
        """
        Create multiple agent instances.
        
        Args:
            agent_names: List of agent names to create
            
        Returns:
            Dictionary mapping agent names to instances
        """
        agents = {}
        
        for name in agent_names:
            try:
                agents[name] = self.create_agent(name)
            except Exception as e:
                print(f"⚠️ Failed to create agent '{name}': {e}")
                agents[name] = None
        
        return agents
    
    @classmethod
    def get_available_agents(cls) -> List[str]:
        """
        Get list of all available agent names.
        
        Returns:
            List of agent names
        """
        return AgentRegistry.list_agents()


# Convenience function
def create_agent(agent_name: str, db_session: Session = None):
    """
    Quick helper to create an agent.
    
    Args:
        agent_name: Name of the agent
        db_session: Optional database session
        
    Returns:
        Agent instance
    """
    factory = AgentFactory(db_session=db_session)
    return factory.create_agent(agent_name)
