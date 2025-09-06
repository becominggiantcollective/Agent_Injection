"""
Core container for managing dependencies and providers.
"""

from typing import Any, Dict, Type, TypeVar, Optional, Callable, Set
from .exceptions import ProviderNotFoundError, CircularDependencyError, InvalidProviderError

T = TypeVar('T')


class Container:
    """
    Dependency injection container that manages providers and resolves dependencies.
    """
    
    def __init__(self) -> None:
        self._providers: Dict[Type, Callable[[], Any]] = {}
        self._singletons: Dict[Type, Any] = {}
        self._resolution_stack: Set[Type] = set()
    
    def register(self, interface: Type[T], provider: Callable[[], T], singleton: bool = False) -> None:
        """
        Register a provider for an interface.
        
        Args:
            interface: The interface/type to register
            provider: Factory function that creates instances
            singleton: Whether to create a single instance (default: False)
        """
        if not callable(provider):
            raise InvalidProviderError(f"Provider for {interface} must be callable")
        
        self._providers[interface] = provider
        
        if singleton and interface not in self._singletons:
            self._singletons[interface] = None
    
    def register_instance(self, interface: Type[T], instance: T) -> None:
        """
        Register a specific instance for an interface.
        
        Args:
            interface: The interface/type to register
            instance: The instance to register
        """
        self._providers[interface] = lambda: instance
        self._singletons[interface] = instance
    
    def resolve(self, interface: Type[T]) -> T:
        """
        Resolve an instance of the given interface.
        
        Args:
            interface: The interface/type to resolve
            
        Returns:
            An instance of the requested type
            
        Raises:
            ProviderNotFoundError: If no provider is registered for the interface
            CircularDependencyError: If a circular dependency is detected
        """
        if interface in self._resolution_stack:
            raise CircularDependencyError(f"Circular dependency detected for {interface}")
        
        if interface not in self._providers:
            raise ProviderNotFoundError(f"No provider registered for {interface}")
        
        # Check if we have a singleton instance
        if interface in self._singletons and self._singletons[interface] is not None:
            return self._singletons[interface]
        
        # Add to resolution stack to detect circular dependencies
        self._resolution_stack.add(interface)
        
        try:
            provider = self._providers[interface]
            instance = provider()
            
            # Store singleton instance if needed
            if interface in self._singletons:
                self._singletons[interface] = instance
            
            return instance
        finally:
            # Remove from resolution stack
            self._resolution_stack.discard(interface)
    
    def is_registered(self, interface: Type) -> bool:
        """
        Check if an interface is registered.
        
        Args:
            interface: The interface/type to check
            
        Returns:
            True if registered, False otherwise
        """
        return interface in self._providers
    
    def clear(self) -> None:
        """Clear all registrations."""
        self._providers.clear()
        self._singletons.clear()
        self._resolution_stack.clear()