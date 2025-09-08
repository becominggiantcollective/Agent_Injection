"""
Decorators for dependency injection.
"""

import functools
from typing import Any, Type, TypeVar, Callable, Optional
from .container import Container
from .injector import Injector

T = TypeVar('T')

# Global default injector
_default_injector: Optional[Injector] = None


def get_default_injector() -> Injector:
    """Get or create the default injector."""
    global _default_injector
    if _default_injector is None:
        _default_injector = Injector()
    return _default_injector


def set_default_injector(injector: Injector) -> None:
    """Set the default injector."""
    global _default_injector
    _default_injector = injector


def injectable(cls: Type[T]) -> Type[T]:
    """
    Decorator to mark a class as injectable.
    
    This decorator modifies the class to automatically inject dependencies
    when instantiated.
    """
    original_init = cls.__init__
    
    @functools.wraps(original_init)
    def new_init(self, *args, **kwargs):
        # If arguments are provided, use them directly
        if args or kwargs:
            original_init(self, *args, **kwargs)
            return
        
        # Try to inject dependencies if no arguments provided
        try:
            injector = get_default_injector()
            instance = injector.inject(cls)
            # Copy the injected instance's attributes to self
            for attr_name, attr_value in instance.__dict__.items():
                setattr(self, attr_name, attr_value)
        except Exception:
            # Fall back to calling original init if injection fails
            original_init(self)
    
    cls.__init__ = new_init
    return cls


def inject(func: Callable = None, *, injector: Injector = None) -> Callable:
    """
    Decorator to inject dependencies into a function.
    
    Args:
        func: The function to decorate (when used without parentheses)
        injector: Optional specific injector to use
    """
    def decorator(f: Callable) -> Callable:
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            target_injector = injector or get_default_injector()
            return target_injector.call(f, *args, **kwargs)
        return wrapper
    
    if func is None:
        # Called with arguments: @inject(injector=...)
        return decorator
    else:
        # Called without arguments: @inject
        return decorator(func)