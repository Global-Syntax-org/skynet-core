# 🤖 Skynet Lite

A lightweight, local AI chatbot powered by Ollama and enhanced with web search capabilities. Built for robotics simulation, swarm intelligence, and general AI assistance with privacy-first local LLM execution.

## ✨ Features

- **🧠 Local AI Processing** - Powered by Ollama with Mistral 7B model
- **🔍 Web Search Integration** - Bing Search API for real-time information
- **💾 Conversation Memory** - Persistent chat history and context management
- **🔌 Plugin Architecture** - Modular system with Semantic Kernel integration
- **🛡️ Privacy-First** - All AI processing happens locally on your machine
- **🚀 Async Architecture** - High-performance async/await implementation
- **🎯 Robotics Ready** - Designed for integration with ROS and Webots

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- [Ollama](https://ollama.com/download) installed and running
- Optional: Bing Search API key for web search

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/skynet-lite.git
   cd skynet-lite
   ```

2. **Run the setup script**
   ```bash
   python setup.py
   ```

3. **Start Ollama and pull the Mistral model**
   ```bash
   ollama serve
   ollama pull mistral
   ```

4. **Configure (Optional)**
   - Set `BING_API_KEY` environment variable for web search
   - Or edit `config.yaml` after first run

5. **Launch Skynet Lite**
   ```bash
   python main.py
   ```

## 🏗️ Architecture

```
skynet-lite/
├── main.py              # Entry point and chat orchestration
├── config.py            # Configuration management
├── setup.py             # Setup and dependency verification
├── models/
│   └── loader.py        # Ollama model interface
├── tools/
│   └── web_search.py    # Bing Search integration
└── plugins/
    └── memory.py        # Conversation memory management
```

## 🔧 Configuration

Skynet Lite supports multiple configuration methods:

### Environment Variables
```bash
export OLLAMA_BASE_URL="http://localhost:11434"
export OLLAMA_MODEL="mistral"
export BING_API_KEY="your-api-key-here"
```

### Configuration File
Create or edit `config.yaml`:
```yaml
ollama:
  base_url: "http://localhost:11434"
  model: "mistral"
  
bing:
  api_key: "your-api-key-here"
  
memory:
  max_turns: 10
```

## 💬 Usage Examples

### Basic Chat
```
You: Hello, what can you help me with?
🤖 Skynet: I'm Skynet Lite, your local AI assistant! I can help with...
```

### Web Search Queries
```
You: What's the latest news about AI?
🔍 Searching the web...
🤖 Skynet: Based on recent search results, here are the latest AI developments...
```

### Commands
- `quit`, `exit`, `bye` - Exit the chat
- Web search triggers: "latest", "recent", "news", "current", "weather", etc.

## 🧩 Plugin Development

Skynet Lite uses a modular plugin architecture. Create new plugins by extending the base patterns:

```python
class CustomPlugin:
    """Custom plugin following Skynet Lite patterns"""
    
    def __init__(self, config: Config):
        self.config = config
    
    async def initialize(self) -> bool:
        """Initialize plugin resources"""
        pass
    
    async def process(self, query: str) -> str:
        """Process user query"""
        pass
```

## 🤝 Integration

### ROS Integration
```python
# Example ROS node integration
import rospy
from skynet_lite import SkynetLite

class SkynetRosNode:
    def __init__(self):
        self.skynet = SkynetLite()
        rospy.init_node('skynet_lite')
```

### Webots Integration
```python
# Example Webots controller integration
from controller import Robot
from skynet_lite import SkynetLite

class SkynetController(Robot):
    def __init__(self):
        super().__init__()
        self.skynet = SkynetLite()
```

## 🧪 Testing

Run the test suite:
```bash
python -m pytest tests/ -v
```

Run with coverage:
```bash
python -m pytest tests/ --cov=. --cov-report=html
```

## 📦 Dependencies

- **semantic-kernel** - AI orchestration framework
- **ollama** - Local LLM integration
- **aiohttp/httpx** - Async HTTP clients
- **pyyaml** - Configuration management
- **rich** - Enhanced terminal output

## 🛠️ Development

### Code Style
- Follow PEP 8 with Black formatting
- Use type hints throughout
- Implement async/await for I/O operations
- Add docstrings to all classes and methods

### Contributing
1. Fork the repository
2. Create a feature branch
3. Follow the coding guidelines
4. Add tests for new functionality
5. Submit a pull request

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Ollama](https://ollama.com/) for local LLM execution
- [Microsoft Semantic Kernel](https://github.com/microsoft/semantic-kernel) for AI orchestration
- [Mistral AI](https://mistral.ai/) for the language model

## 🔮 Roadmap

- [ ] Voice interface integration
- [ ] Multi-model support (GPT-4, Claude, etc.)
- [ ] Advanced robotics control plugins
- [ ] Swarm intelligence coordination
- [ ] Custom training pipeline
- [ ] Web UI interface
- [ ] Docker containerization

---

**Made with ❤️ for the robotics and AI community**
