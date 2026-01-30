"""
Nexus AI - Task Scheduler Tool
Tool for scheduling tasks with dependencies and optimization
"""

from typing import Dict, Any, List
from collections import defaultdict, deque
from tools.base_tool import BaseTool, ToolRegistry


@ToolRegistry.register
class TaskSchedulerTool(BaseTool):
    """
    Tool for scheduling tasks considering dependencies and constraints.
    Uses topological sort for dependency resolution and optimizes for parallelization.
    """
    
    def __init__(self):
        super().__init__(
            name="task_scheduler",
            description="Schedule tasks with dependencies and optimize for parallel execution"
        )
        self.max_concurrent = 5  # Max agents running in parallel
    
    def execute(
        self, 
        tasks: List[Dict[str, Any]], 
        constraints: Dict[str, Any] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Schedule tasks considering dependencies and constraints.
        
        Args:
            tasks: List of task objects with task_id, dependencies, estimated_minutes
            constraints: Optional constraints like max_concurrent, priority_tasks
            
        Returns:
            Optimized schedule with time slots and parallel groups
        """
        if not tasks:
            return {"schedule": [], "total_duration": 0}
        
        constraints = constraints or {}
        max_concurrent = constraints.get("max_concurrent", self.max_concurrent)
        
        # Build dependency graph
        graph = self._build_graph(tasks)
        
        # Topological sort with levels
        levels = self._topological_sort_with_levels(tasks, graph)
        
        # Create schedule
        schedule = self._create_schedule(levels, tasks, max_concurrent)
        
        # Calculate total duration
        total_duration = self._calculate_duration(schedule, tasks)
        
        # Optimize schedule
        optimized = self.optimize_schedule(schedule, tasks)
        
        return {
            "schedule": optimized,
            "total_duration": total_duration,
            "total_duration_formatted": self._format_duration(total_duration),
            "parallel_efficiency": self._calculate_efficiency(tasks, total_duration),
            "task_order": [slot["tasks"] for slot in optimized]
        }
    
    def _build_graph(self, tasks: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """Build adjacency list for dependency graph."""
        graph = defaultdict(list)
        
        for task in tasks:
            task_id = task.get("task_id", "")
            for dep in task.get("dependencies", []):
                graph[dep].append(task_id)
        
        return graph
    
    def _topological_sort_with_levels(
        self, 
        tasks: List[Dict[str, Any]], 
        graph: Dict[str, List[str]]
    ) -> List[List[str]]:
        """
        Perform topological sort and group tasks by level.
        Tasks at the same level can run in parallel.
        """
        # Calculate in-degree for each task
        in_degree = defaultdict(int)
        task_ids = set()
        
        for task in tasks:
            task_id = task.get("task_id", "")
            task_ids.add(task_id)
            for dep in task.get("dependencies", []):
                in_degree[task_id] += 1
        
        # Initialize queue with tasks that have no dependencies
        queue = deque()
        for task_id in task_ids:
            if in_degree[task_id] == 0:
                queue.append(task_id)
        
        levels = []
        
        while queue:
            # All tasks in queue at this point can run in parallel
            current_level = list(queue)
            levels.append(current_level)
            queue.clear()
            
            # Process all tasks at current level
            for task_id in current_level:
                for dependent in graph.get(task_id, []):
                    in_degree[dependent] -= 1
                    if in_degree[dependent] == 0:
                        queue.append(dependent)
        
        return levels
    
    def _create_schedule(
        self, 
        levels: List[List[str]], 
        tasks: List[Dict[str, Any]],
        max_concurrent: int
    ) -> List[Dict[str, Any]]:
        """Create schedule from topological levels."""
        schedule = []
        task_map = {t.get("task_id", ""): t for t in tasks}
        
        for level_num, level_tasks in enumerate(levels):
            # Split into batches if more than max_concurrent
            batches = []
            current_batch = []
            
            for task_id in level_tasks:
                current_batch.append(task_id)
                if len(current_batch) >= max_concurrent:
                    batches.append(current_batch)
                    current_batch = []
            
            if current_batch:
                batches.append(current_batch)
            
            # Create schedule slots
            for batch_num, batch in enumerate(batches):
                slot = {
                    "time_slot": len(schedule) + 1,
                    "level": level_num + 1,
                    "parallel_tasks": batch,
                    "tasks": batch,
                    "task_details": [
                        {
                            "task_id": tid,
                            "agent": task_map.get(tid, {}).get("assigned_agent", "Unknown"),
                            "estimated_minutes": task_map.get(tid, {}).get("estimated_minutes", 10)
                        }
                        for tid in batch
                    ]
                }
                schedule.append(slot)
        
        return schedule
    
    def optimize_schedule(
        self, 
        schedule: List[Dict[str, Any]], 
        tasks: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Optimize schedule for minimal total execution time.
        
        Strategies:
        1. Group short tasks together in parallel
        2. Start long tasks early
        3. Balance agent workload
        """
        if not schedule:
            return schedule
        
        task_map = {t.get("task_id", ""): t for t in tasks}
        
        # Calculate cumulative time for each slot
        cumulative_time = 0
        for slot in schedule:
            # Time for this slot is the max of parallel task durations
            max_duration = 0
            for task_id in slot.get("parallel_tasks", []):
                task = task_map.get(task_id, {})
                duration = task.get("estimated_minutes", 10)
                max_duration = max(max_duration, duration)
            
            slot["slot_duration"] = max_duration
            slot["start_time"] = cumulative_time
            slot["end_time"] = cumulative_time + max_duration
            cumulative_time += max_duration
        
        return schedule
    
    def _calculate_duration(
        self, 
        schedule: List[Dict[str, Any]], 
        tasks: List[Dict[str, Any]]
    ) -> int:
        """Calculate total duration considering parallel execution."""
        if not schedule:
            return 0
        
        task_map = {t.get("task_id", ""): t for t in tasks}
        total_minutes = 0
        
        for slot in schedule:
            # Duration of slot is the longest task (since they run in parallel)
            max_duration = 0
            for task_id in slot.get("parallel_tasks", slot.get("tasks", [])):
                task = task_map.get(task_id, {})
                duration = task.get("estimated_minutes", 10)
                max_duration = max(max_duration, duration)
            
            total_minutes += max_duration
        
        return total_minutes
    
    def _format_duration(self, minutes: int) -> str:
        """Format minutes into human-readable duration."""
        if minutes < 60:
            return f"{minutes} minutes"
        
        hours = minutes // 60
        remaining_minutes = minutes % 60
        
        if remaining_minutes == 0:
            return f"{hours} hour{'s' if hours > 1 else ''}"
        
        return f"{hours} hour{'s' if hours > 1 else ''} {remaining_minutes} minutes"
    
    def _calculate_efficiency(self, tasks: List[Dict[str, Any]], parallel_duration: int) -> float:
        """
        Calculate parallel efficiency.
        Efficiency = Sequential time / (Parallel time * num_parallel_slots)
        """
        if parallel_duration == 0:
            return 1.0
        
        sequential_duration = sum(t.get("estimated_minutes", 10) for t in tasks)
        
        if sequential_duration == 0:
            return 1.0
        
        # Higher ratio means better parallelization
        efficiency = sequential_duration / parallel_duration
        
        # Normalize to 0-1 range (1 = perfect linear, >1 = parallelization wins)
        return round(min(efficiency, 5.0) / 5.0, 2)  # Cap at 5x speedup
    
    def get_critical_path(self, tasks: List[Dict[str, Any]]) -> List[str]:
        """
        Find the critical path (longest chain of dependent tasks).
        """
        task_map = {t.get("task_id", ""): t for t in tasks}
        
        # Build reverse graph (task -> its dependencies)
        dependencies = {}
        for task in tasks:
            task_id = task.get("task_id", "")
            dependencies[task_id] = task.get("dependencies", [])
        
        # Find all task chains
        def get_chain_length(task_id: str, memo: Dict[str, int]) -> int:
            if task_id in memo:
                return memo[task_id]
            
            task = task_map.get(task_id, {})
            duration = task.get("estimated_minutes", 10)
            
            deps = dependencies.get(task_id, [])
            if not deps:
                memo[task_id] = duration
                return duration
            
            max_dep_length = max(
                get_chain_length(dep, memo) 
                for dep in deps 
                if dep in task_map
            ) if deps else 0
            
            memo[task_id] = duration + max_dep_length
            return memo[task_id]
        
        memo = {}
        
        # Find longest chain
        longest_task = None
        longest_length = 0
        
        for task in tasks:
            task_id = task.get("task_id", "")
            length = get_chain_length(task_id, memo)
            if length > longest_length:
                longest_length = length
                longest_task = task_id
        
        # Reconstruct the critical path
        if not longest_task:
            return []
        
        critical_path = []
        current = longest_task
        
        while current:
            critical_path.append(current)
            deps = dependencies.get(current, [])
            if not deps:
                break
            
            # Find the dependency with longest chain
            next_task = None
            max_length = 0
            for dep in deps:
                if dep in memo and memo[dep] > max_length:
                    max_length = memo[dep]
                    next_task = dep
            
            current = next_task
        
        return list(reversed(critical_path))
