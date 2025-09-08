# Agent Injection Framework

A flexible and powerful dependency injection framework designed specifically for AI agents and autonomous systems. This framework provides clean separation of concerns, testability, and modularity for agent-based applications.

## Features

- **Type-safe dependency injection** with Python type hints
- **Decorator-based injection** for clean, readable code
- **Singleton and factory patterns** for efficient resource management
- **Circular dependency detection** to prevent infinite loops
- **Comprehensive testing** with pytest integration
- **Clean abstractions** for agent interfaces and implementations
- **Contextual injection** for session and user-aware agents

## Installation

```bash
pip install -e .
```

For development:
```bash
pip install -e ".[dev]"
```

## Quick Start

### Basic Usage

```python
from agent_injection import Container, Injector, injectable, inject

# Define interfaces
class Logger:
    def log(self, message: str) -> None:
        pass

class ConsoleLogger(Logger):
    def log(self, message: str) -> None:
        print(f"[LOG] {message}")

# Define agent with dependencies
@injectable
class ChatAgent:
    def __init__(self, logger: Logger):
        self.logger = logger
    
    def respond(self, message: str) -> str:
        self.logger.log(f"Processing: {message}")
        return f"I understand: {message}"

# Set up dependency injection
container = Container()
container.register(Logger, lambda: ConsoleLogger(), singleton=True)

injector = Injector(container)
agent = injector.inject(ChatAgent)

# Use the agent
response = agent.respond("Hello, AI!")
```

### Using Decorators

```python
from agent_injection import injectable, inject, get_default_injector

# Set up dependencies
injector = get_default_injector()
injector.container.register(Logger, lambda: ConsoleLogger(), singleton=True)

# Injectable class - automatically injects dependencies
@injectable
class SmartAgent:
    def __init__(self, logger: Logger):
        self.logger = logger

# Function injection
@inject
def process_request(message: str, agent: SmartAgent) -> str:
    return agent.respond(message)

# Usage
agent = SmartAgent()  # Dependencies automatically injected
result = process_request("Hello!")  # Agent automatically injected
```

## Core Components

### Container

The `Container` class manages all dependency registrations and resolves dependencies:

```python
from agent_injection import Container

container = Container()

# Register a factory function
container.register(MyInterface, lambda: MyImplementation())

# Register as singleton
container.register(MyInterface, lambda: MyImplementation(), singleton=True)

# Register a specific instance
container.register_instance(MyInterface, my_instance)

# Resolve dependencies
instance = container.resolve(MyInterface)
```

### Injector

The `Injector` class handles the actual injection of dependencies into classes and functions:

```python
from agent_injection import Injector

injector = Injector(container)

# Inject into class constructor
instance = injector.inject(MyClass)

# Inject into function call
result = injector.call(my_function, arg1, arg2)
```

### Decorators

Use decorators for clean, declarative dependency injection:

```python
from agent_injection import injectable, inject

@injectable
class MyService:
    def __init__(self, dependency: MyDependency):
        self.dependency = dependency

@inject
def my_function(service: MyService) -> str:
    return service.do_something()
```

## Agent Examples

### Basic Agent System

```python
from abc import ABC, abstractmethod
from agent_injection import injectable, Container, Injector

class Agent(ABC):
    @abstractmethod
    def execute(self, task: str) -> str:
        pass

@injectable
class ChatAgent(Agent):
    def __init__(self, logger: Logger, config: ConfigService):
        self.logger = logger
        self.config = config
    
    def execute(self, task: str) -> str:
        self.logger.log(f"ChatAgent executing: {task}")
        return f"Processed: {task}"

@injectable
class AgentOrchestrator:
    def __init__(self, chat_agent: ChatAgent, logger: Logger):
        self.chat_agent = chat_agent
        self.logger = logger
    
    def handle_request(self, request: str) -> str:
        self.logger.log(f"Orchestrating request: {request}")
        return self.chat_agent.execute(request)
```

### Advanced Agent Chain

```python
@injectable
class AgentChain:
    def __init__(self, agents: List[Agent], logger: Logger):
        self.agents = agents
        self.logger = logger
    
    def execute_chain(self, initial_input: str) -> List[str]:
        results = []
        current_input = initial_input
        
        for agent in self.agents:
            result = agent.execute(current_input)
            results.append(result)
            current_input = result
            
        return results
```

## Testing

Run the test suite:

```bash
pytest
```

Run with coverage:

```bash
pytest --cov=agent_injection --cov-report=html
```

## Project Structure

```
agent_injection/
├── __init__.py          # Main package exports
├── container.py         # Dependency container
├── injector.py          # Injection logic
├── decorators.py        # Decorator implementations
└── exceptions.py        # Custom exceptions

examples/
├── basic_agents.py      # Simple agent examples
└── advanced_injection.py # Complex injection patterns

tests/
├── test_container.py    # Container tests
├── test_injector.py     # Injector tests
├── test_decorators.py   # Decorator tests
└── test_integration.py  # Integration tests
```

## Advanced Features

### Circular Dependency Detection

The framework automatically detects and prevents circular dependencies:

```python
# This will raise CircularDependencyError
class ServiceA:
    def __init__(self, service_b: ServiceB): pass

class ServiceB:
    def __init__(self, service_a: ServiceA): pass
```

### Context-Aware Injection

Support for contextual information in agent injection:

```python
@dataclass
class AgentContext:
    user_id: str
    session_id: str
    metadata: Dict[str, Any]

@injectable
class ContextualAgent:
    def __init__(self, context: AgentContext, logger: Logger):
        self.context = context
        self.logger = logger
```

### Factory Patterns

Create agents dynamically with factory classes:

```python
class AgentFactory:
    def __init__(self, injector: Injector):
        self.injector = injector
    
    def create_agent(self, agent_type: Type[Agent]) -> Agent:
        return self.injector.inject(agent_type)
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## License

MIT License - see LICENSE file for details.