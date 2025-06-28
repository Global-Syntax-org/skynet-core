#!/usr/bin/env python3
"""
Development environment setup script for Skynet Lite
Sets up pre-commit hooks, development dependencies, and tooling
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd: str, description: str) -> bool:
    """Run a shell command and return success status"""
    try:
        print(f"🔧 {description}...")
        subprocess.run(cmd.split(), check=True, capture_output=True)
        print(f"✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        return False


def main():
    """Set up development environment"""
    print("🚀 Setting up Skynet Lite development environment...")
    
    # Install development dependencies
    if not run_command(
        f"{sys.executable} -m pip install pre-commit black flake8 mypy pytest pytest-cov",
        "Installing development dependencies"
    ):
        return False
    
    # Set up pre-commit hooks
    pre_commit_config = Path(".pre-commit-config.yaml")
    if not pre_commit_config.exists():
        with open(pre_commit_config, "w") as f:
            f.write("""repos:
  - repo: https://github.com/psf/black
    rev: 23.12.1
    hooks:
      - id: black
        language_version: python3.10
  
  - repo: https://github.com/pycqa/flake8
    rev: 7.0.0
    hooks:
      - id: flake8
        args: [--max-line-length=88, --extend-ignore=E203,W503]
  
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.8.0
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
""")
        print("✅ Created .pre-commit-config.yaml")
    
    # Install pre-commit hooks
    if not run_command("pre-commit install", "Installing pre-commit hooks"):
        return False
    
    # Create tests directory structure
    tests_dir = Path("tests")
    tests_dir.mkdir(exist_ok=True)
    
    for test_file in ["__init__.py", "test_main.py", "test_config.py", "test_models.py"]:
        test_path = tests_dir / test_file
        if not test_path.exists():
            test_path.touch()
    
    print("✅ Created test directory structure")
    
    print("\n🎉 Development environment setup complete!")
    print("📋 Next steps:")
    print("   - Run tests: pytest")
    print("   - Format code: black .")
    print("   - Lint code: flake8 .")
    print("   - Type check: mypy .")


if __name__ == "__main__":
    main()