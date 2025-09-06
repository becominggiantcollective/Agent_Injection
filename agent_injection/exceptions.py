"""
Custom exceptions for the Agent Injection framework.
"""


class AgentInjectionError(Exception):
    """Base exception for agent injection errors."""
    pass


class CircularDependencyError(AgentInjectionError):
    """Raised when a circular dependency is detected."""
    pass


class ProviderNotFoundError(AgentInjectionError):
    """Raised when a required provider is not found."""
    pass


class InvalidProviderError(AgentInjectionError):
    """Raised when a provider is invalid."""
    pass