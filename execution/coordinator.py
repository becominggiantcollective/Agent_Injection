"""
Agent coordination and management.
"""

from typing import Dict, List, Any, Optional, Set
from core.base import BaseAgent


class AgentCoordinator:
    """Coordinates agent lifecycle and resource allocation."""
    
    def __init__(self):
        """Initialize agent coordinator."""
        self.agents: Dict[str, BaseAgent] = {}
        self.agent_groups: Dict[str, Set[str]] = {}
        self.agent_locks: Dict[str, bool] = {}
        self.resource_usage: Dict[str, Dict[str, Any]] = {}
    
    def register_agent(self, agent: BaseAgent, group: Optional[str] = None) -> None:
        """Register an agent with the coordinator."""
        self.agents[agent.agent_id] = agent
        self.agent_locks[agent.agent_id] = False
        self.resource_usage[agent.agent_id] = {
            "active_tasks": 0,
            "total_tasks_completed": 0,
            "last_activity": None
        }
        
        if group:
            if group not in self.agent_groups:
                self.agent_groups[group] = set()
            self.agent_groups[group].add(agent.agent_id)
    
    def unregister_agent(self, agent_id: str) -> bool:
        """Unregister an agent."""
        if agent_id not in self.agents:
            return False
        
        # Remove from all groups
        for group_agents in self.agent_groups.values():
            group_agents.discard(agent_id)
        
        # Clean up
        del self.agents[agent_id]
        del self.agent_locks[agent_id]
        del self.resource_usage[agent_id]
        
        return True
    
    def get_available_agents(self, group: Optional[str] = None) -> List[BaseAgent]:
        """Get list of available (unlocked) agents."""
        if group:
            agent_ids = self.agent_groups.get(group, set())
        else:
            agent_ids = set(self.agents.keys())
        
        available = []
        for agent_id in agent_ids:
            if not self.agent_locks.get(agent_id, True):
                available.append(self.agents[agent_id])
        
        return available
    
    def lock_agent(self, agent_id: str) -> bool:
        """Lock an agent for exclusive use."""
        if agent_id not in self.agents:
            return False
        
        if self.agent_locks[agent_id]:
            return False  # Already locked
        
        self.agent_locks[agent_id] = True
        return True
    
    def unlock_agent(self, agent_id: str) -> bool:
        """Unlock an agent."""
        if agent_id not in self.agents:
            return False
        
        self.agent_locks[agent_id] = False
        return True
    
    def select_best_agents(self, task: Dict[str, Any], max_agents: int = 5, group: Optional[str] = None) -> List[BaseAgent]:
        """Select the best agents for a given task."""
        available_agents = self.get_available_agents(group)
        
        # Filter agents that can handle the task
        suitable_agents = [agent for agent in available_agents if agent.validate_task(task)]
        
        # Score and sort agents
        scored_agents = []
        for agent in suitable_agents:
            score = self._score_agent_for_task(agent, task)
            scored_agents.append((score, agent))
        
        # Sort by score (descending) and return top agents
        scored_agents.sort(key=lambda x: x[0], reverse=True)
        return [agent for _, agent in scored_agents[:max_agents]]
    
    def _score_agent_for_task(self, agent: BaseAgent, task: Dict[str, Any]) -> float:
        """Score an agent for a specific task."""
        score = 0.0
        
        # Base score for capability match
        task_requirements = task.get("requirements", [])
        agent_capabilities = agent.get_capabilities()
        
        if task_requirements:
            matches = len(set(task_requirements) & set(agent_capabilities))
            score += (matches / len(task_requirements)) * 0.6
        else:
            score += 0.6  # No specific requirements
        
        # Bonus for low current load
        usage = self.resource_usage.get(agent.agent_id, {})
        active_tasks = usage.get("active_tasks", 0)
        if active_tasks == 0:
            score += 0.3
        elif active_tasks < 3:
            score += 0.1
        
        # Bonus for experience (completed tasks)
        completed_tasks = usage.get("total_tasks_completed", 0)
        if completed_tasks > 10:
            score += 0.1
        elif completed_tasks > 5:
            score += 0.05
        
        return score
    
    def update_agent_usage(self, agent_id: str, task_started: bool = False, task_completed: bool = False) -> None:
        """Update agent usage statistics."""
        if agent_id not in self.resource_usage:
            return
        
        usage = self.resource_usage[agent_id]
        
        if task_started:
            usage["active_tasks"] = usage.get("active_tasks", 0) + 1
            from datetime import datetime
            usage["last_activity"] = datetime.now()
        
        if task_completed:
            usage["active_tasks"] = max(0, usage.get("active_tasks", 0) - 1)
            usage["total_tasks_completed"] = usage.get("total_tasks_completed", 0) + 1
            from datetime import datetime
            usage["last_activity"] = datetime.now()
    
    def get_coordinator_status(self) -> Dict[str, Any]:
        """Get overall coordinator status."""
        total_agents = len(self.agents)
        locked_agents = sum(1 for locked in self.agent_locks.values() if locked)
        
        return {
            "total_agents": total_agents,
            "available_agents": total_agents - locked_agents,
            "locked_agents": locked_agents,
            "agent_groups": {group: len(agents) for group, agents in self.agent_groups.items()},
            "resource_usage": self.resource_usage
        }