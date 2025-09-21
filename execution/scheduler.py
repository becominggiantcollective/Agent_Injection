"""
Task scheduling and management.
"""

import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum


class TaskStatus(Enum):
    """Task execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ScheduledTask:
    """Represents a scheduled task."""
    task_id: str
    task_data: Dict[str, Any]
    strategy_id: str
    agent_ids: Optional[List[str]]
    scheduled_at: datetime
    priority: int = 0
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class TaskScheduler:
    """Schedules and manages task execution."""
    
    def __init__(self, max_concurrent_tasks: int = 5):
        """Initialize task scheduler."""
        self.max_concurrent_tasks = max_concurrent_tasks
        self.pending_tasks: List[ScheduledTask] = []
        self.running_tasks: Dict[str, ScheduledTask] = {}
        self.completed_tasks: Dict[str, ScheduledTask] = {}
        self.is_running = False
        self._scheduler_task: Optional[asyncio.Task] = None
    
    def schedule_task(
        self, 
        task_id: str, 
        task_data: Dict[str, Any], 
        strategy_id: str,
        agent_ids: Optional[List[str]] = None,
        delay_seconds: int = 0,
        priority: int = 0
    ) -> str:
        """Schedule a task for execution."""
        scheduled_at = datetime.now() + timedelta(seconds=delay_seconds)
        
        scheduled_task = ScheduledTask(
            task_id=task_id,
            task_data=task_data,
            strategy_id=strategy_id,
            agent_ids=agent_ids,
            scheduled_at=scheduled_at,
            priority=priority
        )
        
        self.pending_tasks.append(scheduled_task)
        self.pending_tasks.sort(key=lambda t: (t.scheduled_at, -t.priority))
        
        return task_id
    
    async def start_scheduler(self, execution_engine) -> None:
        """Start the task scheduler."""
        if self.is_running:
            return
        
        self.is_running = True
        self._scheduler_task = asyncio.create_task(self._scheduler_loop(execution_engine))
    
    async def stop_scheduler(self) -> None:
        """Stop the task scheduler."""
        self.is_running = False
        if self._scheduler_task:
            self._scheduler_task.cancel()
            try:
                await self._scheduler_task
            except asyncio.CancelledError:
                pass
    
    async def _scheduler_loop(self, execution_engine) -> None:
        """Main scheduler loop."""
        while self.is_running:
            try:
                await self._process_pending_tasks(execution_engine)
                await asyncio.sleep(1)  # Check every second
            except Exception as e:
                print(f"Scheduler error: {e}")
                await asyncio.sleep(5)  # Wait before retrying
    
    async def _process_pending_tasks(self, execution_engine) -> None:
        """Process pending tasks that are ready to run."""
        now = datetime.now()
        
        # Move ready tasks to running if we have capacity
        while (len(self.running_tasks) < self.max_concurrent_tasks and 
               self.pending_tasks and 
               self.pending_tasks[0].scheduled_at <= now):
            
            task = self.pending_tasks.pop(0)
            task.status = TaskStatus.RUNNING
            self.running_tasks[task.task_id] = task
            
            # Start task execution
            asyncio.create_task(self._execute_task(task, execution_engine))
    
    async def _execute_task(self, task: ScheduledTask, execution_engine) -> None:
        """Execute a single task."""
        try:
            result = await execution_engine.execute_single_task(
                task.task_data, 
                task.strategy_id, 
                task.agent_ids
            )
            task.result = result
            task.status = TaskStatus.COMPLETED
        except Exception as e:
            task.error = str(e)
            task.status = TaskStatus.FAILED
        finally:
            # Move from running to completed
            if task.task_id in self.running_tasks:
                del self.running_tasks[task.task_id]
            self.completed_tasks[task.task_id] = task
    
    def cancel_task(self, task_id: str) -> bool:
        """Cancel a pending task."""
        for i, task in enumerate(self.pending_tasks):
            if task.task_id == task_id:
                task.status = TaskStatus.CANCELLED
                self.pending_tasks.pop(i)
                self.completed_tasks[task_id] = task
                return True
        return False
    
    def get_task_status(self, task_id: str) -> Optional[TaskStatus]:
        """Get status of a specific task."""
        # Check running tasks
        if task_id in self.running_tasks:
            return self.running_tasks[task_id].status
        
        # Check completed tasks
        if task_id in self.completed_tasks:
            return self.completed_tasks[task_id].status
        
        # Check pending tasks
        for task in self.pending_tasks:
            if task.task_id == task_id:
                return task.status
        
        return None
    
    def get_queue_status(self) -> Dict[str, int]:
        """Get overall queue status."""
        return {
            "pending": len(self.pending_tasks),
            "running": len(self.running_tasks),
            "completed": len(self.completed_tasks)
        }