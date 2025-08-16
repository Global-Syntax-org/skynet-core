#!/usr/bin/env python3
"""Bootstrap entrypoint for Skynet Lite.

This file is intentionally small; core logic lives in `skynet.assistant`.
"""
import asyncio
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SkynetLite")


async def main() -> None:
    """Main entrypoint that imports and runs the assistant."""
    from skynet.assistant import SkynetLite

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
