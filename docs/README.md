# Skynet Core Documentation Index

Welcome to the Skynet Core documentation! This index helps you find the right documentation for your needs.

## Quick Start

**New to Skynet Core?** Start here:
1. [User Guide](docs/USER_GUIDE.md) - Complete guide for end users
2. [Installation](README.md#quick-start) - Get up and running in 5 minutes
3. [Web Interface Tutorial](docs/USER_GUIDE.md#using-the-web-interface) - Using the browser interface

## Documentation by Audience

### 👤 End Users
- **[User Guide](docs/USER_GUIDE.md)** - Complete usage guide with examples
- **[README](README.md)** - Project overview and quick start
- **[Troubleshooting](docs/USER_GUIDE.md#troubleshooting)** - Common issues and solutions

### 👨‍💻 Developers
- **[API Reference](docs/API_REFERENCE.md)** - Complete API documentation
- **[Project Overview](docs/PROJECT_OVERVIEW.md)** - Architecture and design
- **[Contributing Guide](CONTRIBUTING.md)** - How to contribute code
- **[Development Setup](CONTRIBUTING.md#development-setup)** - Local development environment

### 🚀 System Administrators  
- **[Deployment Guide](docs/DEPLOYMENT_GUIDE.md)** - Production deployment
- **[Configuration Reference](docs/DEPLOYMENT_GUIDE.md#environment-setup)** - All configuration options
- **[Monitoring Guide](docs/DEPLOYMENT_GUIDE.md#monitoring-and-logging)** - Monitoring and logging

## Documentation by Topic

### Installation & Setup
- [Quick Start](README.md#quick-start) - 5-minute setup
- [Prerequisites](docs/USER_GUIDE.md#installation) - System requirements
- [Development Setup](CONTRIBUTING.md#development-setup) - Developer environment
- [Production Deployment](docs/DEPLOYMENT_GUIDE.md) - Production setup

### Using Skynet Core
- [Web Interface Guide](docs/USER_GUIDE.md#using-the-web-interface) - Browser-based chat
- [Console Interface](docs/USER_GUIDE.md#using-the-console-interface) - Command-line usage
- [Configuration Options](docs/USER_GUIDE.md#configuration) - Customizing behavior
- [Common Use Cases](docs/USER_GUIDE.md#common-use-cases) - Example workflows

### Technical Reference
- [API Reference](docs/API_REFERENCE.md) - Complete API docs
- [Architecture Overview](docs/PROJECT_OVERVIEW.md) - System design
- [Model Loaders](docs/API_REFERENCE.md#loaderclassemanager) - AI provider interfaces
- [Storage Abstraction](docs/STORAGE_ABSTRACTION.md) - Storage backend options and configuration
- [MSSQL Usage Guide](docs/MSSQL_USAGE_GUIDE.md) - Microsoft SQL Server integration
- [GitHub Copilot Integration](docs/COPILOT_INTEGRATION.md) - Copilot setup and configuration
- [Microsoft Copilot Integration](docs/MICROSOFT_COPILOT_INTEGRATION.md) - Microsoft AI assistant setup
-
Note: this project includes two separate Copilot integrations:

- GitHub Copilot (requires `GITHUB_COPILOT_TOKEN` and an internal `COPILOT_API_URL` proxy). See `docs/COPILOT_INTEGRATION.md`.
- Microsoft Copilot (uses `MICROSOFT_COPILOT_API_KEY` and `MICROSOFT_COPILOT_ENDPOINT`). See `docs/MICROSOFT_COPILOT_INTEGRATION.md`.
- [Web Search Integration](docs/PROJECT_OVERVIEW.md#web-search-tools) - Search providers

### Development
- [Contributing Guidelines](CONTRIBUTING.md) - How to contribute
- [Coding Standards](CONTRIBUTING.md#coding-standards) - Code style guide
- [Testing Guide](CONTRIBUTING.md#testing) - Writing and running tests
- [Code Review Process](CONTRIBUTING.md#review-process) - Getting changes merged

### Operations & Deployment
- [Production Deployment](docs/DEPLOYMENT_GUIDE.md#production-deployment) - Server setup
- [Deployment Modes](docs/DEPLOYMENT_GUIDE.md#deployment-modes) - Local, hybrid, and cloud deployment options
- [Docker Deployment](docs/DEPLOYMENT_GUIDE.md#option-2-docker-deployment) - Container deployment
- [Monitoring & Logging](docs/DEPLOYMENT_GUIDE.md#monitoring-and-logging) - Operational monitoring
- [Security Considerations](docs/DEPLOYMENT_GUIDE.md#security-considerations) - Security best practices

## Deployment Modes

Skynet Core supports three main deployment modes:

### 🏠 Local-Only Mode
- **Privacy**: All processing happens locally
- **Requirements**: Ollama + local models
- **Use Cases**: Sensitive data, offline environments
- **Setup**: [Local deployment guide](docs/DEPLOYMENT_GUIDE.md#mode-1-local-only-privacy-first)

### 🌩️ Hybrid Mode (Recommended)
- **Reliability**: Local processing with cloud fallbacks
- **Requirements**: Ollama + optional cloud API keys
- **Use Cases**: Production environments with backup reliability
- **Setup**: [Hybrid deployment guide](docs/DEPLOYMENT_GUIDE.md#mode-2-hybrid-recommended)

### ☁️ Cloud-Only Mode
- **Scalability**: Enterprise cloud AI without local dependencies
- **Requirements**: Cloud AI provider API keys
- **Use Cases**: Serverless deployments, maximum capabilities
- **Setup**: [Cloud deployment guide](docs/DEPLOYMENT_GUIDE.md#mode-3-cloud-only)

## Features & Capabilities

### Core Features
- **Hybrid AI Processing** - Local-first with cloud fallback architecture
- **Storage Abstraction** - SQLite, MSSQL, file, and memory backends
- **Multi-Model Support** - Ollama (local) + OpenAI, Claude, Gemini, Copilot fallbacks
- **Web Search Integration** - DuckDuckGo, Azure, Google search
- **Memory Management** - Conversation context and history
- **Dual Interfaces** - Web browser and console interfaces

### AI Model Support
| Provider | Models | API Key Required | Local Processing |
|----------|--------|------------------|------------------|
| **Ollama** | Mistral, Llama2, CodeLlama, etc. | No | Yes |
| **OpenAI** | GPT-3.5, GPT-4 | Yes | No |
| **Claude** | Claude-3, Claude-2 | Yes | No |
| **Gemini** | Gemini Pro | Yes | No |
| **Copilot** | GitHub Copilot | Yes | No |

### Search Providers
| Provider | API Key Required | Features |
|----------|------------------|----------|
| **DuckDuckGo** | No | Privacy-focused, no tracking |
| **Azure Bing** | Yes | Comprehensive results |
| **Google Custom** | Yes | Customizable search |

## Quick Reference

### Essential Commands

**Console Interface:**
```bash
python3 main.py
```

**Web Interface:**
```bash
cd web && python3 run.py
```
Or:
```bash
cd web && python3 app.py
```

**Testing:**
```bash
# Run all tests
pytest

# Test core functionality
python3 test_components.py

# Test web interface
cd web && python3 diagnose.py
```

### Configuration Files

| File | Purpose | Location |
|------|---------|----------|
| `.env` | Environment variables | Project root |
| `config.yaml` | YAML configuration | Project root |
| `requirements.txt` | Python dependencies | Project root |
| `gunicorn.conf.py` | Production server config | web/ directory |

### Important URLs & Endpoints

**Web Interface:**
- Main chat: `http://localhost:5000/`
- Health check: `http://localhost:5000/health`
- Chat API: `POST http://localhost:5000/chat`
- Clear session: `POST http://localhost:5000/clear`

**Ollama:**
- Service: `http://localhost:11434/`
- Version check: `http://localhost:11434/api/version`
- Models list: `http://localhost:11434/api/tags`

## Troubleshooting Quick Links

### Common Issues
- [AI system not responding](docs/USER_GUIDE.md#ai-system-not-responding)
- [Web search not working](docs/USER_GUIDE.md#web-search-not-working) 
- [Web interface won't load](docs/USER_GUIDE.md#web-interface-wont-load)
- [Slow responses](docs/USER_GUIDE.md#slow-responses)

### Diagnostic Tools
- [System diagnostics](docs/USER_GUIDE.md#check-system-status)
- [Debug mode](docs/USER_GUIDE.md#debug-mode)
- [Log files](docs/USER_GUIDE.md#log-files)
- [Performance optimization](docs/USER_GUIDE.md#performance-optimization)

## Contributing & Community

### How to Contribute
- [Contributing Guide](CONTRIBUTING.md) - Complete contribution guide
- [Good First Issues](https://github.com/StuxnetStudios/skynet-lite/labels/good%20first%20issue) - Beginner-friendly tasks
- [Feature Requests](https://github.com/StuxnetStudios/skynet-lite/issues/new?template=feature_request.md) - Suggest new features
- [Bug Reports](https://github.com/StuxnetStudios/skynet-lite/issues/new?template=bug_report.md) - Report issues

### Community Resources
- [GitHub Repository](https://github.com/StuxnetStudios/skynet-lite)
- [Issue Tracker](https://github.com/StuxnetStudios/skynet-lite/issues)
- [Discussions](https://github.com/StuxnetStudios/skynet-lite/discussions)
- [Changelog](docs/CHANGELOG.md) - Recent changes and updates

## Release Information

- **Current Version**: 1.2.0
- **Current Version**: 1.4.1
- **Latest Release**: [Changelog](docs/CHANGELOG.md#120---2025-08-15)
- **Roadmap**: [Future Plans](README.md#roadmap)
- **Version History**: [Complete Changelog](docs/CHANGELOG.md)

## Getting Help

### Documentation Issues
If you find documentation that is:
- Unclear or confusing
- Missing important information  
- Contains errors or outdated information
- Could benefit from examples

Please [open an issue](https://github.com/StuxnetStudios/skynet-lite/issues/new) or submit a pull request with improvements.

### Support Channels
1. **GitHub Issues** - Bug reports and feature requests
2. **GitHub Discussions** - General questions and community help
3. **Documentation** - Check this documentation first
4. **Code Examples** - See [User Guide examples](docs/USER_GUIDE.md#common-use-cases)

---

**Quick Navigation:**
- [🏠 Back to README](README.md)
- [👤 User Guide](docs/USER_GUIDE.md)
- [🚀 Deployment Guide](docs/DEPLOYMENT_GUIDE.md)
- [👨‍💻 API Reference](docs/API_REFERENCE.md)
- [🤝 Contributing](CONTRIBUTING.md)
