"""
Example implementations of agents using the injection framework.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from agent_injection import injectable, inject, get_default_injector


class Agent(ABC):
    """Base class for all agents."""
    
    @abstractmethod
    def execute(self, task: str) -> str:
        """Execute a task and return the result."""
        pass


class Logger(ABC):
    """Abstract logger interface."""
    
    @abstractmethod
    def log(self, message: str) -> None:
        """Log a message."""
        pass


class ConfigService(ABC):
    """Abstract configuration service interface."""
    
    @abstractmethod
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        pass


# Concrete implementations
class ConsoleLogger(Logger):
    """Simple console logger implementation."""
    
    def log(self, message: str) -> None:
        print(f"[LOG] {message}")


class SimpleConfigService(ConfigService):
    """Simple in-memory configuration service."""
    
    def __init__(self):
        self._config = {
            "max_retries": 3,
            "timeout": 30,
            "api_endpoint": "https://api.example.com"
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        return self._config.get(key, default)


@injectable
class ChatAgent(Agent):
    """A chat agent that can handle conversations."""
    
    def __init__(self, logger: Logger, config: ConfigService):
        self.logger = logger
        self.config = config
        self.conversation_history: List[str] = []
    
    def execute(self, task: str) -> str:
        self.logger.log(f"ChatAgent executing task: {task}")
        
        max_retries = self.config.get("max_retries", 1)
        self.logger.log(f"Max retries configured: {max_retries}")
        
        # Simulate processing
        response = f"I understand you want me to: {task}. How can I help?"
        self.conversation_history.append(f"User: {task}")
        self.conversation_history.append(f"Agent: {response}")
        
        return response


@injectable
class TaskAgent(Agent):
    """An agent specialized in task execution."""
    
    def __init__(self, logger: Logger, config: ConfigService):
        self.logger = logger
        self.config = config
        self.completed_tasks: List[str] = []
    
    def execute(self, task: str) -> str:
        self.logger.log(f"TaskAgent executing task: {task}")
        
        timeout = self.config.get("timeout", 10)
        self.logger.log(f"Task timeout set to: {timeout} seconds")
        
        # Simulate task execution
        result = f"Task '{task}' completed successfully"
        self.completed_tasks.append(task)
        
        return result


@injectable
class AgentOrchestrator:
    """Orchestrates multiple agents to work together."""
    
    def __init__(self, chat_agent: ChatAgent, task_agent: TaskAgent, logger: Logger):
        self.chat_agent = chat_agent
        self.task_agent = task_agent
        self.logger = logger
    
    def process_request(self, request: str) -> Dict[str, Any]:
        """Process a request using multiple agents."""
        self.logger.log(f"Orchestrator processing request: {request}")
        
        # Use chat agent to understand the request
        chat_response = self.chat_agent.execute(request)
        
        # Use task agent to execute any tasks
        task_response = self.task_agent.execute(f"Process: {request}")
        
        return {
            "request": request,
            "chat_response": chat_response,
            "task_response": task_response,
            "chat_history": self.chat_agent.conversation_history,
            "completed_tasks": self.task_agent.completed_tasks
        }


@inject
def process_with_agents(request: str, orchestrator: AgentOrchestrator) -> Dict[str, Any]:
    """
    Function that uses dependency injection to get an orchestrator and process a request.
    """
    return orchestrator.process_request(request)


def setup_dependencies():
    """Set up the dependency injection container with all required services."""
    injector = get_default_injector()
    container = injector.container
    
    # Register concrete implementations
    container.register(Logger, lambda: ConsoleLogger(), singleton=True)
    container.register(ConfigService, lambda: SimpleConfigService(), singleton=True)
    
    # Register agents (these will be created as needed)
    container.register(ChatAgent, lambda: injector.inject(ChatAgent))
    container.register(TaskAgent, lambda: injector.inject(TaskAgent))
    container.register(AgentOrchestrator, lambda: injector.inject(AgentOrchestrator))


if __name__ == "__main__":
    # Example usage
    setup_dependencies()
    
    # Create agents using dependency injection
    orchestrator = get_default_injector().inject(AgentOrchestrator)
    
    # Process some requests
    result = orchestrator.process_request("Help me plan a vacation to Japan")
    print("\nOrchestrator Result:")
    for key, value in result.items():
        print(f"{key}: {value}")
    
    print("\n" + "="*50 + "\n")
    
    # Use the decorated function
    result2 = process_with_agents("Create a presentation about AI")
    print("Function with injection Result:")
    for key, value in result2.items():
        print(f"{key}: {value}")