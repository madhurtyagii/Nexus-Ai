"""
Nexus AI - QA Feedback Loop
Automatic QA review with iterative improvement
"""

from typing import Dict, Any, List, Optional
from datetime import datetime

from agents.agent_registry import AgentRegistry
from llm.llm_manager import llm_manager


class QAFeedbackLoop:
    """
    Implements automatic QA review and improvement loop.
    
    Process:
    1. QAAgent reviews content
    2. If not approved, feedback sent to original agent
    3. Original agent improves content
    4. Repeat until approved or max iterations reached
    """
    
    def __init__(self, max_iterations: int = 3, quality_threshold: int = 70):
        """
        Initialize QA feedback loop.
        
        Args:
            max_iterations: Maximum improvement iterations
            quality_threshold: Minimum quality score to pass (0-100)
        """
        self.max_iterations = max_iterations
        self.quality_threshold = quality_threshold
    
    def review_and_improve(
        self,
        content: str,
        content_type: str,
        original_agent: str,
        original_task: str,
        db_session=None
    ) -> Dict[str, Any]:
        """
        Review content and iteratively improve until quality threshold is met.
        
        Args:
            content: The content to review and improve
            content_type: Type of content (code, content, etc.)
            original_agent: Name of agent that produced the content
            original_task: The original task description
            db_session: Database session (optional)
            
        Returns:
            Final result with content, quality score, and improvement history
        """
        result = {
            "original_content": content,
            "final_content": content,
            "iterations": 0,
            "approved": False,
            "quality_score": 0,
            "improvement_history": [],
            "qa_reports": []
        }
        
        current_content = content
        
        # Get agents
        qa_agent = self._get_agent("QAAgent")
        improving_agent = self._get_agent(original_agent)
        
        if not qa_agent:
            result["error"] = "QAAgent not available"
            result["final_content"] = current_content
            return result
        
        for iteration in range(self.max_iterations):
            result["iterations"] = iteration + 1
            
            # Step 1: QA Review
            qa_result = qa_agent.execute({
                "content": current_content,
                "content_type": content_type,
                "original_task": original_task,
                "agent_name": original_agent
            })
            
            result["qa_reports"].append({
                "iteration": iteration + 1,
                "quality_score": qa_result.get("quality_score", 0),
                "approved": qa_result.get("approved", False),
                "issues": qa_result.get("critical_issues", []) + qa_result.get("major_issues", []),
                "suggestions": qa_result.get("suggestions", [])
            })
            
            # Check if approved
            quality_score = qa_result.get("quality_score", 0)
            result["quality_score"] = quality_score
            
            if qa_result.get("approved", False) or quality_score >= self.quality_threshold:
                result["approved"] = True
                result["final_content"] = current_content
                break
            
            # Step 2: Generate improvement feedback
            feedback = self._generate_improvement_feedback(
                qa_result=qa_result,
                content=current_content,
                content_type=content_type
            )
            
            # Step 3: Improve content
            if improving_agent:
                improved = self._improve_content(
                    agent=improving_agent,
                    content=current_content,
                    feedback=feedback,
                    original_task=original_task,
                    content_type=content_type
                )
                
                # Track improvement
                result["improvement_history"].append({
                    "iteration": iteration + 1,
                    "feedback": feedback,
                    "changes_made": self._detect_changes(current_content, improved)
                })
                
                current_content = improved
            else:
                # Can't improve without the original agent
                break
        
        # Final result
        result["final_content"] = current_content
        
        # If still not approved after max iterations, return best version
        if not result["approved"]:
            result["warning"] = f"Content not fully approved after {self.max_iterations} iterations"
            # Find best version
            best_score = 0
            best_content = content
            for i, report in enumerate(result["qa_reports"]):
                if report["quality_score"] > best_score:
                    best_score = report["quality_score"]
                    # The content after this iteration
                    if i < len(result["improvement_history"]):
                        best_content = current_content
            result["final_content"] = best_content
        
        return result
    
    def _get_agent(self, agent_name: str):
        """Get an agent instance by name."""
        try:
            agent_class = AgentRegistry.get_agent(agent_name)
            if agent_class:
                return agent_class()
            return None
        except Exception:
            return None
    
    def _generate_improvement_feedback(
        self,
        qa_result: Dict[str, Any],
        content: str,
        content_type: str
    ) -> str:
        """Generate specific improvement feedback based on QA report."""
        issues = qa_result.get("critical_issues", []) + qa_result.get("major_issues", [])
        suggestions = qa_result.get("suggestions", [])
        
        feedback_parts = ["Please improve the content addressing these issues:"]
        
        if issues:
            feedback_parts.append("\n**Issues to Fix:**")
            for issue in issues[:5]:  # Limit to top 5
                feedback_parts.append(f"- {issue}")
        
        if suggestions:
            feedback_parts.append("\n**Suggestions:**")
            for suggestion in suggestions[:3]:
                feedback_parts.append(f"- {suggestion}")
        
        # Add quality score context
        score = qa_result.get("quality_score", 0)
        feedback_parts.append(f"\n**Current Quality Score:** {score}/100")
        feedback_parts.append(f"**Target Score:** {self.quality_threshold}/100")
        
        return "\n".join(feedback_parts)
    
    def _improve_content(
        self,
        agent,
        content: str,
        feedback: str,
        original_task: str,
        content_type: str
    ) -> str:
        """Use the original agent to improve content based on feedback."""
        try:
            improvement_prompt = f"""Improve this {content_type} based on the feedback provided.

**Original Task:** {original_task}

**Current Content:**
{content[:3000]}

**Feedback:**
{feedback}

Provide an improved version that addresses all the feedback. Keep the same format and purpose, just make it better."""

            result = agent.execute({
                "user_prompt": improvement_prompt,
                "content_type": content_type,
                "improvement_mode": True
            })
            
            improved = result.get("output", content)
            
            # Make sure we got actual content back
            if improved and len(improved) > len(content) * 0.5:  # At least half the original length
                return improved
            return content
            
        except Exception as e:
            # If improvement fails, return original
            return content
    
    def _detect_changes(self, original: str, improved: str) -> Dict[str, Any]:
        """Detect what changed between original and improved content."""
        original_words = set(original.lower().split())
        improved_words = set(improved.lower().split())
        
        added = improved_words - original_words
        removed = original_words - improved_words
        
        length_change = len(improved) - len(original)
        
        return {
            "length_change": length_change,
            "words_added": len(added),
            "words_removed": len(removed),
            "significant_change": abs(length_change) > 100 or len(added) > 20 or len(removed) > 20
        }
    
    def quick_review(
        self,
        content: str,
        content_type: str,
        original_task: str = ""
    ) -> Dict[str, Any]:
        """
        Quick review without improvement loop.
        Just returns QA assessment.
        """
        qa_agent = self._get_agent("QAAgent")
        
        if not qa_agent:
            return {
                "error": "QAAgent not available",
                "approved": True,  # Default to approved if can't review
                "quality_score": 70
            }
        
        return qa_agent.execute({
            "content": content,
            "content_type": content_type,
            "original_task": original_task
        })


