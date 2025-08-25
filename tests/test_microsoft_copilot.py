#!/usr/bin/env python3
"""
Test script for Microsoft Copilot integration in Skynet Core.

This script tests the Microsoft Copilot loader directly to verify configuration
and connectivity before running the full application.
"""

import os
import sys
import asyncio
import logging
from pathlib import Path
import pytest

pytestmark = pytest.mark.skipif(
    not os.getenv('MICROSOFT_COPILOT_API_KEY'),
    reason='Microsoft Copilot API key not configured'
)

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@pytest.mark.asyncio
async def test_microsoft_copilot_loader():
    """Test the Microsoft Copilot model loader functionality."""
    
    print("🧪 Testing Microsoft Copilot Integration")
    print("=" * 50)
    
    # Check environment variables
    print("\n1. Checking Environment Configuration...")
    
    api_key = os.getenv('MICROSOFT_COPILOT_API_KEY')
    endpoint = os.getenv('MICROSOFT_COPILOT_ENDPOINT')
    model = os.getenv('MICROSOFT_COPILOT_MODEL', 'copilot')
    
    if not api_key:
        print("❌ MICROSOFT_COPILOT_API_KEY not set")
        print("   Please set your Microsoft Copilot API key in environment variables or .env file")
        print("   See docs/MICROSOFT_COPILOT_INTEGRATION.md for setup instructions")
        return False
    else:
        print(f"✅ MICROSOFT_COPILOT_API_KEY: {api_key[:10]}...{api_key[-4:] if len(api_key) > 14 else api_key}")
    
    if endpoint:
        print(f"✅ MICROSOFT_COPILOT_ENDPOINT: {endpoint}")
    else:
        print("ℹ️  MICROSOFT_COPILOT_ENDPOINT: Using default Azure endpoint")
    
    print(f"✅ MICROSOFT_COPILOT_MODEL: {model}")
    
    # Test loader import
    print("\n2. Testing Loader Import...")
    try:
        from loaders.microsoft_copilot_loader import MicrosoftCopilotLoader
        print("✅ MicrosoftCopilotLoader imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import MicrosoftCopilotLoader: {e}")
        return False
    
    # Test loader initialization
    print("\n3. Testing Loader Initialization...")
    try:
        loader = MicrosoftCopilotLoader()
        print("✅ MicrosoftCopilotLoader instance created")
    except Exception as e:
        print(f"❌ Failed to create MicrosoftCopilotLoader: {e}")
        return False
    
    # Test initialization
    print("\n4. Testing Loader.initialize()...")
    try:
        success = await loader.initialize()
        if success:
            print("✅ Loader initialized successfully")
        else:
            print("❌ Loader initialization returned False")
            print("   Check your API key and endpoint configuration")
            return False
    except Exception as e:
        print(f"❌ Loader initialization failed: {e}")
        print("   This might be due to:")
        print("   - Invalid API key")
        print("   - Incorrect endpoint URL")
        print("   - Network connectivity issues")
        print("   - Missing permissions")
        return False
    
    # Test model availability check
    print("\n5. Testing Model Availability...")
    try:
        available = await loader.ensure_model_available()
        if available:
            print("✅ Model availability check passed")
        else:
            print("❌ Model availability check failed")
    except Exception as e:
        print(f"❌ Model availability check error: {e}")
    
    # Test completion generation
    print("\n6. Testing Completion Generation...")
    test_prompts = [
        "Hello! Please respond with a simple greeting.",
        "What is the capital of France?",
        "Explain in one sentence what Microsoft Copilot is."
    ]
    
    for i, test_prompt in enumerate(test_prompts, 1):
        print(f"\n   Test {i}: {test_prompt}")
        try:
            response = await loader.generate_completion(test_prompt)
            if response and response.strip():
                print(f"   ✅ Response: {response[:100]}{'...' if len(response) > 100 else ''}")
            else:
                print(f"   ❌ Empty or invalid response: '{response}'")
                return False
        except Exception as e:
            print(f"   ❌ Completion generation failed: {e}")
            return False
    
    # Test conversation context
    print("\n7. Testing Conversation Context...")
    try:
        # First message
        response1 = await loader.generate_completion("My name is Alice. Remember this.")
        print(f"   First message response: {response1[:50]}...")
        
        # Follow-up message
        response2 = await loader.generate_completion("What is my name?")
        print(f"   Follow-up response: {response2[:50]}...")
        
        if "alice" in response2.lower():
            print("   ✅ Conversation context maintained")
        else:
            print("   ⚠️  Conversation context may not be maintained")
        
        # Reset conversation
        await loader.reset_conversation()
        print("   ✅ Conversation reset successful")
        
    except Exception as e:
        print(f"   ❌ Conversation context test failed: {e}")
    
    # Clean up
    print("\n8. Cleaning Up...")
    try:
        await loader.close()
        print("✅ Loader closed successfully")
    except Exception as e:
        print(f"⚠️  Warning: Error during cleanup: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 All Microsoft Copilot tests passed!")
    print("\nYou can now use Microsoft Copilot in Skynet Core by running:")
    print("   python3 main.py")
    print("\nMicrosoft Copilot will be used as a fallback when other models are unavailable.")
    return True


