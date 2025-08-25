# Skynet Core Deployment Guide

## Production Deployment

### Prerequisites

- Python 3.10+
- **Recommended**: Ollama (for local LLM support)
- **Alternative**: Cloud AI provider API keys
- 4GB+ RAM recommended
- 10GB+ disk space for local models (if using Ollama)

### Environment Setup

1. **Clone and Setup**
   ```bash
   git clone https://github.com/StuxnetStudios/skynet-core.git
   cd skynet-core
   python3 setup.py  # Creates venv and installs dependencies
   ```

2. **Configure Environment Variables**
   ```bash
   # Copy example environment file
   cp .env.example .env
   
   # Edit configuration
   nano .env
   ```

   **Core Configuration Options:**
   ```bash
   # Storage Backend (SQLite is default)
   SKYNET_STORAGE_TYPE=sqlite  # or mssql, file, memory
   
   # Local AI (Primary - Ollama)
   OLLAMA_BASE_URL=http://localhost:11434
   OLLAMA_MODEL=mistral
   
   # Cloud AI Fallbacks (Optional)
   OPENAI_API_KEY=your_openai_key
   ANTHROPIC_API_KEY=your_claude_key
   GEMINI_API_KEY=your_gemini_key
   GITHUB_COPILOT_TOKEN=your_copilot_token
   MICROSOFT_COPILOT_API_KEY=your_ms_copilot_key
   
   # Web Search Providers (Optional)
   AZURE_SEARCH_KEY=your_azure_key
   AZURE_SEARCH_ENDPOINT=your_azure_endpoint
   GOOGLE_API_KEY=your_google_key
   GOOGLE_CX=your_custom_search_engine_id
   
   # Web Interface
   FLASK_ENV=production
   FLASK_SECRET_KEY=your_secret_key_here
   ```

## Deployment Modes

### Mode 1: Local-Only (Privacy-First)
**Best for**: Privacy-sensitive environments, offline operation, development

```bash
# Setup Ollama
ollama serve
ollama pull mistral

# No API keys needed - runs completely local
python3 main.py
```

### Mode 2: Hybrid (Recommended)
**Best for**: Production environments with fallback reliability

```bash
# Setup local Ollama (primary)
ollama serve
ollama pull mistral

# Configure cloud fallbacks in .env
OPENAI_API_KEY=your_key
ANTHROPIC_API_KEY=your_key

python3 main.py
```

### Mode 3: Cloud-Only
**Best for**: Serverless deployments, maximum model capabilities

```bash
# Configure cloud providers in .env (no Ollama needed)
OPENAI_API_KEY=your_key
ANTHROPIC_API_KEY=your_key
GEMINI_API_KEY=your_key

python3 main.py
```

3. **Install and Configure Ollama (for Local/Hybrid modes)**
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
   docker build -t skynet-core .
   docker run -d -p 5000:5000 --name skynet-core skynet-core
   ```

#### Option 3: Systemd Service

1. **Create Service File**
   ```ini
   # /etc/systemd/system/skynet-core.service
   [Unit]
   Description=Skynet Core Web Interface
   After=network.target ollama.service

   [Service]
   Type=exec
   User=skynet
   Group=skynet
   WorkingDirectory=/opt/skynet-core/web
   Environment=PATH=/opt/skynet-core/.venv/bin
   ExecStart=/opt/skynet-core/.venv/bin/gunicorn -c gunicorn.conf.py app:app
   Restart=always
   RestartSec=10

   [Install]
   WantedBy=multi-user.target
   ```

2. **Enable and Start**
   ```bash
   systemctl daemon-reload
   systemctl enable skynet-core
   systemctl start skynet-core
   ```

### Reverse Proxy (Nginx)

```nginx
# /etc/nginx/sites-available/skynet-core
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
        alias /opt/skynet-core/web/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

## Development Setup

### Quick Development Start

```bash
# Clone repository
git clone https://github.com/StuxnetStudios/skynet-core.git
cd skynet-core

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
        logging.FileHandler('skynet-core.log'),
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
      tail -f skynet-core.log
```
   
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
