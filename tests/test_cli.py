"""
Test the CLI functionality.
"""

import pytest
from typer.testing import CliRunner
from cli.main import app


class TestCLI:
    """Test CLI commands."""
    
    def setup_method(self):
        """Set up for each test."""
        self.runner = CliRunner()
    
    def test_cli_help(self):
        """Test CLI help command."""
        result = self.runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "Agent Injection Framework CLI" in result.output
    
    def test_cli_version(self):
        """Test CLI version command."""
        result = self.runner.invoke(app, ["version"])
        assert result.exit_code == 0
        assert "Agent Injection Framework" in result.output
        assert "Version: 0.1.0" in result.output
    
    def test_cli_status(self):
        """Test CLI status command."""
        result = self.runner.invoke(app, ["status"])
        assert result.exit_code == 0
        assert "System Status" in result.output
    
    def test_cli_agents(self):
        """Test CLI agents command."""
        result = self.runner.invoke(app, ["agents"])
        assert result.exit_code == 0
        assert "Registered Agents" in result.output
    
    def test_cli_campaigns(self):
        """Test CLI campaigns command."""
        result = self.runner.invoke(app, ["campaigns"])
        assert result.exit_code == 0
        assert "Campaigns" in result.output
    
    def test_cli_report_system(self):
        """Test CLI system report command."""
        result = self.runner.invoke(app, ["report", "system"])
        assert result.exit_code == 0
        assert "System Performance Report" in result.output
    
    def test_cli_report_agent(self):
        """Test CLI agent report command."""
        result = self.runner.invoke(app, ["report", "agent", "--id", "test-agent"])
        assert result.exit_code == 0
        assert "Agent Report: test-agent" in result.output
    
    def test_cli_report_campaign(self):
        """Test CLI campaign report command."""
        result = self.runner.invoke(app, ["report", "campaign", "--id", "test-campaign"])
        assert result.exit_code == 0
        assert "Campaign Report: test-campaign" in result.output
    
    def test_cli_validate(self, tmp_path):
        """Test CLI validate command."""
        # Create a test config file
        config_file = tmp_path / "test_config.yaml"
        config_file.write_text("test: value")
        
        result = self.runner.invoke(app, ["validate", str(config_file)])
        assert result.exit_code == 0
        assert "Configuration file is valid" in result.output
    
    def test_cli_validate_missing_file(self):
        """Test CLI validate with missing file."""
        result = self.runner.invoke(app, ["validate", "nonexistent.yaml"])
        assert result.exit_code == 1
        assert "File not found" in result.output
    
    def test_cli_run_dry_run(self, tmp_path):
        """Test CLI run with dry-run mode."""
        # Create a test campaign file
        campaign_file = tmp_path / "test_campaign.yaml"
        campaign_file.write_text("name: test\ndescription: test campaign")
        
        result = self.runner.invoke(app, ["run", str(campaign_file), "--dry-run"])
        assert result.exit_code == 0
        assert "DRY RUN MODE" in result.output
    
    def test_cli_run_missing_file(self):
        """Test CLI run with missing campaign file."""
        result = self.runner.invoke(app, ["run", "nonexistent.yaml"])
        assert result.exit_code == 1
        assert "Campaign file not found" in result.output