# 🤖 Skynet Core

- *A hybrid AI chatbot with local-first processing and cloud fallback capabilities. Features advanced web search, enterprise storage options, multi-model intelligence, and comprehensive document management for both local privacy and cloud scalability.

## 🚀 Quick Startn**: 2.1.0-core

A hybrid AI chatbot with local-first processing and cloud fallback capabilities. Features advanced web search, enterprise storage options, multi-model intelligence, and comprehensive document management for both local privacy and cloud scalability.

## ✨ Features

- **🧠 Local-First AI Processing** - Ollama integration with intelligent cloud provider fallback
- **📄 Document Management** - Upload, process, and search documents (PDF, DOCX, XLSX, TXT, MD, CSV)
- **🔍 Smart Document Search** - AI-powered document content retrieval with relevance scoring
- **💾 Flexible Storage** - SQLite default with optional MSSQL, file, and memory backends
- **🌐 Modern Web Interface** - Responsive Flask-based web UI with real-time chat and document management
- **🔌 Plugin Architecture** - Modular system with Semantic Kernel integration
- **🏢 Enterprise Ready** - Scalable storage and cloud provider options
- **🚀 High Performance** - Async architecture with concurrent AI processing
- **🎯 Multi-Model Intelligence** - Seamless switching between local and cloud AI providers
- **🔄 Smart Fallback** - Automatic provider switching for maximum reliability
- **🛠️ Development Tools** - Comprehensive testing and diagnostic utilities
- **Current Version**: 2.1.0-core

A hybrid AI chatbot with local-first processing and cloud fallback capabilities. Features advanced web search, enterprise storage options, and multi-model intelligence for both local privacy and cloud scalability.

## ✨ Features

