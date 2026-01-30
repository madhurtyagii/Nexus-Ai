"""
Nexus AI - Manager Agent
Project planning and multi-agent coordination
"""

import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime

from agents.base_agent import BaseAgent
from agents.agent_registry import AgentRegistry
from tools.project_planner import ProjectPlannerTool
from tools.task_scheduler import TaskSchedulerTool
from llm.llm_manager import llm_manager


@AgentRegistry.register
class ManagerAgent(BaseAgent):
    """
    Manager Agent for project planning and agent coordination.
    
    Responsibilities:
    - Analyze project complexity
    - Break down projects into phases and tasks
    - Assign tasks to appropriate agents
    - Create dependency graphs and schedules
    - Monitor project progress
    - Generate project summaries
    """
    
    SYSTEM_PROMPT = """You are a project manager for an AI agent system.

Your responsibilities:
1. Analyze project requirements and complexity
2. Break down complex projects into manageable phases and tasks
3. Assign tasks to the most appropriate specialized agents:
   - ResearchAgent: Web research, information gathering
   - CodeAgent: Programming, code generation
   - ContentAgent: Writing, documentation
   - DataAgent: Data analysis, visualization
   - QAAgent: Quality assurance, validation
4. Create realistic timelines and schedules
5. Identify dependencies between tasks
6. Coordinate agent work and track progress
7. Generate comprehensive project summaries

Think strategically. Plan thoroughly. Optimize for efficiency and quality."""

    def __init__(self):
        super().__init__(
            name="ManagerAgent",
            role="Project planning and agent coordination",
            system_prompt=self.SYSTEM_PROMPT
        )
        
        # Attach planning tools
        self.project_planner = ProjectPlannerTool()
        self.task_scheduler = TaskSchedulerTool()
        self.tools = [self.project_planner, self.task_scheduler]
        
        # Configuration
        self.max_project_duration = 60 * 60  # 1 hour in seconds
        self.complexity_threshold = 0.7  # Above this, use detailed planning
    
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute project planning and coordination.
        
        Args:
            input_data: {
                "project_description" or "complex_task": str,
                "user_id": int (optional),
                "constraints": dict (optional)
            }
            
        Returns:
            Complete project plan with phases, tasks, schedule
        """
        start_time = datetime.now()
        
        # Get project description
        project_description = input_data.get("project_description") or \
                             input_data.get("complex_task") or \
                             input_data.get("user_prompt", "")
        
        if not project_description:
            return {
                "error": "No project description provided",
                "status": "failed"
            }
        
        # Step 1: Analyze project
        analysis = self._analyze_project(project_description)
        
        # Step 2: Create project plan
        project_plan = self._create_project_plan(analysis, project_description)
        
        # Step 3: Create execution workflow
        workflow = self._create_execution_workflow(project_plan)
        
        # Generate project ID
        project_id = str(uuid.uuid4())[:8]
        
        # Calculate planning time
        planning_time = (datetime.now() - start_time).total_seconds()
        
        result = {
            "project_id": project_id,
            "project_name": self._generate_project_name(project_description),
            "project_description": project_description,
            "analysis": analysis,
            "phases": project_plan.get("phases", []),
            "tasks": self._flatten_tasks(project_plan.get("phases", [])),
            "schedule": project_plan.get("schedule", {}),
            "workflow": workflow,
            "estimated_duration": project_plan.get("total_estimated_time", "45 minutes"),
            "estimated_minutes": project_plan.get("total_minutes", 45),
            "risk_assessment": self._assess_risks(project_plan),
            "planning_time": planning_time,
            "status": "planned"
        }
        
        # Format output
        result["output"] = self._format_project_report(result)
        
        return result
    
    def _analyze_project(self, description: str) -> Dict[str, Any]:
        """
        Analyze project requirements and complexity.
        """
        prompt = f"""Analyze this project and provide a structured assessment.

Project: {description}

Provide:
1. GOAL: What is the main objective? (one sentence)
2. REQUIREMENTS: What needs to be done? (bullet points)
3. DELIVERABLES: What outputs are expected?
4. COMPLEXITY: Rate 1-10 (1=simple, 10=very complex)
5. SCOPE: Estimate size (small, medium, large)
6. EXPERTISE_NEEDED: Which specialists are needed?
7. ESTIMATED_TIME: How long in minutes?

