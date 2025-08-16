import os
import logging

logger = logging.getLogger("SkynetLite.LoaderManager")


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
