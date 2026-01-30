"""
Nexus AI - Project Planner Tool
Tool for breaking projects into phases and tasks
"""

from typing import Dict, Any, List
from tools.base_tool import BaseTool, ToolRegistry
from llm.llm_manager import llm_manager


@ToolRegistry.register
class ProjectPlannerTool(BaseTool):
    """
    Tool for planning complex projects by breaking them into phases and tasks.
    Uses LLM to intelligently decompose project requirements.
    """
    
    PLANNING_PROMPT = """Break down this project into phases and tasks.

Project Description:
{project_description}

Available Agents:
- ResearchAgent: Web research, information gathering
- CodeAgent: Code generation, programming tasks
- ContentAgent: Writing, documentation, content creation
- DataAgent: Data analysis, visualization, statistics
- QAAgent: Quality assurance, validation, review
- ManagerAgent: Project coordination (use sparingly)

Create a detailed project plan with:
1. Multiple phases (Research, Design, Implementation, etc.)
2. Specific tasks within each phase
3. Which agent should handle each task
4. Estimated time for each task
5. Dependencies between tasks

Format your response EXACTLY like this:
PHASES:

PHASE 1: [Phase Name]
- Task 1.1: [Description] | Agent: [AgentName] | Time: [X minutes] | Dependencies: [none or task IDs]
- Task 1.2: [Description] | Agent: [AgentName] | Time: [X minutes] | Dependencies: [1.1]

PHASE 2: [Phase Name]
- Task 2.1: [Description] | Agent: [AgentName] | Time: [X minutes] | Dependencies: [1.2]

CRITICAL_PATH: [comma-separated task IDs that must complete in sequence]
TOTAL_TIME: [X minutes]
"""

    def __init__(self):
        super().__init__(
            name="project_planner",
            description="Break complex projects into phases and tasks with agent assignments"
        )
    
    def execute(self, project_description: str, **kwargs) -> Dict[str, Any]:
        """
        Create a project plan from a description.
        
        Args:
            project_description: Description of the project to plan
            
        Returns:
            Structured project plan with phases, tasks, and schedule
        """
        prompt = self.PLANNING_PROMPT.format(
            project_description=project_description
        )
        
        try:
            response = llm_manager.generate(
                prompt=prompt,
                system_prompt="You are a project planning expert. Create detailed, actionable plans.",
                temperature=0.4
            )
            
            return self._parse_project_plan(response, project_description)
            
        except Exception as e:
            # Fallback simple plan
            return self._create_fallback_plan(project_description, str(e))
    
    def _parse_project_plan(self, response: str, project_description: str) -> Dict[str, Any]:
        """Parse LLM response into structured project plan."""
        phases = []
        current_phase = None
        all_tasks = []
        critical_path = []
        total_time = 0
        
        lines = response.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Parse phase header
            if line.upper().startswith('PHASE'):
                # Save previous phase
                if current_phase and current_phase.get("tasks"):
                    phases.append(current_phase)
                
                # Extract phase info
                parts = line.split(':', 1)
                phase_num = len(phases) + 1
                phase_name = parts[1].strip() if len(parts) > 1 else f"Phase {phase_num}"
                
                current_phase = {
                    "phase_number": phase_num,
                    "phase_name": phase_name,
                    "tasks": []
                }
            
            # Parse task line
            elif line.startswith('-') or line.startswith('•'):
                task_info = self._parse_task_line(line, len(phases) + 1)
                if task_info and current_phase:
                    current_phase["tasks"].append(task_info)
                    all_tasks.append(task_info)
                    total_time += task_info.get("estimated_minutes", 10)
            
            # Parse critical path
            elif line.upper().startswith('CRITICAL_PATH:'):
                path_str = line.split(':', 1)[1].strip()
                critical_path = [t.strip() for t in path_str.split(',') if t.strip()]
            
            # Parse total time
            elif line.upper().startswith('TOTAL_TIME:'):
                import re
                time_match = re.search(r'(\d+)', line)
                if time_match:
                    total_time = int(time_match.group(1))
        
        # Save last phase
        if current_phase and current_phase.get("tasks"):
            phases.append(current_phase)
        
        # Create dependency graph
        dependency_graph = self.create_dependency_graph(phases)
        
        return {
            "phases": phases,
            "total_tasks": len(all_tasks),
            "total_estimated_time": f"{total_time} minutes",
            "total_minutes": total_time,
            "critical_path": critical_path,
            "dependency_graph": dependency_graph,
            "project_description": project_description
        }
    
    def _parse_task_line(self, line: str, phase_num: int) -> Dict[str, Any]:
        """Parse a single task line."""
        import re
        
        # Remove bullet point
        line = line.lstrip('-•').strip()
        
        # Default values
        task_info = {
            "task_id": "",
            "description": "",
            "assigned_agent": "ContentAgent",
            "estimated_time": "10 minutes",
            "estimated_minutes": 10,
            "dependencies": []
        }
        
        # Try to parse structured format: "Task 1.1: Desc | Agent: X | Time: Y | Deps: Z"
        parts = line.split('|')
        
        if len(parts) >= 1:
            # First part is task description
            desc_part = parts[0].strip()
            
            # Extract task ID if present
            task_match = re.match(r'Task\s*(\d+\.\d+):\s*(.*)', desc_part, re.IGNORECASE)
            if task_match:
                task_info["task_id"] = task_match.group(1)
                task_info["description"] = task_match.group(2).strip()
            else:
                # Generate task ID
                task_num = 1  # Will be updated externally if needed
                task_info["task_id"] = f"{phase_num}.{task_num}"
                task_info["description"] = desc_part
        
        # Parse remaining parts
        for part in parts[1:]:
            part = part.strip()
            
            if part.lower().startswith('agent:'):
                agent = part.split(':', 1)[1].strip()
                task_info["assigned_agent"] = agent
            
            elif part.lower().startswith('time:'):
                time_str = part.split(':', 1)[1].strip()
                task_info["estimated_time"] = time_str
                # Extract minutes
                time_match = re.search(r'(\d+)', time_str)
                if time_match:
                    task_info["estimated_minutes"] = int(time_match.group(1))
            
            elif part.lower().startswith('depend'):
                deps_str = part.split(':', 1)[1].strip()
                if deps_str.lower() not in ['none', 'n/a', '-']:
                    deps = [d.strip() for d in deps_str.split(',') if d.strip()]
                    task_info["dependencies"] = deps
        
        return task_info
    
    def create_dependency_graph(self, phases: List[Dict]) -> Dict[str, Any]:
        """
        Build a dependency graph from phases and tasks.
        
        Returns:
            Graph structure with nodes and edges
        """
        nodes = []
        edges = []
        
        for phase in phases:
            for task in phase.get("tasks", []):
                task_id = task.get("task_id", "")
                
                nodes.append({
                    "id": task_id,
                    "phase": phase.get("phase_number"),
                    "agent": task.get("assigned_agent"),
                    "description": task.get("description", "")[:50]
                })
                
                for dep in task.get("dependencies", []):
                    edges.append({
                        "from": dep,
                        "to": task_id
                    })
        
        # Identify parallel tasks (same phase, no dependencies on each other)
        parallel_groups = []
        for phase in phases:
            phase_tasks = phase.get("tasks", [])
            independent = [t["task_id"] for t in phase_tasks if not t.get("dependencies")]
            if len(independent) > 1:
                parallel_groups.append(independent)
        
        return {
            "nodes": nodes,
            "edges": edges,
            "parallel_groups": parallel_groups
        }
    
    def _create_fallback_plan(self, project_description: str, error: str) -> Dict[str, Any]:
        """Create a simple fallback plan when LLM fails."""
        # Detect project type from keywords
        desc_lower = project_description.lower()
        
        phases = []
        
        # Phase 1: Research (if needed)
        if any(kw in desc_lower for kw in ['research', 'find', 'learn', 'investigate']):
            phases.append({
                "phase_number": 1,
                "phase_name": "Research",
                "tasks": [{
                    "task_id": "1.1",
                    "description": "Research the topic",
                    "assigned_agent": "ResearchAgent",
                    "estimated_time": "15 minutes",
                    "estimated_minutes": 15,
                    "dependencies": []
                }]
            })
        
        # Phase 2: Implementation
        impl_agent = "ContentAgent"
        if any(kw in desc_lower for kw in ['code', 'program', 'build', 'develop', 'api', 'function']):
            impl_agent = "CodeAgent"
        elif any(kw in desc_lower for kw in ['data', 'analyze', 'chart', 'statistics']):
            impl_agent = "DataAgent"
        
        phases.append({
            "phase_number": len(phases) + 1,
            "phase_name": "Implementation",
            "tasks": [{
                "task_id": f"{len(phases) + 1}.1",
                "description": "Complete the main task",
                "assigned_agent": impl_agent,
                "estimated_time": "20 minutes",
                "estimated_minutes": 20,
                "dependencies": ["1.1"] if phases else []
            }]
        })
        
        # Phase 3: QA
        phases.append({
            "phase_number": len(phases) + 1,
            "phase_name": "Quality Assurance",
            "tasks": [{
                "task_id": f"{len(phases) + 1}.1",
                "description": "Review and validate output",
                "assigned_agent": "QAAgent",
                "estimated_time": "10 minutes",
                "estimated_minutes": 10,
                "dependencies": [phases[-1]["tasks"][-1]["task_id"]]
            }]
        })
        
        return {
            "phases": phases,
            "total_tasks": sum(len(p["tasks"]) for p in phases),
            "total_estimated_time": f"{sum(t['estimated_minutes'] for p in phases for t in p['tasks'])} minutes",
            "critical_path": [t["task_id"] for p in phases for t in p["tasks"]],
            "dependency_graph": self.create_dependency_graph(phases),
            "project_description": project_description,
            "fallback": True,
            "error": error
        }
