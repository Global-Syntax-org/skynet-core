#!/usr/bin/env python3
"""
Development environment setup script for Skynet Lite
Sets up pre-commit hooks, development dependencies, and tooling
"""

import asyncio
import subprocess
import sys
from pathlib import Path
from typing import Optional


async def run_command_async(cmd: str, description: str) -> bool:
    """Run a shell command asynchronously and return success status"""
    try:
        print(f"🔧 {description}...")
        process = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        
        if process.returncode == 0:
            print(f"✅ {description} completed")
            return True
        else:
            print(f"❌ {description} failed: {stderr.decode()}")
            return False
            
    except Exception as e:
        print(f"❌ {description} failed with exception: {e}")
        return False


def create_pre_commit_config() -> bool:
    """Create pre-commit configuration file"""
    pre_commit_config = Path(".pre-commit-config.yaml")
    
    if pre_commit_config.exists():
        print("✅ .pre-commit-config.yaml already exists")
        return True
    
    try:
        config_content = """repos:
  - repo: https://github.com/psf/black
    rev: 23.12.1
    hooks:
      - id: black
        language_version: python3.10
        args: [--line-length=88]
  
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
        args: [--ignore-missing-imports]
  
  - repo: https://github.com/pycqa/isort
    rev: 5.13.2
    hooks:
      - id: isort
        name: isort (python)
        args: [--profile, black]
"""
        
        with open(pre_commit_config, "w", encoding="utf-8") as f:
            f.write(config_content)
        
        print("✅ Created .pre-commit-config.yaml")
        return True
        
    except Exception as e:
        print(f"❌ Failed to create pre-commit config: {e}")
        return False


def create_test_structure() -> bool:
    """Create test directory structure with proper async test templates"""
    try:
        tests_dir = Path("tests")
        tests_dir.mkdir(exist_ok=True)
        
        # Test files with basic structure
        test_files = {
            "__init__.py": "",
            "conftest.py": '''"""Pytest configuration and fixtures for Skynet Lite tests"""
import pytest
import asyncio
from unittest.mock import AsyncMock, Mock
from skynet.config import Config


@pytest.fixture
def mock_config():
    """Mock configuration for testing"""
    config = Mock(spec=Config)
    config.ollama_base_url = "http://localhost:11434"
    config.ollama_model = "mistral"
    config.bing_api_key = "test-key"
    return config


@pytest.fixture
def event_loop():
    """Create an instance of the default event loop for the test session"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
''',
            "test_main.py": '''"""Tests for main SkynetLite class"""
import pytest
from unittest.mock import AsyncMock, Mock, patch
from main import SkynetLite


@pytest.mark.asyncio
class TestSkynetLite:
    """Test suite for SkynetLite main functionality"""
    
    async def test_initialization(self, mock_config):
        """Test SkynetLite initialization"""
        with patch('main.Config', return_value=mock_config):
            skynet = SkynetLite()
            assert skynet.config == mock_config
    
    async def test_needs_web_search(self, mock_config):
        """Test web search detection logic"""
        with patch('main.Config', return_value=mock_config):
            skynet = SkynetLite()
            
            # Test web search indicators
            assert await skynet._needs_web_search("what's the latest news?")
            assert await skynet._needs_web_search("current weather")
            assert not await skynet._needs_web_search("hello world")
''',
            "test_config.py": '''"""Tests for configuration management"""
import pytest
from unittest.mock import patch, mock_open
    from skynet.config import Config


class TestConfig:
    """Test suite for configuration management"""
    
    def test_default_config(self):
        """Test default configuration values"""
        config = Config()
        assert config.ollama_base_url == "http://localhost:11434"
        assert config.ollama_model == "mistral"
    
    @patch.dict('os.environ', {'OLLAMA_MODEL': 'custom-model'})
    def test_environment_override(self):
        """Test environment variable override"""
        config = Config()
        assert config.ollama_model == "custom-model"
''',
            "test_models.py": '''"""Tests for model loader functionality"""
import pytest
from unittest.mock import AsyncMock, Mock, patch
from models.loader import OllamaModelLoader


@pytest.mark.asyncio
class TestOllamaModelLoader:
    """Test suite for Ollama model loader"""
    
    async def test_model_availability_check(self):
        """Test checking if model is available"""
        loader = OllamaModelLoader()
        
        with patch('ollama.AsyncClient') as mock_client:
            mock_client.return_value.list = AsyncMock(
                return_value={'models': [{'name': 'mistral'}]}
            )
            
            result = await loader.ensure_model_available("mistral")
            assert result is True
    
    async def test_generate_completion(self):
        """Test completion generation"""
        loader = OllamaModelLoader()
        
        with patch('ollama.AsyncClient') as mock_client:
            mock_response = {
                'message': {'content': 'Test response'}
            }
            mock_client.return_value.chat = AsyncMock(return_value=mock_response)
            
            result = await loader.generate_completion("test prompt", "mistral")
            assert result == "Test response"
'''
        }
        
        for filename, content in test_files.items():
            test_path = tests_dir / filename
            if not test_path.exists():
                with open(test_path, "w", encoding="utf-8") as f:
                    f.write(content)
        
        print("✅ Created comprehensive test directory structure")
        return True
        
    except Exception as e:
        print(f"❌ Failed to create test structure: {e}")
        return False


