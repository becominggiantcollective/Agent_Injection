"""
Adaptive execution strategy.
"""

from typing import List, Dict, Any
from core.base import BaseStrategy, BaseAgent


class AdaptiveStrategy(BaseStrategy):
    """Adaptive strategy that chooses execution method based on task and agent characteristics."""
    
    def __init__(self, strategy_id: str, config: Dict[str, Any] = None):
        """Initialize adaptive strategy."""
        super().__init__(strategy_id, config)
        self.parallel_threshold = self.config.get("parallel_threshold", 3)
        self.timeout_threshold = self.config.get("timeout_threshold", 60)
    
    async def execute(self, agents: List[BaseAgent], task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute using adaptive strategy."""
        selected_agents = self.select_agents(agents, task)
        
        # Decide execution strategy based on task and agent characteristics
        if len(selected_agents) >= self.parallel_threshold:
            strategy_type = "parallel"
            # Import here to avoid circular imports
            from .parallel import ParallelStrategy
            strategy = ParallelStrategy("adaptive_parallel", self.config)
        else:
            strategy_type = "sequential"
            from .sequential import SequentialStrategy
            strategy = SequentialStrategy("adaptive_sequential", self.config)
        
        result = await strategy.execute(selected_agents, task)
        result["adaptive_strategy"] = strategy_type
        result["strategy"] = "adaptive"
        
        return result
    
    def select_agents(self, available_agents: List[BaseAgent], task: Dict[str, Any]) -> List[BaseAgent]:
        """Select agents based on task requirements and agent capabilities."""
        suitable_agents = []
        
        for agent in available_agents:
            if agent.validate_task(task):
                # Additional logic for adaptive selection
                agent_score = self._score_agent(agent, task)
                if agent_score > self.config.get("min_agent_score", 0.5):
                    suitable_agents.append(agent)
        
        # Sort by score and take top agents
        max_agents = self.config.get("max_agents", 5)
        suitable_agents.sort(key=lambda a: self._score_agent(a, task), reverse=True)
        
        return suitable_agents[:max_agents]
    
    def _score_agent(self, agent: BaseAgent, task: Dict[str, Any]) -> float:
        """Score an agent for a given task."""
        # Simple scoring based on capabilities match
        task_requirements = task.get("requirements", [])
        agent_capabilities = agent.get_capabilities()
        
        if not task_requirements:
            return 1.0
        
        matches = len(set(task_requirements) & set(agent_capabilities))
        return matches / len(task_requirements) if task_requirements else 1.0