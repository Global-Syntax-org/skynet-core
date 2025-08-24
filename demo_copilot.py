#!/usr/bin/env python3
"""
Demo script showcasing GitHub Copilot integration with Skynet Lite.

This script demonstrates how to use Copilot as an AI provider and 
showcases coding assistance capabilities.
"""

import os
import sys
import asyncio
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Load environment variables
def load_env():
    env_file = project_root / '.env'
    if env_file.exists():
        try:
            from dotenv import load_dotenv
            load_dotenv(env_file)
        except ImportError:
            # Manually parse .env file
            with open(env_file) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key] = value


async def demo_copilot_coding_assistance():
    """Demo Copilot's coding assistance capabilities."""
    
    print("🤖 GitHub Copilot Coding Assistance Demo")
    print("=" * 50)
    
    # Check if Copilot is configured
    if not os.getenv('GITHUB_COPILOT_TOKEN'):
        print("❌ GitHub Copilot not configured.")
        print("Please set GITHUB_COPILOT_TOKEN and COPILOT_API_URL in your .env file.")
        print("See docs/COPILOT_INTEGRATION.md for setup instructions.")
        return
    
    try:
        from loaders.github_copilot_loader import GitHubCopilotModelLoader as CopilotModelLoader
        
        # Initialize Copilot
        copilot = CopilotModelLoader()
        if not await copilot.initialize():
            print("❌ Failed to initialize Copilot")
            return
        
        print("✅ Copilot initialized successfully!")
        print("\nDemonstrating Copilot's coding assistance...\n")
        
        # Demo 1: Code explanation
        print("1️⃣  Code Explanation Demo")
        print("-" * 30)
        code_snippet = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
"""
        
        prompt1 = f"Explain this Python code and suggest improvements:\n{code_snippet}"
        response1 = await copilot.generate_completion(prompt1)
        print(f"🔍 Analyzing code...\n{response1}\n")
        
        # Demo 2: Code generation
        print("2️⃣  Code Generation Demo")
        print("-" * 30)
        prompt2 = "Write a Python function that implements binary search with proper error handling and documentation."
        response2 = await copilot.generate_completion(prompt2)
        print(f"💻 Generating code...\n{response2}\n")
        
        # Demo 3: Debugging assistance
        print("3️⃣  Debugging Assistance Demo")
        print("-" * 30)
        buggy_code = """
def divide_numbers(a, b):
    result = a / b
    return result

# This might cause an error
print(divide_numbers(10, 0))
"""
        
        prompt3 = f"Find and fix the bug in this code:\n{buggy_code}"
        response3 = await copilot.generate_completion(prompt3)
        print(f"🐛 Debugging code...\n{response3}\n")
        
        # Demo 4: Architecture suggestions
        print("4️⃣  Architecture Suggestions Demo")
        print("-" * 30)
        prompt4 = "I'm building a web API for a chatbot. What's the best architecture pattern to use with Python Flask for handling multiple AI model providers?"
        response4 = await copilot.generate_completion(prompt4)
        print(f"🏗️  Architecture advice...\n{response4}\n")
        
        await copilot.close()
        
        print("=" * 50)
        print("🎉 Copilot demo completed!")
        print("\nCopilot can help with:")
        print("• Code explanation and documentation")
        print("• Code generation and completion")
        print("• Bug finding and fixing")
        print("• Architecture and design advice")
        print("• Refactoring suggestions")
        print("• Performance optimization")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")


async def demo_copilot_in_skynet():
    """Demo Copilot integration within Skynet Lite."""
    
    print("\n🚀 Copilot in Skynet Lite Demo")
    print("=" * 50)
    
    try:
        # Temporarily disable other providers to force Copilot usage
        original_env = {}
        providers_to_disable = ['OPENAI_API_KEY', 'ANTHROPIC_API_KEY', 'GOOGLE_API_KEY']
        
        for key in providers_to_disable:
            if key in os.environ:
                original_env[key] = os.environ.pop(key)
        
        # Also ensure Ollama is not available
        original_ollama = os.environ.get('OLLAMA_BASE_URL')
        os.environ['OLLAMA_BASE_URL'] = 'http://invalid:99999'
        
        try:
            from skynet.assistant import SkynetLite
            
            # Initialize Skynet with Copilot
            skynet = SkynetLite()
            
            print("🤖 Skynet Lite initialized with Copilot!")
            print("\nAsking Skynet some questions...\n")
            
            # Demo questions
            questions = [
                "Hello! Can you help me with Python programming?",
                "What's the best way to handle async operations in Python?",
                "Can you write a simple web scraper example?",
                "Explain the Model-View-Controller pattern",
            ]
            
            for i, question in enumerate(questions, 1):
                print(f"{i}️⃣  Question: {question}")
                response = await skynet.chat(question)
                print(f"🤖 Skynet + Copilot: {response[:200]}{'...' if len(response) > 200 else ''}\n")
                
        finally:
            # Restore environment
            for key, value in original_env.items():
                os.environ[key] = value
            if original_ollama:
                os.environ['OLLAMA_BASE_URL'] = original_ollama
            elif 'OLLAMA_BASE_URL' in os.environ:
                del os.environ['OLLAMA_BASE_URL']
                
    except Exception as e:
        print(f"❌ Skynet demo failed: {e}")
        print("Make sure Skynet Lite is properly installed and configured.")


async def main():
    """Main demo function."""
    
    print("🌟 Skynet Lite + GitHub Copilot Demo")
    print("This demo showcases GitHub Copilot integration capabilities.\n")
    
    # Load environment
    load_env()
    
    # Run demos
    await demo_copilot_coding_assistance()
    await demo_copilot_in_skynet()
    
    print("\n🎯 Next Steps:")
    print("• Run 'python3 test_copilot.py' to test your configuration")
    print("• Read 'docs/COPILOT_INTEGRATION.md' for detailed setup")
    print("• Use 'python3 main.py' for interactive chat with Copilot")
    print("• Try the web interface: 'cd web && python3 run.py'")


if __name__ == "__main__":
    asyncio.run(main())
