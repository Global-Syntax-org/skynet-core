<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# Skynet Lite - GitHub Copilot Instructions

This is a Python-based local AI chatbot project that integrates Ollama (local LLM), Bing Search, and Semantic Kernel for conversational AI with web access capabilities.

## Project Context

- **Main Framework**: Semantic Kernel for AI orchestration
- **Local LLM**: Ollama with Mistral 7B model
- **Web Search**: Bing Search API integration
- **Architecture**: Modular plugin-based system
- **Target Use**: Robotics simulation, swarm intelligence, and general AI assistance

## Code Style Guidelines

- Use async/await patterns for all I/O operations
- Follow Python type hints throughout the codebase
- Implement proper error handling with specific exception types
- Use descriptive variable and function names
- Add docstrings to all classes and methods
- Structure code in modules: models/, tools/, plugins/

## Key Components

1. **main.py** - Entry point and chat orchestration
2. **skynet/config.py** - Configuration management with environment variable support
3. **models/loader.py** - Ollama model interface and management
4. **tools/web_search.py** - Bing Search API integration
5. **plugins/memory.py** - Conversation history and context management

## Development Patterns

- Use dependency injection for service configuration
- Implement async context managers for resource cleanup
- Create modular plugins that can be easily added/removed
- Support both local-only and web-enhanced modes
- Design for integration with robotics frameworks (ROS, Webots)

## Testing Considerations

- Mock external API calls (Ollama, Bing Search)
- Test configuration loading from various sources
- Validate conversation memory management
- Ensure graceful degradation when services are unavailable

When suggesting code improvements or new features, consider the modular architecture and maintain compatibility with the existing plugin system.
