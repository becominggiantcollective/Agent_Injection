"""
Taxonomy management for agent classification and capabilities.
"""

from typing import Dict, List, Optional, Any
from pathlib import Path
import yaml
from pydantic import BaseModel, Field


class AgentCapability(BaseModel):
    """Represents a single agent capability."""
    name: str = Field(description="Capability name")
    description: str = Field(description="Capability description")
    category: str = Field(description="Capability category")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Capability parameters")


class AgentType(BaseModel):
    """Represents an agent type in the taxonomy."""
    name: str = Field(description="Agent type name")
    description: str = Field(description="Agent type description")
    capabilities: List[str] = Field(default_factory=list, description="List of capability names")
    base_class: Optional[str] = Field(default=None, description="Base class for this agent type")
    config: Dict[str, Any] = Field(default_factory=dict, description="Agent type configuration")


class Taxonomy(BaseModel):
    """Agent taxonomy definition."""
    version: str = Field(default="1.0", description="Taxonomy version")
    description: str = Field(description="Taxonomy description")
    capabilities: List[AgentCapability] = Field(default_factory=list, description="Available capabilities")
    agent_types: List[AgentType] = Field(default_factory=list, description="Defined agent types")


class TaxonomyManager:
    """Manages agent taxonomy loading and querying."""
    
    def __init__(self, taxonomy_path: Optional[Path] = None):
        """Initialize taxonomy manager."""
        self.taxonomy: Optional[Taxonomy] = None
        if taxonomy_path:
            self.load_taxonomy(taxonomy_path)
    
    def load_taxonomy(self, taxonomy_path: Path) -> None:
        """Load taxonomy from YAML file."""
        with open(taxonomy_path, 'r') as f:
            taxonomy_data = yaml.safe_load(f)
        self.taxonomy = Taxonomy(**taxonomy_data)
    
    def get_agent_type(self, name: str) -> Optional[AgentType]:
        """Get agent type by name."""
        if not self.taxonomy:
            return None
        
        for agent_type in self.taxonomy.agent_types:
            if agent_type.name == name:
                return agent_type
        return None
    
    def get_capability(self, name: str) -> Optional[AgentCapability]:
        """Get capability by name."""
        if not self.taxonomy:
            return None
        
        for capability in self.taxonomy.capabilities:
            if capability.name == name:
                return capability
        return None
    
    def list_agent_types(self) -> List[str]:
        """List all available agent types."""
        if not self.taxonomy:
            return []
        return [agent_type.name for agent_type in self.taxonomy.agent_types]
    
    def list_capabilities(self) -> List[str]:
        """List all available capabilities."""
        if not self.taxonomy:
            return []
        return [capability.name for capability in self.taxonomy.capabilities]