- **🧠 Local-First AI Processing** - Ollama integration with intelligent cloud provider fallback
- **� Flexible Storage** - SQLite default with optional MSSQL, file, and memory backends
- **🌐 Modern Web Interface** - Responsive Flask-based web UI with real-time chat
- **🔌 Plugin Architecture** - Modular system with Semantic Kernel integration
- **🏢 Enterprise Ready** - Scalable storage and cloud provider options
- **🚀 High Performance** - Async architecture with concurrent AI processing
- **🎯 Multi-Model Intelligence** - Seamless switching between local and cloud AI providers
- **🔄 Smart Fallback** - Automatic provider switching for maximum reliability
- **🛠️ Development Tools** - Comprehensive testing and diagnostic utilities

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- **Option A (Local)**: [Ollama](https://ollama.com/download) installed and running
- **Option B (Cloud)**: At least one cloud AI provider API key (OpenAI, Claude, Gemini, etc.)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/StuxnetStudios/skynet-core.git
   cd skynet-core
   ```

2. **Run the setup script**
   ```bash
   python3 setup.py
   ```
   This will:
   - Create a virtual environment
   - Install all dependencies
   - Verify system requirements

3. **Configure your setup (choose one)**
   
   **Option A - Local AI (Recommended)**
   ```bash
   # Start Ollama and pull a model
   ollama serve
   ollama pull mistral
   ```
   
   **Option B - Cloud AI**
   ```bash
   cp .env.example .env
   # Edit .env and add at least one API key
   ```

4. **Launch Skynet Core**
   
   **Console Interface:**
   ```bash
   python3 main.py
   ```
   
   **Web Interface:**
   ```bash
   cd web
   python3 run.py
   # Open http://localhost:5050 in your browser
   ```

> **Note**: Skynet Core automatically tries Ollama first, then falls back to configured cloud providers if needed.
   python3 run.py
   # Open http://localhost:5005 in your browser
   ```

## 🏗️ Architecture

```
skynet-core/
├── main.py              # Entry point and chat orchestration
├── skynet/              # Core package
│   ├── assistant.py     # Main orchestrator and chat loop
│   ├── config.py        # Configuration management
│   ├── loader_manager.py # AI provider management with fallback
│   ├── memory.py        # Conversation memory
│   ├── document_processor.py # Document upload, processing, and search
│   └── storage/         # Storage abstraction layer
│       ├── base.py      # Abstract storage interface
│       ├── sqlite_adapter.py # SQLite storage (default)
│       ├── mssql_adapter.py  # Microsoft SQL Server
│       ├── file_adapter.py   # JSON file storage
│       ├── memory_adapter.py # In-memory storage
│       └── manager.py   # Storage adapter factory
├── loaders/             # AI provider implementations
│   ├── ollama_loader.py # Local Ollama integration
│   ├── openai_loader.py # OpenAI API
│   ├── claude_loader.py # Anthropic Claude
│   ├── gemini_loader.py # Google Gemini
│   └── *_copilot_loader.py # GitHub/Microsoft Copilot
├── web/                 # Web UI interface (modular architecture)
│   ├── app.py           # Main Flask application and configuration
│   ├── auth_routes.py   # Authentication and user management routes
│   ├── chat_routes.py   # Chat messaging and conversation history
│   ├── document_routes.py # Document upload and management API
│   ├── password_routes.py # Password reset and token management
│   ├── static_routes.py # Static pages and utility endpoints
│   ├── auth.py          # Authentication manager and security
│   ├── run.py           # Web UI launcher
│   ├── templates/       # HTML templates with document management
│   └── static/          # CSS and static assets
├── tools/
│   └── web_search.py    # Web search integration
└── plugins/
    └── memory.py        # Conversation memory management
```

## 🔧 Configuration

Skynet Core supports multiple configuration methods with automatic fallback:

### AI Provider Priority Order

1. **Ollama (Local)** - Tried first if available
2. **OpenAI** - Cloud fallback if API key provided
3. **Google Gemini** - Advanced multimodal capabilities
4. **Anthropic Claude** - Advanced reasoning
5. **GitHub Copilot** - Developer assistance
6. **Microsoft Copilot** - Enterprise AI
7. **Local Fallback** - Basic responses if all else fails

### Environment Variables

Copy `.env.example` to `.env` and configure your preferences:
```bash
cp .env.example .env
```

**Storage Configuration:**
```bash
# Storage backend (default: sqlite)
export SKYNET_STORAGE_TYPE="sqlite"  # or mssql, file, memory

# SQLite settings (default)
export SQLITE_DATABASE="data/skynet.db"

# MSSQL settings (optional)
export MSSQL_SERVER="localhost"
export MSSQL_DATABASE="skynet_core"
export MSSQL_USERNAME="sa"
export MSSQL_PASSWORD="your_password"
```

**Local AI (Primary):**
```bash
# Ollama (tried first)
export OLLAMA_BASE_URL="http://localhost:11434"
export OLLAMA_MODEL="mistral"
```

**Cloud AI (Fallbacks - Optional):**
```bash
# OpenAI
export OPENAI_API_KEY="<your_openai_api_key>"
export OPENAI_MODEL="gpt-3.5-turbo"

# Anthropic Claude
export ANTHROPIC_API_KEY="<your_anthropic_api_key>"
export ANTHROPIC_MODEL="claude-3-sonnet-20240229"

# Google Gemini
export GOOGLE_API_KEY="<your_google_api_key>"
export GEMINI_MODEL="gemini-pro"

# GitHub Copilot (Developer assistant)
export GITHUB_COPILOT_TOKEN="<your_github_copilot_token>"
export COPILOT_API_URL="<your_copilot_endpoint_url>"

# Microsoft Copilot (Enterprise AI)
export MICROSOFT_COPILOT_API_KEY="<your_microsoft_api_key>"
export MICROSOFT_COPILOT_ENDPOINT="<your_azure_endpoint>"
```

**Web Search Providers:**
```bash
# DuckDuckGo (Default - No API key required)
# Automatically enabled, privacy-focused search

# Azure Cognitive Services Bing Search
export AZURE_SEARCH_KEY="<your_azure_search_key>"
export AZURE_SEARCH_ENDPOINT="https://<resource-name>.cognitiveservices.azure.com/bing/v7.0/search"

# Google Custom Search JSON API
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
🤖 Skynet: I'm Skynet Core, your local AI assistant! I can help with...
```

### Web Search Queries
```
You: What's the latest news about AI?
🔍 Searching the web...
🤖 Skynet: Based on recent search results, here are the latest AI developments...
```

### Document Management
```
# Upload documents through the web interface
1. Click "Documents" button in the web UI
2. Drag & drop or select files (PDF, DOCX, XLSX, TXT, MD, CSV)
3. Documents are processed and indexed automatically

# AI will search your documents for relevant context
You: What did the quarterly report say about revenue?
🔍 Searching your documents...
🤖 Skynet: Based on your uploaded quarterly report, revenue increased by...
```

### AI Model Switching
```
# Copilot coding assistance
You: Can you help me write a Python function for binary search?
🤖 Skynet (Copilot): Here's a well-documented binary search implementation...

# Try the Copilot demo
python3 demo_copilot.py
```

### Commands
- `quit`, `exit`, `bye` - Exit the chat
- Web search triggers: "latest", "recent", "news", "current", "weather", etc.

## 🧩 Plugin Development

Skynet Core uses a modular plugin architecture. Create new plugins by extending the base patterns:

```python
class CustomPlugin:
    """Custom plugin following Skynet Core patterns"""
    
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

### Records Retention Integration
```python
# Example records retention integration
# Use the records retention plugin to manage record lifecycles and retention policies
from skynet_core import SkynetCore

class RetentionManager:
    def __init__(self):
        self.skynet = SkynetCore()
    
    def apply_policy(self, record_id: str):
        """Apply retention policy to a record"""
        # ...implementation placeholder...
```

## 📖 Documentation

- **[Document Management Guide](docs/DOCUMENT_MANAGEMENT.md)** - Complete guide to document upload and search
- **[Web Architecture Guide](docs/WEB_ARCHITECTURE.md)** - Modular Blueprint architecture documentation  
- **[API Reference](DOCUMENT_FEATURE_SUMMARY.md)** - Document management API endpoints
- **[Contributing Guide](CONTRIBUTING.md)** - Development guidelines and contribution process

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

# Test GitHub Copilot integration
python3 test_copilot.py

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
- **Port 5050 in use**: Change the port in `web/app.py` line `app.run(port=5050)`

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
- [x] Document upload and management system
- [x] Document search and AI integration
- [x] Modular Blueprint architecture for maintainability
- [ ] Voice interface integration
- [ ] Advanced records retention plugins
- [ ] Workflow and coordination for retention policies
- [ ] Custom training pipeline
- [ ] Docker containerization
- [ ] API authentication and rate limiting
- [ ] WebSocket support for real-time chat
- [ ] Plugin marketplace

---

 **Made with ❤️ for the records management and AI community**
