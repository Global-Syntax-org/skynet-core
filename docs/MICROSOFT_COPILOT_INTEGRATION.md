# Microsoft Copilot Integration Guide

This guide explains how to integrate Microsoft Copilot with Skynet Lite as an AI model provider.

## Overview

Microsoft Copilot integration allows you to use Microsoft's AI assistant (formerly Bing Chat) as a fallback AI model when local Ollama is unavailable or when you prefer cloud-based AI assistance with Microsoft's technology stack.

## Microsoft Copilot vs GitHub Copilot

- **Microsoft Copilot**: General-purpose AI assistant, conversational AI, web search integration
- **GitHub Copilot**: Code-focused AI assistant, programming help, developer tools

This guide covers **Microsoft Copilot** integration.

## Prerequisites

You need one of the following:

1. **Azure Cognitive Services** subscription with Copilot API access
2. **Microsoft Graph API** access with Copilot permissions
3. **Microsoft 365 Copilot** enterprise subscription
4. **Azure OpenAI Service** with Copilot models

## Configuration

### Environment Variables

Add these to your `.env` file:

```bash
# Microsoft Copilot Configuration
MICROSOFT_COPILOT_API_KEY=your_microsoft_copilot_api_key_here
MICROSOFT_COPILOT_ENDPOINT=https://api.cognitive.microsoft.com/copilot/v1/chat/completions
MICROSOFT_COPILOT_MODEL=copilot
```

### Configuration Details

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `MICROSOFT_COPILOT_API_KEY` | Your Microsoft API key or subscription key | Yes | None |
| `MICROSOFT_COPILOT_ENDPOINT` | API endpoint for Microsoft Copilot | No | Azure Cognitive Services endpoint |
| `MICROSOFT_COPILOT_MODEL` | Model identifier | No | "copilot" |

## Getting API Access

### Option 1: Azure Cognitive Services