Format your response with these exact labels."""

        try:
            response = llm_manager.generate(
                prompt=prompt,
                system_prompt="You are a project analyst. Be accurate and realistic.",
                temperature=0.3
            )
            
            return self._parse_analysis(response)
            
        except Exception as e:
            return {
                "goal": description[:100],
                "requirements": [description],
                "deliverables": ["Completed output"],
                "complexity": 5,
                "scope": "medium",
                "expertise_needed": ["ContentAgent"],
                "estimated_time": 30,
                "error": str(e)
            }
    
    def _parse_analysis(self, response: str) -> Dict[str, Any]:
        """Parse the analysis response."""
        import re
        
        analysis = {
            "goal": "",
            "requirements": [],
            "deliverables": [],
            "complexity": 5,
            "scope": "medium",
            "expertise_needed": [],
            "estimated_time": 30
        }
        
        lines = response.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            line_upper = line.upper()
            
            if 'GOAL:' in line_upper:
                analysis["goal"] = line.split(':', 1)[1].strip() if ':' in line else ""
                current_section = None
            elif 'REQUIREMENTS:' in line_upper:
                current_section = "requirements"
            elif 'DELIVERABLES:' in line_upper:
                current_section = "deliverables"
            elif 'COMPLEXITY:' in line_upper:
                match = re.search(r'(\d+)', line)
                if match:
                    analysis["complexity"] = min(10, max(1, int(match.group(1))))
                current_section = None
            elif 'SCOPE:' in line_upper:
                scope_text = line.split(':', 1)[1].strip().lower() if ':' in line else ""
                if 'small' in scope_text:
                    analysis["scope"] = "small"
                elif 'large' in scope_text:
                    analysis["scope"] = "large"
                else:
                    analysis["scope"] = "medium"
                current_section = None
            elif 'EXPERTISE' in line_upper:
                expertise = line.split(':', 1)[1].strip() if ':' in line else ""
                # Extract agent names
                agents = re.findall(r'(Research|Code|Content|Data|QA|Manager)Agent', expertise)
                if agents:
                    analysis["expertise_needed"] = [f"{a}Agent" for a in agents]
                current_section = None
            elif 'ESTIMATED_TIME:' in line_upper or 'TIME:' in line_upper:
                match = re.search(r'(\d+)', line)
                if match:
                    analysis["estimated_time"] = int(match.group(1))
                current_section = None
            elif line.startswith('-') or line.startswith('•'):
                item = line.lstrip('-•').strip()
                if current_section and item:
                    analysis[current_section].append(item)
        
        # Default expertise if none found
        if not analysis["expertise_needed"]:
            analysis["expertise_needed"] = ["ContentAgent"]
        
        return analysis
    
    def _create_project_plan(
        self, 
        analysis: Dict[str, Any],
        project_description: str
    ) -> Dict[str, Any]:
        """Create detailed project plan with phases and tasks."""
        # Use project planner tool
        plan = self.project_planner.execute(project_description)
        
        # Get all tasks for scheduling
        all_tasks = self._flatten_tasks(plan.get("phases", []))
        
        # Schedule tasks
        if all_tasks:
            schedule = self.task_scheduler.execute(tasks=all_tasks)
            plan["schedule"] = schedule
        else:
            plan["schedule"] = {"schedule": [], "total_duration": 0}
        
        # Add agent assignments
        plan["agent_assignments"] = self._assign_agents(all_tasks)
        
        return plan
    
    def _flatten_tasks(self, phases: List[Dict]) -> List[Dict[str, Any]]:
        """Flatten phases into a list of tasks."""
        tasks = []
        for phase in phases:
            for task in phase.get("tasks", []):
                task["phase_number"] = phase.get("phase_number")
                task["phase_name"] = phase.get("phase_name")
                tasks.append(task)
        return tasks
    
    def _assign_agents(self, tasks: List[Dict[str, Any]]) -> Dict[str, str]:
        """
        Assign agents to tasks based on task type.
        Returns mapping of task_id -> agent_name.
        """
        assignment_rules = {
            "research": "ResearchAgent",
            "search": "ResearchAgent",
            "find": "ResearchAgent",
            "investigate": "ResearchAgent",
            "code": "CodeAgent",
            "program": "CodeAgent",
            "develop": "CodeAgent",
            "implement": "CodeAgent",
            "build": "CodeAgent",
            "function": "CodeAgent",
            "api": "CodeAgent",
            "write": "ContentAgent",
            "document": "ContentAgent",
            "blog": "ContentAgent",
            "article": "ContentAgent",
            "content": "ContentAgent",
            "data": "DataAgent",
            "analyze": "DataAgent",
            "chart": "DataAgent",
            "statistics": "DataAgent",
            "visualize": "DataAgent",
            "review": "QAAgent",
            "validate": "QAAgent",
            "test": "QAAgent",
            "check": "QAAgent",
            "quality": "QAAgent"
        }
        
        assignments = {}
        
        for task in tasks:
            task_id = task.get("task_id", "")
            
            # Use pre-assigned agent if available
            if task.get("assigned_agent"):
                assignments[task_id] = task["assigned_agent"]
                continue
            
            # Assign based on description
            description = task.get("description", "").lower()
            assigned = "ContentAgent"  # Default
            
            for keyword, agent in assignment_rules.items():
                if keyword in description:
                    assigned = agent
                    break
            
            assignments[task_id] = assigned
            task["assigned_agent"] = assigned
        
        return assignments
    
    def _create_execution_workflow(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Create workflow definition for execution."""
        phases = plan.get("phases", [])
        schedule = plan.get("schedule", {})
        
        workflow = {
            "type": "sequential_phases",
            "phases": [],
            "data_flow": []
        }
        
        prev_phase_output = None
        
        for phase in phases:
            phase_workflow = {
                "phase_number": phase.get("phase_number"),
                "phase_name": phase.get("phase_name"),
                "execution_type": "parallel",  # Tasks within phase can be parallel
                "tasks": phase.get("tasks", []),
                "input_from": prev_phase_output
            }
            
            workflow["phases"].append(phase_workflow)
            
            # Track data flow
            if prev_phase_output:
                workflow["data_flow"].append({
                    "from": prev_phase_output,
                    "to": f"phase_{phase.get('phase_number')}"
                })
            
            prev_phase_output = f"phase_{phase.get('phase_number')}"
        
        return workflow
    
    def _assess_risks(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Assess project risks."""
        phases = plan.get("phases", [])
        tasks = self._flatten_tasks(phases)
        
        # Count dependencies
        total_deps = sum(len(t.get("dependencies", [])) for t in tasks)
        
        # Find critical tasks
        critical_tasks = []
        for task in tasks:
            deps = task.get("dependencies", [])
            if len(deps) > 2:  # Many dependencies = critical
                critical_tasks.append(task.get("task_id"))
        
        # Calculate complexity score
        complexity = plan.get("analysis", {}).get("complexity", 5) if isinstance(plan.get("analysis"), dict) else 5
        
        return {
            "complexity_score": complexity,
            "total_dependencies": total_deps,
            "critical_tasks": critical_tasks,
            "risk_level": "high" if complexity > 7 or len(critical_tasks) > 3 else 
                         "medium" if complexity > 4 else "low"
        }
    
    def _generate_project_name(self, description: str) -> str:
        """Generate a short project name from description."""
        # Take first few words
        words = description.split()[:5]
        name = " ".join(words)
        if len(name) > 50:
            name = name[:47] + "..."
        return name.title()
    
    def get_project_progress(self, project_id: str, db_session) -> Dict[str, Any]:
        """Get current progress of a project."""
        from models.task import Task
        
        # Query tasks for this project
        tasks = db_session.query(Task).filter(
            Task.project_id == project_id
        ).all()
        
        if not tasks:
            return {"error": "Project not found", "progress": 0}
        
        total = len(tasks)
        completed = len([t for t in tasks if t.status == "completed"])
        in_progress = len([t for t in tasks if t.status == "in_progress"])
        failed = len([t for t in tasks if t.status == "failed"])
        
        progress = (completed / total * 100) if total > 0 else 0
        
        return {
            "project_id": project_id,
            "total_tasks": total,
            "completed": completed,
            "in_progress": in_progress,
            "failed": failed,
            "progress_percentage": round(progress, 1),
            "status": "completed" if completed == total else 
                     "in_progress" if in_progress > 0 else
                     "queued"
        }
    
    def _format_project_report(self, result: Dict[str, Any]) -> str:
        """Format project plan as readable report."""
        lines = [
            f"# 📋 Project Plan: {result.get('project_name', 'Untitled')}",
            "",
            f"**Project ID:** {result.get('project_id')}",
            f"**Estimated Duration:** {result.get('estimated_duration')}",
            f"**Risk Level:** {result.get('risk_assessment', {}).get('risk_level', 'medium').upper()}",
            ""
        ]
        
        # Analysis
        analysis = result.get("analysis", {})
        if analysis.get("goal"):
            lines.append(f"## 🎯 Goal")
            lines.append(analysis["goal"])
            lines.append("")
        
        # Phases
        lines.append("## 📊 Execution Plan")
        lines.append("")
        
        for phase in result.get("phases", []):
            lines.append(f"### Phase {phase.get('phase_number')}: {phase.get('phase_name')}")
            for task in phase.get("tasks", []):
                agent = task.get("assigned_agent", "Unknown")
                time = task.get("estimated_time", "10 min")
                lines.append(f"- **{task.get('task_id')}**: {task.get('description')} [{agent}] ({time})")
            lines.append("")
        
        # Schedule summary
        schedule = result.get("schedule", {})
        if schedule.get("total_duration"):
            lines.append(f"## ⏱️ Schedule")
            lines.append(f"**Total Duration:** {schedule.get('total_duration_formatted', schedule.get('total_duration'))} minutes")
            lines.append(f"**Parallel Efficiency:** {schedule.get('parallel_efficiency', 0) * 100:.0f}%")
        
        return "\n".join(lines)
