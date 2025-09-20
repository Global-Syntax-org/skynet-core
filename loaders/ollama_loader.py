# loaders/ollama_loader.py
import aiohttp
import json
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class OllamaModelLoader:
    """Ollama model loader with HTTP API integration"""
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.session = None
        self.available_models = []
    
    def _get_resolved_url(self, endpoint: str = "") -> str:
        """Get URL with localhost resolved to 127.0.0.1 to avoid IPv6 issues"""
        resolved_base = self.base_url.replace('localhost', '127.0.0.1')
        return f"{resolved_base}{endpoint}"
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def initialize(self):
        """Initialize the session and check Ollama availability"""
        if not self.session:
            # Create aiohttp session with IPv4-only connector to avoid IPv6 issues
            connector = aiohttp.TCPConnector(
                family=2,  # Force IPv4 (socket.AF_INET)
                local_addr=None,
                limit=30,
                limit_per_host=8,
            )
            timeout = aiohttp.ClientTimeout(total=10, connect=5)
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout
            )
        
        try:
            # Test connection to Ollama with explicit localhost resolution
            async with self.session.get(self._get_resolved_url("/api/tags")) as response:
                if response.status == 200:
                    data = await response.json()
                    self.available_models = [model['name'] for model in data.get('models', [])]
                    logger.info(f"Connected to Ollama. Available models: {self.available_models}")
                    return True
                else:
                    logger.error(f"Failed to connect to Ollama: HTTP {response.status}")
                    return False
        except Exception as e:
            logger.error(f"Failed to connect to Ollama: {e}")
            return False
    
    async def ensure_model_available(self, model_name: str = "mistral") -> bool:
        """Check if model is available, pull it if not"""
        if not self.available_models:
            await self.initialize()
        
        # Check for exact match or with :latest tag
        model_variants = [model_name, f"{model_name}:latest"]
        if model_name.endswith(":latest"):
            base_name = model_name.replace(":latest", "")
            model_variants.append(base_name)
        
        for variant in model_variants:
            if variant in self.available_models:
                logger.info(f"Model {variant} is available")
                return True
        
        logger.info(f"Model {model_name} not found. Attempting to pull...")
        try:
            async with self.session.post(
                self._get_resolved_url("/api/pull"),
                json={"name": model_name}
            ) as response:
                if response.status == 200:
                    # Stream the pull response
                    async for line in response.content:
                        if line:
                            try:
                                data = json.loads(line.decode())
                                if 'status' in data:
                                    print(f"📥 {data['status']}")
                                if data.get('status') == 'success':
                                    break
                            except json.JSONDecodeError:
                                continue
                    
                    # Refresh available models
                    await self.initialize()
                    return model_name in self.available_models
                else:
                    logger.error(f"Failed to pull model: HTTP {response.status}")
                    return False
        except Exception as e:
            logger.error(f"Error pulling model {model_name}: {e}")
            return False
    
    async def load_model(self, model_name: str = "mistral") -> str:
        """Load/verify model is ready"""
        if await self.ensure_model_available(model_name):
            return f"Ollama model '{model_name}' loaded successfully"
        else:
            raise RuntimeError(f"Failed to load model '{model_name}'")
    
    async def generate_completion(self, prompt: str, model_name: str = "mistral") -> str:
        """Generate text completion using Ollama API"""
        if not self.session:
            await self.initialize()
        
        try:
            payload = {
                "model": model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "top_k": 40,
                    "num_predict": 512
                }
            }
            
            async with self.session.post(
                self._get_resolved_url("/api/generate"),
                json=payload,
                timeout=aiohttp.ClientTimeout(total=60)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('response', '').strip()
                else:
                    error_text = await response.text()
                    logger.error(f"Ollama API error: {response.status} - {error_text}")
                    raise RuntimeError(f"Ollama API error: {response.status}")
                    
        except Exception as e:
            logger.error(f"Error generating completion: {e}")
            raise
    
    async def chat(self, message: str, model_name: str = "mistral", conversation_history: Optional[list] = None) -> str:
        """Chat with model using conversation format"""
        if not self.session:
            await self.initialize()
        
        try:
            # Build messages array
            messages = []
            if conversation_history:
                messages.extend(conversation_history)
            messages.append({"role": "user", "content": message})
            
            payload = {
                "model": model_name,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "top_k": 40
                }
            }
            
            async with self.session.post(
                self._get_resolved_url("/api/chat"),
                json=payload,
                timeout=aiohttp.ClientTimeout(total=60)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('message', {}).get('content', '').strip()
                else:
                    error_text = await response.text()
                    logger.error(f"Ollama chat API error: {response.status} - {error_text}")
                    raise RuntimeError(f"Ollama chat API error: {response.status}")
                    
        except Exception as e:
            logger.error(f"Error in chat: {e}")
            raise
    
    async def close(self):
        """Close the HTTP session"""
        if self.session:
            await self.session.close()
            self.session = None
    
    def get_available_models(self) -> list:
        """Get list of available models"""
        return self.available_models