1. Create an [Azure account](https://azure.microsoft.com/free/)
2. Create a Cognitive Services resource in Azure Portal
3. Navigate to "Keys and Endpoint" section
4. Copy your subscription key and endpoint

```bash
# Example Azure configuration
MICROSOFT_COPILOT_API_KEY=your_azure_subscription_key
MICROSOFT_COPILOT_ENDPOINT=https://your-resource.cognitiveservices.azure.com/copilot/v1/chat/completions
```

### Option 2: Microsoft Graph API

1. Register an application in [Azure AD](https://portal.azure.com/)
2. Grant necessary permissions for Copilot access
3. Generate client credentials
4. Use OAuth2 flow for authentication

```bash
# Example Graph API configuration
MICROSOFT_COPILOT_API_KEY=your_graph_api_token
MICROSOFT_COPILOT_ENDPOINT=https://graph.microsoft.com/v1.0/copilot/chat/completions
```

### Option 3: Azure OpenAI Service

If using Azure OpenAI with Copilot-enabled models:

```bash
# Example Azure OpenAI configuration
MICROSOFT_COPILOT_API_KEY=your_azure_openai_key
MICROSOFT_COPILOT_ENDPOINT=https://your-resource.openai.azure.com/openai/deployments/copilot/chat/completions?api-version=2024-02-15-preview
```

## Testing the Integration

### Basic Test

```bash
# Test Microsoft Copilot configuration
python3 test_microsoft_copilot.py
```

### Manual Testing

```python
import asyncio
from loaders.microsoft_copilot_loader import MicrosoftCopilotLoader

async def test_ms_copilot():
    loader = MicrosoftCopilotLoader()
    if await loader.initialize():
        response = await loader.generate_completion("Hello, Microsoft Copilot!")
        print(f"Response: {response}")
        await loader.close()

asyncio.run(test_ms_copilot())
```

### Integration Test

Once configured, test in Skynet Lite:

```bash
# Run Skynet with Microsoft Copilot
python3 main.py
```

If properly configured and other models are unavailable, you should see:
```
Using MicrosoftCopilotLoader
🤖 Skynet: Hello! I'm powered by Microsoft Copilot...
```

## Features & Capabilities

### Conversation Context
- Maintains conversation history within sessions
- Context-aware responses
- Conversation reset capability

### Response Quality
- High-quality natural language responses
- Web-aware information (when available)
- Multi-turn conversation support

### Integration Benefits
- Seamless fallback when local models unavailable
- Enterprise-grade security and compliance
- Microsoft ecosystem integration

## Troubleshooting

### Common Issues

**Error: "Microsoft Copilot API key not configured"**
- Ensure `MICROSOFT_COPILOT_API_KEY` is set in your environment
- Check that your `.env` file is in the project root
- Verify the API key is valid and not expired

**Error: "Failed to initialize Microsoft Copilot"**
- Verify your API key has proper permissions
- Check that the endpoint URL is correct
- Ensure you have network connectivity to Microsoft services

**Error: "Authentication failed - check API key"**
- Verify your subscription key is active
- Check billing status in Azure Portal
- Ensure the resource isn't suspended

**Error: "Access forbidden - check permissions"**
- Verify your API key has Copilot access permissions
- Check Azure AD app permissions (for Graph API)
- Ensure the subscription includes Copilot services

### Debug Mode

Enable debug logging to troubleshoot issues:

```bash
export LOG_LEVEL=DEBUG
python3 main.py
```

### Network Testing

Test your Microsoft Copilot endpoint manually:

```bash
curl -X POST "https://your-endpoint.com/copilot/v1/chat/completions" \
  -H "Ocp-Apim-Subscription-Key: your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Hello"}],
    "model": "copilot",
    "max_tokens": 100
  }'
```

## Fallback Behavior

Skynet Lite tries AI models in this order:

1. **Ollama** (Primary - Local LLM)
2. **OpenAI** (if `OPENAI_API_KEY` is set)
3. **Claude** (if `ANTHROPIC_API_KEY` is set)
4. **GitHub Copilot** (if `GITHUB_COPILOT_TOKEN` is set)
5. **Microsoft Copilot** (if `MICROSOFT_COPILOT_API_KEY` is set)
6. **Gemini** (if `GOOGLE_API_KEY` is set)
7. **Local fallback** (Basic responses)

## Security Considerations

### API Key Security
- Keep your API keys secure and never commit them to version control
- Use environment variables or Azure Key Vault for production
- Implement key rotation policies
- Monitor API usage and costs

### Data Privacy
- Microsoft Copilot processes data in Microsoft cloud
- Review Microsoft's data processing policies
- Consider data residency requirements
- Implement appropriate data classification

### Network Security
- Use HTTPS endpoints only
- Consider VPN or private endpoints for enterprise deployments
- Implement proper firewall rules
- Monitor network traffic

## Cost Management

### Monitoring Usage
- Track API calls and token usage
- Set up billing alerts in Azure Portal
- Monitor costs regularly
- Implement usage quotas if needed

### Optimization Tips
- Use appropriate `max_tokens` limits
- Implement caching for repeated queries
- Consider request batching where possible
- Monitor and optimize conversation length

## Alternative Solutions

If you cannot get Microsoft Copilot API access, consider:

1. **Azure OpenAI Service** - Direct access to GPT models via Azure
2. **OpenAI GPT-4** - Similar capabilities with public API
3. **Anthropic Claude** - Advanced reasoning capabilities
4. **Google Gemini Pro** - Multimodal AI capabilities
5. **Local models via Ollama** - Privacy-focused, no API keys required

## Enterprise Integration

### Microsoft 365 Integration
- Integrate with Microsoft Graph for enhanced context
- Access organizational data (with proper permissions)
- Leverage Microsoft 365 Copilot features

### Azure Integration
- Use Azure Key Vault for secrets management
- Implement Azure AD authentication
- Leverage Azure monitoring and logging

### Compliance
- Microsoft Copilot supports enterprise compliance requirements
- GDPR, HIPAA, SOC 2 compliance available
- Data residency options in supported regions

## Support

For Microsoft Copilot-specific integration issues:

1. Check [Microsoft Copilot documentation](https://docs.microsoft.com/copilot)
2. Review [Azure Cognitive Services docs](https://docs.microsoft.com/azure/cognitive-services)
3. Check the `loaders/microsoft_copilot_loader.py` implementation
4. Open an issue in the Skynet Lite repository with debug logs
5. Contact Microsoft Azure support for API-related issues

## API Reference

### Environment Variables
```bash
MICROSOFT_COPILOT_API_KEY=<your_api_key>
MICROSOFT_COPILOT_ENDPOINT=<api_endpoint>
MICROSOFT_COPILOT_MODEL=<model_name>
```

### Python Usage
```python
from loaders.microsoft_copilot_loader import MicrosoftCopilotLoader

# Initialize
loader = MicrosoftCopilotLoader()
await loader.initialize()

# Generate completion
response = await loader.generate_completion("Your prompt here")

# Reset conversation context
await loader.reset_conversation()

# Clean up
await loader.close()
```
