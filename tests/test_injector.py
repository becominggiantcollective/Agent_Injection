"""
Tests for the Injector class.
"""

import pytest
from agent_injection import Container, Injector
from agent_injection.exceptions import AgentInjectionError


class MockService:
    """Mock service for testing."""
    
    def __init__(self, value: str = "mock"):
        self.value = value


class ServiceTestClassWithDependency:
    """Test class that requires a dependency."""
    
    def __init__(self, service: MockService):
        self.service = service


class ServiceTestClassWithOptionalDependency:
    """Test class with optional dependency."""
    
    def __init__(self, service: MockService = None):
        self.service = service


class ServiceTestClassWithMultipleDependencies:
    """Test class with multiple dependencies."""
    
    def __init__(self, service1: MockService, service2: MockService):
        self.service1 = service1
        self.service2 = service2


class ServiceTestClassNoDependencies:
    """Test class with no dependencies."""
    
    def __init__(self):
        self.initialized = True


def helper_function(service: MockService) -> str:
    """Helper function that requires a dependency."""
    return f"Function called with {service.value}"


def helper_function_optional(service: MockService = None) -> str:
    """Helper function with optional dependency."""
    if service:
        return f"Function called with {service.value}"
    return "Function called without service"


def helper_function_no_deps() -> str:
    """Helper function with no dependencies."""
    return "Function called"


class TestInjector:
    """Test cases for the Injector class."""
    
    def test_inject_class_with_dependency(self):
        """Test injecting a class with dependencies."""
        container = Container()
        container.register(MockService, lambda: MockService("injected"))
        
        injector = Injector(container)
        instance = injector.inject(ServiceTestClassWithDependency)
        
        assert isinstance(instance, ServiceTestClassWithDependency)
        assert isinstance(instance.service, MockService)
        assert instance.service.value == "injected"
    
    def test_inject_class_optional_dependency(self):
        """Test injecting a class with optional dependencies."""
        container = Container()
        container.register(MockService, lambda: MockService("optional"))
        
        injector = Injector(container)
        instance = injector.inject(ServiceTestClassWithOptionalDependency)
        
        assert isinstance(instance, ServiceTestClassWithOptionalDependency)
        assert isinstance(instance.service, MockService)
        assert instance.service.value == "optional"
    
    def test_inject_class_no_dependencies(self):
        """Test injecting a class with no dependencies."""
        container = Container()
        injector = Injector(container)
        
        instance = injector.inject(ServiceTestClassNoDependencies)
        
        assert isinstance(instance, ServiceTestClassNoDependencies)
        assert instance.initialized is True
    
    def test_inject_class_missing_required_dependency(self):
        """Test error when required dependency is missing."""
        container = Container()
        injector = Injector(container)
        
        with pytest.raises(AgentInjectionError) as exc_info:
            injector.inject(ServiceTestClassWithDependency)
        
        assert "No provider found for required parameter" in str(exc_info.value)
    
    def test_inject_class_multiple_dependencies(self):
        """Test injecting a class with multiple dependencies."""
        container = Container()
        container.register(MockService, lambda: MockService("shared"), singleton=True)
        
        injector = Injector(container)
        instance = injector.inject(ServiceTestClassWithMultipleDependencies)
        
        assert isinstance(instance, ServiceTestClassWithMultipleDependencies)
        assert instance.service1 is instance.service2  # Should be same singleton instance
        assert instance.service1.value == "shared"
    
    def test_call_function_with_dependency(self):
        """Test calling a function with dependency injection."""
        container = Container()
        container.register(MockService, lambda: MockService("function_dep"))
        
        injector = Injector(container)
        result = injector.call(helper_function)
        
        assert result == "Function called with function_dep"
    
    def test_call_function_with_provided_args(self):
        """Test calling a function with provided arguments."""
        container = Container()
        injector = Injector(container)
        
        service = MockService("provided")
        result = injector.call(helper_function, service=service)
        
        assert result == "Function called with provided"
    
    def test_call_function_optional_dependency(self):
        """Test calling a function with optional dependency."""
        container = Container()
        container.register(MockService, lambda: MockService("optional_func"))
        
        injector = Injector(container)
        result = injector.call(helper_function_optional)
        
        assert result == "Function called with optional_func"
    
    def test_call_function_no_dependencies(self):
        """Test calling a function with no dependencies."""
        container = Container()
        injector = Injector(container)
        
        result = injector.call(helper_function_no_deps)
        
        assert result == "Function called"
    
    def test_injector_with_default_container(self):
        """Test injector with default container."""
        injector = Injector()
        
        # Should not raise an error
        assert injector.container is not None
        assert isinstance(injector.container, Container)
    
    def test_injector_with_custom_container(self):
        """Test injector with custom container."""
        custom_container = Container()
        injector = Injector(custom_container)
        
        assert injector.container is custom_container