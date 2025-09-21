"""
Base classes for agents and strategies.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class BaseAgent(ABC):
    """Base class for all agents in the system."""
    
    def __init__(self, agent_id: str, config: Optional[Dict[str, Any]] = None):
        """Initialize the agent."""
        self.agent_id = agent_id
        self.config = config or {}
        self.status = "initialized"
        self.metadata: Dict[str, Any] = {}
    
    @abstractmethod
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a task and return results."""
        pass
    
    @abstractmethod
    def validate_task(self, task: Dict[str, Any]) -> bool:
        """Validate if the agent can handle this task."""
        pass
    
    def get_capabilities(self) -> List[str]:
        """Return list of agent capabilities."""
        return []
    
    def get_status(self) -> str:
        """Get current agent status."""
        return self.status
    
    def set_metadata(self, key: str, value: Any) -> None:
        """Set agent metadata."""
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get agent metadata."""
        return self.metadata.get(key, default)


class BaseStrategy(ABC):
    """Base class for execution strategies."""
    
    def __init__(self, strategy_id: str, config: Optional[Dict[str, Any]] = None):
        """Initialize the strategy."""
        self.strategy_id = strategy_id
        self.config = config or {}
    
    @abstractmethod
    async def execute(self, agents: List[BaseAgent], task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute strategy with given agents and task."""
        pass
    
    @abstractmethod
    def select_agents(self, available_agents: List[BaseAgent], task: Dict[str, Any]) -> List[BaseAgent]:
        """Select appropriate agents for the task."""
        pass
    
    def get_strategy_info(self) -> Dict[str, Any]:
        """Get strategy information."""
        return {
            "strategy_id": self.strategy_id,
            "config": self.config
        }


class TaskResult(BaseModel):
    """Result of a task execution."""
    task_id: str
    agent_id: str
    status: str
    result: Dict[str, Any]
    metadata: Dict[str, Any] = {}
    error: Optional[str] = None


class Campaign(BaseModel):
    """Represents an agent campaign configuration."""
    name: str
    description: str
    strategy: str
    agents: List[str]
    tasks: List[Dict[str, Any]]
    config: Dict[str, Any] = {}