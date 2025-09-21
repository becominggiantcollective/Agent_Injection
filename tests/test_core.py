"""
Test core module functionality.
"""

import pytest
from pathlib import Path
import tempfile
import yaml
from core.config import Config, get_config, set_config
from core.taxonomy import TaxonomyManager, Taxonomy, AgentType, AgentCapability
from core.base import BaseAgent, BaseStrategy, Campaign


class TestConfig:
    """Test configuration management."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = Config()
        assert config.environment == "development"
        assert config.debug is False
        assert config.log_level == "INFO"
        assert config.max_agents == 10
    
    def test_config_from_dict(self):
        """Test creating config from dictionary."""
        config_data = {
            "environment": "production",
            "debug": True,
            "max_agents": 20
        }
        config = Config(**config_data)
        assert config.environment == "production"
        assert config.debug is True
        assert config.max_agents == 20
    
    def test_config_file_operations(self):
        """Test saving and loading config from file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            config_data = {
                "environment": "test",
                "debug": True,
                "max_agents": 5
            }
            yaml.dump(config_data, f)
            config_path = Path(f.name)
        
        try:
            # Load config from file
            config = Config.from_file(config_path)
            assert config.environment == "test"
            assert config.debug is True
            assert config.max_agents == 5
            
            # Modify and save
            config.environment = "modified"
            config.to_file(config_path)
            
            # Load again to verify changes
            config2 = Config.from_file(config_path)
            assert config2.environment == "modified"
            
        finally:
            config_path.unlink()
    
    def test_global_config(self):
        """Test global configuration management."""
        original_config = get_config()
        
        # Set new config
        new_config = Config(environment="test_global")
        set_config(new_config)
        
        # Verify global config changed
        retrieved_config = get_config()
        assert retrieved_config.environment == "test_global"
        
        # Restore original config
        set_config(original_config)


class TestTaxonomy:
    """Test taxonomy management."""
    
    def test_capability_creation(self):
        """Test creating agent capabilities."""
        capability = AgentCapability(
            name="test_capability",
            description="Test capability",
            category="test",
            parameters={"max_value": 100}
        )
        assert capability.name == "test_capability"
        assert capability.category == "test"
        assert capability.parameters["max_value"] == 100
    
    def test_agent_type_creation(self):
        """Test creating agent types."""
        agent_type = AgentType(
            name="TestAgent",
            description="Test agent type",
            capabilities=["capability1", "capability2"],
            base_class="BaseAgent"
        )
        assert agent_type.name == "TestAgent"
        assert len(agent_type.capabilities) == 2
        assert "capability1" in agent_type.capabilities
    
    def test_taxonomy_creation(self):
        """Test creating complete taxonomy."""
        capability = AgentCapability(
            name="chat",
            description="Chat capability",
            category="communication"
        )
        
        agent_type = AgentType(
            name="ChatAgent",
            description="Chat agent",
            capabilities=["chat"]
        )
        
        taxonomy = Taxonomy(
            version="1.0",
            description="Test taxonomy",
            capabilities=[capability],
            agent_types=[agent_type]
        )
        
        assert taxonomy.version == "1.0"
        assert len(taxonomy.capabilities) == 1
        assert len(taxonomy.agent_types) == 1
    
    def test_taxonomy_manager(self):
        """Test taxonomy manager functionality."""
        manager = TaxonomyManager()
        
        # Create test taxonomy
        capability = AgentCapability(
            name="test_cap",
            description="Test capability",
            category="test"
        )
        
        agent_type = AgentType(
            name="TestAgent",
            description="Test agent",
            capabilities=["test_cap"]
        )
        
        taxonomy = Taxonomy(
            description="Test taxonomy",
            capabilities=[capability],
            agent_types=[agent_type]
        )
        
        manager.taxonomy = taxonomy
        
        # Test retrieval methods
        retrieved_type = manager.get_agent_type("TestAgent")
        assert retrieved_type is not None
        assert retrieved_type.name == "TestAgent"
        
        retrieved_cap = manager.get_capability("test_cap")
        assert retrieved_cap is not None
        assert retrieved_cap.name == "test_cap"
        
        # Test listing methods
        types = manager.list_agent_types()
        assert "TestAgent" in types
        
        caps = manager.list_capabilities()
        assert "test_cap" in caps


class MockAgent(BaseAgent):
    """Mock agent for testing."""
    
    async def execute(self, task):
        """Mock execute method."""
        return {"status": "completed", "result": "mock_result"}
    
    def validate_task(self, task):
        """Mock validate method."""
        return True


class MockStrategy(BaseStrategy):
    """Mock strategy for testing."""
    
    async def execute(self, agents, task):
        """Mock execute method."""
        return {"strategy": "mock", "agents": len(agents)}
    
    def select_agents(self, available_agents, task):
        """Mock agent selection."""
        return available_agents[:1]


class TestBaseClasses:
    """Test base classes."""
    
    def test_base_agent(self):
        """Test BaseAgent functionality."""
        agent = MockAgent("test_agent", {"param": "value"})
        
        assert agent.agent_id == "test_agent"
        assert agent.config["param"] == "value"
        assert agent.status == "initialized"
        
        # Test metadata operations
        agent.set_metadata("key1", "value1")
        assert agent.get_metadata("key1") == "value1"
        assert agent.get_metadata("nonexistent", "default") == "default"
    
    def test_base_strategy(self):
        """Test BaseStrategy functionality."""
        strategy = MockStrategy("test_strategy", {"setting": "value"})
        
        assert strategy.strategy_id == "test_strategy"
        assert strategy.config["setting"] == "value"
        
        info = strategy.get_strategy_info()
        assert info["strategy_id"] == "test_strategy"
        assert info["config"]["setting"] == "value"
    
    def test_campaign_model(self):
        """Test Campaign model."""
        campaign = Campaign(
            name="test_campaign",
            description="Test campaign",
            strategy="test_strategy",
            agents=["agent1", "agent2"],
            tasks=[{"type": "test", "data": {}}],
            config={"timeout": 300}
        )
        
        assert campaign.name == "test_campaign"
        assert len(campaign.agents) == 2
        assert len(campaign.tasks) == 1
        assert campaign.config["timeout"] == 300