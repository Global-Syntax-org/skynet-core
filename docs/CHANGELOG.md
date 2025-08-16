# Skynet Lite Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Voice interface integration
- Docker containerization 
- WebSocket support for real-time chat
- Plugin marketplace
- API authentication and rate limiting

## [1.4.1] - 2025-08-16

### Changed
- Export tooling: SQL scripts and CLI exporter under `scripts/`
- UI: "New Chat" button renamed to "Clear" for clarity
- Database: Normalized DB path to use single `web/skynet_lite.db` file for all operations
- Documentation: Removed duplicate sections from README
- Removed public forgot-password route; reset token flow retained

### Added
- Conversation export tools with test harness
- Robust SQL export with Python fallback when sqlite3 CLI unavailable

### Fixed
- File permissions: `scripts/` directory and executable files properly configured
- Database path consistency: AuthManager and web app now use same DB file


## [1.2.0] - 2025-08-15

### Added
- **Web User Interface**
  - Complete Flask-based web UI with responsive design
  - Real-time chat interface with message history
  - Session management and conversation persistence
  - Mobile-friendly responsive design
  - New Chat functionality to clear conversation history

- **Multi-Model Support**
  - Automatic fallback system for multiple AI providers
  - Support for OpenAI GPT models
  - Support for Anthropic Claude models  
  - Support for Google Gemini models
  - Support for GitHub Copilot integration
  - Intelligent model loader management with priority ordering

- **Enhanced Search Integration**
  - DuckDuckGo search as primary provider (no API key required)
  - Azure Cognitive Services Bing Search integration
  - Google Custom Search API support
  - Automatic search provider fallback

- **Development and Diagnostic Tools**
  - Comprehensive diagnostic script (`web/diagnose.py`)
  - Web interface test suite (`web/test_web.py`)
  - Health check endpoints for monitoring
  - Enhanced error reporting and logging

- **Documentation**
  - Complete User Guide for end users
  - Comprehensive Deployment Guide for production
  - Updated API Reference with web endpoints
  - Enhanced PROJECT_OVERVIEW with current architecture

### Changed
- **Improved Configuration Management**
  - Multi-source configuration (environment variables, YAML files)
  - Better validation and type checking
  - Support for production and development environments

- **Enhanced Memory Management**
  - More intelligent conversation context handling
  - Configurable memory limits
  - Session-based memory for web interface
  - Persistent memory for console interface

- **Better Error Handling**
  - Graceful fallback between model providers
  - Improved error messages and user feedback
  - Automatic retry logic for transient failures
  - Better logging and debugging capabilities

### Fixed
- Async/await pattern implementation throughout codebase
- Memory leaks in long-running conversations
- Race conditions in web interface
- Model loading timeout issues

## [1.0.0] - 2025-01-XX

### Added
- **Core Architecture**
  - Modular plugin-based system with `models/`, `tools/`, `plugins/` structure
  - Async/await patterns throughout the codebase
  - Dependency injection for service configuration
  - Comprehensive type hints and documentation

- **Local LLM Integration**
  - Ollama integration with Mistral 7B model
  - Async model loading and management
  - Completion generation with error handling
  - Resource cleanup and connection management

- **Web Search Integration**
  - DuckDuckGo search integration (privacy-focused)
  - No API keys required
  - HTML scraping and Instant Answer API support
  - Search result formatting for LLM consumption

- **Configuration Management**
  - Multi-source configuration support
  - Environment variable overrides
  - YAML configuration file support
  - Default value management

- **Conversation Memory**
  - Persistent conversation history
  - Configurable memory limits
  - Context-aware response generation
  - File-based persistence

- **Development Infrastructure**
  - Comprehensive test suite with pytest
  - Pre-commit hooks for code quality
  - GitHub Actions CI/CD pipeline
  - Development setup scripts

### Changed
- **Migration from Bing Search to DuckDuckGo**
  - Removed API key requirements
  - Enhanced privacy protection
  - Eliminated rate limiting issues
  - Improved reliability for continuous operation

### Technical Details

#### Architecture
```
skynet-lite/
├── main.py              # Entry point and chat orchestration
├── config.py            # Configuration management
├── requirements.txt     # Dependencies
├── models/
│   ├── __init__.py     # Package initialization
│   └── loader.py       # Ollama model interface
├── tools/
│   └── web_search.py   # DuckDuckGo integration
└── plugins/
    └── memory.py       # Conversation memory
```

#### Key Features
- **Async/Await Patterns**: All I/O operations use async/await
- **Type Safety**: Comprehensive type hints with mypy validation
- **Error Handling**: Specific exception types with graceful degradation
- **Resource Management**: Proper cleanup with async context managers
- **Plugin System**: Protocol-based plugin architecture
- **Configuration**: Environment variables + YAML file support

#### Dependencies
- `semantic-kernel>=1.1.0,<2.0.0` - AI orchestration framework
- `ollama>=0.1.7` - Local LLM integration
- `aiohttp>=3.9.0` - Async HTTP client for web search
- `pyyaml>=6.0.1` - Configuration file parsing
- `rich>=13.7.1` - Enhanced terminal output

### Breaking Changes
- **Bing Search API Removal**: Replaced with DuckDuckGo (no API keys needed)
- **Configuration Schema**: Updated to support new search provider options
- **Environment Variables**: `BING_API_KEY` removed, `SEARCH_PROVIDER` added

### Migration Guide

#### From Bing Search to DuckDuckGo
1. Remove `BING_API_KEY` environment variable
2. Update configuration:
   ```yaml
   # Old
   bing:
     api_key: "your-api-key"
   
   # New
   search:
     provider: "duckduckgo"
     max_results: 3
   ```
3. No code changes required - interface remains the same

#### Plugin Development
```python
# New plugin protocol
class PluginProtocol(Protocol):
    async def initialize(self) -> bool: ...
    async def process(self, input_data: Any) -> Any: ...
    async def close(self) -> None: ...
```

### Documentation
- **README.md**: Comprehensive project documentation
- **API Reference**: Complete API documentation
- **Architecture Guide**: Detailed architecture explanation
- **Development Guide**: Development setup and guidelines
- **Plugin Development**: Plugin creation documentation

### Performance Improvements
- **Async Processing**: Non-blocking I/O operations
- **Connection Pooling**: Efficient HTTP connection management
- **Memory Optimization**: Configurable conversation history limits
- **Resource Cleanup**: Proper async resource management

### Security Enhancements
- **Privacy-First**: Local LLM processing with no data sharing
- **No API Keys**: DuckDuckGo integration without authentication
- **Data Locality**: Conversation history stored locally
- **Secure Defaults**: Conservative configuration defaults

### Robotics Integration
- **ROS Compatibility**: Designed for ROS node integration
- **Webots Support**: Controller integration patterns
- **Real-time Processing**: Optimized for robotics response times
- **Resource Constraints**: Efficient resource usage

### Quality Assurance
- **Test Coverage**: Comprehensive test suite with async patterns
- **Code Quality**: Black formatting, flake8 linting, mypy type checking
- **CI/CD Pipeline**: Automated testing and quality checks
- **Documentation**: Comprehensive API and architecture documentation

This release establishes Skynet Lite as a robust, modular AI chatbot system with strong privacy protections, comprehensive testing, and robotics integration capabilities.