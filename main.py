#!/usr/bin/env python3
"""
Skynet Lite - Local AI Chatbot with Web Search
A lightweight chatbot powered by Ollama + Mistral and Bing Search
"""

import asyncio
from typing import Optional
import semantic_kernel as sk

from models.loader import OllamaModelLoader
from tools.web_search import BingSearchTool
from plugins.memory import ChatMemoryManager
from config import Config


class SkynetLite:
    """Main Skynet Lite chatbot orchestrator"""
    
    def __init__(self):
        self.config = Config()
        self.kernel = sk.Kernel()
        self.model_loader = OllamaModelLoader()
        self.search_tool = BingSearchTool(self.config.bing_api_key)
        self.memory_manager = ChatMemoryManager()
        
    async def initialize(self) -> bool:
        """Initialize the chatbot components"""
        print("🚀 Initializing Skynet Lite...")
        
        # Check if Ollama model is available
        if not await self.model_loader.ensure_model_available(self.config.ollama_model):
            print("❌ Failed to initialize Ollama model")
            return False
        
        print("🧠 Connecting to Ollama...")
        
        # Skip semantic-kernel Ollama connector to avoid version compatibility issues
        # Use direct model_loader integration instead
        
        # Set up web search capabilities
        if self.config.bing_api_key:
            print("🔍 Bing Search ready")
        else:
            print("⚠️  No Bing API key found. Web search disabled.")
        
        print("✅ Skynet Lite ready for action!")
        return True
        
    async def chat_loop(self) -> None:
        """Main chat interaction loop"""
        print("\n💬 Chat with Skynet Lite (type 'quit' to exit)")
        print("=" * 50)
        
        while True:
            try:
                user_input = input("\nYou: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    print("🤖 Goodbye! Skynet Lite signing off.")
                    break
                
                if not user_input:
                    continue
                
                # Add to memory
                self.memory_manager.add_user_message(user_input)
                
                # Check if web search is needed
                if await self._needs_web_search(user_input):
                    response = await self._handle_web_search_query(user_input)
                else:
                    response = await self._handle_local_query(user_input)
                
                print(f"\n🤖 Skynet: {response}")
                
                # Add response to memory
                self.memory_manager.add_assistant_message(response)
                
            except KeyboardInterrupt:
                print("\n\n🤖 Goodbye! Skynet Lite signing off.")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                
    async def _needs_web_search(self, query: str) -> bool:
        """Determine if query needs web search based on keywords"""
        web_indicators = [
            "latest", "recent", "news", "current", "today", "now",
            "weather", "stock", "price", "update", "what's happening",
            "breaking", "live", "trending", "market", "bitcoin"
        ]
        return any(indicator in query.lower() for indicator in web_indicators)
    
    async def _handle_web_search_query(self, query: str) -> str:
        """Handle queries that require web search"""
        if not self.config.bing_api_key:
            return "I need a Bing API key to search the web. Please configure it in config.yaml or set BING_API_KEY environment variable."
        
        try:
            print("🔍 Searching the web...")
            # Get search results
            search_results = await self.search_tool.search_and_summarize(query, max_results=3)
            
            # Use local LLM to process the search results
            full_prompt = f"""Based on the following search results, provide a helpful answer to the user's question: "{query}"

Search Results:
{search_results}

Please provide a concise, accurate answer based on this information. Be specific and cite key facts from the search results."""
            
            return await self.model_loader.generate_completion(full_prompt, self.config.ollama_model)
            
        except Exception as e:
            return f"Sorry, I encountered an error while searching: {str(e)}"
    
    async def _handle_local_query(self, query: str) -> str:
        """Handle queries using local LLM only"""
        try:
            # Get conversation history for context
            history = self.memory_manager.get_conversation_history()
            
            # Create prompt with context
            if history and history != "No conversation history yet.":
                full_prompt = f"""Previous conversation:
{history}

User: {query}
Assistant:"""
            else:
                full_prompt = f"""You are Skynet Lite, a helpful AI assistant powered by local AI technology. You are knowledgeable, friendly, and provide accurate information. Respond naturally and helpfully to the user's question.

User: {query}
Assistant:"""
            
            response = await self.model_loader.generate_completion(full_prompt, self.config.ollama_model)
            return response or "I'm having trouble generating a response right now. Please try again."
            
        except Exception as e:
            return f"Sorry, I encountered an error: {str(e)}"


async def main() -> None:
    """Main entry point for Skynet Lite"""
    chatbot = SkynetLite()
    
    try:
        if await chatbot.initialize():
            await chatbot.chat_loop()
        else:
            print("❌ Failed to initialize Skynet Lite")
            print("🔧 Make sure Ollama is running: ollama serve")
            print("🔧 And ensure the model is available: ollama pull mistral")
    except Exception as e:
        print(f"❌ Failed to start Skynet Lite: {e}")
        print("🔧 Make sure Ollama is running: ollama serve")
    finally:
        # Clean up resources
        try:
            await chatbot.model_loader.close()
            await chatbot.search_tool.close()
        except Exception as cleanup_error:
            print(f"⚠️  Warning during cleanup: {cleanup_error}")


if __name__ == "__main__":
    asyncio.run(main())