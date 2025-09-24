#!/usr/bin/env python3
"""
Run all tests and generate coverage report.
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd, description=""):
    """Run a command and return success status."""
    print(f"\n{'='*50}")
    print(f"🔄 {description or cmd}")
    print('='*50)
    
    try:
        result = subprocess.run(cmd, shell=True, check=True)
        print(f"✅ {description or cmd} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description or cmd} failed with exit code {e.returncode}")
        return False


def main():
    """Run comprehensive testing."""
    print("🧪 Running comprehensive test suite for Agent Injection")
    
    success = True
    
    # Run pytest with coverage
    if not run_command(
        "python -m pytest tests/ -v --cov=agent_injection --cov=core --cov=strategies --cov=execution --cov=analysis --cov=reporting --cov=feedback --cov=storage --cov=cli --cov-report=html --cov-report=term",
        "Running pytest with coverage"
    ):
        success = False
    
    # Run mypy type checking
    modules_to_check = [
        "agent_injection",
        "core", 
        "strategies",
        "execution",
        "analysis", 
        "reporting",
        "feedback",
        "storage",
        "cli"
    ]
    
    for module in modules_to_check:
        if Path(module).exists():
            if not run_command(f"python -m mypy {module} --ignore-missing-imports", f"Type checking {module}"):
                print(f"⚠️  Type checking failed for {module} (continuing...)")
    
    # Run flake8 linting
    if not run_command("python -m flake8 . --max-line-length=88 --extend-ignore=E203,W503", "Running flake8 linting"):
        print("⚠️  Linting issues found (continuing...)")
    
    # Test CLI functionality
    if not run_command("python -m cli --help", "Testing CLI help"):
        success = False
    
    if not run_command("python -m cli version", "Testing CLI version command"):
        success = False
    
    # Generate final report
    print(f"\n{'='*70}")
    if success:
        print("🎉 All critical tests passed!")
        print("📊 Coverage report generated in htmlcov/")
        print("🔍 Check htmlcov/index.html for detailed coverage")
    else:
        print("⚠️  Some tests failed. Check output above for details.")
        sys.exit(1)
    
    print("="*70)


if __name__ == "__main__":
    main()