@pytest.mark.asyncio
async def test_integration_in_skynet():
    """Test Microsoft Copilot integration within the full Skynet system."""
    
    print("\n🧪 Testing Microsoft Copilot in Full Skynet Integration")
    print("=" * 50)
    
    try:
        # Import the loader manager
        from skynet.loader_manager import LoaderManager
        
        # Force Microsoft Copilot by temporarily removing other API keys
        original_env = {}
        env_keys_to_remove = [
            'OPENAI_API_KEY', 'ANTHROPIC_API_KEY', 'GOOGLE_API_KEY', 'GITHUB_COPILOT_TOKEN'
        ]
        
        for key in env_keys_to_remove:
            if key in os.environ:
                original_env[key] = os.environ[key]
                del os.environ[key]
        
        # Also ensure Ollama is not available by setting invalid URL
        original_ollama = os.environ.get('OLLAMA_BASE_URL')
        os.environ['OLLAMA_BASE_URL'] = 'http://invalid:99999'
        
        try:
            # Initialize the loader manager
            manager = LoaderManager()
            success = await manager.initialize()
            
            if success and hasattr(manager, 'loader'):
                loader_type = type(manager.loader).__name__
                print(f"✅ LoaderManager initialized with: {loader_type}")
                
                if 'MicrosoftCopilot' in loader_type:
                    print("🎉 Microsoft Copilot successfully selected as primary loader!")
                    
                    # Test a completion through the manager
                    response = await manager.generate_completion("Hello from Skynet Core with Microsoft Copilot!")
                    if response:
                        print(f"✅ Integration test successful: {response[:100]}...")
                    else:
                        print("❌ Integration test failed: empty response")
                else:
                    print(f"⚠️  Expected MicrosoftCopilotLoader but got {loader_type}")
                    print("   This might mean Microsoft Copilot is not configured or another provider took priority")
            else:
                print("❌ LoaderManager initialization failed")
                
        finally:
            # Restore original environment
            for key, value in original_env.items():
                os.environ[key] = value
            
            if original_ollama:
                os.environ['OLLAMA_BASE_URL'] = original_ollama
            elif 'OLLAMA_BASE_URL' in os.environ:
                del os.environ['OLLAMA_BASE_URL']
                
    except Exception as e:
        print(f"❌ Integration test failed: {e}")


def load_env_file():
    """Load environment variables from .env file if it exists."""
    env_file = project_root / '.env'
    if env_file.exists():
        print(f"📄 Loading environment from {env_file}")
        try:
            from dotenv import load_dotenv
            load_dotenv(env_file)
            print("✅ Environment loaded successfully")
        except ImportError:
            print("⚠️  python-dotenv not available, skipping .env file")
            # Manually parse simple .env file
            with open(env_file) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key] = value


async def main():
    """Main test function."""
    print("🚀 Skynet Core - Microsoft Copilot Integration Test")
    print("This script tests Microsoft Copilot configuration and connectivity.\n")
    
    # Load environment variables
    load_env_file()
    
    # Run tests
    success = await test_microsoft_copilot_loader()
    
    if success:
        await test_integration_in_skynet()
    else:
        print("\n❌ Basic Microsoft Copilot tests failed. Please check your configuration.")
        print("\nFor help, see: docs/MICROSOFT_COPILOT_INTEGRATION.md")
        print("\nCommon setup steps:")
        print("1. Get an Azure Cognitive Services subscription")
        print("2. Create a Copilot resource in Azure Portal")
        print("3. Copy the subscription key to MICROSOFT_COPILOT_API_KEY")
        print("4. Set the endpoint URL to MICROSOFT_COPILOT_ENDPOINT")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
