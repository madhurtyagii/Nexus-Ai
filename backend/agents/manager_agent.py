"""Nexus AI - Manager Agent.

This module implements the ManagerAgent, responsible for high-level project 
analysis, strategic planning, task decomposition, and multi-agent workflow 
coordination.
"""

import uuid
import json
import anyio
from typing import Dict, Any, List, Optional
from datetime import datetime

from agents.base_agent import BaseAgent
from agents.agent_registry import AgentRegistry
from tools.project_planner import ProjectPlannerTool
from tools.task_scheduler import TaskSchedulerTool
from tools.architect_tool import ArchitectTool
from llm.llm_manager import llm_manager


@AgentRegistry.register
class ManagerAgent(BaseAgent):
    """Agent specialized in project management and agent orchestration.
    
    The ManagerAgent acts as a strategic lead, breaking down complex user 
    requests into actionable plans with multiple phases. It identifies the 
    best-suited specialized agents for each subtask and constructs efficient 
    execution workflows.
    
    Attributes:
        name: Agent identifier ("ManagerAgent").
        role: Description of the agent's purpose.
        system_prompt: Core principles for strategic planning.
        project_planner: Tool for decomposition and phase generation.
        
    Example:
        >>> agent = ManagerAgent()
        >>> result = agent.execute({"complex_task": "Build a stock dashboard"})
        >>> print(result["output"]["phases"])
    """
    
    SYSTEM_PROMPT = """You are the Lead Project Architect and a friendly strategic partner for Nexus AI.
    
    Your primary mission is to transform high-level human ideas into cohesive, fully-realized project structures while being conversational, supportive, and flexible.
    
    Your core responsibilities:
    1. **Design Architecture**: When a user wants to build something new, design the folder structure and explain the vision clearly.
    2. **Autonomous Building**: Use the 'Architect' tool to scaffold projects while keeping the user informed of your progress.
    3. **Strategic Planning**: Break down complex projects into logical execution phases and explain *why* they matter.
    4. **Agent Coordination**: Assign sub-tasks to specialists and act as the friendly lead coordinator.
    5. **Media Synthesis**: Leverage VisualAgent and AudioAgent for immersive prototypes.
    6. **Quality & Integrity**: Ensure the architecture follows best practices while being open to user refinements.
    
    Think like a System Architect but talk like a helpful collaborator. Be precise in building, but flexible in conversation."""

    def __init__(self, llm_manager=None, db_session=None):
        # Attach building and planning tools
        self.project_planner = ProjectPlannerTool()
        self.task_scheduler = TaskSchedulerTool()
        self.architect = ArchitectTool()
        tools = [self.project_planner, self.task_scheduler, self.architect]
        
        super().__init__(
            name="ManagerAgent",
            role="Lead System Architect and Agent Coordinator",
            system_prompt=self.SYSTEM_PROMPT,
            llm_manager=llm_manager,
            db_session=db_session,
            tools=tools
        )
        
        # Configuration
        self.max_project_duration = 60 * 60  # 1 hour in seconds
        self.complexity_threshold = 0.7  # Above this, use detailed planning
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Orchestrates multi-agent workflows and performs project planning.
        
        Args:
            input_data: A dictionary containing:
                - project_description/complex_task (str): The high-level request.
                - user_id (int, optional): The user initiating the request.
                - constraints (dict, optional): Resource or time limitations.
                
        Returns:
            dict: Structured project plan including phases, task assignments, 
                risk assessments, and execution workflows.
        """
        start_time = datetime.now()
        
        # Get project description and refinement prompt
        project_description = input_data.get("project_description") or \
                             input_data.get("complex_task") or \
                             input_data.get("user_prompt", "")
        
        refinement_prompt = input_data.get("refinement_prompt")
        
        if not project_description and not refinement_prompt:
            return {
                "error": "No project description or refinement prompt provided",
                "status": "failed"
            }
        
        import anyio
        
        # Step 1: Detect if this is a building/scaffolding request
        build_keywords = ["build", "scaffold", "architect", "structure", "create a project", "bootstrap"]
        is_build_request = any(kw in project_description.lower() for kw in build_keywords)
        
        build_status = None
        if is_build_request:
            print(f"🏗️ ManagerAgent: Designing system architecture...")
            # Step 1.1: Design structure via LLM
            structure = await self._design_architecture(project_description)
            
            # Step 1.2: Physically build the project
            project_name = self._generate_project_name(project_description)
            print(f"🔨 ManagerAgent: Physically scaffolding '{project_name}'...")
            build_result = await self.use_tool("Architect", project_name=project_name, structure=structure)
            
            if build_result.get("success"):
                build_status = build_result.get("data")
                print(f"✅ ManagerAgent: Architecture built at {build_status.get('root_path')}")

        import anyio
        
        # Step 2: Analyze project or Refine existing plan
        if refinement_prompt:
            print(f"🔄 ManagerAgent: Refining existing plan based on feedback...")
            existing_plan = input_data.get("existing_plan")
            
            # Use LLM to refine the plan
            project_plan = await self._refine_project_plan(
                description=project_description,
                existing_plan=existing_plan,
                refinement_prompt=refinement_prompt
            )
            analysis = await anyio.to_thread.run_sync(self._analyze_project, f"{project_description}\nRefinement: {refinement_prompt}")
        else:
            print(f"🤖 ManagerAgent: Analyzing project...")
            analysis = await anyio.to_thread.run_sync(self._analyze_project, project_description)
            
            # Step 3: Create project plan
            print(f"📋 ManagerAgent: creating plan...")
            project_plan = await anyio.to_thread.run_sync(self.project_planner.execute, project_description)
        
        # Step 4: Create execution workflow
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
            "build_info": build_status, # Include build info in output
            "status": "architected" if build_status else "planned"
        }
        
        # Format output
        result["output"] = self._format_project_report(result)
        
        return result

    async def _refine_project_plan(self, description: str, existing_plan: List[Dict], refinement_prompt: str) -> Dict[str, Any]:
        """Ask LLM to update an existing project plan based on new instructions."""
        prompt = f"""You are the Lead Project Architect. Refine the existing project plan based on the user's new instructions.
        
