"""
Integration tests that test the complete framework.
"""

import pytest
from agent_injection import Container, Injector, injectable, inject, get_default_injector, set_default_injector


# Test interfaces and implementations
class DatabaseService:
    """Abstract database service."""
    
    def save(self, data: str) -> str:
        raise NotImplementedError


class LoggerService:
    """Abstract logger service."""
    
    def log(self, message: str) -> None:
        raise NotImplementedError


class ConfigService:
    """Abstract configuration service."""
    
    def get_setting(self, key: str) -> str:
        raise NotImplementedError


class MockDatabase(DatabaseService):
    """Mock database implementation."""
    
    def save(self, data: str) -> str:
        return f"Saved: {data}"


class MockLogger(LoggerService):
    """Mock logger implementation."""
    
    def __init__(self):
        self.messages = []
    
    def log(self, message: str) -> None:
        self.messages.append(message)


class MockConfig(ConfigService):
    """Mock configuration implementation."""
    
    def get_setting(self, key: str) -> str:
        settings = {
            "app_name": "TestApp",
            "version": "1.0.0",
            "debug": "true"
        }
        return settings.get(key, "default")


@injectable
class UserService:
    """Service that depends on database and logger."""
    
    def __init__(self, database: DatabaseService, logger: LoggerService):
        self.database = database
        self.logger = logger
    
    def create_user(self, username: str) -> str:
        self.logger.log(f"Creating user: {username}")
        result = self.database.save(f"user:{username}")
        self.logger.log(f"User created: {result}")
        return result


@injectable
class ApplicationService:
    """Service that depends on multiple other services."""
    
    def __init__(self, user_service: UserService, config: ConfigService, logger: LoggerService):
        self.user_service = user_service
        self.config = config
        self.logger = logger
    
    def initialize(self) -> str:
        app_name = self.config.get_setting("app_name")
        version = self.config.get_setting("version")
        
        self.logger.log(f"Initializing {app_name} v{version}")
        return f"{app_name} v{version} initialized"
    
    def handle_user_creation(self, username: str) -> str:
        self.logger.log(f"Handling user creation request for: {username}")
        result = self.user_service.create_user(username)
        return f"Application handled: {result}"


@inject
def process_user_request(username: str, app_service: ApplicationService) -> str:
    """Function that uses dependency injection."""
    return app_service.handle_user_creation(username)


class TestIntegration:
    """Integration tests for the complete framework."""
    
    def setup_method(self):
        """Set up for each test."""
        # Create fresh container and injector
        container = Container()
        injector = Injector(container)
        set_default_injector(injector)
        
        # Register all services
        container.register(DatabaseService, lambda: MockDatabase(), singleton=True)
        container.register(LoggerService, lambda: MockLogger(), singleton=True)
        container.register(ConfigService, lambda: MockConfig(), singleton=True)
        
        # Register services that depend on other services
        container.register(UserService, lambda: injector.inject(UserService))
        container.register(ApplicationService, lambda: injector.inject(ApplicationService))
    
    def test_complete_dependency_chain(self):
        """Test resolving a complete dependency chain."""
        injector = get_default_injector()
        
        # Resolve the top-level service
        app_service = injector.inject(ApplicationService)
        
        # Verify all dependencies are properly injected
        assert isinstance(app_service, ApplicationService)
        assert isinstance(app_service.user_service, UserService)
        assert isinstance(app_service.user_service.database, MockDatabase)
        assert isinstance(app_service.user_service.logger, MockLogger)
        assert isinstance(app_service.config, MockConfig)
        assert isinstance(app_service.logger, MockLogger)
    
    def test_singleton_behavior_across_chain(self):
        """Test that singleton services are shared across the dependency chain."""
        injector = get_default_injector()
        
        app_service = injector.inject(ApplicationService)
        
        # Logger should be the same instance in both app_service and user_service
        assert app_service.logger is app_service.user_service.logger
    
    def test_service_functionality(self):
        """Test that services work correctly together."""
        injector = get_default_injector()
        
        app_service = injector.inject(ApplicationService)
        
        # Test initialization
        init_result = app_service.initialize()
        assert init_result == "TestApp v1.0.0 initialized"
        
        # Test user creation
        user_result = app_service.handle_user_creation("testuser")
        assert "Saved: user:testuser" in user_result
        
        # Check that logging occurred
        logger = app_service.logger
        assert len(logger.messages) >= 3  # At least 3 log messages
        assert any("Initializing TestApp" in msg for msg in logger.messages)
        assert any("Creating user: testuser" in msg for msg in logger.messages)
    
    def test_decorated_function_injection(self):
        """Test function decoration with dependency injection."""
        result = process_user_request("functionuser")
        
        assert "Saved: user:functionuser" in result
    
    def test_multiple_instances_different_containers(self):
        """Test that different containers maintain separate instances."""
        # Create first container and resolve service
        container1 = Container()
        injector1 = Injector(container1)
        container1.register(LoggerService, lambda: MockLogger(), singleton=True)
        
        logger1 = injector1.inject(MockLogger)
        logger1.log("Container 1 message")
        
        # Create second container and resolve service
        container2 = Container()
        injector2 = Injector(container2)
        container2.register(LoggerService, lambda: MockLogger(), singleton=True)
        
        logger2 = injector2.inject(MockLogger)
        logger2.log("Container 2 message")
        
        # Should be different instances
        assert logger1 is not logger2
        assert len(logger1.messages) == 1
        assert len(logger2.messages) == 1
        assert logger1.messages[0] == "Container 1 message"
        assert logger2.messages[0] == "Container 2 message"
    
    def test_circular_dependency_detection_integration(self):
        """Test circular dependency detection in a real scenario."""
        container = Container()
        injector = Injector(container)
        
        # Create circular dependency
        class ServiceA:
            def __init__(self, service_b):
                self.service_b = service_b
        
        class ServiceB:
            def __init__(self, service_a):
                self.service_a = service_a
        
        container.register(ServiceA, lambda: ServiceA(injector.container.resolve(ServiceB)))
        container.register(ServiceB, lambda: ServiceB(injector.container.resolve(ServiceA)))
        
        with pytest.raises(Exception):  # Should detect circular dependency
            injector.inject(ServiceA)
    
    def test_optional_dependencies_integration(self):
        """Test optional dependencies in integration scenario."""
        # Define a class without the @injectable decorator first
        class OptionalService:
            def __init__(self, logger: LoggerService = None):
                self.logger = logger
        
        # Create a fresh container for this test
        fresh_container = Container()
        fresh_injector = Injector(fresh_container)
        
        # Test without registering logger - should be None
        service = fresh_injector.inject(OptionalService)
        assert service.logger is None
        
        # Test with registered logger
        fresh_container.register(LoggerService, lambda: MockLogger())
        service_with_logger = fresh_injector.inject(OptionalService)
        assert isinstance(service_with_logger.logger, MockLogger)