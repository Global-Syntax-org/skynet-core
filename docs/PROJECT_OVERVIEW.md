# Skynet Lite - Project Overview

## Current Status
Skynet Lite is a modular AI chatbot system that combines local LLM processing with web search capabilities, designed for robotics integration and privacy-first operation.

## Architecture Overview

### Core Components

#### 1. Main Orchestrator (`main.py`)
- **Purpose**: Central chat loop and component coordination
- **Pattern**: Async/await with dependency injection
- **Key Features**:
  - Query classification (local vs web search)
  - Context-aware conversation management
  - Graceful error handling and fallback mechanisms

```python
class SkynetLite:
    """Main orchestrator following modular architecture"""
    
    def __init__(self):
        self.config = Config()                    # Configuration management
        self.kernel = sk.Kernel()                 # Semantic Kernel integration
        self.model_loader = OllamaModelLoader()   # Local LLM interface
        self.search_tool = None                   # Web search (lazy initialization)
        self.memory_manager = ChatMemoryManager() # Conversation memory
    
    async def initialize(self) -> bool:
        """Async initialization with dependency checking"""
        
    async def chat_loop(self) -> None:
        """Main interaction loop with error handling"""
```

#### 2. Configuration Management (`config.py`)
- **Purpose**: Multi-source configuration with environment override
- **Pattern**: Dataclass with validation and type hints
- **Sources**: Default values → Environment variables → YAML files

```python
@dataclass
class Config:
    """Configuration with multiple source support"""
    
    # Ollama Configuration
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "mistral"
    
    # Search Configuration
    search_provider: str = "duckduckgo"  # Updated from Bing
    search_max_results: int = 3
    
    # Memory Configuration
    memory_max_turns: int = 10
    memory_file: str = "conversation_history.json"
```

#### 3. Model Interface (`models/loader.py`)
- **Purpose**: Async interface to Ollama with resource management
- **Pattern**: Async context manager with proper cleanup
- **Features**:
  - Model availability checking
  - Completion generation with error handling
  - Resource cleanup and connection management

```python
class OllamaModelLoader:
    """Async Ollama interface with resource management"""
    
    async def ensure_model_available(self, model_name: str) -> bool:
        """Check and download model if needed"""
        
    async def generate_completion(self, prompt: str, model: str) -> str:
        """Generate completion with error handling"""
        
    async def close(self) -> None:
        """Clean up async resources"""
```

#### 4. Web Search Integration (`tools/web_search.py`)
- **Purpose**: Privacy-focused web search with DuckDuckGo
- **Pattern**: Async context manager with session management
- **Migration**: Moved from Bing Search API to DuckDuckGo (no API keys)

```python
class DuckDuckGoSearchTool:
    """Privacy-focused web search integration"""
    
    async def __aenter__(self):
        """Async context manager entry"""
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Resource cleanup"""
        
    async def search(self, query: str, max_results: int = 5) -> List[Dict]:
        """Search with structured results"""
        
    async def search_and_summarize(self, query: str, max_results: int = 3) -> str:
        """Search and format for LLM consumption"""
```

#### 5. Memory Management (`plugins/memory.py`)
- **Purpose**: Conversation context and history management
- **Pattern**: Plugin architecture with configurable retention
- **Features**:
  - Conversation history tracking
  - Context-aware memory retrieval
  - Configurable memory limits

```python
class ChatMemoryManager:
    """Conversation memory with configurable retention"""
    
    def add_user_message(self, message: str) -> None:
        """Add user message to history"""
        
    def add_assistant_message(self, message: str) -> None:
        """Add assistant response to history"""
        
    def get_conversation_history(self, max_turns: int = None) -> str:
        """Get formatted conversation context"""
```

## Data Flow Architecture

```
User Input → Query Classification → Route Decision
                                         ↓
Local Query ←→ Web Search Query ←→ Context Memory
    ↓               ↓                    ↓
Ollama LLM ←→ DuckDuckGo Search ←→ Memory Manager
    ↓               ↓                    ↓
Response Generation ←→ Context Update ←→ User Output
```

## Plugin System Architecture

### Plugin Protocol
```python
class PluginProtocol(Protocol):
    """Standard interface for all plugins"""
    
    async def initialize(self) -> bool: ...
    async def process(self, input_data: Any) -> Any: ...
    async def close(self) -> None: ...
```

