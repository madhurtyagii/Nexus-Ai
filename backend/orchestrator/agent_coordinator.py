"""
Nexus AI - Agent Coordinator
Orchestrates multi-agent collaboration and workflows
"""

import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field, asdict

from sqlalchemy.orm import Session

from agents.agent_factory import AgentFactory
from messaging.message_broker import MessageBroker, MessageType, message_broker
from llm.llm_manager import LLMManager


class WorkflowStatus(Enum):
    """Status of a collaborative workflow."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    WAITING = "waiting"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class WorkflowStep:
    """A step in an agent workflow."""
    step_id: str
    agent_name: str
    action: str
    input_data: Dict[str, Any]
    depends_on: List[str] = field(default_factory=list)
    status: str = "pending"
    output: Dict[str, Any] = field(default_factory=dict)
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Workflow:
    """A multi-agent collaborative workflow."""
    workflow_id: str
    name: str
    description: str
    steps: List[WorkflowStep]
    status: str = "pending"
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    completed_at: Optional[str] = None
    final_output: Dict[str, Any] = field(default_factory=dict)
    
    def get_ready_steps(self) -> List[WorkflowStep]:
        """Get steps that are ready to execute (dependencies met)."""
        completed_ids = {s.step_id for s in self.steps if s.status == "completed"}
        ready = []
        
        for step in self.steps:
            if step.status == "pending":
                if all(dep in completed_ids for dep in step.depends_on):
                    ready.append(step)
        
        return ready
    
    def is_complete(self) -> bool:
        """Check if all steps are completed."""
        return all(s.status == "completed" for s in self.steps)
    
    def has_failed(self) -> bool:
        """Check if any step has failed."""
        return any(s.status == "failed" for s in self.steps)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "workflow_id": self.workflow_id,
            "name": self.name,
            "description": self.description,
            "steps": [s.to_dict() for s in self.steps],
            "status": self.status,
            "created_at": self.created_at,
            "completed_at": self.completed_at,
            "final_output": self.final_output
        }


class AgentCoordinator:
    """
    Coordinates multi-agent workflows and collaboration.
    
    Features:
    - Define and execute multi-step workflows
    - Handle agent dependencies
    - Data passing between agents
    - Parallel execution when possible
    """
    
    def __init__(
        self,
        db_session: Session,
        llm_manager: LLMManager,
        message_broker: MessageBroker = None
    ):
        self.db = db_session
        self.llm = llm_manager
        self.broker = message_broker or message_broker
        self.factory = AgentFactory(db_session=db_session, llm=llm_manager)
        
        # Active workflows
        self.workflows: Dict[str, Workflow] = {}
        
        # Step outputs for data passing
        self._step_outputs: Dict[str, Dict[str, Any]] = {}
    
    def create_workflow(
        self,
        name: str,
        description: str,
        steps: List[Dict[str, Any]]
    ) -> Workflow:
        """
        Create a new workflow definition.
        
        Args:
            name: Workflow name
            description: What this workflow does
            steps: List of step definitions
            
        Returns:
            Created Workflow object
        """
        import uuid
        workflow_id = str(uuid.uuid4())[:8]
        
        workflow_steps = []
        for i, step_def in enumerate(steps):
            step = WorkflowStep(
                step_id=step_def.get("id", f"step_{i}"),
                agent_name=step_def["agent"],
                action=step_def.get("action", "execute"),
                input_data=step_def.get("input", {}),
                depends_on=step_def.get("depends_on", [])
            )
            workflow_steps.append(step)
        
        workflow = Workflow(
            workflow_id=workflow_id,
            name=name,
            description=description,
            steps=workflow_steps
        )
        
        self.workflows[workflow_id] = workflow
        print(f"📋 Created workflow '{name}' with {len(steps)} steps")
        
        return workflow
    
    async def execute_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """
        Execute a workflow synchronously.
        
        Args:
            workflow_id: ID of workflow to execute
            
        Returns:
            Workflow results
        """
        if workflow_id not in self.workflows:
            return {"status": "error", "error": f"Workflow {workflow_id} not found"}
        
        workflow = self.workflows[workflow_id]
        workflow.status = WorkflowStatus.IN_PROGRESS.value
        
        print(f"🚀 Starting workflow: {workflow.name}")
        
        self._step_outputs[workflow_id] = {}
        
        while not workflow.is_complete() and not workflow.has_failed():
            # Get steps ready to execute
            ready_steps = workflow.get_ready_steps()
            
            if not ready_steps:
                if workflow.has_failed():
                    break
                # Stuck - no steps ready but not complete
                print("⚠️ Workflow stuck - no steps ready")
                workflow.status = WorkflowStatus.FAILED.value
                break
            
            # Execute ready steps
            for step in ready_steps:
                await self._execute_step(workflow, step)
        
        # Finalize workflow
        if workflow.is_complete():
            workflow.status = WorkflowStatus.COMPLETED.value
            workflow.completed_at = datetime.utcnow().isoformat()
            
            # Combine outputs
            workflow.final_output = {
                "steps": self._step_outputs.get(workflow_id, {}),
                "summary": self._generate_workflow_summary(workflow)
            }
            
            print(f"✅ Workflow '{workflow.name}' completed")
        else:
            workflow.status = WorkflowStatus.FAILED.value
            print(f"❌ Workflow '{workflow.name}' failed")
        
        return workflow.to_dict()
    
    async def _execute_step(self, workflow: Workflow, step: WorkflowStep):
        """Execute a single workflow step."""
        step.status = "in_progress"
        step.started_at = datetime.utcnow().isoformat()
        
        print(f"  🔄 Executing step '{step.step_id}' with {step.agent_name}")
        
        try:
            # Prepare input data with outputs from dependencies
            input_data = dict(step.input_data)
            
            for dep_id in step.depends_on:
                dep_output = self._step_outputs.get(workflow.workflow_id, {}).get(dep_id)
                if dep_output:
                    input_data[f"from_{dep_id}"] = dep_output
            
            # Create and execute agent
            agent = self.factory.create_agent(step.agent_name)
            result = await agent.execute(input_data)
            
            # Store output
            step.output = result
            step.status = "completed"
            step.completed_at = datetime.utcnow().isoformat()
            
            # Save for dependent steps
            if workflow.workflow_id not in self._step_outputs:
                self._step_outputs[workflow.workflow_id] = {}
            self._step_outputs[workflow.workflow_id][step.step_id] = result.get("output", result)
            
            print(f"  ✅ Step '{step.step_id}' completed")
            
        except Exception as e:
            step.status = "failed"
            step.output = {"error": str(e)}
            print(f"  ❌ Step '{step.step_id}' failed: {e}")
    
    def _generate_workflow_summary(self, workflow: Workflow) -> str:
        """Generate a summary of workflow results."""
        completed_steps = [s for s in workflow.steps if s.status == "completed"]
        
        summary_parts = [f"Workflow '{workflow.name}' completed {len(completed_steps)}/{len(workflow.steps)} steps."]
        
        for step in completed_steps:
            output = step.output.get("output", "")
            if isinstance(output, dict):
                output_preview = output.get("summary", str(output)[:100])
            else:
                output_preview = str(output)[:100]
            summary_parts.append(f"- {step.agent_name}: {output_preview}...")
        
        return "\n".join(summary_parts)
    
    # Predefined Workflow Templates
    
    async def research_and_report(
        self,
        topic: str,
        include_code_examples: bool = False
    ) -> Dict[str, Any]:
        """
        Research a topic and create a comprehensive report.
        
        Steps:
        1. ResearchAgent - Gather information
        2. ContentAgent - Write the report
        3. (Optional) CodeAgent - Generate code examples
        """
        steps = [
            {
                "id": "research",
                "agent": "ResearchAgent",
                "action": "research",
                "input": {
                    "action": "research",
                    "topic": topic,
                    "depth": "comprehensive"
                }
            },
            {
                "id": "write_report",
                "agent": "ContentAgent",
                "action": "write",
                "input": {
                    "action": "blog",
                    "topic": f"Comprehensive report on: {topic}",
                    "tone": "professional",
                    "length": "long"
                },
                "depends_on": ["research"]
            }
        ]
        
        if include_code_examples:
            steps.append({
                "id": "code_examples",
                "agent": "CodeAgent",
                "action": "generate",
                "input": {
                    "action": "generate",
                    "task": f"Generate practical code examples for: {topic}",
                    "language": "python"
                },
                "depends_on": ["research"]
            })
        
        workflow = self.create_workflow(
            name=f"Research Report: {topic[:30]}",
            description=f"Research {topic} and create a report",
            steps=steps
        )
        
        return await self.execute_workflow(workflow.workflow_id)
    
    async def analyze_and_visualize(
        self,
        data: Any,
        question: str = None
    ) -> Dict[str, Any]:
        """
        Analyze data and create visualizations/report.
        
        Steps:
        1. DataAgent - Analyze the data
        2. ContentAgent - Write insights report
        """
        steps = [
            {
                "id": "analyze",
                "agent": "DataAgent",
                "action": "analyze",
                "input": {
                    "action": "analyze",
                    "data": data,
                    "question": question
                }
            },
            {
                "id": "report",
                "agent": "ContentAgent",
                "action": "write",
                "input": {
                    "action": "blog",
                    "topic": f"Data Analysis Report: {question or 'Key Insights'}",
                    "tone": "analytical"
                },
                "depends_on": ["analyze"]
            }
        ]
        
        workflow = self.create_workflow(
            name="Data Analysis Report",
            description="Analyze data and create insights report",
            steps=steps
        )
        
        return await self.execute_workflow(workflow.workflow_id)
    
    async def code_review_and_document(
        self,
        code: str,
        language: str = "python"
    ) -> Dict[str, Any]:
        """
        Review code and generate documentation.
        
        Steps:
        1. CodeAgent - Review the code
        2. ContentAgent - Generate documentation
        """
        steps = [
            {
                "id": "review",
                "agent": "CodeAgent",
                "action": "review",
                "input": {
                    "action": "review",
                    "code": code,
                    "language": language
                }
            },
            {
                "id": "explain",
                "agent": "CodeAgent",
                "action": "explain",
                "input": {
                    "action": "explain",
                    "code": code,
                    "language": language
                }
            },
            {
                "id": "document",
                "agent": "ContentAgent",
                "action": "write",
                "input": {
                    "action": "docs",
                    "topic": "Code Documentation",
                    "code_reference": code
                },
                "depends_on": ["review", "explain"]
            }
        ]
        
        workflow = self.create_workflow(
            name="Code Review & Documentation",
            description="Review code and generate documentation",
            steps=steps
        )
        
        return await self.execute_workflow(workflow.workflow_id)
    
    def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a workflow."""
        if workflow_id in self.workflows:
            return self.workflows[workflow_id].to_dict()
        return None
    
    def list_workflows(self) -> List[Dict[str, Any]]:
        """List all workflows."""
        return [w.to_dict() for w in self.workflows.values()]


# Global coordinator instance (lazy initialization)
_coordinator = None

def get_coordinator(db_session: Session, llm_manager: LLMManager) -> AgentCoordinator:
    """Get or create the global coordinator instance."""
    global _coordinator
    if _coordinator is None:
        _coordinator = AgentCoordinator(db_session, llm_manager)
    return _coordinator