Project: {description}
Existing Plan: {json.dumps(existing_plan, indent=2)}
Refinement Instructions: {refinement_prompt}

Update the phases and tasks accordingly. Return a valid JSON object in the exact same format as the existing plan.
Expected JSON format: {{ "phases": [...], "total_estimated_time": "...", "total_minutes": ... }}

JSON:"""
        try:
            response = self.llm.generate(
                prompt=prompt,
                system="Respond with valid JSON only. Preserve the existing project structure but modify/add phases/tasks as requested.",
                temperature=0.3
            )
            
            # Clean response
            import re
            json_str = response.strip()
            if json_str.startswith("```"):
                json_str = re.sub(r"```(json)?\n", "", json_str)
                json_str = json_str.split("```")[0].strip()
            
            return json.loads(json_str)
        except Exception as e:
            print(f"❌ Refinement Error: {e}")
            return {"phases": existing_plan, "total_minutes": 30, "error": str(e)}

    async def _design_architecture(self, description: str) -> Dict[str, Any]:
        """Ask LLM to design a technical folder/file structure."""
        prompt = f"""You are a Master System Architect. Design a comprehensive, professional, and scalable folder/file structure for the following project.
        
Project Goal: {description}

Provide your design in JSON format ONLY. 
Be precise. Include all standard directories (src, tests, docs, config, etc.) and core files with realistic boilerplate comments.

Expected JSON Structure:
{{
    "folders": ["list/of/nested/directories"],
    "files": {{
        "path/to/file.py": "content here",
        "README.md": "# Project Title\\n## Overview\\n..."
    }}
}}
JSON:"""

        try:
            response = self.llm.generate(
                prompt=prompt,
                system="Respond with valid JSON only. No prose. No markdown blocks.",
                temperature=0.2
            )
            
            # Clean response (remove json code blocks if present)
            import re
            json_str = response.strip()
            if json_str.startswith("```"):
                json_str = re.sub(r"```(json)?\n", "", json_str)
                json_str = json_str.split("```")[0].strip()
            
            return json.loads(json_str)
        except Exception as e:
            print(f"❌ Architect Design Error: {e}")
            return {
                "folders": ["src"],
                "files": {"README.md": f"# {description}\n\nArchitecture generation failed."}
            }
    
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
                system="You are a project analyst. Be accurate and realistic.",
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
            "quality": "QAAgent",
            "image": "VisualAgent",
            "logo": "VisualAgent",
            "design": "VisualAgent",
            "illustration": "VisualAgent",
            "icon": "VisualAgent",
            "ui": "VisualAgent"
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
