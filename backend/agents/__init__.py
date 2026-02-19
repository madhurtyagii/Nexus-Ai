"""
Nexus AI - Agents Package
Export all agents
"""

from agents.base_agent import BaseAgent
from agents.agent_registry import AgentRegistry, agent_registry
from agents.agent_factory import AgentFactory, create_agent

def register_all_agents():
    """Import and register all specialized agents."""
    from agents.research_agent import ResearchAgent
    from agents.code_agent import CodeAgent
    from agents.content_agent import ContentAgent
    from agents.data_agent import DataAgent
    from agents.qa_agent import QAAgent
    from agents.manager_agent import ManagerAgent
    from agents.visual_agent import VisualAgent
    from agents.memory_agent import MemoryAgent
    
    return {
        "ResearchAgent": ResearchAgent,
        "CodeAgent": CodeAgent,
        "ContentAgent": ContentAgent,
        "DataAgent": DataAgent,
        "QAAgent": QAAgent,
        "ManagerAgent": ManagerAgent,
        "VisualAgent": VisualAgent,
        "MemoryAgent": MemoryAgent
    }

__all__ = [
    "BaseAgent",
    "AgentRegistry",
    "agent_registry", 
    "AgentFactory",
    "create_agent",
    "register_all_agents"
]

