# loaders/claude_loader.py
import aiohttp
import json
import logging
import os
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)

class ClaudeModelLoader:
    """Claude model loader using Anthropic's API"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        self.base_url = "https://api.anthropic.com/v1"
        self.session = None
        self.model_name = "claude-3-5-sonnet-20241022"  # Latest Claude model
        self.available_models = [
            "claude-3-5-sonnet-20241022",
            "claude-3-5-haiku-20241022", 
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307"
        ]
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def initialize(self) -> bool:
        """Initialize the session and check API key"""
        if not self.api_key:
            logger.error("No Anthropic API key provided. Set ANTHROPIC_API_KEY environment variable.")
            return False
        
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        # Test API connection
        try:
            headers = {
                "x-api-key": self.api_key,
                "content-type": "application/json",
                "anthropic-version": "2023-06-01"
            }
            
            # Make a simple test request
            test_payload = {
                "model": self.model_name,
                "max_tokens": 10,
                "messages": [{"role": "user", "content": "Hi"}]
            }
            
            async with self.session.post(
                f"{self.base_url}/messages",
                json=test_payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status == 200:
                    logger.info(f"Connected to Claude API successfully. Using model: {self.model_name}")
                    return True
                else:
                    error_text = await response.text()
                    logger.error(f"Failed to connect to Claude API: {response.status} - {error_text}")
                    return False
                    
        except Exception as e:
            logger.error(f"Failed to connect to Claude API: {e}")
            return False
    
    async def ensure_model_available(self, model_name: str = None) -> bool:
        """Check if model is available (Claude models are always available via API)"""
        if model_name and model_name in self.available_models:
            self.model_name = model_name
            logger.info(f"Using Claude model: {self.model_name}")
            return True
        elif not model_name:
            logger.info(f"Using default Claude model: {self.model_name}")
            return True
        else:
            logger.warning(f"Model {model_name} not in available models. Using default: {self.model_name}")
            return True
    
    async def load_model(self, model_name: str = None) -> str:
        """Load/verify model is ready"""
        if await self.ensure_model_available(model_name):
            return f"Claude model '{self.model_name}' ready"
        else:
            raise RuntimeError(f"Failed to load Claude model")
    
    async def generate_completion(self, prompt: str, model_name: str = None) -> str:
        """Generate text completion using Claude API"""
        if not self.session:
            await self.initialize()
        
        if not self.api_key:
            raise RuntimeError("No Anthropic API key available")
        
        model = model_name or self.model_name
        
        try:
            headers = {
                "x-api-key": self.api_key,
                "content-type": "application/json",
                "anthropic-version": "2023-06-01"
            }
            
            # Format as a message for Claude
            payload = {
                "model": model,
                "max_tokens": 1024,
                "temperature": 0.7,
                "messages": [
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ]
            }
            
            async with self.session.post(
                f"{self.base_url}/messages",
                json=payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=60)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    # Extract text from Claude's response format
                    content = data.get('content', [])
                    if content and isinstance(content, list) and len(content) > 0:
                        return content[0].get('text', '').strip()
                    else:
                        return "No response from Claude"
                else:
                    error_text = await response.text()
                    logger.error(f"Claude API error: {response.status} - {error_text}")
                    raise RuntimeError(f"Claude API error: {response.status}")
                    
        except Exception as e:
            logger.error(f"Error generating completion with Claude: {e}")
            raise
    
    async def chat(self, message: str, model_name: str = None, conversation_history: Optional[List[Dict]] = None) -> str:
        """Chat with Claude using conversation format"""
        if not self.session:
            await self.initialize()
        
        if not self.api_key:
            raise RuntimeError("No Anthropic API key available")
        
        model = model_name or self.model_name
        
        try:
            headers = {
                "x-api-key": self.api_key,
                "content-type": "application/json",
                "anthropic-version": "2023-06-01"
            }
            
            # Build messages array
            messages = []
            if conversation_history:
                # Convert from your format to Claude's format if needed
                for entry in conversation_history:
                    if entry.get('role') in ['user', 'assistant']:
                        messages.append({
                            "role": entry['role'],
                            "content": entry['content']
                        })
            
            # Add current message
            messages.append({
                "role": "user",
                "content": message
            })
            
            payload = {
                "model": model,
                "max_tokens": 1024,
                "temperature": 0.7,
                "messages": messages
            }
            
            async with self.session.post(
                f"{self.base_url}/messages",
                json=payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=60)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    # Extract text from Claude's response format
                    content = data.get('content', [])
                    if content and isinstance(content, list) and len(content) > 0:
                        return content[0].get('text', '').strip()
                    else:
                        return "No response from Claude"
                else:
                    error_text = await response.text()
                    logger.error(f"Claude chat API error: {response.status} - {error_text}")
                    raise RuntimeError(f"Claude chat API error: {response.status}")
                    
        except Exception as e:
            logger.error(f"Error in Claude chat: {e}")
            raise
    
    async def close(self):
        """Close the HTTP session"""
        if self.session:
            await self.session.close()
            self.session = None
    
    def get_available_models(self) -> List[str]:
        """Get list of available Claude models"""
        return self.available_models
