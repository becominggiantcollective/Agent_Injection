"""
Configuration management for Agent Injection framework.
"""

from typing import Any, Dict, Optional
from pathlib import Path
import yaml
from pydantic import BaseModel, Field


class Config(BaseModel):
    """Configuration management for the agent system."""
    
    # Core settings
    environment: str = Field(default="development", description="Environment mode")
    debug: bool = Field(default=False, description="Enable debug mode")
    log_level: str = Field(default="INFO", description="Logging level")
    
    # Agent settings
    max_agents: int = Field(default=10, description="Maximum number of concurrent agents")
    agent_timeout: int = Field(default=300, description="Agent timeout in seconds")
    
    # Storage settings
    storage_backend: str = Field(default="memory", description="Storage backend type")
    storage_config: Dict[str, Any] = Field(default_factory=dict, description="Storage configuration")
    
    # API settings
    api_key: Optional[str] = Field(default=None, description="API key for external services")
    base_url: Optional[str] = Field(default=None, description="Base URL for external services")
    
    @classmethod
    def from_file(cls, config_path: Path) -> "Config":
        """Load configuration from YAML file."""
        with open(config_path, 'r') as f:
            config_data = yaml.safe_load(f)
        return cls(**config_data)
    
    def to_file(self, config_path: Path) -> None:
        """Save configuration to YAML file."""
        with open(config_path, 'w') as f:
            yaml.dump(self.model_dump(), f, default_flow_style=False)


# Global configuration instance
_config: Optional[Config] = None


def get_config() -> Config:
    """Get the global configuration instance."""
    global _config
    if _config is None:
        _config = Config()
    return _config


def set_config(config: Config) -> None:
    """Set the global configuration instance."""
    global _config
    _config = config