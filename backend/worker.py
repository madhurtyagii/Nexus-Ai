"""
Nexus AI - Background Worker
Processes tasks from Redis queue using real agents
"""

import time
import signal
import sys
import uuid
from datetime import datetime
from typing import Optional, Dict, Any

from database import SessionLocal
from models.task import Task, Subtask, TaskStatus
from orchestrator.queue import task_queue
from llm.llm_manager import llm_manager
from logging_config import get_worker_logger
from agents.agent_factory import AgentFactory
from tools.tool_registry import ToolRegistry
from exceptions.custom_exceptions import TaskExecutionError, AgentError, DatabaseError
from utils.retries import retry
from messaging import (
    emit_task_event_sync,
    emit_agent_progress_sync,
    WebSocketEventType
)

# Memory tracking
try:
    from memory.conversation_tracker import get_conversation_tracker
    MEMORY_ENABLED = True
except ImportError:
    MEMORY_ENABLED = False


class Worker:
    """
    Background worker that processes subtasks from Redis queue.
    
    Features:
    - Pulls tasks from Redis queue
    - Executes real AI agents (Research, Code, etc.)
    - Updates database with results
    - Handles failures with retry mechanism
    """
    
    def __init__(self, worker_id: str = None):
        """
        Initialize worker.
        
        Args:
            worker_id: Unique identifier for this worker instance
        """
        self.worker_id = worker_id or str(uuid.uuid4())[:8]
        self.running = False
        self.logger = get_worker_logger(self.worker_id)
        self.queue = task_queue
        self.db = None
        
        # Initialize tool registry (registers default tools)
        self.tool_registry = ToolRegistry()
        
        # Statistics
        self.tasks_processed = 0
        self.tasks_failed = 0
    
    def _get_db(self):
        """Get a new database session."""
        return SessionLocal()
    
    def run(self, polling_interval: int = 2):
        """
        Main worker loop.
        
        Args:
            polling_interval: Seconds to wait when queue is empty
        """
        self.running = True
        self.logger.info(f"🚀 Worker {self.worker_id} started")
        self.logger.info(f"📋 Registered agents: {AgentFactory.get_available_agents()}")
        self.logger.info(f"🔧 Registered tools: {[t['name'] for t in self.tool_registry.list_tools()]}")
        
        import asyncio
        while self.running:
            try:
                # Try to get a subtask from queue
                subtask_id = self.queue.dequeue(timeout=polling_interval)
                
                if subtask_id is None:
                    # Queue empty, continue polling
                    continue
                
                # Process the subtask
                self.logger.info(f"📥 Picked up subtask {subtask_id}")
                # Use asyncio.run or similar if not already in a loop, 
                # but worker.py should ideally be run in an event loop
                asyncio.run(self.process_subtask(subtask_id))
                
            except KeyboardInterrupt:
                self.logger.info("⚠️ Received interrupt signal")
                break
            except Exception as e:
                self.logger.error(f"❌ Worker error: {e}")
                time.sleep(polling_interval)
        
        self.shutdown()
    
    @retry(exceptions=(DatabaseError, AgentError), tries=3, delay=1)
    async def process_subtask(self, subtask_id: int) -> bool:
        """
        Process a single subtask.
        
        Args:
            subtask_id: Subtask ID to process
            
        Returns:
            True if successful
        """
        db = self._get_db()
        
        try:
            # Mark as processing
            self.queue.mark_processing(subtask_id)
            
            # Get subtask from database
            subtask = db.query(Subtask).filter(Subtask.id == subtask_id).first()
            if not subtask:
                self.logger.error(f"❌ Subtask {subtask_id} not found in database")
                return False
            
            # Update status in database
            subtask.status = TaskStatus.IN_PROGRESS.value
            db.commit()
            
            self.logger.info(f"🤖 Executing {subtask.assigned_agent} for subtask {subtask_id}")
            
            # Emit WebSocket event for agent start
            emit_task_event_sync(
                WebSocketEventType.AGENT_STARTED,
                subtask.task_id,
                {
                    "agent_name": subtask.assigned_agent,
                    "subtask_id": subtask_id,
                    "status": "starting"
                }
            )
            
            # Execute agent logic
            input_data = subtask.input_data or {}
            
            # START FIX: Inject content for QAAgent if missing
            if subtask.assigned_agent == "QAAgent" and "content" not in input_data:
                self.logger.info(f"🔧 QAAgent missing content, attempting to fetch from completed sibling subtasks...")
                # Find ALL completed sibling subtasks for this parent task
                prev_subtasks = db.query(Subtask).filter(
                    Subtask.task_id == subtask.task_id,
                    Subtask.id < subtask_id,
                    Subtask.status == TaskStatus.COMPLETED.value
                ).order_by(Subtask.id.asc()).all()
                
                if prev_subtasks:
                    content_parts = []
                    has_code = False
                    for prev in prev_subtasks:
                        if prev.output_data:
                            self.logger.info(f"✅ Collecting output from subtask {prev.id} ({prev.assigned_agent})")
                            output_content = prev.output_data.get("output", "")
                            if isinstance(output_content, dict):
                                if "code" in output_content:
                                    output_content = output_content["code"]
                                    has_code = True
                                elif "content" in output_content:
                                    output_content = output_content["content"]
                                elif "body" in output_content:
                                    output_content = output_content.get("subject", "") + "\n\n" + output_content.get("body", "")
                                elif "summary" in output_content:
                                    output_content = output_content.get("summary", "")
                                else:
                                    output_content = str(output_content)
                            if output_content:
                                content_parts.append(f"--- Output from {prev.assigned_agent} ---\n{str(output_content)}")
                            if prev.assigned_agent == "CodeAgent":
                                has_code = True
                    
                    input_data = dict(input_data)  # Create copy to modify
                    input_data["content"] = "\n\n".join(content_parts) if content_parts else "No content available from previous agents"
                    input_data["content_type"] = "code" if has_code else "general"
                    
                    # Inject original_task from parent task
                    parent_task = db.query(Task).filter(Task.id == subtask.task_id).first()
                    if parent_task and parent_task.user_prompt:
                        input_data["original_task"] = parent_task.user_prompt
                        # Add premium quality instruction
                        quality_warning = f"\n\nCRITICAL QUALITY DIRECTIVE:\nYou are working on a high-stakes PROJECT: '{parent_task.user_prompt}'.\nDO NOT use generic placeholders (like 'BankAccount' or 'example').\nDO NOT produce boilerplate. Implement REAL logic specifically for this project.\nProfessional, production-grade output is MANDATORY."
                        input_data["content"] = input_data.get("content", "") + quality_warning
                    
                    self.logger.info(f"💉 Injected content and quality directive into QAAgent")
            
            # Inject quality directive for ALL agents if they have original_task
            if "original_task" in input_data and subtask.assigned_agent != "QAAgent":
                quality_warning = f"\n\n[QUALITY DIRECTIVE]: You are implementing a part of project: '{input_data['original_task']}'. DO NOT use generic placeholders or example code. Provide specialized, production-ready implementation."
                if isinstance(input_data.get("instruction"), str):
                    input_data["instruction"] += quality_warning
                elif "prompt" in input_data:
                    input_data["prompt"] += quality_warning
            # END FIX

            output = await self.execute_agent(
                subtask.assigned_agent,
                input_data,
                db
            )
            
            # Update subtask with output
            subtask.output_data = output
            
            # Check for failure in agent output
            is_failure = False
            if isinstance(output, dict) and output.get("status") == "error":
                is_failure = True
            
            if is_failure:
                # If silent_retry is on, don't mark as FAILED to avoid UI red badges
                agent_error = output.get("error") or output.get("output", "Agent execution failed")
                if input_data.get("silent_retry"):
                    subtask.status = TaskStatus.IN_PROGRESS.value  # Keep it "In Progress" or "Processing"
                    subtask.error_message = f"Silent Retry Attempt: {agent_error}"
                    self.logger.info(f"🤐 Silent failure for {subtask.assigned_agent}, keeping status as IN_PROGRESS")
                else:
                    subtask.status = TaskStatus.FAILED.value
                    subtask.error_message = agent_error
                self.logger.warning(f"❌ Agent {subtask.assigned_agent} returned error: {subtask.error_message}")
            else:
                subtask.status = TaskStatus.COMPLETED.value
            
            subtask.completed_at = datetime.utcnow()
            db.commit()
            
            # Mark complete in Redis
            self.queue.mark_complete(subtask_id, output)
            
            self.logger.info(f"✅ Subtask {subtask_id} completed")
            self.tasks_processed += 1
            
            # Track agent response in memory system
            if MEMORY_ENABLED:
                try:
                    tracker = get_conversation_tracker()
                    # Get user_id from parent task
                    task = db.query(Task).filter(Task.id == subtask.task_id).first()
                    response_content = self._extract_agent_output_for_memory(output)
                    tracker.track_agent_response(
                        agent_name=subtask.assigned_agent,
                        task_id=subtask.task_id,
                        response=response_content,
                        metadata={
                            "success": True,
                            "execution_time": (subtask.completed_at - subtask.created_at).total_seconds() if subtask.completed_at else 0
                        },
                        user_id=task.user_id if task else None
                    )
                except Exception as e:
                    self.logger.debug(f"Memory tracking skipped: {e}")
            
            # Emit WebSocket event for completion
            emit_task_event_sync(
                WebSocketEventType.AGENT_COMPLETED,
                subtask.task_id,
                {
                    "agent_name": subtask.assigned_agent,
                    "subtask_id": subtask_id,
                    "status": "completed"
                }
            )
            
            # Check if parent task is complete
            self._check_task_completion(db, subtask.task_id)
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Subtask {subtask_id} failed: {e}")
            
            # Mark as failed (will retry if retries < max)
            self.queue.mark_failed(subtask_id, str(e))
            
            # Update database — respect silent_retry to avoid UI red badges
            try:
                subtask = db.query(Subtask).filter(Subtask.id == subtask_id).first()
                if subtask:
                    if input_data.get("silent_retry"):
                        subtask.status = TaskStatus.IN_PROGRESS.value
                        subtask.error_message = f"Silent Retry: {str(e)}"
                        self.logger.info(f"🤐 Silent exception for {subtask.assigned_agent}, keeping IN_PROGRESS")
                    else:
                        subtask.status = TaskStatus.FAILED.value
                        subtask.error_message = str(e)
                    db.commit()
            except:
                pass
            
            self.tasks_failed += 1
            return False
        finally:
            db.close()
    
    async def execute_agent(
        self, 
        agent_name: str, 
        input_data: Dict[str, Any],
        db_session
    ) -> Dict[str, Any]:
        """
        Execute agent logic using the real agent framework.
        
        Args:
            agent_name: Name of the agent to execute
            input_data: Input data for the agent
            db_session: Database session
            
        Returns:
            Agent output dictionary
        """
        try:
            # Create agent using factory
            factory = AgentFactory(db_session=db_session, llm=llm_manager)
            agent = factory.create_agent(agent_name)
            
            self.logger.info(f"🔄 Agent {agent_name} starting execution...")
            
            # Execute the agent
            result = await agent.execute(input_data)
            
            self.logger.info(f"✅ Agent {agent_name} completed with status: {result.get('status')}")
            
            # Track agent output in memory system
            if MEMORY_ENABLED:
                try:
                    tracker = get_conversation_tracker()
                    task_id = input_data.get("task_id")
                    user_id = input_data.get("user_id")
                    
                    # Get output content
                    output_content = result.get("output", "")
                    if isinstance(output_content, dict):
                        output_content = str(output_content)
                    
                    if task_id and output_content:
                        tracker.track_agent_response(
                            agent_name=agent_name,
                            task_id=task_id,
                            response=output_content[:5000],  # Limit size
                            metadata={
                                "success": result.get("status") == "success",
                                "execution_time": result.get("execution_time_seconds", 0)
                            },
                            user_id=user_id
                        )
                        self.logger.debug(f"📝 Tracked {agent_name} output to memory")
                except Exception as mem_err:
                    self.logger.warning(f"⚠️ Failed to track agent output: {mem_err}")
            
            return result
            
        except ValueError as e:
            # Agent not found - use fallback
            self.logger.warning(f"⚠️ Agent {agent_name} not registered, using fallback")
            return self._fallback_execute(agent_name, input_data)
        except Exception as e:
            self.logger.error(f"❌ Agent {agent_name} execution error: {e}")
            return {
                "status": "error",
                "output": f"Agent execution failed: {str(e)}",
                "agent_name": agent_name,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def _fallback_execute(
        self,
        agent_name: str,
        input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Fallback execution for unregistered agents.
        Uses LLM directly.
        """
        prompt = input_data.get("original_prompt", "No prompt provided")
        
        system_prompt = f"""You are {agent_name} - an AI assistant.
Process this task and provide a helpful response.
Be concise but thorough."""

        response = llm_manager.generate(
            prompt=prompt,
            system=system_prompt,
            use_cache=False
        )
        
        return {
            "status": "success",
            "output": response or "Task processed successfully.",
            "agent_name": agent_name,
            "timestamp": datetime.utcnow().isoformat(),
            "note": "Executed using fallback (agent not fully implemented)"
        }
    
    def _extract_agent_output_for_memory(self, output: Dict[str, Any]) -> str:
        """
        Extract output content from agent result for memory storage.
        
        Args:
            output: Agent output dictionary
            
        Returns:
            String content suitable for memory storage
        """
        if not output:
            return ""
        
        # Get the main output content
        content = output.get("output", "")
        
        if isinstance(content, dict):
            # Try to extract meaningful text from dict
            if "content" in content:
                content = content["content"]
            elif "text" in content:
                content = content["text"]
            elif "body" in content:
                content = content.get("subject", "") + "\n\n" + content.get("body", "")
            else:
                content = str(content)
        
        if not isinstance(content, str):
            content = str(content)
        
        # Limit size for memory storage
        return content[:5000] if len(content) > 5000 else content
    
    def _check_task_completion(self, db, task_id: int):
        """Check if all subtasks are done and update parent task status accordingly."""
        subtasks = db.query(Subtask).filter(Subtask.task_id == task_id).all()

        if not subtasks:
            return

        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            return

        # Classify subtasks by status
        completed = [s for s in subtasks if s.status == TaskStatus.COMPLETED.value]
        failed = [s for s in subtasks if s.status == TaskStatus.FAILED.value]
        queued = [s for s in subtasks if s.status == TaskStatus.QUEUED.value]
        in_progress = [s for s in subtasks if s.status == TaskStatus.IN_PROGRESS.value]

        # If there are still genuinely queued items, worker hasn't finished yet
        if queued:
            return

        # Detect "stuck" IN_PROGRESS subtasks: running for more than 5 minutes
        # These are likely silent_retry subtasks that errored and got frozen
        STUCK_TIMEOUT_SECONDS = 300
        genuinely_running = []
        stuck = []
        now = datetime.utcnow()
        for s in in_progress:
            if s.created_at:
                elapsed = (now - s.created_at).total_seconds()
                if elapsed > STUCK_TIMEOUT_SECONDS:
                    stuck.append(s)
                else:
                    genuinely_running.append(s)
            else:
                stuck.append(s)

        # Mark stuck subtasks as failed so they don't block completion forever
        for s in stuck:
            s.status = TaskStatus.FAILED.value
            s.error_message = s.error_message or "Timed out — stuck in processing"
            self.logger.warning(f"⏱️ Subtask {s.id} ({s.assigned_agent}) was stuck, marked as failed")
        if stuck:
            db.commit()
            # Refresh failed list
            failed = [s for s in subtasks if s.status == TaskStatus.FAILED.value] + stuck

        # If there are still genuinely running subtasks, wait
        if genuinely_running:
            return

        # === All subtasks are now either completed or failed — resolve the task ===
        all_ok = all(s.status == TaskStatus.COMPLETED.value for s in subtasks if s not in stuck)
        any_ok = len(completed) > 0

        if all_ok and not failed and not stuck:
            # Perfect — everything completed
            combined_output = []
            for s in subtasks:
                if s.output_data:
                    agent = s.assigned_agent
                    output = s.output_data.get("output", "")

                    if isinstance(output, dict):
                        formatted = f"## {agent} Results\n\n"

                        def unwrap_text(val):
                            if isinstance(val, dict):
                                return val.get("summary") or val.get("text") or val.get("content") or str(val)
                            return str(val) if val else ""

                        if "content" in output:
                            formatted += unwrap_text(output.get("content"))
                        elif "body" in output:
                            subject = output.get("subject", "")
                            if subject:
                                formatted += f"**Subject:** {subject}\n\n"
                            formatted += output.get("body", "")
                        elif "documentation" in output:
                            formatted += unwrap_text(output.get("documentation"))
                        elif "tutorial" in output:
                            formatted += unwrap_text(output.get("tutorial"))
                        elif "readme" in output:
                            formatted += unwrap_text(output.get("readme"))
                        elif "summary" in output or "key_findings" in output:
                            summary_val = output.get("summary", "")
                            formatted += unwrap_text(summary_val)
                            key_findings = output.get("key_findings", [])
                            if key_findings and isinstance(key_findings, list):
                                formatted += "\n\n### Key Findings:\n"
                                for finding in key_findings:
                                    finding_text = unwrap_text(finding) if isinstance(finding, dict) else str(finding)
                                    formatted += f"- {finding_text}\n"
                            sources = output.get("sources", [])
                            if sources and isinstance(sources, list):
                                formatted += "\n\n### Sources:\n"
                                for src in sources[:5]:
                                    if isinstance(src, dict):
                                        formatted += f"- [{src.get('title', 'Link')}]({src.get('url', '')})\n"
                                    else:
                                        formatted += f"- {src}\n"
                        elif "code" in output:
                            lang = output.get("language", "")
                            code_text = output.get("code", "")
                            explanation = output.get("explanation") or output.get("description", "")
                            if explanation:
                                formatted += f"{unwrap_text(explanation)}\n\n"
                            formatted += f"```{lang}\n{code_text}\n```"
                        else:
                            for k, v in output.items():
                                if k in ["status", "agent_name", "execution_time_seconds", "tokens_used",
                                         "timestamp", "word_count", "estimated_read_time", "sections",
                                         "tags", "researched_at", "confidence_score", "query"]:
                                    continue
                                clean_key = k.replace("_", " ").title()
                                if isinstance(v, str) and v:
                                    formatted += f"\n\n### {clean_key}\n{v}"
                                elif isinstance(v, list) and v:
                                    formatted += f"\n\n### {clean_key}\n"
                                    for item in v[:15]:
                                        item_text = unwrap_text(item) if isinstance(item, dict) else str(item)
                                        formatted += f"- {item_text}\n"
                                elif isinstance(v, dict):
                                    formatted += f"\n\n### {clean_key}\n{unwrap_text(v)}"
                        combined_output.append(formatted)
                    elif output:
                        combined_output.append(f"## {agent} Results\n\n{output}")

            task.status = TaskStatus.COMPLETED.value
            task.output = "\n\n---\n\n".join(combined_output)
            task.completed_at = datetime.utcnow()
            self.logger.info(f"🎉 Task {task_id} completed successfully!")

            emit_task_event_sync(
                WebSocketEventType.TASK_COMPLETED,
                task_id,
                {"status": "completed", "message": "All subtasks completed successfully"}
            )

        elif any_ok:
            # Partial success — at least some agents succeeded, compile what we have
            combined_output = []
            for s in completed:
                if s.output_data:
                    agent = s.assigned_agent
                    output = s.output_data.get("output", "")
                    if isinstance(output, dict):
                        combined_output.append(f"## {agent} Results\n\n{str(output)}")
                    elif output:
                        combined_output.append(f"## {agent} Results\n\n{output}")

            task.status = TaskStatus.COMPLETED.value
            task.output = "\n\n---\n\n".join(combined_output) if combined_output else "Task completed with partial results."
            task.completed_at = datetime.utcnow()
            self.logger.warning(f"⚠️ Task {task_id} completed with partial results ({len(completed)}/{len(subtasks)} subtasks succeeded)")

            emit_task_event_sync(
                WebSocketEventType.TASK_COMPLETED,
                task_id,
                {"status": "completed", "message": f"Completed with partial results ({len(completed)}/{len(subtasks)} subtasks)"}
            )

        else:
            # Total failure — nothing succeeded
            task.status = TaskStatus.FAILED.value
            task.completed_at = datetime.utcnow()
            self.logger.error(f"❌ Task {task_id} failed — no subtasks completed")

            emit_task_event_sync(
                WebSocketEventType.TASK_FAILED,
                task_id,
                {"status": "failed", "message": "All subtasks failed"}
            )

        db.commit()

    
    def shutdown(self):
        """Gracefully shutdown the worker."""
        self.running = False
        self.logger.info(f"👋 Worker {self.worker_id} shutting down")
        self.logger.info(f"📊 Stats: Processed={self.tasks_processed}, Failed={self.tasks_failed}")


def run_worker():
    """Entry point to run a worker."""
    worker = Worker()
    
    # Set up signal handlers
    def signal_handler(sig, frame):
        print("\n🛑 Shutting down worker...")
        worker.running = False
    
    try:
        import signal
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    except (ValueError, RuntimeError):
        # Signals only work in main thread
        pass
    
    # Start worker
    worker.run()


def start_worker_thread():
    """Starts the worker in a background thread (for single-process environments)."""
    import threading
    worker = Worker()
    thread = threading.Thread(target=worker.run, daemon=True)
    thread.start()
    return thread


if __name__ == "__main__":
    run_worker()
