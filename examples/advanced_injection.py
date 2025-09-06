"""
Advanced example showing more complex agent injection patterns.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from agent_injection import injectable, inject, Container, Injector


@dataclass
class AgentContext:
    """Context object that carries information between agents."""
    user_id: str
    session_id: str
    request_id: str
    metadata: Dict[str, Any]


class MemoryStore(ABC):
    """Abstract memory store for agents."""
    
    @abstractmethod
    def store(self, key: str, value: Any) -> None:
        """Store a value."""
        pass
    
    @abstractmethod
    def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve a value."""
        pass


class ExternalAPI(ABC):
    """Abstract external API interface."""
    
    @abstractmethod
    def call(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Make an API call."""
        pass


# Concrete implementations
class InMemoryStore(MemoryStore):
    """Simple in-memory storage."""
    
    def __init__(self):
        self._store: Dict[str, Any] = {}
    
    def store(self, key: str, value: Any) -> None:
        self._store[key] = value
    
    def retrieve(self, key: str) -> Optional[Any]:
        return self._store.get(key)


class MockAPI(ExternalAPI):
    """Mock external API for demonstration."""
    
    def call(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "status": "success",
            "endpoint": endpoint,
            "data": data,
            "response": f"Mock response for {endpoint}"
        }


@injectable
class ContextualAgent:
    """An agent that maintains context across interactions."""
    
    def __init__(self, memory: MemoryStore, api: ExternalAPI):
        self.memory = memory
        self.api = api
    
    def process_with_context(self, context: AgentContext, message: str) -> Dict[str, Any]:
        """Process a message with context."""
        # Store context
        context_key = f"context_{context.session_id}"
        self.memory.store(context_key, context)
        
        # Retrieve previous interactions
        history_key = f"history_{context.session_id}"
        history = self.memory.retrieve(history_key) or []
        
        # Process the message
        response = f"Processed '{message}' for user {context.user_id}"
        
        # Update history
        history.append({"message": message, "response": response})
        self.memory.store(history_key, history)
        
        # Make external API call if needed
        api_response = self.api.call("/process", {
            "user_id": context.user_id,
            "message": message
        })
        
        return {
            "response": response,
            "history_length": len(history),
            "api_response": api_response,
            "context": context
        }


@injectable  
class AgentChain:
    """A chain of agents that process data sequentially."""
    
    def __init__(self, contextual_agent: ContextualAgent, memory: MemoryStore):
        self.agents: List[ContextualAgent] = [contextual_agent]
        self.memory = memory
    
    def add_agent(self, agent: ContextualAgent) -> None:
        """Add an agent to the chain."""
        self.agents.append(agent)
    
    def execute_chain(self, context: AgentContext, initial_message: str) -> List[Dict[str, Any]]:
        """Execute the chain of agents."""
        results = []
        current_message = initial_message
        
        for i, agent in enumerate(self.agents):
            # Create a new context for each step
            step_context = AgentContext(
                user_id=context.user_id,
                session_id=f"{context.session_id}_step_{i}",
                request_id=context.request_id,
                metadata={**context.metadata, "step": i}
            )
            
            result = agent.process_with_context(step_context, current_message)
            results.append(result)
            
            # Use the response as input for the next agent
            current_message = result["response"]
        
        return results


class AgentFactory:
    """Factory for creating agents with different configurations."""
    
    def __init__(self, injector: Injector):
        self.injector = injector
    
    def create_contextual_agent(self) -> ContextualAgent:
        """Create a new contextual agent."""
        return self.injector.inject(ContextualAgent)
    
    def create_agent_chain(self, num_agents: int = 1) -> AgentChain:
        """Create an agent chain with the specified number of agents."""
        chain = self.injector.inject(AgentChain)
        
        # Add additional agents to the chain
        for _ in range(num_agents - 1):  # -1 because chain already has one agent
            agent = self.create_contextual_agent()
            chain.add_agent(agent)
        
        return chain


def setup_advanced_container() -> Container:
    """Set up a container with advanced configuration."""
    container = Container()
    
    # Register singletons for shared services
    container.register(MemoryStore, lambda: InMemoryStore(), singleton=True)
    container.register(ExternalAPI, lambda: MockAPI(), singleton=True)
    
    # Register agent types (new instances each time)
    injector = Injector(container)
    container.register(ContextualAgent, lambda: injector.inject(ContextualAgent))
    container.register(AgentChain, lambda: injector.inject(AgentChain))
    
    return container


@inject
def demonstrate_advanced_injection(factory: AgentFactory, context: AgentContext) -> None:
    """Demonstrate advanced injection patterns."""
    print("=== Advanced Agent Injection Demo ===\n")
    
    # Create a single contextual agent
    agent = factory.create_contextual_agent()
    result = agent.process_with_context(context, "Hello, I need help with a complex task")
    
    print("Single Agent Result:")
    print(f"Response: {result['response']}")
    print(f"History Length: {result['history_length']}")
    print(f"API Response: {result['api_response']['response']}")
    print()
    
    # Create an agent chain
    chain = factory.create_agent_chain(num_agents=3)
    chain_results = chain.execute_chain(context, "Process this through multiple agents")
    
    print("Agent Chain Results:")
    for i, result in enumerate(chain_results):
        print(f"Step {i+1}: {result['response']}")
    print()


if __name__ == "__main__":
    # Set up advanced container
    container = setup_advanced_container()
    injector = Injector(container)
    
    # Register the factory
    factory = AgentFactory(injector)
    container.register_instance(AgentFactory, factory)
    
    # Create context
    context = AgentContext(
        user_id="user123",
        session_id="session456", 
        request_id="req789",
        metadata={"source": "demo", "priority": "high"}
    )
    container.register_instance(AgentContext, context)
    
    # Run the demonstration by calling it directly with injector
    injector.call(demonstrate_advanced_injection)