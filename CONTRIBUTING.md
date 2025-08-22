# Contributing to Skynet Lite

Thank you for your interest in contributing to Skynet Lite! This guide will help you get started with contributing to our privacy-first AI assistant project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Contributing Guidelines](#contributing-guidelines)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Documentation](#documentation)
- [Issue Reporting](#issue-reporting)

## Code of Conduct

This project adheres to a code of conduct that ensures a welcoming environment for all contributors. By participating, you agree to:

- Be respectful and inclusive
- Focus on constructive feedback
- Help maintain a harassment-free environment
- Support newcomers and answer questions patiently

## Getting Started

### Prerequisites

- Python 3.10 or higher
- Git
- Ollama (for local LLM testing)
- Basic knowledge of async/await programming

### Fork and Clone

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/skynet-lite.git
   cd skynet-lite
   ```

3. **Add upstream remote**:
   ```bash
   git remote add upstream https://github.com/StuxnetStudios/skynet-lite.git
   ```

## Development Setup

### Environment Setup

1. **Create virtual environment**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   # or
   .venv\Scripts\activate     # Windows
   ```

2. **Install development dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

3. **Install pre-commit hooks**:
   ```bash
   pre-commit install
   ```

4. **Set up Ollama** (for testing):
   ```bash
   ollama serve
   ollama pull mistral
   ```

### Development Dependencies

Create `requirements-dev.txt` if it doesn't exist:
```
# Testing
pytest>=7.4.0
pytest-asyncio>=0.21.0
pytest-cov>=4.1.0
pytest-mock>=3.11.1

# Code Quality
black>=23.0.0
flake8>=7.0.0
mypy>=1.5.0
isort>=5.12.0

# Development Tools
ipython>=8.15.0
pre-commit>=3.4.0
```

## Contributing Guidelines

### Types of Contributions

We welcome various types of contributions:

#### 🐛 Bug Reports
- Use the bug report template
- Include steps to reproduce
- Provide system information
- Include error logs when possible

#### ✨ Feature Requests  
- Use the feature request template
- Explain the use case
- Provide examples if possible
- Consider backward compatibility

#### 📚 Documentation
- Fix typos and improve clarity
- Add examples and tutorials
- Translate documentation
- Improve API documentation

#### 💻 Code Contributions
- Bug fixes
- New features
- Performance improvements
- Test coverage improvements

### Contribution Areas

#### High Priority Areas
- **Model Loaders**: Add support for new AI providers
- **Search Providers**: Integrate additional search engines
- **Web Interface**: UI/UX improvements
- **Testing**: Increase test coverage
- **Documentation**: User guides and examples

#### Core Components to Understand

1. **Main Orchestrator** (`main.py`)
   - Central coordination
   - Async chat handling
   - Error management

2. **Model Loaders** (`loaders/`)
   - AI provider interfaces
   - Fallback mechanisms
   - Configuration handling

3. **Web Interface** (`web/`)
   - Flask application
   - Frontend assets
   - API endpoints

4. **Tools** (`tools/`)
   - Web search integration
   - External service connectors

## Pull Request Process

### Before Starting

1. **Check existing issues** to avoid duplicate work
2. **Open an issue** for major features or changes
3. **Discuss the approach** with maintainers
4. **Create a feature branch** from `main`

### Development Workflow

1. **Create feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/issue-description
   ```

2. **Make your changes**:
   - Follow coding standards
   - Add tests for new functionality
   - Update documentation
   - Ensure all tests pass

3. **Commit your changes**:
   ```bash
   git add .
   git commit -m "feat: add new model loader for XYZ"
   ```

4. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

5. **Create Pull Request**:
   - Use the PR template
   - Link related issues
   - Provide detailed description
   - Include screenshots for UI changes

### Commit Message Format

We use conventional commits:

```
type(scope): description

[optional body]

[optional footer]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Formatting, missing semicolons, etc.
- `refactor`: Code change that neither fixes a bug nor adds a feature
- `test`: Adding missing tests
- `chore`: Changes to build process or auxiliary tools

**Examples:**
```
feat(web): add dark mode toggle
fix(loader): handle timeout errors gracefully
docs(api): update endpoint documentation
test(search): add unit tests for DuckDuckGo provider
```

## Coding Standards

### Python Style Guide

We follow PEP 8 with some modifications:

#### Code Formatting
- **Line length**: 88 characters (Black default)
- **Indentation**: 4 spaces
- **Quotes**: Double quotes for strings
- **Imports**: Use isort for import ordering

#### Type Hints
Always use type hints:
```python
async def process_message(message: str, user_id: Optional[str] = None) -> str:
    """Process a user message and return response."""
    pass
```

#### Async/Await
Use async/await consistently:
```python
# Good
async def fetch_data():
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()

# Bad
def fetch_data():
    return requests.get(url).json()
```

#### Error Handling
Use specific exceptions:
```python
# Good
   # Note: OLLAMA_BASE_URL is deprecated; prefer `OLLAMA_MODEL` and `skynet.config`
   # ollama_base_url: str = field(
   #     metadata={"env": "OLLAMA_BASE_URL", "description": "Ollama server URL"}
   # )
try:
    result = await model.generate(prompt)
except ModelNotAvailableError:
    logger.warning("Model unavailable, trying fallback")
    result = await fallback_model.generate(prompt)
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    raise

# Bad
try:
    result = await model.generate(prompt)
except:
    pass
```

#### Documentation
Use Google-style docstrings:
```python
async def search_web(query: str, max_results: int = 5) -> List[SearchResult]:
    """Search the web for information.
    
    Args:
        query: The search query string
        max_results: Maximum number of results to return
        
    Returns:
        List of search results with title, snippet, and URL
        
    Raises:
        SearchProviderError: If all search providers fail
        NetworkError: If network connectivity issues occur
    """
    pass
```

### Web Development Standards

#### HTML/CSS
- Use semantic HTML5 elements
- Follow responsive design principles
- Ensure accessibility (ARIA labels, alt text)
- Use CSS Grid/Flexbox for layouts

#### JavaScript
- Use modern ES6+ features
- Implement error handling
- Follow progressive enhancement
- Comment complex logic

### Configuration Management

#### Environment Variables
- Use descriptive names
- Provide sensible defaults
- Document all variables
- Use typing for validation

```python
@dataclass
class Config:
    """Application configuration with environment variable support."""
    
    # AI Model Configuration
    ollama_base_url: str = field(
        default="http://localhost:11434",
        metadata={"env": "OLLAMA_BASE_URL", "description": "Ollama server URL"}
    )
```

## Testing

### Test Structure

```
tests/
├── unit/           # Unit tests for individual components
├── integration/    # Integration tests for component interaction
├── e2e/           # End-to-end tests for full workflows
└── fixtures/      # Test data and fixtures
```

### Writing Tests

#### Unit Tests
```python
import pytest
from unittest.mock import Mock, patch
from skynet_lite.loaders.ollama_loader import OllamaLoader

@pytest.mark.asyncio
async def test_ollama_loader_initialization():
    """Test OllamaLoader initializes correctly."""
    loader = OllamaLoader()
    assert loader.base_url == "http://localhost:11434"
    assert loader.model is None

@pytest.mark.asyncio
async def test_ollama_loader_generate_response():
    """Test response generation with mocked Ollama."""
    with patch('aiohttp.ClientSession.post') as mock_post:
        mock_post.return_value.__aenter__.return_value.json.return_value = {
            'response': 'Test response'
        }
        
        loader = OllamaLoader()
        response = await loader.generate("Test prompt")
        assert response == "Test response"
```

#### Integration Tests
```python
@pytest.mark.asyncio
async def test_skynet_lite_with_web_search():
    """Test SkynetLite integrates web search correctly."""
    skynet = SkynetLite()
    await skynet.initialize()
    
    # Test web search trigger
    response = await skynet.chat("What's the latest news?")
    assert "search" in response.lower() or len(response) > 50
```

#### Test Configuration
Use `pytest.ini`:
```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --asyncio-mode=auto
    --cov=skynet_lite
    --cov-report=html
    --cov-report=term-missing
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_main.py

# Run with coverage
pytest --cov=skynet_lite --cov-report=html

# Run only unit tests
pytest tests/unit/

# Run tests matching pattern
pytest -k "test_ollama"
```

## Documentation

### Types of Documentation

#### Code Documentation
- Docstrings for all public functions/classes
- Inline comments for complex logic
- Type hints for all function signatures

#### User Documentation
- User Guide for end users
- API Reference for developers
- Deployment Guide for system administrators

#### Developer Documentation
- Architecture overview
- Contributing guidelines
- Testing procedures

### Documentation Standards

#### Markdown Guidelines
- Use descriptive headers
- Include code examples
- Add table of contents for long documents
- Use proper linking between documents

#### Code Examples
Always include working examples:
```python
# Example: Using Skynet Lite programmatically
from skynet_lite import SkynetLite
import asyncio

async def main():
    skynet = SkynetLite()
    await skynet.initialize()
    
    response = await skynet.chat("Hello, world!")
    print(response)

if __name__ == "__main__":
    asyncio.run(main())
```

### Building Documentation

```bash
# Generate API documentation
python3 -m pydoc -w skynet_lite

# Check documentation links
pytest --doctest-modules skynet_lite/

# Spell check (if available)
cspell "docs/**/*.md"
```

## Issue Reporting

### Bug Reports

Include the following information:

1. **Environment Details**:
   - Operating system
   - Python version
   - Skynet Lite version
   - Ollama version (if applicable)

2. **Steps to Reproduce**:
   - Detailed step-by-step instructions
   - Input data used
   - Expected vs actual behavior

3. **Error Information**:
   - Full error messages
   - Stack traces
   - Log files (if available)

4. **Additional Context**:
   - Screenshots (for UI issues)
   - Configuration details
   - Recent changes to setup

### Feature Requests

Provide the following:

1. **Problem Description**:
   - What problem does this solve?
   - Who would benefit from this feature?

2. **Proposed Solution**:
   - Detailed description of the feature
   - How it should work
   - Alternative approaches considered

3. **Examples**:
   - Use cases
   - Similar features in other tools
   - Mockups or diagrams (if applicable)

## Review Process

### Code Review Checklist

Reviewers will check:

- [ ] Code follows style guidelines
- [ ] Tests are included and passing
- [ ] Documentation is updated
- [ ] No breaking changes (or properly documented)
- [ ] Performance implications considered
- [ ] Security implications reviewed
- [ ] Backward compatibility maintained

### Getting Your PR Reviewed

1. **Self-review first**: Check your own code thoroughly
2. **Keep PRs focused**: One feature/fix per PR
3. **Respond to feedback**: Address reviewer comments promptly
4. **Be patient**: Reviews take time, especially for large changes

### Review Timeline

- **Simple fixes**: 1-2 days
- **New features**: 3-7 days
- **Major changes**: 1-2 weeks

## Release Process

### Versioning

We follow [Semantic Versioning](https://semver.org/):
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Checklist

- [ ] All tests passing
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Version numbers updated
- [ ] Security review completed
- [ ] Performance testing done

## Getting Help

### Communication Channels

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and ideas
- **Pull Request Comments**: Code-specific discussions

### Mentorship

New contributors can:
- Look for "good first issue" labels
- Ask for guidance in issues
- Request code review help
- Join pair programming sessions (when available)

### Resources

- [Python Async Programming Guide](https://docs.python.org/3/library/asyncio.html)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Ollama API Documentation](https://github.com/ollama/ollama/blob/main/docs/api.md)
- [pytest Documentation](https://docs.pytest.org/)

Thank you for contributing to Skynet Lite! Your contributions help make privacy-first AI accessible to everyone.
