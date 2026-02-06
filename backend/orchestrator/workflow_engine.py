"""
Nexus AI - Workflow Engine
Advanced workflow orchestration with parallel/sequential execution and dependencies
"""

import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
import uuid

from database import SessionLocal
from models.task import Task, Subtask, TaskStatus
from agents.agent_registry import AgentRegistry
from llm.llm_manager import llm_manager
from messaging import emit_task_event_sync, emit_agent_progress_sync, WebSocketEventType


class WorkflowEngine:
    """
    Advanced workflow engine for executing complex multi-agent workflows.
    
    Features:
    - Parallel task execution
    - Sequential task execution with dependencies
    - Agent collaboration patterns
    - Error recovery and retries
    - Real-time progress tracking
    """
    
    def __init__(self, db_session=None, max_concurrent: int = 5):
        """
        Initialize workflow engine.
        
        Args:
            db_session: Database session (optional, will create new if not provided)
            max_concurrent: Maximum concurrent agent executions
        """
        self.db = db_session
        self.max_concurrent = max_concurrent
        self.executor = ThreadPoolExecutor(max_workers=max_concurrent)
        self.active_workflows = {}
        self.completed_tasks = {}
    
    def execute_workflow(
        self, 
        workflow: Dict[str, Any], 
        task_id: int,
        user_id: int = None
    ) -> Dict[str, Any]:
        """
        Execute a complete workflow.
        
        Args:
            workflow: Workflow definition with phases and tasks
            task_id: Parent task ID
            user_id: User ID for tracking
            
        Returns:
            Workflow execution results
        """
        workflow_id = str(uuid.uuid4())[:8]
        self.active_workflows[workflow_id] = {
            "status": "running",
            "started_at": datetime.now(),
            "task_id": task_id
        }
        
        results = {
            "workflow_id": workflow_id,
            "task_id": task_id,
            "phases_completed": 0,
            "tasks_completed": 0,
            "phase_results": [],
            "errors": [],
            "status": "running"
        }
        
        try:
            phases = workflow.get("phases", [])
            
            for phase in phases:
                phase_result = self._execute_phase(
                    phase=phase,
                    task_id=task_id,
                    workflow_id=workflow_id,
                    previous_outputs=results.get("phase_results", [])
                )
                
                results["phase_results"].append(phase_result)
                results["phases_completed"] += 1
                results["tasks_completed"] += phase_result.get("tasks_completed", 0)
                
                # Check for phase failure
                if phase_result.get("status") == "failed":
                    # Attempt recovery
                    recovery = self._handle_workflow_failure(
                        workflow=workflow,
                        failed_phase=phase,
                        error=phase_result.get("error", "Unknown error")
                    )
                    
                    if recovery.get("action") == "abort":
                        # If critical, stop the entire workflow
                        results["status"] = "failed"
                        results["errors"].append(phase_result.get("error"))
                        break
                    elif recovery.get("action") == "skip":
                        # For optional phases (like non-critical QA), just move on
                        continue
                    elif recovery.get("action") == "retry":
                        # Re-run the phase once if requested by recovery logic
                        phase_result = self._execute_phase(
                            phase=phase,
                            task_id=task_id,
                            workflow_id=workflow_id,
                            previous_outputs=results.get("phase_results", [])
                        )
                        results["phase_results"][-1] = phase_result
                
                # Emit progress
                # Calculate simple progress based on phase completion for now
                progress_pct = (results["phases_completed"] / len(phases)) * 100
                
                emit_task_event_sync(
                    task_id=task_id,
                    event_type=WebSocketEventType.TASK_PROGRESS,
                    data={
                        "workflow_id": workflow_id,
                        "phase": phase.get("phase_name"),
                        "progress": progress_pct
                    }
                )
            
            # Set final status
            if results["status"] == "running":
                results["status"] = "completed"
            
            # Combine outputs
            results["combined_output"] = self._combine_outputs(results["phase_results"])
            
        except Exception as e:
            results["status"] = "failed"
            results["errors"].append(str(e))
        
        finally:
            self.active_workflows[workflow_id]["status"] = results["status"]
            self.active_workflows[workflow_id]["completed_at"] = datetime.now()
        
        return results
    
    def _execute_phase(
        self, 
        phase: Dict[str, Any], 
        task_id: int,
        workflow_id: str,
        previous_outputs: List[Dict] = None
    ) -> Dict[str, Any]:
        """
        Execute a single phase of the workflow.
        
        Handles parallel and sequential task execution within the phase.
        """
        phase_result = {
            "phase_number": phase.get("phase_number"),
            "phase_name": phase.get("phase_name"),
            "tasks_completed": 0,
            "task_results": [],
            "status": "running"
        }
        
        tasks = phase.get("tasks", [])
        execution_type = phase.get("execution_type", "sequential")
        
        # Gather outputs from previous phases
        dependency_outputs = {}
        if previous_outputs:
            for prev in previous_outputs:
                for task_result in prev.get("task_results", []):
                    dependency_outputs[task_result.get("task_id")] = task_result.get("output")
        
        try:
            if execution_type == "parallel":
                # Execute all tasks in parallel
                task_results = self._execute_parallel_tasks(
                    tasks=tasks,
                    task_id=task_id,
                    dependency_outputs=dependency_outputs
                )
            else:
                # Execute tasks sequentially
                task_results = self._execute_sequential_tasks(
                    tasks=tasks,
                    task_id=task_id,
                    dependency_outputs=dependency_outputs
                )
            
            phase_result["task_results"] = task_results
            phase_result["tasks_completed"] = len([r for r in task_results if r.get("status") == "completed"])
            
            # Determine phase status
            failed_tasks = [r for r in task_results if r.get("status") == "failed"]
            if failed_tasks:
                phase_result["status"] = "partial" if phase_result["tasks_completed"] > 0 else "failed"
                phase_result["error"] = failed_tasks[0].get("error")
            else:
                phase_result["status"] = "completed"
                
        except Exception as e:
            phase_result["status"] = "failed"
            phase_result["error"] = str(e)
        
        return phase_result
    
    def _execute_parallel_tasks(
        self,
        tasks: List[Dict],
        task_id: int,
        dependency_outputs: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Execute multiple tasks in parallel using thread pool."""
        results = []
        
        with ThreadPoolExecutor(max_workers=self.max_concurrent) as executor:
            future_to_task = {}
            
            for task in tasks:
                # Check dependencies
                deps_satisfied, deps_output = self._check_dependencies(
                    task, dependency_outputs
                )
                
                if not deps_satisfied:
                    results.append({
                        "task_id": task.get("task_id"),
                        "description": task.get("description", ""),
                        "agent": task.get("assigned_agent", "Unknown"),
                        "status": "skipped",
                        "error": "Dependencies not satisfied",
                        "output": None
                    })
                    continue
                
                # Submit task for execution
                future = executor.submit(
                    self._execute_task_with_agent,
                    task,
                    task.get("assigned_agent", "ContentAgent"),
                    deps_output,
                    task_id
                )
                future_to_task[future] = task
            
            # Collect results as they complete from the thread pool
            for future in as_completed(future_to_task):
                task = future_to_task[future]
                try:
                    # Impose a 5-minute safety timeout on individual agent tasks
                    result = future.result(timeout=300) 
                    results.append(result)
                    self.completed_tasks[task.get("task_id")] = result
                except Exception as e:
                    results.append({
                        "task_id": task.get("task_id"),
                        "status": "failed",
                        "error": str(e)
                    })
        
        return results
    
    def _execute_sequential_tasks(
        self,
        tasks: List[Dict],
        task_id: int,
        dependency_outputs: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Execute tasks one by one in sequence."""
        results = []
        local_outputs = dict(dependency_outputs)
        
        for task in tasks:
            # Check dependencies
            deps_satisfied, deps_output = self._check_dependencies(task, local_outputs)
            
            if not deps_satisfied:
                results.append({
                    "task_id": task.get("task_id"),
                    "description": task.get("description", ""),
                    "agent": task.get("assigned_agent", "Unknown"),
                    "status": "skipped",
                    "error": "Dependencies not satisfied",
                    "output": None
                })
                # Stop on failure (sequential execution)
                break
            
            # Execute task
            result = self._execute_task_with_agent(
                task=task,
                agent_name=task.get("assigned_agent", "ContentAgent"),
                dependency_outputs=deps_output,
                parent_task_id=task_id
            )
            
            results.append(result)
            
            # Store output for dependent tasks
            if result.get("status") == "completed":
                local_outputs[task.get("task_id")] = result.get("output")
                self.completed_tasks[task.get("task_id")] = result
            else:
                # Stop on failure (sequential execution)
                break
        
        return results
    
    def _execute_task_with_agent(
        self,
        task: Dict[str, Any],
        agent_name: str,
        dependency_outputs: Dict[str, Any],
        parent_task_id: int
    ) -> Dict[str, Any]:
        """
        Execute a single task by dispatching to the Redis queue and waiting for results.
        
        Refactored to use the robust Worker system instead of in-memory threads.
        """
        task_id = task.get("task_id", "unknown")
        
        try:
            # 1. Create Subtask in Database
            # We need a new session here because this runs in a thread
            db = SessionLocal()
            try:
                # Check if subtask already exists (recovery)
                # For simplicity in this implementation, we create a new one
                
                input_data = {
                    "task": task.get("description", ""),
                    "prompt": task.get("description", ""),
                    "user_prompt": task.get("description", ""),
                    "task_description": task.get("description", ""),
                    "dependency_outputs": dependency_outputs,
                    "parent_task_id": parent_task_id,
                    "workflow_task_id": task_id
                }
                
                print(f"!!! DEBUG: input_data keys created: {list(input_data.keys())} !!!")
                print(f"!!! DEBUG: dependency_outputs present: {bool(dependency_outputs)} !!!")
                
                # Special handling for QAAgent content injection
                if agent_name == "QAAgent" and dependency_outputs:
                    # Join all dependency outputs as content
                    content_parts = []
                    for dep_id, dep_out in dependency_outputs.items():
                        if isinstance(dep_out, dict):
                             # Try to extract actual content/code if structured
                             if "code" in dep_out:
                                 dep_out = dep_out.get("code")
                             elif "output" in dep_out:
                                 dep_out = dep_out.get("output")
                             else:
                                 dep_out = str(dep_out)
                        content_parts.append(str(dep_out))
                    input_data["content"] = "\n\n".join(content_parts)
                    input_data["content_type"] = "general"

                subtask = Subtask(
                    task_id=parent_task_id,
                    assigned_agent=agent_name,
                    input_data=input_data,
                    status=TaskStatus.QUEUED.value
                )
                
                db.add(subtask)
                db.commit()
                db.refresh(subtask)
                subtask_db_id = subtask.id
                
                print(f"🚀 Dispatched task {task_id} (DB ID: {subtask_db_id}) to {agent_name}")
                
                # 2. Enqueue to Redis
                from redis_client import enqueue_task
                if not enqueue_task(subtask_db_id):
                    raise Exception("Failed to enqueue task to Redis")
                
                # 3. Wait for completion (Polling)
                # This blocks the workflow thread, but allows the Worker to do the heavy lifting
                # and enables persistence/visibility in the UI through the database state.
                
                max_retries = 300  # 300 * 2s = 10 minutes timeout
                import time
                
                for _ in range(max_retries):
                    db.refresh(subtask)
                    
                    if subtask.status == TaskStatus.COMPLETED.value:
                        print(f"✅ Task {task_id} completed via Worker")
                        output = subtask.output_data
                        # Standardize output format
                        if output and isinstance(output, dict) and "output" in output:
                            output = output["output"]
                            
                        return {
                            "task_id": task_id,
                            "agent": agent_name,
                            "status": "completed",
                            "output": output,
                            "execution_time": 0  # Could calculate from DB timestamps
                        }
                    
                    if subtask.status == TaskStatus.FAILED.value:
                        raise Exception(f"Worker failed: {subtask.error_message}")
                        
                    time.sleep(2)
                    
                raise Exception("Task execution timed out")
                
            finally:
                db.close()
            
        except Exception as e:
            print(f"❌ Task {task_id} execution failed: {e}")
            return {
                "task_id": task_id,
                "agent": agent_name,
                "status": "failed",
                "error": str(e)
            }
    
    def _check_dependencies(
        self, 
        task: Dict[str, Any], 
        available_outputs: Dict[str, Any]
    ) -> tuple:
        """
        Check if all dependencies are satisfied.
        
        Returns:
            (satisfied: bool, dependency_outputs: dict)
        """
        dependencies = task.get("dependencies", [])
        
        if not dependencies:
            return True, {}
        
        outputs = {}
        for dep in dependencies:
            if dep not in available_outputs:
                return False, {}
            outputs[dep] = available_outputs[dep]
        
        return True, outputs
    
    def _handle_workflow_failure(
        self,
        workflow: Dict[str, Any],
        failed_phase: Dict[str, Any],
        error: str
    ) -> Dict[str, Any]:
        """
        Handle workflow failure and determine recovery action.
        
        Returns:
            Recovery action: abort, skip, or retry
        """
        phase_name = failed_phase.get("phase_name", "")
        
        # Critical phases that should abort
        critical_keywords = ["implementation", "core", "main", "critical"]
        is_critical = any(kw in phase_name.lower() for kw in critical_keywords)
        
        if is_critical:
            return {"action": "abort", "reason": f"Critical phase failed: {error}"}
        
        # Non-critical phases can be skipped
        if "qa" in phase_name.lower() or "optional" in phase_name.lower():
            return {"action": "skip", "reason": "Non-critical phase, continuing"}
        
        # Default: retry once
        return {"action": "retry", "reason": "Retrying failed phase"}
    
    def _combine_outputs(self, phase_results: List[Dict]) -> str:
        """Combine all phase outputs into a single result."""
        combined = []
        
        for phase in phase_results:
            phase_name = phase.get("phase_name", "Phase")
            combined.append(f"\n## {phase_name}\n")
            
            for task_result in phase.get("task_results", []):
                if task_result.get("status") == "completed":
                    output = task_result.get("output", "")
                    if isinstance(output, dict):
                        # Handle ResearchAgent structured output
                        if "summary" in output and "key_findings" in output:
                            summary = output.get("summary", "")
                            
                            # Handle nested/escaped JSON in summary
                            if isinstance(summary, str) and summary.strip().startswith("{"):
                                try:
                                    import json
                                    parsed = json.loads(summary.strip())
                                    if isinstance(parsed, dict) and "summary" in parsed:
                                        summary = parsed.get("summary", summary)
                                except:
                                    # Fallback: use regex to extract text after "summary":
                                    import re
                                    match = re.search(r'"summary"\s*:\s*"([^"]+)', summary)
                                    if match:
                                        # Get full value - might be multiline
                                        start = summary.find('"summary"')
                                        if start >= 0:
                                            # Find the value after ":"
                                            rest = summary[start:]
                                            val_start = rest.find('": "') or rest.find('":"')
                                            if val_start >= 0:
                                                val_rest = rest[val_start + 4:]
                                                # Find the closing quote (not escaped)
                                                end = 0
                                                for i, c in enumerate(val_rest):
                                                    if c == '"' and (i == 0 or val_rest[i-1] != '\\'):
                                                        end = i
                                                        break
                                                if end > 0:
                                                    summary = val_rest[:end]
                            elif isinstance(summary, dict):
                                summary = summary.get("summary", str(summary))
                            
                            key_findings = output.get("key_findings", [])
                            sources = output.get("sources", [])
                            
                            formatted = f"### Summary\n\n{summary}\n\n"
                            
                            if key_findings:
                                formatted += "### Key Findings\n\n"
                                for i, finding in enumerate(key_findings, 1):
                                    if isinstance(finding, str):
                                        formatted += f"{i}. {finding}\n"
                                    else:
                                        formatted += f"{i}. {str(finding)}\n"
                                formatted += "\n"
                            
                            if sources:
                                formatted += "### Sources\n\n"
                                for source in sources[:5]:  # Limit to 5 sources
                                    if isinstance(source, dict):
                                        title = source.get("title", "Untitled")
                                        url = source.get("url", "")
                                        formatted += f"- [{title}]({url})\n"
                                    else:
                                        formatted += f"- {str(source)}\n"
                            
                            output = formatted
                        
                        # Handle CodeAgent structured output
                        elif "code" in output and "language" in output:
                            lang = output.get("language", "")
                            code = output.get("code", "")
                            explanation = output.get("explanation", "")
                            output = f"### Code ({lang})\n\n```{lang}\n{code}\n```\n\n**Explanation:** {explanation}"
                        
                        # Handle ContentAgent structured output
                        elif "content" in output:
                            output = output.get("content", "")
                        elif "body" in output:
                            output = output.get("body", "")
                        
                        # Handle generic dict with output key
                        elif "output" in output:
                            inner = output.get("output", {})
                            if isinstance(inner, dict):
                                # Try to format it nicely
                                output = self._format_dict_as_markdown(inner)
                            else:
                                output = str(inner)
                        
                        # Fallback for other dicts
                        else:
                            output = self._format_dict_as_markdown(output)
                    
                    combined.append(str(output))
        
        return "\n".join(combined)
    
    def _format_dict_as_markdown(self, data: Dict) -> str:
        """Format a dictionary as readable markdown."""
        lines = []
        for key, value in data.items():
            if key in ["execution_time", "agent", "status", "error"]:
                continue  # Skip metadata
            
            # Format key as heading
            formatted_key = key.replace("_", " ").title()
            
            if isinstance(value, list):
                lines.append(f"### {formatted_key}\n")
                for i, item in enumerate(value, 1):
                    if isinstance(item, dict):
                        lines.append(f"{i}. {item.get('title', item.get('name', str(item)))}")
                    else:
                        lines.append(f"{i}. {item}")
                lines.append("")
            elif isinstance(value, dict):
                lines.append(f"### {formatted_key}\n")
                lines.append(self._format_dict_as_markdown(value))
            else:
                if len(str(value)) > 100:
                    lines.append(f"### {formatted_key}\n\n{value}\n")
                else:
                    lines.append(f"**{formatted_key}:** {value}\n")
        
        return "\n".join(lines)
    
    # Collaboration Patterns
    
    def pattern_code_with_docs(
        self, 
        code_task: Dict, 
        docs_task: Dict,
        task_id: int
    ) -> Dict[str, Any]:
        """
        Execute code generation followed by documentation.
        
        Pattern:
        1. CodeAgent generates code
        2. ContentAgent documents the code
        3. QAAgent reviews both
        """
        results = {"pattern": "code_with_docs", "steps": []}
        
        # Step 1: Generate code
        code_result = self._execute_task_with_agent(
            task=code_task,
            agent_name="CodeAgent",
            dependency_outputs={},
            parent_task_id=task_id
        )
        results["steps"].append(code_result)
        
        if code_result.get("status") != "completed":
            results["status"] = "failed"
            return results
        
        # Step 2: Generate documentation
        docs_task["description"] = f"Document this code:\n{code_result.get('output', '')[:2000]}"
        docs_result = self._execute_task_with_agent(
            task=docs_task,
            agent_name="ContentAgent",
            dependency_outputs={"code": code_result.get("output")},
            parent_task_id=task_id
        )
        results["steps"].append(docs_result)
        
        # Step 3: QA Review
        qa_result = self._execute_task_with_agent(
            task={"task_id": "qa_review", "description": "Review code and documentation"},
            agent_name="QAAgent",
            dependency_outputs={
                "code": code_result.get("output"),
                "docs": docs_result.get("output")
            },
            parent_task_id=task_id
        )
        results["steps"].append(qa_result)
        
        results["status"] = "completed"
        results["output"] = {
            "code": code_result.get("output"),
            "documentation": docs_result.get("output"),
            "qa_report": qa_result.get("output")
        }
        
        return results
    
    def pattern_research_and_blog(
        self,
        research_task: Dict,
        blog_task: Dict,
        task_id: int
    ) -> Dict[str, Any]:
        """
        Research a topic and write a blog post.
        
        Pattern:
        1. ResearchAgent gathers information
        2. ContentAgent writes blog using research
        3. QAAgent reviews blog
        """
        results = {"pattern": "research_and_blog", "steps": []}
        
        # Step 1: Research
        research_result = self._execute_task_with_agent(
            task=research_task,
            agent_name="ResearchAgent",
            dependency_outputs={},
            parent_task_id=task_id
        )
        results["steps"].append(research_result)
        
        if research_result.get("status") != "completed":
            results["status"] = "failed"
            return results
        
        # Step 2: Write blog
        blog_task["description"] = f"Write a blog post based on this research:\n{research_result.get('output', '')[:3000]}"
        blog_result = self._execute_task_with_agent(
            task=blog_task,
            agent_name="ContentAgent",
            dependency_outputs={"research": research_result.get("output")},
            parent_task_id=task_id
        )
        results["steps"].append(blog_result)
        
        # Step 3: QA Review
        qa_result = self._execute_task_with_agent(
            task={"task_id": "qa_review", "description": "Review blog for accuracy and quality"},
            agent_name="QAAgent",
            dependency_outputs={
                "research": research_result.get("output"),
                "blog": blog_result.get("output")
            },
            parent_task_id=task_id
        )
        results["steps"].append(qa_result)
        
        results["status"] = "completed"
        results["output"] = {
            "research": research_result.get("output"),
            "blog": blog_result.get("output"),
            "qa_report": qa_result.get("output")
        }
        
        return results
    
    def pattern_data_analysis_report(
        self,
        analysis_task: Dict,
        report_task: Dict,
        task_id: int
    ) -> Dict[str, Any]:
        """
        Analyze data and create a report.
        
        Pattern:
        1. DataAgent analyzes data
        2. ContentAgent writes narrative report
        3. QAAgent reviews report
        """
        results = {"pattern": "data_analysis_report", "steps": []}
        
        # Step 1: Data Analysis
        analysis_result = self._execute_task_with_agent(
            task=analysis_task,
            agent_name="DataAgent",
            dependency_outputs={},
            parent_task_id=task_id
        )
        results["steps"].append(analysis_result)
        
        # Step 2: Write Report
        report_task["description"] = f"Write a report based on this analysis:\n{analysis_result.get('output', '')[:3000]}"
        report_result = self._execute_task_with_agent(
            task=report_task,
            agent_name="ContentAgent",
            dependency_outputs={"analysis": analysis_result.get("output")},
            parent_task_id=task_id
        )
        results["steps"].append(report_result)
        
        # Step 3: QA Review
        qa_result = self._execute_task_with_agent(
            task={"task_id": "qa_review", "description": "Review report quality"},
            agent_name="QAAgent",
            dependency_outputs={"report": report_result.get("output")},
            parent_task_id=task_id
        )
        results["steps"].append(qa_result)
        
        results["status"] = "completed"
        results["output"] = {
            "analysis": analysis_result.get("output"),
            "report": report_result.get("output"),
            "qa_report": qa_result.get("output")
        }
        
        return results
