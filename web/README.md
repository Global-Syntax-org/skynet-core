# Skynet Lite Web UI

Simple Flask-based web interface for Skynet Lite.

## Features

- 💬 Chat interface with Skynet Lite
- 🔍 Web search integration (DuckDuckGo/Azure/Google)
- 📱 Responsive design
- 🧹 Clear chat functionality
- ⚡ Real-time responses

## Quick Start

1. **Install Flask** (if not already installed):
   ```bash
   pip install flask
   ```

2. **Start Ollama** (if using local models):
   ```bash
   ollama serve
   ollama pull mistral
   ```

3. **Run the web interface**:
   ```bash
   cd web
   python3 run.py
   ```
   
   Or directly:
   ```bash
   python3 app.py
   ```

4. **Open your browser**:
   ```
   http://localhost:5000
   ```

## Configuration

The web UI uses the same configuration as the main Skynet Lite application:

- Environment variables (OLLAMA_MODEL, AZURE_SEARCH_KEY, etc.)
   - Note: `OLLAMA_BASE_URL` is deprecated; use `skynet.config` for advanced configuration.
- `config.yaml` file in the parent directory

**Database**: User accounts and conversation history are stored in `web/skynet_lite.db`.

## API Endpoints

- `GET /` - Main chat interface
- `POST /chat` - Send message and get response
- `POST /clear` - Clear chat session
- `GET /health` - Health check

## Customization

- Edit `templates/index.html` for UI changes
- Modify `static/style.css` for styling
- Extend `app.py` for additional functionality

## Security Notes

- This is a development server, not for production use
- No authentication implemented
- Sessions are memory-based (cleared on restart)

## Troubleshooting

- **Flask not found**: Run `pip install flask`
- **Ollama connection error**: Ensure Ollama is running on port 11434
- **Port 5000 in use**: Change the port in `app.py`
- **CORS issues**: Add CORS headers if needed for cross-origin requests
