"""
Agent Injection Framework

A flexible dependency injection framework for AI agents and autonomous systems.
"""

__version__ = "0.1.0"
__author__ = "Becoming Giant Collective"

from .container import Container
from .injector import Injector
from .decorators import injectable, inject, get_default_injector, set_default_injector
from .exceptions import AgentInjectionError, CircularDependencyError, ProviderNotFoundError

__all__ = [
    "Container",
    "Injector", 
    "injectable",
    "inject",
    "get_default_injector",
    "set_default_injector",
    "AgentInjectionError",
    "CircularDependencyError",
    "ProviderNotFoundError",
]