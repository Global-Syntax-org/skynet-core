#!/usr/bin/env python3
"""
Skynet Lite - Local AI Chatbot with Web Search
A lightweight chatbot powered by Ollama + Mistral and Bing Search
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import asyncio
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SkynetLite")


class LoaderManager:
    """Manages different model loaders with fallback support"""
    
    def __init__(self):
        self.loader = None
        self.model = None

    async def initialize(self):
        """Initialize the best available model loader"""
        # Try Ollama first
        try:
            from loaders.ollama_loader import OllamaModelLoader
            self.loader = OllamaModelLoader()
            
            # Initialize and test connection
            if not await self.loader.initialize():
                raise RuntimeError("Failed to connect to Ollama")
            
            logger.info("Using OllamaModelLoader")
            return True
        except (ModuleNotFoundError, ImportError):
            logger.warning("OllamaModelLoader not available. Trying Claude.")
        except Exception as e:
            logger.warning(f"Failed to initialize OllamaModelLoader: {e}. Trying Claude.")
        
        # Try OpenAI (ChatGPT) next if API key is available
        if os.getenv('OPENAI_API_KEY'):
            try:
                from loaders.openai_loader import OpenAIModelLoader
                self.loader = OpenAIModelLoader()
                if not await self.loader.initialize():
                    raise RuntimeError("Failed to initialize OpenAI loader")
                logger.info("Using OpenAIModelLoader")
                return True
            except (ModuleNotFoundError, ImportError) as e:
                logger.warning(f"OpenAIModelLoader not available: {e}")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAIModelLoader: {e}")

        # Try Gemini (Google) next if API key is available
        if os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY'):
            try:
                from loaders.gemini_loader import GeminiModelLoader
                self.loader = GeminiModelLoader()
                if not await self.loader.initialize():
                    raise RuntimeError("Failed to initialize Gemini loader")
                logger.info("Using GeminiModelLoader")
                return True
            except (ModuleNotFoundError, ImportError) as e:
                logger.warning(f"GeminiModelLoader not available: {e}")
            except Exception as e:
                logger.error(f"Failed to initialize GeminiModelLoader: {e}")

        # Try Claude second if API key is available
        if os.getenv('ANTHROPIC_API_KEY'):
            try:
                from loaders.claude_loader import ClaudeModelLoader
                self.loader = ClaudeModelLoader()
                
                # Initialize and test connection
                if not await self.loader.initialize():
                    raise RuntimeError("Failed to connect to Claude API")
                
                logger.info("Using ClaudeModelLoader")
                return True
            except (ModuleNotFoundError, ImportError) as e:
                logger.warning(f"ClaudeModelLoader not available: {e}")
            except Exception as e:
                logger.error(f"Failed to initialize ClaudeModelLoader: {e}")
        else:
            logger.info("No ANTHROPIC_API_KEY found, skipping Claude.")
        
        # Try Copilot if token is available
        if os.getenv('GITHUB_COPILOT_TOKEN'):
            try:
                from loaders.copilot_loader import CopilotModelLoader
                self.loader = CopilotModelLoader()
                if not await self.loader.initialize():
                    raise RuntimeError("Failed to initialize Copilot loader")
                logger.info("Using CopilotModelLoader")
                return True
            except (ModuleNotFoundError, ImportError) as e:
                logger.warning(f"CopilotModelLoader not available: {e}")
            except Exception as e:
                logger.error(f"Failed to initialize CopilotModelLoader: {e}")

        # Fall back to LocalModelLoader
        try:
            from loaders.local_loader import LocalModelLoader
            self.loader = LocalModelLoader()
            logger.info("Using LocalModelLoader")
        except (ModuleNotFoundError, ImportError):
            logger.error("No model loaders available. Aborting.")
            raise RuntimeError("No compatible model loaders found")
        
        return True

    async def shutdown(self):
        """Clean up resources"""
        if self.loader and hasattr(self.loader, 'close'):
            await self.loader.close()


class MemoryManager:
    """Simple conversation memory management"""
    
    def __init__(self, max_history=10):
        self.conversation_history = []
        self.max_history = max_history
    
    def add_user_message(self, message: str):
        self.conversation_history.append({"role": "user", "content": message})
        self._trim_history()
    
    def add_assistant_message(self, message: str):
        self.conversation_history.append({"role": "assistant", "content": message})
        self._trim_history()
    
    def _trim_history(self):
        if len(self.conversation_history) > self.max_history * 2:  # *2 for user+assistant pairs
            self.conversation_history = self.conversation_history[-self.max_history * 2:]
    
    def get_conversation_history(self) -> str:
        if not self.conversation_history:
            return "No conversation history yet."
        
        history = []
        for entry in self.conversation_history[-6:]:  # Last 3 exchanges
            role = entry["role"].title()
            content = entry["content"]
            history.append(f"{role}: {content}")
        
        return "\n".join(history)


class SkynetLite:
    """Main chatbot class"""
    
    def __init__(self):
        self.loader_manager = LoaderManager()
        self.memory_manager = MemoryManager()
        self.search_tool = None
        self.config = self._load_config()
    
    def _load_config(self):
        """Load configuration using the proper Config class"""
        from config import Config
        return Config()
    
    async def initialize(self) -> bool:
        """Initialize the chatbot"""
        try:
            await self.loader_manager.initialize()
            
            # Ensure the model is available (only if the method exists and takes the right parameters)
            if hasattr(self.loader_manager.loader, 'ensure_model_available'):
                try:
                    # Check method signature - some loaders might not take model name parameter
                    import inspect
                    sig = inspect.signature(self.loader_manager.loader.ensure_model_available)
                    param_count = len(sig.parameters)
                    
                    if param_count > 1:  # Method takes model name parameter
                        model_ready = await self.loader_manager.loader.ensure_model_available(self.config.ollama_model)
                    else:  # Method takes no parameters
                        model_ready = await self.loader_manager.loader.ensure_model_available()
                    
                    if not model_ready:
                        logger.warning(f"Model {self.config.ollama_model} may not be ready, but continuing...")
                except Exception as e:
                    logger.warning(f"Could not verify model availability: {e}")
            
            # Initialize search tool based on configuration
            try:
                from tools.web_search import create_search_tool
                self.search_tool = await create_search_tool(
                    provider=getattr(self.config, 'search_provider', 'duckduckgo'),
                    use_instant_only=not getattr(self.config, 'search_use_instant_answers', True)
                )
                logger.info(f"Initialized {self.config.search_provider} search tool")
            except ImportError:
                logger.warning("Search tools not available. Web search disabled.")
            except Exception as e:
                logger.warning(f"Failed to initialize search tool: {e}. Web search disabled.")
            
            logger.info("Skynet Lite initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Skynet Lite: {e}")
            return False
    
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
                logger.error(f"Error in chat loop: {e}")
                print(f"\n❌ Error: {e}")
    
    async def _needs_web_search(self, query: str) -> bool:
        """Determine if query needs web search based on keywords"""
        if not self.search_tool:
            return False
        
        web_indicators = [
            "latest", "recent", "news", "current", "today", "now",
            "weather", "stock", "price", "update", "what's happening",
            "breaking", "live", "trending", "market", "bitcoin",
            "search", "look up", "find information"
        ]
        
        return any(indicator in query.lower() for indicator in web_indicators)
    
    async def _handle_web_search_query(self, query: str) -> str:
        """Handle queries that require web search"""
        try:
            print("🔍 Searching the web...")
            # Get search results using DuckDuckGo
            search_results = await self.search_tool.search_and_summarize(query, max_results=3)
            
            # Use local LLM to process the search results
            full_prompt = f"""Based on the following search results, provide a helpful answer to the user's question: "{query}"

