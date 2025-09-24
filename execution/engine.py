"""
Main execution engine for running agent campaigns.
"""

import asyncio
from typing import Dict, List, Any, Optional
from core.base import BaseAgent, BaseStrategy, Campaign, TaskResult
from core.config import get_config


class ExecutionEngine:
    """Main execution engine for agent campaigns."""
    
    def __init__(self):
        """Initialize execution engine."""
        self.config = get_config()
        self.active_campaigns: Dict[str, Campaign] = {}
        self.agents: Dict[str, BaseAgent] = {}
        self.strategies: Dict[str, BaseStrategy] = {}
        self.results: List[TaskResult] = []
    
    def register_agent(self, agent: BaseAgent) -> None:
        """Register an agent with the engine."""
        self.agents[agent.agent_id] = agent
    
    def register_strategy(self, strategy: BaseStrategy) -> None:
        """Register an execution strategy."""
        self.strategies[strategy.strategy_id] = strategy
    
    def unregister_agent(self, agent_id: str) -> None:
        """Unregister an agent."""
        if agent_id in self.agents:
            del self.agents[agent_id]
    
    def unregister_strategy(self, strategy_id: str) -> None:
        """Unregister a strategy."""
        if strategy_id in self.strategies:
            del self.strategies[strategy_id]
    
    async def run_campaign(self, campaign: Campaign) -> Dict[str, Any]:
        """Run a complete campaign."""
        self.active_campaigns[campaign.name] = campaign
        
        try:
            # Get the strategy
            strategy = self.strategies.get(campaign.strategy)
            if not strategy:
                raise ValueError(f"Strategy '{campaign.strategy}' not found")
            
            # Get the agents
            campaign_agents = []
            for agent_id in campaign.agents:
                agent = self.agents.get(agent_id)
                if agent:
                    campaign_agents.append(agent)
                else:
                    print(f"Warning: Agent '{agent_id}' not found")
            
            if not campaign_agents:
                raise ValueError("No valid agents found for campaign")
            
            # Execute all tasks
            campaign_results = []
            for i, task in enumerate(campaign.tasks):
                task_with_id = {**task, "task_id": f"{campaign.name}-task-{i}"}
                result = await strategy.execute(campaign_agents, task_with_id)
                campaign_results.append(result)
            
            final_result = {
                "campaign": campaign.name,
                "status": "completed",
                "task_results": campaign_results,
                "total_tasks": len(campaign.tasks),
                "successful_tasks": len([r for r in campaign_results if r.get("successful_agents", 0) > 0])
            }
            
        except Exception as e:
            final_result = {
                "campaign": campaign.name,
                "status": "failed",
                "error": str(e),
                "task_results": []
            }
        
        finally:
            if campaign.name in self.active_campaigns:
                del self.active_campaigns[campaign.name]
        
        return final_result
    
    async def execute_single_task(self, task: Dict[str, Any], strategy_id: str, agent_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        """Execute a single task."""
        strategy = self.strategies.get(strategy_id)
        if not strategy:
            raise ValueError(f"Strategy '{strategy_id}' not found")
        
        # Use specific agents or all available agents
        if agent_ids:
            agents = [self.agents[aid] for aid in agent_ids if aid in self.agents]
        else:
            agents = list(self.agents.values())
        
        if not agents:
            raise ValueError("No agents available for task execution")
        
        return await strategy.execute(agents, task)
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get status of all registered agents."""
        return {
            agent_id: {
                "status": agent.get_status(),
                "capabilities": agent.get_capabilities(),
                "metadata": agent.metadata
            }
            for agent_id, agent in self.agents.items()
        }
    
    def get_active_campaigns(self) -> List[str]:
        """Get list of active campaign names."""
        return list(self.active_campaigns.keys())