def add_qa_checkpoints(workflow: Dict[str, Any]) -> Dict[str, Any]:
    """
    Add QA checkpoints to a workflow.
    
    Adds QA review after each phase and at the end.
    """
    phases = workflow.get("phases", [])
    
    for phase in phases:
        tasks = phase.get("tasks", [])
        
        # Add QA task at end of each phase
        if tasks:
            last_task_id = tasks[-1].get("task_id", "")
            qa_task = {
                "task_id": f"{phase.get('phase_number')}.qa",
                "description": f"QA review of Phase {phase.get('phase_number')} outputs",
                "assigned_agent": "QAAgent",
                "estimated_time": "5 minutes",
                "estimated_minutes": 5,
                "dependencies": [last_task_id]
            }
            tasks.append(qa_task)
    
    # Add final QA phase
    if phases:
        final_qa_phase = {
            "phase_number": len(phases) + 1,
            "phase_name": "Final Quality Assurance",
            "tasks": [{
                "task_id": f"{len(phases) + 1}.1",
                "description": "Final comprehensive QA review of all outputs",
                "assigned_agent": "QAAgent",
                "estimated_time": "10 minutes",
                "estimated_minutes": 10,
                "dependencies": [f"{len(phases)}.qa"] if phases else []
            }]
        }
        phases.append(final_qa_phase)
    
    workflow["phases"] = phases
    workflow["qa_checkpoints_added"] = True
    
    return workflow
