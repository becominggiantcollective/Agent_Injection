"""
Parallel execution strategy.
"""

import asyncio
from typing import List, Dict, Any
from core.base import BaseStrategy, BaseAgent


class ParallelStrategy(BaseStrategy):
    """Execute agents in parallel."""
    
    async def execute(self, agents: List[BaseAgent], task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute agents in parallel."""
        tasks = []
        
        for agent in agents:
            if agent.validate_task(task):
                tasks.append(self._execute_agent(agent, task))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        processed_results = []
        for i, result in enumerate(results):
            agent = agents[i]
            if isinstance(result, Exception):
                processed_results.append({
                    "agent_id": agent.agent_id,
                    "status": "error",
                    "error": str(result)
                })
            else:
                processed_results.append({
                    "agent_id": agent.agent_id,
                    "status": "success",
                    "result": result
                })
        
        return {
            "strategy": "parallel",
            "task": task,
            "results": processed_results,
            "total_agents": len(agents),
            "successful_agents": len([r for r in processed_results if r["status"] == "success"])
        }
    
    async def _execute_agent(self, agent: BaseAgent, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single agent."""
        return await agent.execute(task)
    
    def select_agents(self, available_agents: List[BaseAgent], task: Dict[str, Any]) -> List[BaseAgent]:
        """Select agents that can handle the task."""
        return [agent for agent in available_agents if agent.validate_task(task)]