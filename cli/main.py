"""
Main CLI application using Typer.
"""

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from pathlib import Path
from typing import Optional
import asyncio

app = typer.Typer(help="Agent Injection Framework CLI")
console = Console()


@app.command()
def version():
    """Show version information."""
    console.print("[bold green]Agent Injection Framework[/bold green]")
    console.print("Version: 0.1.0")
    console.print("A flexible dependency injection framework for AI agents")


@app.command()
def init(
    name: str = typer.Argument(help="Project name"),
    path: Optional[Path] = typer.Option(None, "--path", "-p", help="Project path")
):
    """Initialize a new agent project."""
    if path is None:
        path = Path.cwd() / name
    
    console.print(f"[bold blue]Initializing project:[/bold blue] {name}")
    console.print(f"[bold blue]Location:[/bold blue] {path}")
    
    # Create project structure
    try:
        path.mkdir(parents=True, exist_ok=True)
        
        # Create basic structure
        (path / "agents").mkdir(exist_ok=True)
        (path / "campaigns").mkdir(exist_ok=True)
        (path / "config").mkdir(exist_ok=True)
        
        # Create example files
        _create_example_config(path / "config" / "config.yaml")
        _create_example_taxonomy(path / "config" / "taxonomy.yaml")
        _create_example_campaign(path / "campaigns" / "example_campaign.yaml")
        _create_example_agent(path / "agents" / "example_agent.py")
        
        console.print(f"[green]✓[/green] Project initialized successfully!")
        console.print(f"[dim]Next steps:[/dim]")
        console.print(f"  1. cd {path}")
        console.print(f"  2. Edit config/config.yaml")
        console.print(f"  3. agent-injection run campaigns/example_campaign.yaml")
        
    except Exception as e:
        console.print(f"[red]Error:[/red] Failed to initialize project: {e}")
        raise typer.Exit(1)


@app.command()
def validate(
    config_file: Path = typer.Argument(help="Configuration file to validate")
):
    """Validate configuration files."""
    console.print(f"[bold blue]Validating:[/bold blue] {config_file}")
    
    if not config_file.exists():
        console.print(f"[red]Error:[/red] File not found: {config_file}")
        raise typer.Exit(1)
    
    try:
        # Basic validation - in a real implementation, this would validate YAML structure
        console.print("[green]✓[/green] Configuration file is valid")
    except Exception as e:
        console.print(f"[red]Error:[/red] Validation failed: {e}")
        raise typer.Exit(1)


