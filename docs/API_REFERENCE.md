# Skynet Lite API Reference

## Core Classes

### SkynetLite

Main orchestrator class that coordinates all components.

```python
class SkynetLite:
    """Main Skynet Lite chatbot orchestrator"""
    
    def __init__(self) -> None:
        """Initialize with default configuration"""
    
    async def initialize(self) -> bool:
        """Initialize all components
        
        Returns:
            True if initialization successful, False otherwise
        """
    
    async def chat_loop(self) -> None:
        """Main chat interaction loop"""
    
    async def _needs_web_search(self, query: str) -> bool:
        """Determine if query requires web search
        
        Args:
            query: User query string
            
        Returns:
            True if web search needed, False for local processing
        """
    
    async def _handle_local_query(self, query: str) -> str:
        """Handle query using local LLM only
        
        Args:
            query: User query string
            
        Returns:
            Generated response from local LLM
        """
    
    async def _handle_web_search_query(self, query: str) -> str:
        """Handle query requiring web search
        
        Args:
            query: User query string
            
        Returns:
            Response based on web search results and LLM processing
        """
```

### Config

Configuration management with multi-source support.

```python
@dataclass
class Config:
    """Configuration class with environment and file support"""
    
    # Ollama Configuration
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "mistral"
    
    # Search Configuration
    search_provider: str = "duckduckgo"
    search_max_results: int = 3
    
    # Memory Configuration
    memory_max_turns: int = 10
    memory_file: str = "conversation_history.json"
    
    def __init__(self) -> None:
        """Initialize with environment and file overrides"""
    
    def create_default_config_file(self) -> None:
        """Create default config.yaml file"""
```

### OllamaModelLoader

Async interface to Ollama with resource management.

```python
class OllamaModelLoader:
    """Async Ollama model interface"""
    
    def __init__(self) -> None:
        """Initialize loader"""
    
    async def ensure_model_available(self, model_name: str) -> bool:
        """Check if model is available, download if needed
        
        Args:
            model_name: Name of the Ollama model
            
        Returns:
            True if model available, False otherwise
        """
    
    async def generate_completion(
        self, 
        prompt: str, 
        model: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None
    ) -> Optional[str]:
        """Generate completion from prompt
        
        Args:
            prompt: Input prompt for the model
            model: Model name to use
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            
        Returns:
            Generated text or None if failed
        """
    
    async def close(self) -> None:
        """Close async resources"""
```

### DuckDuckGoSearchTool

Privacy-focused web search integration.

```python
class DuckDuckGoSearchTool:
    """DuckDuckGo search integration"""
    
    def __init__(self) -> None:
        """Initialize search tool"""
    
    async def __aenter__(self):
        """Async context manager entry"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
    
    async def search(
        self, 
        query: str, 
        max_results: int = 5
    ) -> List[Dict[str, Any]]:
        """Search DuckDuckGo
        
        Args:
            query: Search query string
            max_results: Maximum results to return
            
        Returns:
            List of search result dictionaries
        """
    
    async def search_and_summarize(
        self, 
        query: str, 
        max_results: int = 3
    ) -> str:
        """Search and format for LLM consumption
        
        Args:
            query: Search query
            max_results: Maximum results to include
            
        Returns:
            Formatted search results summary
        """
    
    async def search_recent_news(
        self, 
        topic: str, 
        max_results: int = 3
    ) -> str:
        """Search for recent news
        
        Args:
            topic: News topic to search
            max_results: Maximum results
            
        Returns:
            Recent news summary
        """
```

### DuckDuckGoInstantAnswerTool

Instant answer API integration.

```python
class DuckDuckGoInstantAnswerTool:
    """DuckDuckGo Instant Answer API"""
    
    async def get_instant_answer(self, query: str) -> Optional[Dict[str, Any]]:
        """Get instant answer
        
        Args:
            query: Query string
            
        Returns:
            Instant answer data or None
        """
```

### ChatMemoryManager

Conversation memory management.