def create_development_config() -> bool:
    """Create development-specific configuration files"""
    try:
        # Create pytest.ini for test configuration
        pytest_ini = Path("pytest.ini")
        if not pytest_ini.exists():
            with open(pytest_ini, "w", encoding="utf-8") as f:
                f.write("""[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --tb=short
    --strict-markers
    --disable-warnings
    --asyncio-mode=auto
markers =
    asyncio: marks tests as async
    integration: marks tests as integration tests
    unit: marks tests as unit tests
""")
            print("✅ Created pytest.ini")
        
        # Create .editorconfig for consistent coding style
        editorconfig = Path(".editorconfig")
        if not editorconfig.exists():
            with open(editorconfig, "w", encoding="utf-8") as f:
                f.write("""root = true

[*]
charset = utf-8
end_of_line = lf
insert_final_newline = true
trim_trailing_whitespace = true
indent_style = space
indent_size = 4

[*.{yml,yaml}]
indent_size = 2

[*.md]
trim_trailing_whitespace = false
""")
            print("✅ Created .editorconfig")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to create development config: {e}")
        return False


async def main() -> None:
    """Set up development environment with proper async handling"""
    print("🚀 Setting up Skynet Lite development environment...")
    
    success = True
    
    # Install development dependencies
    dev_packages = [
        "pre-commit>=3.6.0",
        "black>=23.12.0", 
        "flake8>=7.0.0",
        "mypy>=1.8.0",
        "isort>=5.13.0",
        "pytest>=7.4.0",
        "pytest-asyncio>=0.23.0",
        "pytest-cov>=4.1.0",
        "pytest-mock>=3.12.0"
    ]
    
    install_cmd = f"{sys.executable} -m pip install {' '.join(dev_packages)}"
    if not await run_command_async(install_cmd, "Installing development dependencies"):
        success = False
    
    # Create configuration files
    if not create_pre_commit_config():
        success = False
    
    if not create_development_config():
        success = False
    
    # Install pre-commit hooks
    if not await run_command_async("pre-commit install", "Installing pre-commit hooks"):
        success = False
    
    # Create test structure
    if not create_test_structure():
        success = False
    
    # Run initial pre-commit to ensure everything works
    print("🔧 Running initial pre-commit check...")
    await run_command_async("pre-commit run --all-files", "Initial pre-commit validation")
    
    if success:
        print("\n🎉 Development environment setup complete!")
        print("📋 Available commands:")
        print("   - Run tests: pytest")
        print("   - Run tests with coverage: pytest --cov=. --cov-report=html")
        print("   - Format code: black .")
        print("   - Sort imports: isort .")
        print("   - Lint code: flake8 .")
        print("   - Type check: mypy .")
        print("   - Run pre-commit: pre-commit run --all-files")
        print("\n🔧 Integration with IDEs:")
        print("   - VS Code: Install Python, Black Formatter, and Flake8 extensions")
        print("   - PyCharm: Configure Black as external tool and enable type checking")
    else:
        print("\n❌ Some setup steps failed. Please check the errors above.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())