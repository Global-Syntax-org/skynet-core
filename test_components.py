#!/usr/bin/env python3
"""
Simple test script for Skynet Lite components
"""

import asyncio
from config import Config
from models.loader import OllamaModelLoader
from tools.web_search import BingSearchTool
from plugins.memory import ChatMemoryManager


async def test_config():
    """Test configuration loading"""
    print("🔧 Testing configuration...")
    config = Config()
    print(f"   Ollama URL: {config.ollama_base_url}")
    print(f"   Model: {config.ollama_model}")
    print(f"   Bing API: {'✅ Configured' if config.bing_api_key else '❌ Not configured'}")
    return True


async def test_ollama():
    """Test Ollama connection"""
    print("🤖 Testing Ollama connection...")
    async with OllamaModelLoader() as loader:
        if await loader.check_ollama_status():
            print("   ✅ Ollama is running")
            models = await loader.list_models()
            print(f"   Available models: {len(models)}")
            return True
        else:
            print("   ❌ Ollama is not accessible")
            return False


async def test_memory():
    """Test memory management"""
    print("🧠 Testing memory management...")
    memory = ChatMemoryManager(max_history=5)
    
    # Add some test messages
    memory.add_user_message("Hello, Skynet!")
    memory.add_assistant_message("Hello! How can I help you today?")
    memory.add_user_message("Tell me about yourself")
    memory.add_assistant_message("I'm Skynet Lite, a local AI assistant.")
    
    history = memory.get_conversation_history()
    print(f"   Conversation length: {len(memory.conversation_history)} messages")
    print(f"   Recent context: {len(memory.get_recent_context(2))} messages")
    
    return True


async def test_search():
    """Test web search (if configured)"""
    print("🔍 Testing web search...")
    config = Config()
    
    if not config.bing_api_key:
        print("   ⚠️ Skipping - no Bing API key")
        return True
    
    async with BingSearchTool(config.bing_api_key) as search_tool:
        try:
            results = await search_tool.search("Python programming", count=2)
            print(f"   Search results: {len(results)} found")
            if results:
                print(f"   First result: {results[0]['title'][:50]}...")
            return True
        except Exception as e:
            print(f"   ❌ Search failed: {e}")
            return False


async def main():
    """Run all tests"""
    print("🧪 Testing Skynet Lite Components")
    print("=" * 40)
    
    tests = [
        ("Configuration", test_config),
        ("Ollama Connection", test_ollama),
        ("Memory Management", test_memory),
        ("Web Search", test_search)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append(result)
        except Exception as e:
            print(f"   ❌ {test_name} failed: {e}")
            results.append(False)
        print()
    
    print("=" * 40)
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print("🎉 All tests passed! Skynet Lite is ready.")
    else:
        print(f"⚠️ {passed}/{total} tests passed. Check the issues above.")
    
    return 0 if passed == total else 1


if __name__ == "__main__":
    asyncio.run(main())
