# Getting Started with Agent Injection

This guide will help you get started with the Agent Injection framework quickly.

## Installation

```bash
# Install from source
git clone https://github.com/becominggiantcollective/Agent_Injection.git
cd Agent_Injection
pip install -e .

# For development
pip install -e ".[dev]"
```

## Basic Concepts

### 1. Container
The Container manages all your dependencies and their lifecycles.

```python
from agent_injection import Container

container = Container()
container.register(MyInterface, lambda: MyImplementation())
instance = container.resolve(MyInterface)
```

### 2. Injector
The Injector handles dependency injection into classes and functions.

```python
from agent_injection import Injector

injector = Injector(container)
instance = injector.inject(MyClass)
```

### 3. Decorators
Use decorators for clean, declarative injection.

```python
from agent_injection import injectable, inject

@injectable
class MyService:
    def __init__(self, dependency: MyDependency):
        self.dependency = dependency

@inject
def my_function(service: MyService):
    return service.do_something()
```

## Quick Example

```python
from agent_injection import Container, Injector, injectable

# Define interfaces
class Logger:
    def log(self, message: str): pass

class Database:
    def save(self, data: str): pass

# Define implementations
class ConsoleLogger(Logger):
    def log(self, message: str):
        print(f"[LOG] {message}")

class InMemoryDatabase(Database):
    def __init__(self):
        self.data = []
    
    def save(self, data: str):
        self.data.append(data)
        return f"Saved: {data}"

# Define agent with dependencies
@injectable
class UserAgent:
    def __init__(self, logger: Logger, database: Database):
        self.logger = logger
        self.database = database
    
    def create_user(self, username: str):
        self.logger.log(f"Creating user: {username}")
        result = self.database.save(f"user:{username}")
        self.logger.log(f"User created successfully")
        return result

# Set up container
container = Container()
container.register(Logger, lambda: ConsoleLogger(), singleton=True)
container.register(Database, lambda: InMemoryDatabase(), singleton=True)

# Create and use agent
injector = Injector(container)
agent = injector.inject(UserAgent)
result = agent.create_user("alice")
print(result)
```

## Testing

The framework is designed to make testing easy:

```python
import pytest
from unittest.mock import Mock

def test_user_agent():
    # Create mocks
    mock_logger = Mock(spec=Logger)
    mock_database = Mock(spec=Database)
    mock_database.save.return_value = "test result"
    
    # Create agent with mocks
    agent = UserAgent(mock_logger, mock_database)
    
    # Test
    result = agent.create_user("test_user")
    
    # Verify
    mock_logger.log.assert_called()
    mock_database.save.assert_called_with("user:test_user")
    assert result == "test result"
```

## Next Steps

- Check out the `examples/` directory for more complex scenarios
- Read the full README.md for comprehensive documentation
- Explore the test suite in `tests/` for usage patterns
- Look at advanced patterns like agent chains and factories

## Common Patterns

### Singleton Services
```python
container.register(Logger, lambda: ConsoleLogger(), singleton=True)
```

### Factory Functions
```python
def create_agent_with_config(config_path: str):
    config = load_config(config_path)
    return MyAgent(config)

container.register(MyAgent, lambda: create_agent_with_config("config.json"))
```

### Optional Dependencies
```python
@injectable
class OptionalAgent:
    def __init__(self, required_service: RequiredService, optional_service: OptionalService = None):
        self.required = required_service
        self.optional = optional_service
```

### Agent Composition
```python
@injectable
class CompositeAgent:
    def __init__(self, chat_agent: ChatAgent, task_agent: TaskAgent):
        self.chat_agent = chat_agent
        self.task_agent = task_agent
    
    def handle_request(self, request: str):
        understanding = self.chat_agent.process(request)
        return self.task_agent.execute(understanding)
```