### Plugin Integration Pattern
```python
# Plugin loading in main orchestrator
async def initialize(self) -> bool:
    """Initialize with plugin discovery"""
    
    # Core plugins
    self.search_tool = await create_search_tool(self.config.search_provider)
    self.memory_manager = ChatMemoryManager(self.config)
    
    # Dynamic plugin loading
    for plugin_name in self.config.enabled_plugins:
        plugin = await self.load_plugin(plugin_name)
        self.plugins[plugin_name] = plugin
```

## Development Patterns

### Async/Await Guidelines
- All I/O operations use async/await
- Proper resource management with context managers
- Error handling with specific exception types
- Graceful degradation when services unavailable

### Type Hints and Documentation
```python
from typing import Dict, List, Optional, Any, Protocol
import asyncio
import aiohttp

async def search_and_process(
    query: str,
    max_results: int = 3,
    timeout: float = 30.0
) -> Optional[str]:
    """
    Search query and process results with LLM
    
    Args:
        query: Search query string
        max_results: Maximum search results to process
        timeout: Request timeout in seconds
        
    Returns:
        Processed response or None if failed
        
    Raises:
        SearchError: When search operation fails
        LLMError: When LLM processing fails
    """
```

### Error Handling Patterns
```python
# Specific exception handling
try:
    result = await operation()
except ConnectionError as e:
    logger.error(f"Connection failed: {e}")
    return fallback_result()
except ValidationError as e:
    logger.error(f"Invalid input: {e}")
    return error_response()
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    return generic_error_response()
```

## Testing Architecture

### Test Structure
```
tests/
├── conftest.py          # Shared fixtures and configuration
├── test_main.py         # Integration tests for main orchestrator
├── test_config.py       # Configuration management tests
├── test_models.py       # Model loader unit tests
├── test_web_search.py   # Web search integration tests
└── test_memory.py       # Memory management tests
```

### Mock Patterns
```python
@pytest.fixture
async def mock_ollama_client():
    """Mock Ollama client for testing"""
    client = AsyncMock()
    client.chat = AsyncMock(return_value={
        'message': {'content': 'Test response'}
    })
    return client

@pytest.mark.asyncio
async def test_completion_generation(mock_ollama_client):
    """Test completion generation with mocked client"""
    loader = OllamaModelLoader()
    
    with patch('ollama.AsyncClient', return_value=mock_ollama_client):
        result = await loader.generate_completion("test prompt", "mistral")
        assert result == "Test response"
```

## Configuration Management

### Environment Variables
```bash
# Ollama Configuration
export OLLAMA_BASE_URL="http://localhost:11434"
export OLLAMA_MODEL="mistral"

# Search Configuration
export SEARCH_PROVIDER="duckduckgo"
export SEARCH_MAX_RESULTS="3"

# Memory Configuration
export MEMORY_MAX_TURNS="10"
export MEMORY_FILE="conversation_history.json"
```

### YAML Configuration
```yaml
# config.yaml
ollama:
  base_url: "http://localhost:11434"
  model: "mistral"

search:
  provider: "duckduckgo"  # or "duckduckgo_instant"
  max_results: 3

memory:
  max_turns: 10
  file: "conversation_history.json"

plugins:
  enabled:
    - "web_search"
    - "memory"
```

## Deployment Considerations

### Local Development
- All services run locally (Ollama, Python application)
- No external API dependencies (DuckDuckGo doesn't require keys)
- Configuration through environment variables or YAML

### Production Deployment
- Docker containerization for consistent environments
- Volume mounts for conversation history persistence
- Health checks for Ollama service availability
- Graceful shutdown handling

### Robotics Integration
- ROS node compatibility patterns
- Webots controller integration examples
- Real-time response optimization
- Resource constraint handling

## Recent Changes

### Migration from Bing Search to DuckDuckGo
- **Reason**: Bing Search API retirement and privacy concerns
- **Benefits**: No API keys, better privacy, no rate limits
- **Implementation**: Async HTML scraping + Instant Answer API
- **Configuration**: Updated search provider options

### Enhanced Plugin Architecture
- **Protocol-based design**: Standardized plugin interface
- **Async context managers**: Proper resource management
- **Dynamic loading**: Runtime plugin discovery and loading
- **Error isolation**: Plugin failures don't crash main system

This documentation reflects the current modular architecture and development patterns used throughout Skynet Lite, providing a comprehensive guide for developers working with the system.