# Skynet Lite Deployment Guide

## Production Deployment

### Prerequisites

- Python 3.10+
- Ollama (for local LLM support)
- 4GB+ RAM recommended
- 10GB+ disk space for models

### Environment Setup

1. **Clone and Setup**
   ```bash
   git clone https://github.com/StuxnetStudios/skynet-lite.git
   cd skynet-lite
   python3 setup.py  # Creates venv and installs dependencies
   ```

2. **Configure Environment Variables**
   ```bash
   # Copy example environment file
   cp .env.example .env
   
   # Edit configuration
   nano .env
   ```

   **Required Variables:**
   ```bash
   # Ollama Configuration
   # Note: OLLAMA_BASE_URL is deprecated in favor of package-based configuration.
   # Configure the model name using OLLAMA_MODEL and use `skynet.config` for advanced settings.
   # If you run Ollama on a custom URL, you may still set OLLAMA_BASE_URL.
   OLLAMA_MODEL=mistral
   
   # Optional: API Keys for fallback models
   OPENAI_API_KEY=your_openai_key
   ANTHROPIC_API_KEY=your_claude_key
   GEMINI_API_KEY=your_gemini_key
   
   # Optional: Search Provider Keys
   AZURE_SEARCH_KEY=your_azure_key
   AZURE_SEARCH_ENDPOINT=your_azure_endpoint
   GOOGLE_API_KEY=your_google_key
   GOOGLE_CX=your_custom_search_engine_id
   
   # Web Interface
   FLASK_ENV=production
   FLASK_SECRET_KEY=your_secret_key_here
   ```

3. **Install and Configure Ollama**
   ```bash
   # Install Ollama (Linux)
   curl -fsSL https://ollama.com/install.sh | sh
   
   # Start Ollama service
   systemctl start ollama
   systemctl enable ollama
   
   # Pull required models
   ollama pull mistral
   ollama pull llama2  # Optional backup model
   ```

### Production Web Server

#### Option 1: Gunicorn (Recommended)

1. **Install Gunicorn**
   ```bash
   source .venv/bin/activate
   pip install gunicorn
   ```

2. **Create Gunicorn Configuration**
   ```python
   # gunicorn.conf.py
   bind = "0.0.0.0:5000"
   workers = 4
   worker_class = "sync"
   timeout = 120
   keepalive = 2
   max_requests = 1000
   max_requests_jitter = 100
   preload_app = True
   ```

3. **Run with Gunicorn**
   ```bash
   cd web
   gunicorn -c gunicorn.conf.py app:app
   ```

#### Option 2: Docker Deployment

1. **Create Dockerfile**
   ```dockerfile
   FROM python:3.11-slim

   WORKDIR /app
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt

   COPY . .
   EXPOSE 5000

   CMD ["gunicorn", "-c", "gunicorn.conf.py", "web.app:app"]
   ```

2. **Build and Run**
   ```bash
   docker build -t skynet-lite .
   docker run -d -p 5000:5000 --name skynet-lite skynet-lite
   ```

#### Option 3: Systemd Service

1. **Create Service File**
   ```ini
   # /etc/systemd/system/skynet-lite.service
   [Unit]
   Description=Skynet Lite Web Interface
   After=network.target ollama.service

   [Service]
   Type=exec
   User=skynet
   Group=skynet
   WorkingDirectory=/opt/skynet-lite/web
   Environment=PATH=/opt/skynet-lite/.venv/bin
   ExecStart=/opt/skynet-lite/.venv/bin/gunicorn -c gunicorn.conf.py app:app
   Restart=always
   RestartSec=10

   [Install]
   WantedBy=multi-user.target
   ```

2. **Enable and Start**
   ```bash
   systemctl daemon-reload
   systemctl enable skynet-lite
   systemctl start skynet-lite
   ```

### Reverse Proxy (Nginx)

```nginx
# /etc/nginx/sites-available/skynet-lite
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_timeout 120s;
    }

    location /static {
        alias /opt/skynet-lite/web/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

## Development Setup

### Quick Development Start

```bash
# Clone repository
git clone https://github.com/StuxnetStudios/skynet-lite.git
cd skynet-lite

