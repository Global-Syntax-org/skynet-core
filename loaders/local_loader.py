# loaders/local_loader.py
import logging
import random
from typing import Optional, List, Dict

logger = logging.getLogger(__name__)

class LocalModelLoader:
    """
    Fallback local model loader that provides basic responses
    This is used when neither Ollama nor Claude are available
    """
    
    def __init__(self):
        self.model_name = "fallback-local"
        self.responses = [
            "I'm running in local fallback mode. For better responses, please set up Ollama or provide an Anthropic API key.",
            "This is a basic fallback response. Consider installing Ollama for local AI or using Claude for advanced capabilities.",
            "I'm operating with limited functionality. To unlock full AI capabilities, please configure Ollama or Claude.",
            "Local fallback mode active. For intelligent responses, please set up a proper AI backend.",
            "I can provide basic interactions, but for real AI conversations, please configure Ollama or Claude."
        ]
    
    async def initialize(self) -> bool:
        """Initialize the local fallback loader"""
        logger.info("Initialized LocalModelLoader (fallback mode)")
        return True
    
    async def ensure_model_available(self) -> bool:
        """Model is always 'available' in fallback mode"""
        logger.info("LocalModelLoader: Using fallback responses")
        return True
    
    async def load_model(self) -> str:
        """Load the fallback model"""
        return "Local fallback model loaded"
    
    async def generate_completion(self, prompt: str, model_name: str = None) -> str:
        """Generate a basic completion response"""
        try:
            # Simple keyword-based responses
            prompt_lower = prompt.lower()
            
            if any(word in prompt_lower for word in ['hello', 'hi', 'hey', 'greetings']):
                return "Hello! I'm running in fallback mode. For better AI responses, please set up Ollama or Claude."
            
            elif any(word in prompt_lower for word in ['help', 'support', 'assist']):
                return """I can provide basic help. To get full AI capabilities:
                
1. For local AI: Install and run Ollama
   - Install: curl -fsSL https://ollama.com/install.sh | sh
   - Run: ollama serve
   - Pull a model: ollama pull mistral
   
2. For cloud AI: Get an Anthropic API key
   - Set: export ANTHROPIC_API_KEY="your_key_here"
   
Then restart this chatbot for full functionality."""
            
            elif any(word in prompt_lower for word in ['weather', 'news', 'current', 'latest']):
                return "I cannot access real-time information in fallback mode. Please set up Ollama or Claude for web search capabilities."
            
            elif any(word in prompt_lower for word in ['quit', 'exit', 'bye', 'goodbye']):
                return "Goodbye! Consider setting up Ollama or Claude for better conversations next time."
            
            else:
                # Return a random fallback response
                base_response = random.choice(self.responses)
                return f"You asked: '{prompt}'\n\n{base_response}"
                
        except Exception as e:
            logger.error(f"Error in LocalModelLoader.generate_completion: {e}")
            return "I encountered an error in fallback mode. Please set up Ollama or Claude for reliable AI responses."
    
    async def chat(self, message: str, model_name: str = None, conversation_history: Optional[List] = None) -> str:
        """Chat using the fallback model"""
        return await self.generate_completion(message, model_name)
    
    async def close(self):
        """Clean up resources (nothing to clean up in fallback mode)"""
        pass
    
    def get_available_models(self) -> List[str]:
        """Get list of available models"""
        return [self.model_name]