```python
class ChatMemoryManager:
    """Conversation memory manager"""
    
    def __init__(self, max_turns: int = 10, memory_file: str = "conversation_history.json"):
        """Initialize memory manager
        
        Args:
            max_turns: Maximum conversation turns to remember
            memory_file: File to persist conversation history
        """
    
    def add_user_message(self, message: str) -> None:
        """Add user message to history
        
        Args:
            message: User message text
        """
    
    def add_assistant_message(self, message: str) -> None:
        """Add assistant response to history
        
        Args:
            message: Assistant response text
        """
    
    def get_conversation_history(self, max_turns: Optional[int] = None) -> str:
        """Get formatted conversation history
        
        Args:
            max_turns: Maximum turns to include
            
        Returns:
            Formatted conversation context
        """
    
    def clear_history(self) -> None:
        """Clear conversation history"""
    
    def save_to_file(self) -> None:
        """Save history to file"""
    
    def load_from_file(self) -> None:
        """Load history from file"""
```

## Factory Functions

### create_search_tool

Factory function for search tool creation.

```python
async def create_search_tool(use_instant_answers: bool = False) -> Any:
    """Create appropriate DuckDuckGo search tool
    
    Args:
        use_instant_answers: Whether to use instant answer API only
        
    Returns:
        Configured search tool instance
    """
```

## Plugin Protocol

### PluginProtocol

Standard interface for all plugins.

```python
class PluginProtocol(Protocol):
    """Protocol that all plugins should implement"""
    
    async def initialize(self) -> bool:
        """Initialize plugin resources
        
        Returns:
            True if successful, False otherwise
        """
    
    async def process(self, input_data: Any) -> Any:
        """Process input data
        
        Args:
            input_data: Input to process
            
        Returns:
            Processed result
        """
    
    async def close(self) -> None:
        """Clean up plugin resources"""
```

## Error Handling

### Custom Exceptions

```python
class SkynetLiteError(Exception):
    """Base exception for Skynet Lite"""
    pass

class ConfigurationError(SkynetLiteError):
    """Configuration-related errors"""
    pass

class ModelError(SkynetLiteError):
    """Model loading/processing errors"""
    pass

class SearchError(SkynetLiteError):
    """Search-related errors"""
    pass

class MemoryError(SkynetLiteError):
    """Memory management errors"""
    pass
```

## Configuration Options

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OLLAMA_BASE_URL` | Ollama server URL | `http://localhost:11434` |
| `OLLAMA_MODEL` | Model name to use | `mistral` |
| `SEARCH_PROVIDER` | Search provider | `duckduckgo` |
| `SEARCH_MAX_RESULTS` | Max search results | `3` |
| `MEMORY_MAX_TURNS` | Max conversation turns | `10` |
| `MEMORY_FILE` | Memory persistence file | `conversation_history.json` |

### YAML Configuration Schema

```yaml
ollama:
  base_url: string          # Ollama server URL
  model: string             # Model name

search:
  provider: string          # "duckduckgo" or "duckduckgo_instant"
  max_results: integer      # Maximum search results

memory:
  max_turns: integer        # Maximum conversation turns
  file: string              # Persistence file path

plugins:
  enabled: list[string]     # List of enabled plugin names
```

## Usage Examples

### Basic Usage

```python
import asyncio
from main import SkynetLite

async def main():
    """Basic usage example"""
    chatbot = SkynetLite()
    
    if await chatbot.initialize():
        await chatbot.chat_loop()
    else:
        print("Failed to initialize")

if __name__ == "__main__":
    asyncio.run(main())
```

### Custom Configuration

```python
from config import Config
from main import SkynetLite

# Custom configuration
config = Config()
config.ollama_model = "llama2"
config.search_max_results = 5

chatbot = SkynetLite()
chatbot.config = config
```

### Plugin Development

```python
from typing import Any
from config import Config

class CustomPlugin:
    """Example custom plugin"""
    
    def __init__(self, config: Config):
        self.config = config
        self.initialized = False
    
    async def initialize(self) -> bool:
        """Initialize plugin"""
        try:
            # Plugin initialization logic
            self.initialized = True
            return True
        except Exception as e:
            print(f"Plugin initialization failed: {e}")
            return False
    
    async def process(self, input_data: Any) -> Any:
        """Process input"""
        if not self.initialized:
            await self.initialize()
        
        # Plugin processing logic
        return f"Processed: {input_data}"
    
    async def close(self) -> None:
        """Cleanup resources"""
        self.initialized = False
```

This API reference provides comprehensive documentation for all major components and interfaces in Skynet Lite, following the project's modular architecture and async patterns.