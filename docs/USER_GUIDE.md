# Skynet Lite User Guide

## Getting Started

### What is Skynet Lite?

Skynet Lite is a privacy-first AI assistant that runs entirely on your local machine. It combines the power of local language models with web search capabilities to provide intelligent, contextual responses while keeping your data private.

### Key Benefits

- **🛡️ Privacy-First**: All AI processing happens locally on your computer
- **🌐 Web-Enhanced**: Can search the internet for current information
- **💬 Two Interfaces**: Use either the console or web browser interface
- **🧠 Memory**: Remembers your conversation context
- **🔌 Extensible**: Support for multiple AI models and search providers

## Installation

### Quick Start (5 minutes)

1. **Download and Setup**
   ```bash
   git clone https://github.com/StuxnetStudios/skynet-lite.git
   cd skynet-lite
   python3 setup.py
   ```

2. **Install Ollama** (the local AI engine)
   
   **On Linux/Mac:**
   ```bash
   curl -fsSL https://ollama.com/install.sh | sh
   ```
   
   **On Windows:**
   - Download from [ollama.com](https://ollama.com)
   - Run the installer

3. **Start Ollama and Download a Model**
   ```bash
   # Start Ollama in background
   ollama serve
   
   # Download the Mistral model (4GB download)
   ollama pull mistral
   ```

4. **Launch Skynet Lite**
   
   **Web Interface (Recommended):**
   ```bash
   cd web
   python3 run.py
   ```
   Then open http://localhost:5000 in your browser
   
   **Console Interface:**
   ```bash
   python3 main.py
   ```

## Using the Web Interface

### Main Features

The web interface provides a clean, chat-like experience similar to ChatGPT but running locally.

#### Starting a Conversation

1. Open http://localhost:5000 in your browser
2. Type your question in the input box
3. Press Enter or click "Send"
4. Wait for the AI response

#### Example Conversations

**Basic Questions:**
```
You: What is Python programming?
🤖 Skynet: Python is a high-level, interpreted programming language...
```

**Web Search Queries:**
```
You: What's the latest news about AI?
🔍 Searching the web...
🤖 Skynet: Based on recent search results, here are the latest AI developments...
```

**Follow-up Questions:**
```
You: Tell me about machine learning
🤖 Skynet: Machine learning is a subset of artificial intelligence...

You: Can you give me an example?
🤖 Skynet: Certainly! Building on what I just explained about machine learning...
```

#### Interface Controls

- **Send Button**: Submit your message
- **New Chat**: Clear conversation history and start fresh
- **Auto-scroll**: Messages automatically scroll to the latest

#### Mobile Support

The web interface works on mobile devices:
- Responsive design adapts to screen size
- Touch-friendly controls
- Optimized for mobile typing

### Advanced Features

#### Memory Management

Skynet Lite remembers your conversation:
- Keeps track of previous questions and answers
- Maintains context across multiple messages
- Automatically manages memory to prevent overload

**Clear Memory:**
Click "New Chat" to start with a clean slate.

#### Web Search Integration

Skynet automatically detects when you need current information:

**Triggers web search:**
- "latest", "recent", "current", "today"
- "news", "breaking", "trending"
- "weather", "stock prices", "market"
- "search for", "look up", "find information"

**Examples:**
```
You: What's the weather like today?
🔍 Searching the web...

You: Latest developments in renewable energy
🔍 Searching the web...

You: Current Bitcoin price
🔍 Searching the web...
```

#### Conversation Export

Currently, conversations are stored in browser session. For persistent storage:
1. Copy important responses before closing browser
2. Use the console interface for persistent history
3. Future updates will include conversation export

## Using the Console Interface

### Starting Console Mode

```bash
cd skynet-lite
python3 main.py
```

### Console Commands

**Basic Usage:**
```
💬 Chat with Skynet Lite (type 'quit' to exit)
==================================================

You: Hello, how are you?
🤖 Skynet: Hello! I'm functioning well and ready to help...

You: What can you do?
🤖 Skynet: I can help with a wide range of tasks...
```

**Exit Commands:**
- `quit` - Exit gracefully
- `exit` - Exit gracefully  
- `bye` - Exit gracefully
- `Ctrl+C` - Force exit

### Console vs Web Interface

| Feature | Console | Web |
|---------|---------|-----|
| **Ease of Use** | Command-line users | Everyone |
| **Interface** | Text-based | Visual/Browser |
| **Memory** | Persistent file | Session-based |
| **Startup** | Instant | Requires browser |
| **Mobile** | No | Yes |
| **Sharing** | Copy/paste | Screenshot/share |

## Configuration

### Environment Variables

Create a `.env` file to customize behavior:

```bash
# AI Model Configuration
# (Deprecated) OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=mistral

# Memory Settings
MAX_MEMORY_TURNS=10

# Web Search (optional)
AZURE_SEARCH_KEY=your_key_here
GOOGLE_API_KEY=your_key_here
GOOGLE_CX=your_search_engine_id

# Web Interface
FLASK_SECRET_KEY=your_secret_key
```

### Using Different Models

**Available Ollama Models:**
```bash
# Fast, smaller models (good for basic tasks)
ollama pull llama2:7b

# Balanced performance
ollama pull mistral        # Default
ollama pull codellama      # Good for programming

# Larger, more capable models
ollama pull llama2:70b     # Requires 40GB+ RAM
ollama pull mixtral        # Mixture of experts
```

**Switch models by editing config:**
```bash
export OLLAMA_MODEL=codellama
python3 main.py
```

### Using Cloud APIs (Optional)

For enhanced capabilities, you can configure cloud API fallbacks:

```bash
# OpenAI (ChatGPT)
export OPENAI_API_KEY=your_openai_key

# Anthropic (Claude)  
export ANTHROPIC_API_KEY=your_claude_key

# Google (Gemini)
export GEMINI_API_KEY=your_gemini_key
```

**Automatic Fallback Order:**
1. Ollama (local) - Primary
2. OpenAI - If local fails
3. Claude - If OpenAI unavailable
4. Gemini - If Claude unavailable
5. Basic responses - Final fallback

## Common Use Cases

### Programming Help

```
You: How do I create a Python function?
🤖 Skynet: Here's how to create a Python function:

def function_name(parameters):
    """Optional docstring"""
    # Function body
    return result

Example:
def greet(name):
    return f"Hello, {name}!"
```

### Research and Information

```
You: Tell me about quantum computing
🤖 Skynet: Quantum computing is a revolutionary approach to computation...

You: What are the latest breakthroughs?
🔍 Searching the web...
🤖 Skynet: Based on recent research, here are the latest quantum computing breakthroughs...
```

### Writing and Editing

```
You: Help me write a professional email
🤖 Skynet: I'd be happy to help! Here's a template for a professional email:

Subject: [Clear, specific subject line]

Dear [Name],

[Opening greeting and purpose]
[Main content with clear points]
[Action items or next steps]
[Professional closing]

Best regards,
[Your name]
```

### Creative Tasks

```
You: Write a short story about a robot
🤖 Skynet: Here's a short story for you:

"The Last Maintenance"

In the year 2157, maintenance robot R-247 performed its daily rounds...
```

### Learning and Education

```
You: Explain photosynthesis in simple terms
🤖 Skynet: Photosynthesis is how plants make their own food using sunlight...

You: Can you give me a more detailed explanation?
🤖 Skynet: Certainly! Let me expand on that with more scientific detail...
```

## Troubleshooting

### Common Issues

#### "AI system not responding"

**Symptoms:** Messages sent but no response
**Solutions:**
1. Check if Ollama is running: `ollama ps`
2. Restart Ollama: `ollama serve`
3. Check model is downloaded: `ollama list`
4. Restart Skynet Lite

#### "Web search not working"

**Symptoms:** Search attempts fail or return no results
**Solutions:**
1. Check internet connection
2. Try a different search query
3. Check if search providers are working
4. Disable web search temporarily

#### "Web interface won't load"

**Symptoms:** Browser shows connection error
**Solutions:**
1. Check if Flask is running: look for "Running on http://127.0.0.1:5000"
2. Try different port: edit `app.py` and change port number
3. Check firewall settings
4. Try console interface instead

#### "Slow responses"

**Symptoms:** Long wait times for responses
**Solutions:**
1. Use smaller model: `ollama pull llama2:7b`
2. Close other applications to free RAM
3. Check system resources: `htop` or Task Manager
4. Use cloud API fallback

### Getting Help

#### Check System Status
```bash
# Test core functionality
python3 test_components.py

# Test web interface
cd web
python3 diagnose.py

# Check Ollama
curl http://localhost:11434/api/version
```

#### Debug Mode
```bash
# Console with debug info
python3 main.py --verbose

# Web interface debug
export FLASK_ENV=development
cd web
python3 app.py
```

#### Log Files
Check these files for error messages:
- `skynet-lite.log` (if configured)
- Console output
- Browser developer console (F12)

### Performance Optimization

#### Hardware Requirements

**Minimum:**
- 4GB RAM
- 2GB free disk space
- Any modern CPU

**Recommended:**
- 8GB+ RAM
- SSD storage
- Multi-core CPU
- GPU (for some models)

#### Speed Tips

1. **Use faster models:**
   ```bash
   ollama pull llama2:7b  # Smaller, faster
   ```

2. **Increase RAM:**
   - Close unnecessary applications
   - Use lighter operating system

3. **SSD Storage:**
   - Store models on SSD if possible
   - Enable SSD optimizations

4. **Model Management:**
   ```bash
   # Remove unused models
   ollama rm large_model_name
   
   # List all models
   ollama list
   ```

## Privacy and Security

### Data Privacy

**What stays local:**
- All conversations
- AI model processing
- Configuration files
- Memory/history

**What goes online (only if enabled):**
- Web search queries
- Cloud API requests (if configured)

### Disabling Online Features

**Disable web search:**
```bash
export ENABLE_WEB_SEARCH=false
```

**Use only local models:**
- Don't set any API keys
- Only use Ollama models

### Secure Usage

1. **Keep software updated:**
   ```bash
   git pull origin main
   pip install -r requirements.txt --upgrade
   ```

2. **Protect API keys:**
   - Store in `.env` file
   - Don't share or commit to version control
   - Rotate keys regularly

3. **Network security:**
   - Use HTTPS in production
   - Consider VPN for cloud APIs
   - Monitor network traffic

## Advanced Usage

### Customizing Prompts

You can modify the system prompts by editing the loader files in `loaders/` directory.

### Adding Custom Search Providers

Extend the web search functionality by modifying `tools/web_search.py`.

### Integration with Other Tools

Skynet Lite can be integrated with:
- Jupyter notebooks
- VS Code extensions
- Custom applications via API
- Robotics frameworks (ROS, Webots)

### Batch Processing

For processing multiple queries:
```python
from main import SkynetLite
import asyncio

async def batch_process(queries):
    skynet = SkynetLite()
    await skynet.initialize()
    
    for query in queries:
        response = await skynet.chat(query)
        print(f"Q: {query}")
        print(f"A: {response}\n")

# Usage
queries = ["What is AI?", "Explain machine learning", "Current AI trends"]
asyncio.run(batch_process(queries))
```

This user guide covers all essential aspects of using Skynet Lite effectively. For technical details, see the API Reference and Deployment Guide.
