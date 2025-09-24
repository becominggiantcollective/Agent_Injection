"""
Sequential execution strategy.
"""

from typing import List, Dict, Any
from core.base import BaseStrategy, BaseAgent


class SequentialStrategy(BaseStrategy):
    """Execute agents sequentially, one after another."""
    
    async def execute(self, agents: List[BaseAgent], task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute agents sequentially."""
        results = []
        
        for agent in agents:
            if agent.validate_task(task):
                try:
                    result = await agent.execute(task)
                    results.append({
                        "agent_id": agent.agent_id,
                        "status": "success",
                        "result": result
                    })
                except Exception as e:
                    results.append({
                        "agent_id": agent.agent_id,
                        "status": "error",
                        "error": str(e)
                    })
        
        return {
            "strategy": "sequential",
            "task": task,
            "results": results,
            "total_agents": len(agents),
            "successful_agents": len([r for r in results if r["status"] == "success"])
        }
    
    def select_agents(self, available_agents: List[BaseAgent], task: Dict[str, Any]) -> List[BaseAgent]:
        """Select agents that can handle the task."""
        return [agent for agent in available_agents if agent.validate_task(task)]