# Setup development environment
python3 setup.py
source .venv/bin/activate

# Install development dependencies
pip install -r requirements-dev.txt

# Start Ollama (in separate terminal)
ollama serve

# Pull model
ollama pull mistral

# Run console interface
python3 main.py

# OR run web interface
cd web
python3 run.py
```

### Development Dependencies

Create `requirements-dev.txt`:
```
# Testing
pytest>=7.4.0
pytest-asyncio>=0.21.0
pytest-cov>=4.1.0
pytest-mock>=3.11.1

# Code Quality
black>=23.0.0
flake8>=7.0.0
mypy>=1.5.0
isort>=5.12.0

# Development Tools
ipython>=8.15.0
jupyter>=1.0.0
pre-commit>=3.4.0
```

### Pre-commit Hooks

```bash
# Install pre-commit
pip install pre-commit

# Setup hooks
pre-commit install
```

Create `.pre-commit-config.yaml`:
```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.7.0
    hooks:
      - id: black

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.5.1
    hooks:
      - id: mypy
```

### Testing in Development

```bash
# Run all tests
python3 -m pytest tests/ -v

# Run with coverage
python3 -m pytest tests/ --cov=. --cov-report=html

# Test specific components
python3 test_components.py
python3 test_ollama.py
python3 test_ddg_search.py

# Test web interface
cd web
python3 test_web.py
python3 diagnose.py
```

### Hot Reload Development

```bash
# Web interface with auto-reload
cd web
export FLASK_ENV=development
python3 app.py

# Console with file watching (using entr)
find . -name "*.py" | entr -r python3 main.py
```

## Monitoring and Logging

### Application Logging

```python
# Enhanced logging configuration
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('skynet-lite.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
```

### Health Monitoring

Monitor these endpoints:
- `GET /health` - Basic health check
- Check Ollama service: `curl http://localhost:11434/api/version`
- Monitor log files for errors
- Track response times and memory usage

### Performance Metrics

Key metrics to monitor:
- Response time per request
- Memory usage
- Ollama model loading time
- Web search latency
- Error rates by endpoint

## Security Considerations

### API Security

1. **Rate Limiting**
   ```python
   from flask_limiter import Limiter
   from flask_limiter.util import get_remote_address

   limiter = Limiter(
       app,
       key_func=get_remote_address,
       default_limits=["200 per day", "50 per hour"]
   )
   ```

2. **Input Validation**
   - Sanitize all user inputs
   - Limit message length
   - Validate JSON payloads

3. **HTTPS in Production**
   - Use TLS certificates
   - Redirect HTTP to HTTPS
   - Set secure headers

### Environment Security

- Store secrets in environment variables
- Use restricted file permissions
- Regular security updates
- Monitor access logs

## Troubleshooting

### Common Issues

1. **Ollama Connection Failed**
   ```bash
   # Check if Ollama is running
   systemctl status ollama
   curl http://localhost:11434/api/version
   
   # Restart if needed
   systemctl restart ollama
   ```

2. **Memory Issues**
   ```bash
   # Check system memory
   free -h
   
   # Monitor Ollama memory usage
   ps aux | grep ollama
   ```

3. **Web Interface Not Loading**
   ```bash
   # Check Flask logs
   tail -f skynet-lite.log
   
   # Test endpoints directly
   curl http://localhost:5000/health
   ```

4. **Model Loading Slow**
   - Ensure sufficient RAM (4GB+ recommended)
   - Use SSD storage for models
   - Consider smaller models for limited hardware

### Debug Mode

```bash
# Enable debug logging
export SKYNET_DEBUG=true

# Run with verbose output
python3 main.py --verbose

# Web interface debug mode
export FLASK_ENV=development
cd web
python3 app.py
```

## Backup and Recovery

### Configuration Backup

```bash
# Backup configuration
tar -czf skynet-config-$(date +%Y%m%d).tar.gz .env config.yaml

# Backup conversation history
cp conversation_history.json backup/
```

### Model Recovery

```bash
# Re-download models if corrupted
ollama rm mistral
ollama pull mistral

# Verify model integrity
ollama list
```

This deployment guide ensures reliable production deployment and smooth development workflow for Skynet Lite.
