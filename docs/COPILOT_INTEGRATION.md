# GitHub Copilot Integration Guide

This guide explains how to integrate GitHub Copilot with Skynet Lite as an AI model provider.

## Overview

GitHub Copilot integration in Skynet Lite allows you to use Copilot as a fallback AI model when local Ollama is unavailable or when you prefer cloud-based AI assistance.

## Important Note

GitHub Copilot does **not** provide a public REST API for chat completions like OpenAI or Anthropic. The integration requires one of the following:

1. **Enterprise GitHub Copilot** - Access to internal Copilot APIs
2. **Custom Proxy Endpoint** - Your own proxy that accepts Copilot tokens
3. **Modified Implementation** - Custom integration using VS Code extension APIs

## Configuration

### Environment Variables

Add these to your `.env` file:

```bash
# GitHub Copilot Configuration
GITHUB_COPILOT_TOKEN=your_github_copilot_token_here
COPILOT_API_URL=https://api.github.com/copilot/chat/completions
COPILOT_MODEL=copilot
```

### Configuration Details

| Variable | Description | Required |
|----------|-------------|----------|
| `GITHUB_COPILOT_TOKEN` | Your GitHub Copilot authentication token | Yes |
| `COPILOT_API_URL` | API endpoint for Copilot completions | Yes |
| `COPILOT_MODEL` | Model identifier (default: "copilot") | No |

## Getting a Copilot Token

### Option 1: GitHub Copilot for Business/Enterprise

If you have access to GitHub Copilot for Business or Enterprise:

1. Contact your GitHub organization administrator
2. Request API access credentials
3. Follow your organization's internal documentation

### Option 2: Custom Proxy Implementation

You can create a proxy service that:

1. Accepts your Copilot subscription credentials
2. Interfaces with VS Code Copilot extension APIs
3. Provides REST API compatibility

Example proxy architecture:
```
Skynet Lite → Your Proxy Server → VS Code Copilot Extension → GitHub Copilot
```

### Option 3: Development Integration

For development purposes, you can:

1. Use VS Code with Copilot extension
2. Create a local proxy that communicates with the extension
3. Route requests through the local development setup

## Testing the Integration

Once configured, test Copilot integration:

```bash
# Run the integration test
python3 test_integration.py

# Or test manually in console
python3 main.py
```

If Copilot is properly configured and other models are unavailable, you should see:
```
Using CopilotModelLoader
🤖 Skynet: Hello! I'm powered by GitHub Copilot...
```

## Troubleshooting

### Common Issues

**Error: "Copilot token or API URL not configured"**
- Ensure `GITHUB_COPILOT_TOKEN` and `COPILOT_API_URL` are set
- Check that your `.env` file is in the project root

**Error: "Failed to initialize Copilot loader"**
- Verify your token is valid
- Check that the API URL is accessible
- Ensure you have proper network connectivity

**Error: "CopilotModelLoader not available"**
- Check that `httpx` is installed: `pip install httpx`
- Verify the copilot_loader.py file exists in the loaders/ directory

### Debug Mode

Enable debug logging to troubleshoot issues:

```bash
export LOG_LEVEL=DEBUG
python3 main.py
```

### Network Testing

Test your Copilot endpoint manually:

```bash
curl -X POST "your_copilot_api_url" \
  -H "Authorization: Bearer your_copilot_token" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "copilot",
    "prompt": "Hello, world!",
    "max_tokens": 100
  }'
```

## Fallback Behavior

Skynet Lite tries AI models in this order:

1. **Ollama** (Primary - Local LLM)
2. **OpenAI** (if `OPENAI_API_KEY` is set)
3. **Claude** (if `ANTHROPIC_API_KEY` is set)
4. **Copilot** (if `GITHUB_COPILOT_TOKEN` is set)
5. **Gemini** (if `GOOGLE_API_KEY` is set)
6. **Local fallback** (Basic responses)

## Security Considerations

- Keep your Copilot token secure and never commit it to version control
- Use environment variables or secure secret management
- Consider token rotation and expiration policies
- Monitor API usage and costs (if applicable)

## Alternative Solutions

If you cannot get direct Copilot API access, consider:

1. **OpenAI GPT-4** - Similar capabilities with public API
2. **Anthropic Claude** - Advanced reasoning and coding assistance
3. **Google Gemini Pro** - Multimodal AI capabilities
4. **Local models via Ollama** - Privacy-focused, no API keys required

## Support

For Copilot-specific integration issues:

1. Check the [GitHub Copilot documentation](https://docs.github.com/en/copilot)
2. Review the `loaders/copilot_loader.py` implementation
3. Open an issue in the Skynet Lite repository with debug logs
4. Consult your organization's Copilot administrators (for enterprise users)
