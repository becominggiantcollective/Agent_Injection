"""
Core module for Agent Injection framework.

Contains the fundamental components and abstractions for the agent system.
"""

from .config import Config
from .taxonomy import TaxonomyManager
from .base import BaseAgent, BaseStrategy

__all__ = [
    "Config",
    "TaxonomyManager", 
    "BaseAgent",
    "BaseStrategy",
]