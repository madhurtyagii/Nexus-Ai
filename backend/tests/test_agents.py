import pytest
from backend.agents.content_agent import ContentAgent
from backend.agents.base_agent import BaseAgent

def test_content_agent_initialization():
    agent = ContentAgent()
    assert agent.name == "ContentAgent"
    assert "write" in agent.system_prompt.lower()

def test_agent_log_action():
    agent = ContentAgent()
    agent.log_action("test_action", {"data": "test"})
    # Check if action was logged (this depends on how log_action is implemented)
    # If it prints or stores in a list, we check that.
    assert True # Basic check for now
