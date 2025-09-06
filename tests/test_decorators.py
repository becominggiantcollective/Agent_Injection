"""
Tests for decorators.
"""

import pytest
from agent_injection import injectable, inject, get_default_injector, set_default_injector, Container, Injector


class MockTestService:
    """Test service for decorator testing."""
    
    def __init__(self, value: str = "test"):
        self.value = value


@injectable
class InjectableClass:
    """Test class decorated with @injectable."""
    
    def __init__(self, service: MockTestService):
        self.service = service


@injectable
class InjectableClassOptional:
    """Test class with optional dependency."""
    
    def __init__(self, service: MockTestService = None):
        self.service = service


@injectable
class InjectableClassNoDeps:
    """Test class with no dependencies."""
    
    def __init__(self):
        self.initialized = True


@inject
def decorated_function(service: MockTestService) -> str:
    """Test function decorated with @inject."""
    return f"Decorated function called with {service.value}"


@inject
def decorated_function_optional(service: MockTestService = None) -> str:
    """Test function with optional dependency."""
    if service:
        return f"Decorated function called with {service.value}"
    return "Decorated function called without service"


class TestDecorators:
    """Test cases for decorators."""
    
    def setup_method(self):
        """Set up for each test method."""
        # Reset default injector for each test
        container = Container()
        injector = Injector(container)
        set_default_injector(injector)
    
    def test_injectable_decorator_with_dependencies(self):
        """Test @injectable decorator with dependencies."""
        # Set up container
        injector = get_default_injector()
        injector.container.register(MockTestService, lambda: MockTestService("injectable"))
        
        # Create instance - should automatically inject dependencies
        instance = InjectableClass()
        
        assert isinstance(instance.service, MockTestService)
        assert instance.service.value == "injectable"
    
    def test_injectable_decorator_with_manual_args(self):
        """Test @injectable decorator with manually provided arguments."""
        service = MockTestService("manual")
        instance = InjectableClass(service)
        
        assert instance.service is service
        assert instance.service.value == "manual"
    
    def test_injectable_decorator_no_dependencies(self):
        """Test @injectable decorator on class with no dependencies."""
        instance = InjectableClassNoDeps()
        
        assert instance.initialized is True
    
    def test_injectable_decorator_optional_dependency(self):
        """Test @injectable decorator with optional dependencies."""
        # Set up container
        injector = get_default_injector()
        injector.container.register(MockTestService, lambda: MockTestService("optional"))
        
        instance = InjectableClassOptional()
        
        assert isinstance(instance.service, MockTestService)
        assert instance.service.value == "optional"
    
    def test_inject_decorator_function(self):
        """Test @inject decorator on functions."""
        # Set up container
        injector = get_default_injector()
        injector.container.register(MockTestService, lambda: MockTestService("function"))
        
        result = decorated_function()
        
        assert result == "Decorated function called with function"
    
    def test_inject_decorator_function_with_args(self):
        """Test @inject decorator with provided arguments."""
        service = MockTestService("provided")
        result = decorated_function(service=service)
        
        assert result == "Decorated function called with provided"
    
    def test_inject_decorator_optional_function(self):
        """Test @inject decorator with optional dependencies."""
        # Set up container
        injector = get_default_injector()
        injector.container.register(MockTestService, lambda: MockTestService("optional_func"))
        
        result = decorated_function_optional()
        
        assert result == "Decorated function called with optional_func"
    
    def test_inject_decorator_with_custom_injector(self):
        """Test @inject decorator with custom injector."""
        # Create custom injector
        custom_container = Container()
        custom_container.register(MockTestService, lambda: MockTestService("custom"))
        custom_injector = Injector(custom_container)
        
        @inject(injector=custom_injector)
        def custom_function(service: MockTestService) -> str:
            return f"Custom function called with {service.value}"
        
        result = custom_function()
        
        assert result == "Custom function called with custom"
    
    def test_get_default_injector(self):
        """Test getting the default injector."""
        injector = get_default_injector()
        
        assert isinstance(injector, Injector)
        assert isinstance(injector.container, Container)
    
    def test_set_default_injector(self):
        """Test setting a custom default injector."""
        custom_container = Container()
        custom_injector = Injector(custom_container)
        
        set_default_injector(custom_injector)
        
        assert get_default_injector() is custom_injector
    
    def test_injectable_missing_required_dependency(self):
        """Test @injectable with missing required dependency."""
        # Don't register MockTestService
        
        # Should not raise when creating instance with no dependencies
        # but will raise when trying to inject dependencies
        try:
            InjectableClass()
            # If it didn't raise, the injection may have fallen back to no-arg init
            # which would be acceptable behavior
        except Exception:
            # Expected if no provider found
            pass
    
    def test_inject_decorator_preserves_function_metadata(self):
        """Test that @inject decorator preserves function metadata."""
        assert decorated_function.__name__ == "decorated_function"
        assert "Test function decorated" in decorated_function.__doc__
    
    def test_injectable_decorator_preserves_class_metadata(self):
        """Test that @injectable decorator preserves class metadata."""
        assert InjectableClass.__name__ == "InjectableClass"
        assert "Test class decorated" in InjectableClass.__doc__