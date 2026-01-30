"""
Nexus AI - Agents Package
Export all agents
"""

from agents.base_agent import BaseAgent
from agents.agent_registry import AgentRegistry, agent_registry
from agents.agent_factory import AgentFactory, create_agent

# Import agents to register them
from agents.research_agent import ResearchAgent
from agents.code_agent import CodeAgent
from agents.content_agent import ContentAgent
from agents.data_agent import DataAgent
from agents.qa_agent import QAAgent
from agents.manager_agent import ManagerAgent

__all__ = [
    "BaseAgent",
    "AgentRegistry",
    "agent_registry", 
    "AgentFactory",
    "create_agent",
    "ResearchAgent",
    "CodeAgent",
    "ContentAgent",
    "DataAgent",
    "QAAgent",
    "ManagerAgent",
]

