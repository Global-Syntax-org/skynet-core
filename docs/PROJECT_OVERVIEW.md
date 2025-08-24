# Skynet Core - Project Overview

## Current Status
Skynet Core is a production-ready cloud-first AI chatbot system that combines multiple enterprise AI providers with advanced web search capabilities, featuring both console and web interfaces. Designed for enterprise deployment, scalable architecture, and intelligent multi-model AI processing.

## Key Achievements
- ✅ Cloud-first multi-model support (OpenAI, Claude, Gemini, GitHub Copilot, Microsoft Copilot)
- ✅ Enterprise-grade web UI with responsive Flask interface
- ✅ Advanced web search integration with multiple providers
- ✅ Persistent conversation memory with enterprise features
- ✅ Comprehensive test suite and diagnostic tools
- ✅ Docker-ready cloud deployment configuration
- ✅ Production-ready scaling and monitoring

## Architecture Overview

### System Architecture
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Client    │◄──►│   Flask App     │◄──►│  Skynet Core    │
│  (Browser UI)   │    │  (Web Server)   │    │ (AI Orchestrator│
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                       ▲
                                                       │
         ┌─────────────────┬─────────────────┬─────────────────┐
         │                 │                 │                 │
         ▼                 ▼                 ▼                 ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│ Cloud AI Models │ │   Web Search    │ │ Memory Manager  │ │   Config Mgmt   │
│ (OpenAI/Claude) │ │ (DDG/Azure/etc) │ │ (Conversation)  │ │ (Multi-source)  │
└─────────────────┘ └─────────────────┘ └─────────────────┘ └─────────────────┘
```

### Core Components

#### 1. Main Orchestrator (`main.py`)
- **Purpose**: Central chat loop and component coordination
- **Pattern**: Async/await with dependency injection
- **Key Features**:
  - Multi-model loader management with automatic fallback
  - Query classification (local vs web search)
  - Context-aware conversation management
  - Graceful error handling and recovery mechanisms
  - Support for both programmatic and interactive use

```python
class SkynetLite:
    """Main orchestrator following modular architecture"""
    
    def __init__(self):
        self.config = Config()                      # Configuration management
        self.loader_manager = LoaderManager()       # Multi-model support
        self.memory_manager = MemoryManager()       # Conversation memory
        self.search_tool = None                     # Web search (lazy init)
    
    async def initialize(self) -> bool:
        """Async initialization with dependency checking"""
        
    async def chat(self, user_message: str) -> str:
        """Single message processing for web API"""
        
    async def chat_loop(self) -> None:
        """Interactive console loop"""
```

#### 2. Web Interface (`web/app.py`)
- **Purpose**: Flask-based web UI for browser interaction with multi-model AI support
- **Pattern**: RESTful API with session management and async processing
- **Key Features**:
  - Responsive design with mobile support
  - Real-time chat interface with model selection
  - Session persistence and conversation memory
  - Background async processing for multiple AI providers
  - Health check and diagnostics endpoints
  - Auto-fallback between OpenAI, Claude, GitHub Copilot, Microsoft Copilot, and Gemini

```python
@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat messages via HTTP POST"""
    
@app.route('/clear', methods=['POST']) 
def clear_session():
    """Clear conversation history"""
    
@app.route('/health')
def health():
    """System health check"""
```

#### 3. Model Loader Management (`loaders/`)
- **Purpose**: Unified interface for multiple AI model providers
- **Pattern**: Strategy pattern with automatic fallback
- **Supported Models**:
  - **OpenAI** (GPT models) - Primary choice for reliability
  - **Claude** (Anthropic) - Advanced reasoning and analysis
  - **GitHub Copilot** - Development and coding assistant
  - **Microsoft Copilot** - Enterprise AI assistant
  - **Gemini** (Google) - Multimodal AI capabilities

```python
class LoaderManager:
    """Manages different model loaders with fallback support"""
    
    async def initialize(self):
        """Try cloud AI loaders in priority order"""
        # 1. OpenAI (if API key available)
        # 2. Claude (if API key available)
        # 3. GitHub Copilot (if token available)
        # 4. Microsoft Copilot (if API key available)
        # 5. Gemini (if API key available)
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

#### 3. Cloud AI Interface (`loaders/`)
- **Purpose**: Async interface to cloud AI providers with resource management
- **Pattern**: Async context manager with proper cleanup and fallback
- **Features**:
  - Multi-provider support with intelligent routing
  - Rate limiting and quota management
  - Error handling with automatic retries
  - Resource cleanup and connection pooling

```python
class CloudAILoader:
    """Async cloud AI interface with resource management"""
    
    async def ensure_model_available(self, model_name: str) -> bool:
        """Check model availability and access permissions"""
        
    async def generate_completion(self, prompt: str, model: str) -> str:
        """Generate completion with error handling and retries"""
        
    async def close(self) -> None:
        """Clean up async resources and connections"""
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
Cloud Query ←→ Web Search Query ←→ Context Memory
    ↓               ↓                    ↓
Cloud AI API ←→ DuckDuckGo Search ←→ Memory Manager
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
# Primary AI Provider (Choose one)
export OPENAI_API_KEY="<your_openai_api_key>"
export OPENAI_MODEL="gpt-3.5-turbo"

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
openai:
  api_key: "your_openai_api_key"
  model: "gpt-3.5-turbo"

search:
  provider: "duckduckgo"
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

### Cloud Development
- All AI processing happens in the cloud via secure APIs
- No local dependencies or complex installations
- Configuration through environment variables or YAML
- Support for multiple concurrent API providers

### Production Deployment
- Docker containerization for cloud-native environments
- Volume mounts for conversation history persistence
- Health checks for API connectivity and rate limits
- Graceful shutdown and failover handling
- Auto-scaling support for enterprise workloads

### Enterprise Integration
- Multi-cloud deployment support
- Enterprise authentication and authorization
- Advanced monitoring and logging capabilities
- Cost optimization and usage tracking

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