Search Results:
{search_results}

Please provide a concise, accurate answer based on this information. Be specific and cite key facts from the search results."""
            
            return await self._generate_completion(full_prompt)
            
        except Exception as e:
            logger.error(f"Web search error: {e}")
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
            
            response = await self._generate_completion(full_prompt)
            return response or "I'm having trouble generating a response right now. Please try again."
            
        except Exception as e:
            logger.error(f"Local query error: {e}")
            return f"Sorry, I encountered an error: {str(e)}"
    
    async def _generate_completion(self, prompt: str) -> str:
        """Generate completion using the loaded model"""
        try:
            loader = self.loader_manager.loader
            
            # Try different method names that might exist in your OllamaModelLoader
            if hasattr(loader, 'generate_completion'):
                return await loader.generate_completion(prompt, self.config.ollama_model)
            elif hasattr(loader, 'generate'):
                return await loader.generate(prompt)
            elif hasattr(loader, 'chat'):
                return await loader.chat(prompt)
            elif hasattr(loader, 'complete'):
                return await loader.complete(prompt)
            elif hasattr(loader, 'query'):
                return await loader.query(prompt)
            elif hasattr(loader, 'ask'):
                return await loader.ask(prompt)
            else:
                # Debug: Print available methods
                available_methods = [method for method in dir(loader) if not method.startswith('_')]
                logger.error(f"Available methods in loader: {available_methods}")
                raise NotImplementedError(f"Model loader doesn't support text generation. Available methods: {available_methods}")
        except Exception as e:
            logger.error(f"Completion generation error: {e}")
            raise
    
    async def shutdown(self):
        """Clean up resources"""
        await self.loader_manager.shutdown()
        if self.search_tool and hasattr(self.search_tool, 'close'):
            await self.search_tool.close()


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
        logger.error(f"Failed to start Skynet Lite: {e}")
        print(f"❌ Failed to start Skynet Lite: {e}")
        print("🔧 Make sure Ollama is running: ollama serve")
        print("🔧 And ensure the model is available: ollama pull mistral")
    finally:
        # Clean up resources
        try:
            await chatbot.shutdown()
        except Exception as cleanup_error:
            logger.warning(f"Warning during cleanup: {cleanup_error}")


if __name__ == "__main__":
    asyncio.run(main())
