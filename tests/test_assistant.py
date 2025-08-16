import asyncio
import os
import sys

# Ensure the repository root is on sys.path so tests can import the local package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from skynet.assistant import SkynetLite


class FakeLoader:
    async def initialize(self):
        return True

    async def close(self):
        return None

    async def generate(self, prompt: str):
        return "fake response based on prompt"


class FakeLoaderManager:
    def __init__(self):
        self.loader = FakeLoader()

    async def initialize(self):
        return True

    async def shutdown(self):
        await self.loader.close()


def test_chat_with_fake_loader():
    lm = FakeLoaderManager()
    bot = SkynetLite(loader_manager=lm)

    async def run():
        ok = await bot.initialize()
        assert ok is True
        resp = await bot.chat("Hello")
        assert "fake response" in resp
        await bot.shutdown()

    asyncio.run(run())