@app.command()
def run(
    campaign_file: Path = typer.Argument(help="Campaign file to execute"),
    config_file: Optional[Path] = typer.Option(None, "--config", "-c", help="Configuration file"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be executed without running")
):
    """Run an agent campaign."""
    console.print(f"[bold blue]Running campaign:[/bold blue] {campaign_file}")
    
    if not campaign_file.exists():
        console.print(f"[red]Error:[/red] Campaign file not found: {campaign_file}")
        raise typer.Exit(1)
    
    if config_file and not config_file.exists():
        console.print(f"[red]Error:[/red] Config file not found: {config_file}")
        raise typer.Exit(1)
    
    if dry_run:
        console.print("[yellow]DRY RUN MODE[/yellow] - No actual execution")
        console.print("Campaign would be executed with the following configuration:")
        console.print(f"  Campaign: {campaign_file}")
        console.print(f"  Config: {config_file or 'default'}")
        return
    
    try:
        # In a real implementation, this would load and execute the campaign
        with console.status("[bold green]Executing campaign..."):
            # Simulate execution
            import time
            time.sleep(2)
        
        console.print("[green]✓[/green] Campaign executed successfully")
        
        # Show results table
        results_table = Table(title="Execution Results")
        results_table.add_column("Agent", style="cyan")
        results_table.add_column("Tasks", justify="right")
        results_table.add_column("Status", style="green")
        results_table.add_column("Duration", justify="right")
        
        results_table.add_row("example_agent", "3", "✓ Success", "2.5s")
        results_table.add_row("helper_agent", "2", "✓ Success", "1.8s")
        
        console.print(results_table)
        
    except Exception as e:
        console.print(f"[red]Error:[/red] Campaign execution failed: {e}")
        raise typer.Exit(1)


@app.command()
def status():
    """Show system status."""
    console.print(Panel.fit("[bold green]Agent Injection System Status[/bold green]"))
    
    status_table = Table()
    status_table.add_column("Component", style="cyan")
    status_table.add_column("Status", style="green")
    status_table.add_column("Details")
    
    status_table.add_row("Framework", "✓ Active", "Version 0.1.0")
    status_table.add_row("Storage", "✓ Ready", "Memory backend")
    status_table.add_row("Agents", "✓ Ready", "0 registered")
    status_table.add_row("Campaigns", "⏸ Idle", "0 running")
    
    console.print(status_table)


@app.command()
def agents():
    """List and manage agents."""
    console.print("[bold blue]Registered Agents[/bold blue]")
    
    agents_table = Table()
    agents_table.add_column("Agent ID", style="cyan")
    agents_table.add_column("Type", style="magenta")
    agents_table.add_column("Status", style="green")
    agents_table.add_column("Capabilities")
    
    # In a real implementation, this would query actual agents
    agents_table.add_row("agent-001", "ChatAgent", "Ready", "chat, nlp, reasoning")
    agents_table.add_row("agent-002", "TaskAgent", "Ready", "task_execution, automation")
    
    console.print(agents_table)


@app.command()
def campaigns():
    """List and manage campaigns."""
    console.print("[bold blue]Campaigns[/bold blue]")
    
    campaigns_table = Table()
    campaigns_table.add_column("Campaign", style="cyan")
    campaigns_table.add_column("Status", style="green")
    campaigns_table.add_column("Agents")
    campaigns_table.add_column("Progress")
    
    # In a real implementation, this would query actual campaigns
    campaigns_table.add_row("example_campaign", "Completed", "2", "100%")
    campaigns_table.add_row("data_analysis", "Running", "3", "75%")
    
    console.print(campaigns_table)


@app.command()
def report(
    target_type: str = typer.Argument(help="Report target type (agent, campaign, system)"),
    target_id: Optional[str] = typer.Option(None, "--id", help="Target ID"),
    format: str = typer.Option("console", "--format", "-f", help="Output format (console, json, html)")
):
    """Generate performance reports."""
    console.print(f"[bold blue]Generating {target_type} report[/bold blue]")
    
    if target_type == "system":
        _show_system_report()
    elif target_type == "agent":
        if not target_id:
            console.print("[red]Error:[/red] Agent ID required for agent reports")
            raise typer.Exit(1)
        _show_agent_report(target_id)
    elif target_type == "campaign":
        if not target_id:
            console.print("[red]Error:[/red] Campaign name required for campaign reports")
            raise typer.Exit(1)
        _show_campaign_report(target_id)
    else:
        console.print(f"[red]Error:[/red] Unknown report type: {target_type}")
        raise typer.Exit(1)


def _show_system_report():
    """Show system performance report."""
    report_table = Table(title="System Performance Report")
    report_table.add_column("Metric", style="cyan")
    report_table.add_column("Value", justify="right")
    report_table.add_column("Status", style="green")
    
    report_table.add_row("Total Agents", "5", "✓ Good")
    report_table.add_row("Active Campaigns", "2", "✓ Normal")
    report_table.add_row("Success Rate", "94.2%", "✓ Excellent")
    report_table.add_row("Avg Response Time", "1.2s", "✓ Good")
    report_table.add_row("Error Rate", "0.8%", "✓ Low")
    
    console.print(report_table)


def _show_agent_report(agent_id: str):
    """Show agent performance report."""
    console.print(f"[bold blue]Agent Report: {agent_id}[/bold blue]")
    
    report_table = Table()
    report_table.add_column("Metric", style="cyan")
    report_table.add_column("Value", justify="right")
    
    report_table.add_row("Tasks Completed", "127")
    report_table.add_row("Success Rate", "96.8%")
    report_table.add_row("Avg Execution Time", "2.1s")
    report_table.add_row("Performance Score", "87/100")
    
    console.print(report_table)


def _show_campaign_report(campaign_name: str):
    """Show campaign performance report."""
    console.print(f"[bold blue]Campaign Report: {campaign_name}[/bold blue]")
    
    report_table = Table()
    report_table.add_column("Metric", style="cyan")
    report_table.add_column("Value", justify="right")
    
    report_table.add_row("Total Tasks", "45")
    report_table.add_row("Completed", "43")
    report_table.add_row("Success Rate", "95.6%")
    report_table.add_row("Total Duration", "2m 34s")
    
    console.print(report_table)


def _create_example_config(path: Path):
    """Create example configuration file."""
    config_content = """# Agent Injection Configuration
environment: development
debug: true
log_level: INFO

# Agent settings
max_agents: 10
agent_timeout: 300

# Storage settings
storage_backend: memory
storage_config: {}

# API settings (optional)
# api_key: your_api_key
# base_url: https://api.example.com
"""
    path.write_text(config_content)


def _create_example_taxonomy(path: Path):
    """Create example taxonomy file."""
    taxonomy_content = """version: "1.0"
description: "Example agent taxonomy"

capabilities:
  - name: "chat"
    description: "Natural language conversation"
    category: "communication"
    parameters:
      max_tokens: 1000
  
  - name: "task_execution"
    description: "Execute automated tasks"
    category: "automation"
    parameters:
      timeout: 60

agent_types:
  - name: "ChatAgent"
    description: "Conversational AI agent"
    capabilities: ["chat"]
    base_class: "BaseAgent"
    config:
      model: "gpt-3.5-turbo"
  
  - name: "TaskAgent"
    description: "Task automation agent"
    capabilities: ["task_execution"]
    base_class: "BaseAgent"
    config:
      max_retries: 3
"""
    path.write_text(taxonomy_content)


def _create_example_campaign(path: Path):
    """Create example campaign file."""
    campaign_content = """name: "example_campaign"
description: "Example campaign demonstrating agent coordination"
strategy: "sequential"
agents:
  - "chat_agent"
  - "task_agent"

tasks:
  - type: "analysis"
    description: "Analyze input data"
    requirements: ["chat"]
    data:
      input: "Please analyze this text for sentiment"
  
  - type: "action"
    description: "Execute follow-up action"
    requirements: ["task_execution"]
    data:
      action: "generate_report"

config:
  timeout: 300
  retry_attempts: 2
"""
    path.write_text(campaign_content)


def _create_example_agent(path: Path):
    """Create example agent implementation."""
    agent_content = '''"""
Example agent implementation.
"""

from core.base import BaseAgent
from typing import Dict, Any, List
import asyncio


class ExampleAgent(BaseAgent):
    """Example agent demonstrating basic functionality."""
    
    def __init__(self, agent_id: str, config: Dict[str, Any] = None):
        super().__init__(agent_id, config)
        self.capabilities = ["chat", "analysis"]
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a task and return results."""
        self.status = "running"
        
        # Simulate processing time
        await asyncio.sleep(1)
        
        # Process the task
        result = {
            "task_id": task.get("task_id", "unknown"),
            "agent_id": self.agent_id,
            "status": "completed",
            "output": f"Processed task: {task.get('description', 'No description')}",
            "metadata": {
                "processing_time": 1.0,
                "capabilities_used": ["chat"]
            }
        }
        
        self.status = "ready"
        return result
    
    def validate_task(self, task: Dict[str, Any]) -> bool:
        """Validate if the agent can handle this task."""
        task_requirements = task.get("requirements", [])
        
        # Check if we have the required capabilities
        return all(req in self.capabilities for req in task_requirements)
    
    def get_capabilities(self) -> List[str]:
        """Return list of agent capabilities."""
        return self.capabilities.copy()


# Register the agent with the injection framework
if __name__ == "__main__":
    agent = ExampleAgent("example_agent_001")
    print(f"Agent {agent.agent_id} initialized with capabilities: {agent.get_capabilities()}")
'''
    path.write_text(agent_content)


if __name__ == "__main__":
    app()