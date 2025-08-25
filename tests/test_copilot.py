#!/usr/bin/env python3
"""
Test script for GitHub Copilot integration in Skynet Core.

This script tests the Copilot loader directly to verify configuration
and connectivity before running the full application.
"""

import os
import sys
import asyncio
import logging
from pathlib import Path
import pytest

# Skip entire module if required Copilot environment variables are missing
pytestmark = pytest.mark.skipif(
    not (os.getenv('GITHUB_COPILOT_TOKEN') and os.getenv('COPILOT_API_URL')),
    reason='Copilot environment not configured'
)

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@pytest.mark.asyncio
async def test_copilot_loader():
    """Test the Copilot model loader functionality."""
    
    print("🧪 Testing GitHub Copilot Integration")
    print("=" * 50)
    
    # Check environment variables
    print("\n1. Checking Environment Configuration...")
    
    token = os.getenv('GITHUB_COPILOT_TOKEN')
    api_url = os.getenv('COPILOT_API_URL')
    model = os.getenv('COPILOT_MODEL', 'copilot')
    
    if not token:
        print("❌ GITHUB_COPILOT_TOKEN not set")
        print("   Please set your Copilot token in environment variables or .env file")
        return False
    else:
        print(f"✅ GITHUB_COPILOT_TOKEN: {token[:10]}...{token[-4:] if len(token) > 14 else token}")
    
    if not api_url:
        print("❌ COPILOT_API_URL not set")
        print("   Please set your Copilot API endpoint in environment variables or .env file")
        return False
    else:
        print(f"✅ COPILOT_API_URL: {api_url}")
    
    print(f"✅ COPILOT_MODEL: {model}")
    
    # Test loader import
    print("\n2. Testing Loader Import...")
    try:
        from loaders.github_copilot_loader import GitHubCopilotModelLoader as CopilotModelLoader
        print("✅ CopilotModelLoader imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import CopilotModelLoader: {e}")
        return False
    
    # Test loader initialization
    print("\n3. Testing Loader Initialization...")
    try:
        loader = CopilotModelLoader()
        print("✅ CopilotModelLoader instance created")
    except Exception as e:
        print(f"❌ Failed to create CopilotModelLoader: {e}")
        return False
    
    # Test initialization
    print("\n4. Testing Loader.initialize()...")
    try:
        success = await loader.initialize()
        if success:
            print("✅ Loader initialized successfully")
        else:
            print("❌ Loader initialization returned False")
            return False
    except Exception as e:
        print(f"❌ Loader initialization failed: {e}")
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
    test_prompt = "Hello! Please respond with a simple greeting."
    
    try:
        response = await loader.generate_completion(test_prompt)
        if response and response.strip():
            print(f"✅ Completion generated successfully")
            print(f"   Prompt: {test_prompt}")
            print(f"   Response: {response[:100]}{'...' if len(response) > 100 else ''}")
        else:
            print("❌ Empty or invalid response from Copilot")
            print(f"   Response: '{response}'")
            return False
    except Exception as e:
        print(f"❌ Completion generation failed: {e}")
        return False
    
    # Clean up
    print("\n7. Cleaning Up...")
    try:
        await loader.close()
        print("✅ Loader closed successfully")
    except Exception as e:
        print(f"⚠️  Warning: Error during cleanup: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 All Copilot tests passed!")
    print("\nYou can now use Copilot in Skynet Core by running:")
    print("   python3 main.py")
    print("\nCopilot will be used as a fallback when Ollama is unavailable.")
    return True


@pytest.mark.asyncio
async def test_integration_in_skynet():
    """Test Copilot integration within the full Skynet system."""
    
    print("\n🧪 Testing Copilot in Full Skynet Integration")
    print("=" * 50)
    
    try:
        # Import the loader manager
        from skynet.loader_manager import LoaderManager
        
        # Force Copilot by temporarily removing other API keys
        original_env = {}
        env_keys_to_remove = ['OPENAI_API_KEY', 'ANTHROPIC_API_KEY', 'GOOGLE_API_KEY']
        
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
                
                if 'Copilot' in loader_type:
                    print("🎉 Copilot successfully selected as primary loader!")
                    
                    # Test a completion through the manager
                    response = await manager.generate_completion("Hello from Skynet Core!")
                    if response:
                        print(f"✅ Integration test successful: {response[:50]}...")
                    else:
                        print("❌ Integration test failed: empty response")
                else:
                    print(f"⚠️  Expected CopilotModelLoader but got {loader_type}")
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
    print("🚀 Skynet Core - GitHub Copilot Integration Test")
    print("This script tests GitHub Copilot configuration and connectivity.\n")
    
    # Load environment variables
    load_env_file()
    
    # Run tests
    success = await test_copilot_loader()
    
    if success:
        await test_integration_in_skynet()
    else:
        print("\n❌ Basic Copilot tests failed. Please check your configuration.")
        print("\nFor help, see: docs/COPILOT_INTEGRATION.md")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
