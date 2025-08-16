# 🤖 Skynet Lite

- **Current Version**: 1.4.1

A lightweight, local AI chatbot powered by Ollama and enhanced with web search capabilities. Built for robotics simulation, swarm intelligence, and general AI assistance with privacy-first local LLM execution.

## ✨ Features

- **🧠 Local AI Processing** - Powered by Ollama with Mistral 7B model
- **🔍 Web Search Integration** - DuckDuckGo by default, with optional Azure Search and Google Custom Search providers
- **💾 Conversation Memory** - Persistent chat history and context management
- **🌐 Web Interface** - Clean, responsive Flask-based web UI alongside console interface
- **🔌 Plugin Architecture** - Modular system with Semantic Kernel integration
- **🛡️ Privacy-First** - All AI processing happens locally on your machine
- **🚀 Async Architecture** - High-performance async/await implementation
- **🎯 Robotics Ready** - Designed for integration with ROS and Webots
- **🔄 Multi-Model Support** - Fallback support for OpenAI, Claude, Gemini, and GitHub Copilot
- **🛠️ Development Tools** - Diagnostic utilities and test scripts included

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- [Ollama](https://ollama.com/download) installed and running

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/StuxnetStudios/skynet-lite.git
   cd skynet-lite
   ```

2. **Run the setup script**
   ```bash
   python3 setup.py
   ```
   This will:
   - Create a virtual environment
   - Install all dependencies
   - Verify system requirements

3. **Start Ollama and pull the Mistral model**
   ```bash
   ollama serve
   ollama pull mistral
   ```

4. **Launch Skynet Lite**
   
   **Console Interface:**
   ```bash
   python3 main.py
   ```
   
   **Web Interface:**
   ```bash
   cd web
   python3 run.py
   # Open http://localhost:5000 in your browser
   ```
   
   **Alternative web startup:**
   ```bash
   cd web
   python3 app.py
   ```

## 🏗️ Architecture

```
skynet-lite/
├── main.py              # Entry point and chat orchestration
├── config.py            # Configuration management
├── setup.py             # Setup and dependency verification
├── web/                 # Web UI interface
│   ├── app.py           # Flask web application
│   ├── run.py           # Web UI launcher
│   ├── templates/       # HTML templates
│   └── static/          # CSS and static assets
├── models/
│   └── loader.py        # Ollama model interface
├── tools/
│   └── web_search.py    # DuckDuckGo + Azure Search + Google Custom Search integration
└── plugins/
    └── memory.py        # Conversation memory management
```

## 🔧 Configuration

Skynet Lite supports multiple configuration methods:

### Environment Variables
```bash
export OLLAMA_BASE_URL="http://localhost:11434"
export OLLAMA_MODEL="mistral"

# Web search providers (choose one)
# DuckDuckGo requires no credentials and is used by default
# To use Azure Cognitive Services Bing Search (Azure Search), set:
export AZURE_SEARCH_KEY="<your_azure_search_key>"
export AZURE_SEARCH_ENDPOINT="https://<resource-name>.cognitiveservices.azure.com/bing/v7.0/search"

# To use Google Custom Search JSON API, set:
export GOOGLE_API_KEY="<your_google_api_key>"
export GOOGLE_CX="<your_custom_search_engine_id>"
```

### Configuration File
Create or edit `config.yaml`:
```yaml
ollama:
  base_url: "http://localhost:11434"
  model: "mistral"
  
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
python3 -m pytest tests/ -v
```

Test specific components:
```bash
# Test core functionality
python3 test_components.py

# Test Ollama integration
python3 test_ollama.py

# Test web search
python3 test_ddg_search.py

# Test web interface
cd web
python3 test_web.py

# Run diagnostics
cd web
python3 diagnose.py
```

Run with coverage:
```bash
python3 -m pytest tests/ --cov=. --cov-report=html
```

## 📦 Dependencies

- **semantic-kernel** - AI orchestration framework
- **ollama** - Local LLM integration
- **flask** - Web interface framework
- **aiohttp/httpx** - Async HTTP clients
- **beautifulsoup4 & lxml** - HTML parsing for DuckDuckGo scraping (if used)
- **pyyaml** - Configuration management
- **rich** - Enhanced terminal output

## 🔧 Troubleshooting

### Web Interface Issues
- **"Error: Sorry, I encountered an error"**: Ensure Ollama is running (`ollama serve`)
- **Flask not found**: Run `pip install flask` or `pip install -r requirements.txt`
- **Port 5000 in use**: Change the port in `web/app.py` line `app.run(port=5000)`

### Search Issues  
- **No search results**: Check your internet connection for DuckDuckGo
- **Azure Search not working**: Verify `AZURE_SEARCH_KEY` and `AZURE_SEARCH_ENDPOINT`
- **Google Search failing**: Ensure `GOOGLE_API_KEY` and `GOOGLE_CX` are set correctly

### Model Issues
- **Ollama connection failed**: Start Ollama with `ollama serve` and verify port 11434
- **Model not found**: Pull the model with `ollama pull mistral`
- **Slow responses**: Models run locally; performance depends on your hardware

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

- [x] Web UI interface 
- [x] Multi-model support (OpenAI, Claude, Gemini, Copilot)
- [x] DuckDuckGo search integration
- [x] Flask web interface with diagnostics
- [ ] Voice interface integration
- [ ] Advanced robotics control plugins
- [ ] Swarm intelligence coordination
- [ ] Custom training pipeline
- [ ] Docker containerization
- [ ] API authentication and rate limiting
- [ ] WebSocket support for real-time chat
- [ ] Plugin marketplace

---

**Made with ❤️ for the robotics and AI community**
