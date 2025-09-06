"""
Main injector class that provides dependency injection functionality.
"""

import inspect
from typing import Any, Type, TypeVar, Dict, get_type_hints
from .container import Container
from .exceptions import AgentInjectionError

T = TypeVar('T')


class Injector:
    """
    Main injector class that handles dependency injection.
    """
    
    def __init__(self, container: Container = None) -> None:
        self.container = container or Container()
    
    def inject(self, cls: Type[T]) -> T:
        """
        Create an instance of a class with its dependencies injected.
        
        Args:
            cls: The class to instantiate
            
        Returns:
            An instance of the class with dependencies injected
        """
        # Get the constructor signature
        sig = inspect.signature(cls.__init__)
        type_hints = get_type_hints(cls.__init__)
        
        # Prepare arguments for constructor
        kwargs = {}
        
        for param_name, param in sig.parameters.items():
            if param_name == 'self':
                continue
                
            # Get the type annotation
            param_type = type_hints.get(param_name)
            if param_type is None and param.annotation != inspect.Parameter.empty:
                param_type = param.annotation
            
            if param_type is not None:
                # Check if we have a provider for this type
                if self.container.is_registered(param_type):
                    kwargs[param_name] = self.container.resolve(param_type)
                elif param.default == inspect.Parameter.empty:
                    # Required parameter with no provider
                    raise AgentInjectionError(
                        f"No provider found for required parameter '{param_name}' "
                        f"of type {param_type} in {cls}"
                    )
        
        return cls(**kwargs)
    
    def call(self, func: callable, *args, **kwargs) -> Any:
        """
        Call a function with dependency injection.
        
        Args:
            func: The function to call
            *args: Positional arguments to pass to the function
            **kwargs: Keyword arguments to pass to the function
            
        Returns:
            The result of the function call
        """
        sig = inspect.signature(func)
        type_hints = get_type_hints(func)
        
        # Inject dependencies that aren't provided in kwargs
        for param_name, param in sig.parameters.items():
            if param_name in kwargs:
                continue  # Already provided
                
            param_type = type_hints.get(param_name)
            if param_type is None and param.annotation != inspect.Parameter.empty:
                param_type = param.annotation
            
            if param_type is not None and self.container.is_registered(param_type):
                kwargs[param_name] = self.container.resolve(param_type)
        
        return func(*args, **kwargs)