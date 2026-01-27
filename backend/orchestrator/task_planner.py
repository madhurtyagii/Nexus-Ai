"""
Nexus AI - Task Planner
Breaks down complex tasks into sequential steps with dependencies
"""

import json
from typing import Dict, List, Any, Optional
from collections import defaultdict

from llm.llm_manager import llm_manager


class TaskPlanner:
    """
    Decomposes complex tasks into step-by-step subtasks
    with dependency resolution and execution ordering.
    """
    
    DECOMPOSITION_PROMPT = """You are a task decomposition expert.
Break down this task into sequential steps that can be executed by specialized agents.

Available agents:
- ResearchAgent: Web research, fact-finding
- CodeAgent: Code generation, debugging
- ContentAgent: Writing, documentation
- DataAgent: Data analysis, visualization
- QAAgent: Quality validation
- MemoryAgent: Context retrieval
- ManagerAgent: Coordination

Task: {user_prompt}
Required agents: {agents}

Respond with JSON only:
{{
    "steps": [
        {{
            "step_number": 1,
            "agent": "<agent name>",
            "instruction": "<specific instruction for this agent>",
            "dependencies": [],
            "estimated_seconds": 30
        }}
    ]
}}

Rules:
- Order steps logically (research before analysis, analysis before writing)
- Include dependencies as list of step_numbers that must complete first
- Keep instructions specific and actionable
- Estimate realistic time for each step"""

    def __init__(self):
        """Initialize task planner."""
        self.llm = llm_manager
    
    def decompose_task(
        self, 
        user_prompt: str, 
        required_agents: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Break complex prompt into step-by-step subtasks.
        
        Args:
            user_prompt: The user's task description
            required_agents: List of agents to use
            
        Returns:
            List of step dictionaries
        """
        prompt = self.DECOMPOSITION_PROMPT.format(
            user_prompt=user_prompt,
            agents=", ".join(required_agents)
        )
        
        response = self.llm.generate(prompt, use_cache=True)
        
        if not response:
            return self._fallback_decomposition(user_prompt, required_agents)
        
        try:
            # Parse JSON from response
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                response = response.split("```")[1].split("```")[0]
            
            data = json.loads(response.strip())
            steps = data.get("steps", [])
            
            # Validate steps
            valid_steps = []
            for step in steps:
                if "step_number" in step and "agent" in step and "instruction" in step:
                    step.setdefault("dependencies", [])
                    step.setdefault("estimated_seconds", 30)
                    valid_steps.append(step)
            
            return valid_steps if valid_steps else self._fallback_decomposition(user_prompt, required_agents)
            
        except json.JSONDecodeError:
            return self._fallback_decomposition(user_prompt, required_agents)
    
    def _fallback_decomposition(
        self, 
        user_prompt: str, 
        required_agents: List[str]
    ) -> List[Dict[str, Any]]:
        """Simple fallback decomposition - one step per agent."""
        steps = []
        for i, agent in enumerate(required_agents):
            steps.append({
                "step_number": i + 1,
                "agent": agent,
                "instruction": f"Process the following task using your expertise: {user_prompt}",
                "dependencies": [i] if i > 0 else [],  # Each step depends on previous
                "estimated_seconds": 30
            })
        return steps
    
    def determine_execution_order(
        self, 
        steps: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Resolve dependencies and create execution order.
        
        Uses topological sort to determine order.
        Identifies which steps can run in parallel.
        
        Args:
            steps: List of step dictionaries with dependencies
            
        Returns:
            Execution order with sequential and parallel groups
        """
        if not steps:
            return {"sequential_groups": [], "parallel_groups": []}
        
        # Build dependency graph
        step_map = {s["step_number"]: s for s in steps}
        in_degree = defaultdict(int)
        dependents = defaultdict(list)
        
        for step in steps:
            step_num = step["step_number"]
            in_degree[step_num] = len(step.get("dependencies", []))
            for dep in step.get("dependencies", []):
                dependents[dep].append(step_num)
        
        # Topological sort with level tracking
        sequential_groups = []
        remaining = set(step_map.keys())
        
        while remaining:
            # Find all steps with no remaining dependencies
            ready = [s for s in remaining if in_degree[s] == 0]
            
            if not ready:
                # Circular dependency - break by taking first remaining
                ready = [min(remaining)]
            
            sequential_groups.append(ready)
            
            # Remove processed steps and update dependencies
            for step_num in ready:
                remaining.discard(step_num)
                for dependent in dependents[step_num]:
                    in_degree[dependent] -= 1
        
        # Identify parallel groups (steps at same level with no cross-dependencies)
        parallel_groups = []
        for group in sequential_groups:
            if len(group) > 1:
                parallel_groups.append(group)
        
        return {
            "sequential_groups": sequential_groups,
            "parallel_groups": parallel_groups,
            "total_steps": len(steps)
        }
    
    def estimate_resources(self, steps: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate estimated tokens and time.
        
        Args:
            steps: List of step dictionaries
            
        Returns:
            Resource estimates
        """
        if not steps:
            return {"estimated_tokens": 0, "estimated_time_seconds": 0}
        
        # Count words in all instructions
        total_words = sum(
            len(step.get("instruction", "").split())
            for step in steps
        )
        
        # Estimate tokens (words × 1.5 for input, 2× for estimated output)
        estimated_tokens = int(total_words * 1.5 * 3)  # Input + output + system prompts
        
        # Sum estimated time from steps, or default to 30s per step
        estimated_time = sum(
            step.get("estimated_seconds", 30)
            for step in steps
        )
        
        return {
            "estimated_tokens": estimated_tokens,
            "estimated_time_seconds": estimated_time,
            "step_count": len(steps)
        }


# Global planner instance
task_planner = TaskPlanner()
