#!/usr/bin/env python3
"""
Setup development environment for Agent Injection.
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd, description=""):
    """Run a command and handle errors."""
    print(f"Running: {description or cmd}")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {cmd}")
        print(f"Exit code: {e.returncode}")
        if e.stderr:
            print(f"Error output: {e.stderr}")
        return False


def main():
    """Set up development environment."""
    print("Setting up Agent Injection development environment...")
    
    # Install package in development mode
    if not run_command("pip install -e .", "Installing package in development mode"):
        sys.exit(1)
    
    # Install development dependencies
    dev_deps = [
        "pytest>=7.0.0",
        "pytest-cov>=4.0.0",
        "black>=23.0.0",
        "flake8>=6.0.0",
        "mypy>=1.0.0",
        "pre-commit>=3.0.0",
        "typer>=0.9.0",
        "rich>=13.0.0",
        "httpx>=0.24.0",
        "sqlmodel>=0.0.14",
        "tqdm>=4.65.0",
        "pyyaml>=6.0.0"
    ]
    
    for dep in dev_deps:
        if not run_command(f"pip install {dep}", f"Installing {dep}"):
            print(f"Warning: Failed to install {dep}")
    
    # Set up pre-commit hooks
    if Path(".pre-commit-config.yaml").exists():
        run_command("pre-commit install", "Setting up pre-commit hooks")
    
    print("\n✅ Development environment setup complete!")
    print("\nNext steps:")
    print("1. Run tests: pytest")
    print("2. Format code: black .")
    print("3. Check types: mypy .")
    print("4. Try CLI: python -m cli --help")


if __name__ == "__main__":
    main()