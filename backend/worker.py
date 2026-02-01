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
        
        while self.running:
            try:
                # Try to get a subtask from queue
                subtask_id = self.queue.dequeue(timeout=polling_interval)
                
                if subtask_id is None:
                    # Queue empty, continue polling
                    continue
                
                # Process the subtask
                self.logger.info(f"📥 Picked up subtask {subtask_id}")
                self.process_subtask(subtask_id)
                
            except KeyboardInterrupt:
                self.logger.info("⚠️ Received interrupt signal")
                break
            except Exception as e:
                self.logger.error(f"❌ Worker error: {e}")
                time.sleep(polling_interval)
        
        self.shutdown()
    
    @retry(exceptions=(DatabaseError, AgentError), tries=3, delay=1)
    def process_subtask(self, subtask_id: int) -> bool:
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
                self.logger.info(f"🔧 QAAgent missing content, attempting to fetch from previous subtask...")
                # Find most recent completed sibling subtask
                prev_subtask = db.query(Subtask).filter(
                    Subtask.task_id == subtask.task_id,
                    Subtask.id < subtask_id,
                    Subtask.status == TaskStatus.COMPLETED.value
                ).order_by(Subtask.id.desc()).first()
                
                if prev_subtask and prev_subtask.output_data:
                    self.logger.info(f"✅ Found previous subtask {prev_subtask.id} ({prev_subtask.assigned_agent})")
                    output_content = prev_subtask.output_data.get("output", "")
                    if isinstance(output_content, dict):
                         if "code" in output_content: output_content = output_content["code"]
                         elif "content" in output_content: output_content = output_content["content"]
                         else: output_content = str(output_content)
                    
                    input_data = dict(input_data) # Create copy to modify
                    input_data["content"] = str(output_content)
                    input_data["content_type"] = "code" if prev_subtask.assigned_agent == "CodeAgent" else "general"
                    self.logger.info(f"💉 Injected content (len={len(input_data['content'])}) into QAAgent input")
                else:
                    self.logger.warning("⚠️ No previous completed subtask found to inject content from")
            # END FIX

            output = self.execute_agent(
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
                subtask.status = TaskStatus.FAILED.value
                subtask.error_message = output.get("output", "Agent execution failed")
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
            
            # Update database
            try:
                subtask = db.query(Subtask).filter(Subtask.id == subtask_id).first()
                if subtask:
                    subtask.status = TaskStatus.FAILED.value
                    subtask.error_message = str(e)
                    db.commit()
            except:
                pass
            
            self.tasks_failed += 1
            return False
        finally:
            db.close()
    
    def execute_agent(
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
            result = agent.execute(input_data)
            
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
        """Check if all subtasks are complete and update parent task."""
        subtasks = db.query(Subtask).filter(Subtask.task_id == task_id).all()
        
        if not subtasks:
            return
        
        all_completed = all(s.status == TaskStatus.COMPLETED.value for s in subtasks)
        any_failed = any(s.status == TaskStatus.FAILED.value for s in subtasks)
        
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            return
        
        if all_completed:
            # Combine outputs from all subtasks
            combined_output = []
            for s in subtasks:
                if s.output_data:
                    agent = s.assigned_agent
                    output = s.output_data.get("output", "")
                    
                    # Handle nested output structure
                    if isinstance(output, dict):
                        formatted = f"## {agent} Results\n\n"
                        
                        # Content-based outputs (blog, documentation, email, etc.)
                        if "content" in output:
                            formatted += output.get("content", "")
                        elif "body" in output:
                            # Email format
                            subject = output.get("subject", "")
                            if subject:
                                formatted += f"**Subject:** {subject}\n\n"
                            formatted += output.get("body", "")
                        elif "documentation" in output:
                            formatted += output.get("documentation", "")
                        elif "tutorial" in output:
                            formatted += output.get("tutorial", "")
                        elif "readme" in output:
                            formatted += output.get("readme", "")
                        elif "summary" in output:
                            # Research format
                            formatted += output.get("summary", "")
                            key_findings = output.get("key_findings", [])
                            sources = output.get("sources", [])
                            
                            if key_findings:
                                formatted += "\n\n### Key Findings:\n"
                                for finding in key_findings:
                                    formatted += f"- {finding}\n"
                            
                            if sources:
                                formatted += "\n\n### Sources:\n"
                                for src in sources[:3]:
                                    formatted += f"- [{src.get('title', 'Link')}]({src.get('url', '')})\n"
                        elif "code" in output:
                            # Code format
                            lang = output.get("language", "")
                            formatted += f"```{lang}\n{output.get('code', '')}\n```"
                        else:
                            # Fallback: show all key-value pairs
                            for k, v in output.items():
                                if k not in ["word_count", "estimated_read_time", "sections", "tags"]:
                                    if isinstance(v, str) and len(v) > 50:
                                        formatted += f"\n\n### {k.replace('_', ' ').title()}\n{v}"
                                    elif isinstance(v, list):
                                        formatted += f"\n\n### {k.replace('_', ' ').title()}\n"
                                        for item in v[:10]:
                                            formatted += f"- {item}\n"
                        
                        combined_output.append(formatted)
                    elif output:
                        combined_output.append(f"## {agent} Results\n\n{output}")
            
            task.status = TaskStatus.COMPLETED.value
            task.output = "\n\n---\n\n".join(combined_output)
            task.completed_at = datetime.utcnow()
            
            self.logger.info(f"🎉 Task {task_id} completed!")
            
            # Emit task completed event
            emit_task_event_sync(
                WebSocketEventType.TASK_COMPLETED,
                task_id,
                {
                    "status": "completed",
                    "message": "All subtasks completed successfully"
                }
            )
            
        elif any_failed and not any(s.status in [TaskStatus.QUEUED.value, TaskStatus.IN_PROGRESS.value] for s in subtasks):
            # All done but some failed
            task.status = TaskStatus.FAILED.value
            self.logger.warning(f"⚠️ Task {task_id} has failed subtasks")
            
            # Emit task failed event
            emit_task_event_sync(
                WebSocketEventType.TASK_FAILED,
                task_id,
                {
                    "status": "failed",
                    "message": "Some subtasks failed"
                }
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
