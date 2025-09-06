"""
Tests for the Container class.
"""

import pytest
from agent_injection import Container
from agent_injection.exceptions import ProviderNotFoundError, CircularDependencyError, InvalidProviderError


class MockInterface:
    """Test interface for dependency injection."""
    pass


class MockImplementation(MockInterface):
    """Test implementation of the interface."""
    
    def __init__(self, value: str = "test"):
        self.value = value


class AnotherMockInterface:
    """Another test interface."""
    pass


class AnotherMockImplementation(AnotherMockInterface):
    """Another test implementation."""
    
    def __init__(self, dependency: MockInterface):
        self.dependency = dependency


class CircularA:
    """Class for testing circular dependencies."""
    pass


class CircularB:
    """Class for testing circular dependencies."""
    pass


class TestContainer:
    """Test cases for the Container class."""
    
    def test_register_and_resolve(self):
        """Test basic registration and resolution."""
        container = Container()
        
        # Register a provider
        container.register(MockInterface, lambda: MockImplementation("hello"))
        
        # Resolve the interface
        instance = container.resolve(MockInterface)
        
        assert isinstance(instance, MockImplementation)
        assert instance.value == "hello"
    
    def test_register_instance(self):
        """Test registering a specific instance."""
        container = Container()
        test_instance = MockImplementation("instance")
        
        container.register_instance(MockInterface, test_instance)
        
        resolved = container.resolve(MockInterface)
        assert resolved is test_instance
    
    def test_singleton_behavior(self):
        """Test singleton registration."""
        container = Container()
        
        # Register as singleton
        container.register(MockInterface, lambda: MockImplementation("singleton"), singleton=True)
        
        # Resolve multiple times
        instance1 = container.resolve(MockInterface)
        instance2 = container.resolve(MockInterface)
        
        # Should be the same instance
        assert instance1 is instance2
    
    def test_non_singleton_behavior(self):
        """Test non-singleton registration (default)."""
        container = Container()
        
        # Register without singleton flag
        container.register(MockInterface, lambda: MockImplementation("non-singleton"))
        
        # Resolve multiple times
        instance1 = container.resolve(MockInterface)
        instance2 = container.resolve(MockInterface)
        
        # Should be different instances
        assert instance1 is not instance2
        assert instance1.value == instance2.value == "non-singleton"
    
    def test_provider_not_found(self):
        """Test error when provider is not found."""
        container = Container()
        
        with pytest.raises(ProviderNotFoundError) as exc_info:
            container.resolve(MockInterface)
        
        assert "No provider registered" in str(exc_info.value)
    
    def test_circular_dependency_detection(self):
        """Test circular dependency detection."""
        container = Container()
        
        # Set up circular dependencies
        def create_a():
            return container.resolve(CircularB)
        
        def create_b():
            return container.resolve(CircularA)
        
        container.register(CircularA, create_a)
        container.register(CircularB, create_b)
        
        with pytest.raises(CircularDependencyError) as exc_info:
            container.resolve(CircularA)
        
        assert "Circular dependency detected" in str(exc_info.value)
    
    def test_invalid_provider(self):
        """Test error when provider is not callable."""
        container = Container()
        
        with pytest.raises(InvalidProviderError) as exc_info:
            container.register(MockInterface, "not callable")
        
        assert "must be callable" in str(exc_info.value)
    
    def test_is_registered(self):
        """Test checking if interface is registered."""
        container = Container()
        
        assert not container.is_registered(MockInterface)
        
        container.register(MockInterface, lambda: MockImplementation())
        
        assert container.is_registered(MockInterface)
    
    def test_clear(self):
        """Test clearing all registrations."""
        container = Container()
        
        container.register(MockInterface, lambda: MockImplementation())
        container.register(AnotherMockInterface, lambda: AnotherMockImplementation(MockImplementation()))
        
        assert container.is_registered(MockInterface)
        assert container.is_registered(AnotherMockInterface)
        
        container.clear()
        
        assert not container.is_registered(MockInterface)
        assert not container.is_registered(AnotherMockInterface)
    
    def test_complex_dependency_chain(self):
        """Test resolving complex dependency chains."""
        container = Container()
        
        # Register dependencies
        container.register(MockInterface, lambda: MockImplementation("dependency"))
        container.register(AnotherMockInterface, lambda: AnotherMockImplementation(container.resolve(MockInterface)))
        
        # Resolve the dependent interface
        instance = container.resolve(AnotherMockInterface)
        
        assert isinstance(instance, AnotherMockImplementation)
        assert isinstance(instance.dependency, MockImplementation)
        assert instance.dependency.value == "dependency"