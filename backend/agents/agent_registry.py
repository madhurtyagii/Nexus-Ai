"""
Nexus AI - Agent Registry
Singleton registry for managing all AI agents
"""

from typing import Dict, Type, List, Any, Optional
from sqlalchemy.orm import Session

from llm.llm_manager import LLMManager


class AgentRegistry:
    """
    Singleton registry for AI agents.
    
    Maintains a mapping of agent names to agent classes.
    Supports decorator-based registration.
    """
    
    _instance = None
    _agents: Dict[str, Type] = {}
    _lazy_agents: Dict[str, str] = {
        "ResearchAgent": "agents.research_agent.ResearchAgent",
        "CodeAgent": "agents.code_agent.CodeAgent",
        "ContentAgent": "agents.content_agent.ContentAgent",
        "DataAgent": "agents.data_agent.DataAgent",
        "QAAgent": "agents.qa_agent.QAAgent",
        "ManagerAgent": "agents.manager_agent.ManagerAgent",
    }
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    def register(cls, agent_class: Type = None, name: str = None):
        """
        Register an agent class (eager or lazy).
        """
        def decorator(cls_to_register):
            agent_name = name or cls_to_register.__name__
            AgentRegistry._agents[agent_name] = cls_to_register
            # Remove from lazy if it's already loaded
            if agent_name in AgentRegistry._lazy_agents:
                del AgentRegistry._lazy_agents[agent_name]
            print(f"✅ Registered agent: {agent_name}")
            return cls_to_register
        
        if agent_class is not None:
            return decorator(agent_class)
        else:
            return decorator
    
    @classmethod
    def get_agent_class(cls, agent_name: str) -> Optional[Type]:
        """
        Get an agent class by name, loading it lazily if necessary.
        """
        if agent_name in cls._agents:
            return cls._agents[agent_name]
        
        if agent_name in cls._lazy_agents:
            module_path = cls._lazy_agents[agent_name]
            try:
                import importlib
                module_name, class_name = module_path.rsplit(".", 1)
                print(f"🚚 Lazy loading agent: {agent_name} from {module_name}")
                module = importlib.import_module(module_name)
                cls_to_register = getattr(module, class_name)
                cls._agents[agent_name] = cls_to_register
                del cls._lazy_agents[agent_name]
                return cls_to_register
            except Exception as e:
                print(f"❌ Failed to lazy load agent {agent_name}: {e}")
                return None
            
        return None
    
    @classmethod
    def get_agent(cls, agent_name: str, **kwargs):
        """
        Get an agent. If kwargs are provided, returns an instance.
        Otherwise returns the class.
        """
        if kwargs:
            return cls.get_agent_full(agent_name, **kwargs)
        return cls._agents.get(agent_name)
    
    @classmethod
    def get_agent_full(
        cls, 
        agent_name: str, 
        llm_manager: LLMManager,
        db_session: Session,
        tools: List[Any] = None
    ):
        """
        Create and return an agent instance with all dependencies.
        
        Args:
            agent_name: Name of the agent
            llm_manager: LLM manager instance
            db_session: Database session
            tools: Optional list of tools
            
        Returns:
            Agent instance
            
        Raises:
            ValueError: If agent not found
        """
        agent_class = cls.get_agent_class(agent_name)
        
        if agent_class is None:
            available = list(cls._agents.keys())
            raise ValueError(f"Agent '{agent_name}' not found. Available: {available}")
        
        return agent_class(
            llm_manager=llm_manager,
            db_session=db_session,
            tools=tools or []
        )
    
    @classmethod
    def list_agents(cls) -> List[str]:
        """
        List all registered agent names.
        
        Returns:
            List of agent names
        """
        return list(cls._agents.keys())
    
    @classmethod
    def get_agent_info(cls, agent_name: str) -> Dict[str, Any]:
        """
        Get information about an agent.
        
        Args:
            agent_name: Name of the agent
            
        Returns:
            Agent information dictionary
        """
        agent_class = cls.get_agent_class(agent_name)
        
        if agent_class is None:
            return {"error": f"Agent '{agent_name}' not found"}
        
        # Get info from class attributes
        return {
            "name": agent_name,
            "class": agent_class.__name__,
            "role": getattr(agent_class, 'DEFAULT_ROLE', 'Unknown'),
            "description": agent_class.__doc__ or "No description"
        }
    
    @classmethod
    def clear(cls):
        """Clear all registered agents (for testing)."""
        cls._agents = {}


# Global registry instance
agent_registry = AgentRegistry()
