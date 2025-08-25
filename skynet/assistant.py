import asyncio
import logging
import inspect

from .loader_manager import LoaderManager
from .memory import MemoryManager

logger = logging.getLogger("SkynetCore.Assistant")


class SkynetLite:
    """Main chatbot class"""

    def __init__(self, config=None, loader_manager=None, memory_manager=None):
        self.loader_manager = loader_manager or LoaderManager()
        self.memory_manager = memory_manager or MemoryManager()
        self.search_tool = None
        self.config = config or self._load_config()

    def _load_config(self):
        """Load configuration using the proper Config class"""
        # Prefer the package-local config so imports are package-qualified
        try:
            from skynet.config import Config
        except Exception:
            # Fall back to top-level shim for backward compatibility
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

            logger.info("Skynet Core initialized successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize Skynet Core: {e}")
            return False

    async def chat(self, user_message: str) -> str:
        """Process a single chat message and return response"""
        try:
            if not user_message.strip():
                return "Please provide a message."

            # Add to memory
            self.memory_manager.add_user_message(user_message)

            # Check if web search is needed
            if await self._needs_web_search(user_message):
                response = await self._handle_web_search_query(user_message)
            else:
                response = await self._handle_local_query(user_message)

            # Add response to memory
            self.memory_manager.add_assistant_message(response)

            return response

        except Exception as e:
            logger.error(f"Error processing chat message: {e}")
            return f"Sorry, I encountered an error: {str(e)}"

    async def chat_loop(self) -> None:
        """Main chat interaction loop"""
        print("\n💬 Chat with Skynet Core (type 'quit' to exit)")
        print("=" * 50)

        while True:
            try:
                user_input = input("\nYou: ").strip()

                if user_input.lower() in ['quit', 'exit', 'bye']:
                    print("🤖 Goodbye! Skynet Core signing off.")
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
                print("\n\n🤖 Goodbye! Skynet Core signing off.")
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
                full_prompt = f"""You are Skynet Core, a helpful AI assistant powered by local AI technology. You are knowledgeable, friendly, and provide accurate information. Respond naturally and helpfully to the user's question.

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
