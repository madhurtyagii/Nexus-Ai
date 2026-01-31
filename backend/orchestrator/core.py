"""Nexus AI - Orchestrator Core.

This module provides the primary logic for task decomposition, agent assignment, 
and multi-agent workflow coordination. It uses LLMs to analyze user prompts 
and breaks them down into executable subtasks assigned to specialized agents.

Classes:
    OrchestratorEngine: Coordinates the overall task execution lifecycle.
"""

import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from models.task import Task, Subtask, TaskStatus
from models.agent import Agent
from llm.llm_manager import llm_manager
from redis_client import enqueue_task
from backend.exceptions.custom_exceptions import TaskExecutionError, DatabaseError
from backend.utils.retries import retry


class OrchestratorEngine:
    """The central brain responsible for task analysis and execution planning.
    
    The OrchestratorEngine takes raw user prompts, analyzes their complexity 
    and requirements using LLMs, and converts them into a series of subtasks 
    that are then enqueued for background processing by specialized agents.
    
    Attributes:
        db (Session): SQLAlchemy database session for task persistence.
        llm (LLMManager): Utility for interacting with configured LLM models.
    """
    
    ANALYSIS_SYSTEM_PROMPT = """You are a task analyzer for an AI agent system.
    
Available agents:
- ResearchAgent: Web research, information gathering, fact-finding
- CodeAgent: Code generation, debugging, code review
- ContentAgent: Writing documentation, blogs, marketing copy
- DataAgent: Data analysis, visualization, SQL queries
- QAAgent: Quality assurance, validation, testing
- MemoryAgent: Context retrieval, user preference learning
- ManagerAgent: Task planning, coordination (use for complex multi-step tasks)

Analyze the user's task and respond with JSON only:
{
    "complexity_score": <float 0-1, where 0=trivial, 1=very complex>,
    "required_agents": [<list of agent names needed>],
    "task_type": "<research|coding|writing|data|mixed>",
    "estimated_time": "<e.g., '2 minutes', '10 minutes'>",
    "reasoning": "<brief explanation of why these agents>"
}"""

    def __init__(self, db: Session):
        """Initializes the OrchestratorEngine with a database session.
        
        Args:
            db: A SQLAlchemy database session object.
        """
        self.db = db
        self.llm = llm_manager
    
    @retry(exceptions=(Exception,), tries=3, delay=2)
    def analyze_task(self, user_prompt: str, user_id: int = 1) -> Dict[str, Any]:
        """Analyzes a user's task prompt to determine necessary agents and complexity.
        
        Uses the LLM to parse the intent, assign appropriate agents, estimate 
        execution time, and assign a complexity score.
        
        Args:
            user_prompt: The raw text description of the task from the user.
            user_id: ID of the user owning the task. Defaults to 1.
            
        Returns:
            dict: Analysis results containing 'complexity_score', 
                'required_agents', 'task_type', 'estimated_time', and 'reasoning'.
            
        Example:
            >>> engine = OrchestratorEngine(db)
            >>> analysis = engine.analyze_task("Write a blog post about AI")
            >>> print(analysis["required_agents"])
            ['ContentAgent']
        """
        print(f"🔍 Analyzing task: {user_prompt[:50]}...")
        
        response = self.llm.generate(
            prompt=f"Analyze this task: {user_prompt}",
            system=self.ANALYSIS_SYSTEM_PROMPT,
            use_cache=True
        )
        
        if not response:
            # Fallback analysis if LLM fails
            return self._fallback_analysis(user_prompt)
        
        try:
            # Try to parse JSON from response
            # Handle case where LLM wraps JSON in markdown code block
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                response = response.split("```")[1].split("```")[0]
            
            analysis = json.loads(response.strip())
            
            # Validate required fields
            analysis.setdefault("complexity_score", 0.3)
            analysis.setdefault("required_agents", ["ResearchAgent"])
            analysis.setdefault("task_type", "mixed")
            analysis.setdefault("estimated_time", "5 minutes")
            
            print(f"✅ Analysis: {analysis['required_agents']}, complexity={analysis['complexity_score']}")
            return analysis
            
        except json.JSONDecodeError:
            print(f"⚠️ Failed to parse LLM analysis, using fallback")
            return self._fallback_analysis(user_prompt)
    
    def _fallback_analysis(self, user_prompt: str) -> Dict[str, Any]:
        """Performs simple keyword-based analysis when the LLM is unavailable.
        
        Args:
            user_prompt: The raw task description.
            
        Returns:
            dict: Basic analysis mapping keywords to agents.
        """
        prompt_lower = user_prompt.lower()
        
        agents = []
        task_type = "mixed"
        complexity = 0.3
        
        # Keyword matching for agent selection
        if any(w in prompt_lower for w in ["research", "find", "search", "look up", "what is"]):
            agents.append("ResearchAgent")
            task_type = "research"
        
        if any(w in prompt_lower for w in ["code", "program", "function", "debug", "script", "python", "javascript"]):
            agents.append("CodeAgent")
            task_type = "coding"
            complexity = 0.5
        
        if any(w in prompt_lower for w in ["write", "draft", "blog", "article", "document", "email"]):
            agents.append("ContentAgent")
            task_type = "writing"
        
        if any(w in prompt_lower for w in ["analyze", "data", "chart", "graph", "csv", "statistics"]):
            agents.append("DataAgent")
            task_type = "data"
            complexity = 0.5
        
        # Default to Research if no match
        if not agents:
            agents = ["ResearchAgent"]
        
        # Complex tasks need Manager
        if len(agents) > 2 or len(user_prompt) > 500:
            agents.insert(0, "ManagerAgent")
            complexity = 0.7
        
        return {
            "complexity_score": complexity,
            "required_agents": agents,
            "task_type": task_type,
            "estimated_time": f"{len(agents) * 2} minutes",
            "reasoning": "Keyword-based fallback analysis"
        }
    
    def create_execution_plan(
        self, 
        task_id: int, 
        analysis: Dict[str, Any]
    ) -> List[int]:
        """Generates subtasks based on the provided task analysis.
        
        Args:
            task_id: The ID of the parent task row.
            analysis: The output of analyze_task() defining required agents.
            
        Returns:
            List[int]: A list of IDs for the newly created subtasks.
            
        Raises:
            ValueError: If the parent task_id does not exist.
        """
        required_agents = analysis.get("required_agents", ["ResearchAgent"])
        complexity = analysis.get("complexity_score", 0.3)
        
        # Get task details
        task = self.db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise ValueError(f"Task {task_id} not found")
        
        subtask_ids = []
        
        # Create subtask for each agent
        for i, agent_name in enumerate(required_agents):
            input_data = {
                "original_prompt": task.user_prompt,
                "agent_role": agent_name,
                "step_number": i + 1,
                "total_steps": len(required_agents),
                "complexity": complexity,
                "previous_context": []  # Will be populated during execution
            }
            
            subtask = Subtask(
                task_id=task_id,
                assigned_agent=agent_name,
                input_data=input_data,
                status=TaskStatus.QUEUED.value
            )
            
            self.db.add(subtask)
            self.db.flush()  # Get the ID before commit
            subtask_ids.append(subtask.id)
            
            print(f"📋 Created subtask {subtask.id} for {agent_name}")
        
        self.db.commit()
        
        print(f"✅ Created execution plan: {len(subtask_ids)} subtasks")
        return subtask_ids
    
    @retry(exceptions=(TaskExecutionError, DatabaseError), tries=3, delay=1)
    def execute_task(self, task_id: int) -> Dict[str, Any]:
        """Runs the complete end-to-end task execution pipeline.
        
        Orchestrates analysis, subtask creation, and enqueuing to background 
        workers.
        
        Args:
            task_id: The ID of the task to process.
            
        Returns:
            dict: Summary of the triggered execution, including subtask IDs.
            
        Raises:
            TaskExecutionError: If any stage of the pipeline fails.
            DatabaseError: If database persistence fails during the process.
        """
        print(f"🚀 Executing task {task_id}")
        
        try:
            # Get task
            task = self.db.query(Task).filter(Task.id == task_id).first()
            if not task:
                raise TaskExecutionError(f"Task {task_id} not found")
            
            # Analyze
            analysis = self.analyze_task(task.user_prompt)
            
            # Update task with analysis
            task.complexity_score = analysis.get("complexity_score", 0.3)
            task.status = TaskStatus.IN_PROGRESS.value
            self.db.commit()
            
            # Create execution plan
            subtask_ids = self.create_execution_plan(task_id, analysis)
            
            # Enqueue subtasks to Redis
            for subtask_id in subtask_ids:
                enqueue_task(subtask_id)
            
            return {
                "task_id": task_id,
                "status": "in_progress",
                "analysis": analysis,
                "subtask_ids": subtask_ids,
                "message": f"Created {len(subtask_ids)} subtasks"
            }
        except Exception as e:
            self.db.rollback()
            if isinstance(e, TaskExecutionError):
                raise e
            raise TaskExecutionError(f"Failed to execute task {task_id}: {str(e)}")
    
    def get_task_progress(self, task_id: int) -> Dict[str, Any]:
        """Retrieves and calculates the current progress of a task.
        
        Args:
            task_id: The ID of the task to check.
            
        Returns:
            dict: Progress report containing percentage complete, 
                subtask counts, and active agent details.
        """
        task = self.db.query(Task).filter(Task.id == task_id).first()
        if not task:
            return {"error": "Task not found"}
        
        subtasks = self.db.query(Subtask).filter(Subtask.task_id == task_id).all()
        
        total = len(subtasks)
        completed = len([s for s in subtasks if s.status == TaskStatus.COMPLETED.value])
        in_progress = len([s for s in subtasks if s.status == TaskStatus.IN_PROGRESS.value])
        failed = len([s for s in subtasks if s.status == TaskStatus.FAILED.value])
        
        progress = (completed / total * 100) if total > 0 else 0
        
        current_agent = None
        for s in subtasks:
            if s.status == TaskStatus.IN_PROGRESS.value:
                current_agent = s.assigned_agent
                break
        
        return {
            "task_id": task_id,
            "status": task.status,
            "progress_percentage": round(progress, 1),
            "current_agent": current_agent,
            "subtasks_completed": completed,
            "subtasks_in_progress": in_progress,
            "subtasks_failed": failed,
            "subtasks_total": total
        }
