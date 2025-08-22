#!/usr/bin/env python3
"""
Setup script for Skynet Lite
Helps with initial configuration and dependency verification
"""

import os
import subprocess
import sys
from pathlib import Path


def check_python_version():
    """Check if Python version is 3.10+"""
    if sys.version_info < (3, 10):
        print("❌ Python 3.10+ is required")
        print(f"   Current version: {sys.version}")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True


def check_ollama():
    """Check if Ollama is installed and accessible"""
    try:
        result = subprocess.run(
            ["ollama", "--version"], 
            capture_output=True, 
            text=True, 
            timeout=10
        )
        if result.returncode == 0:
            print("✅ Ollama is installed")
            return True
        else:
            print("❌ Ollama command failed")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("❌ Ollama not found")
        print("   Install from: https://ollama.com/download")
        return False


def install_dependencies():
    """Install Python dependencies"""
    print("📦 Installing Python dependencies...")
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ], check=True)
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        return False


def check_config():
    """Check configuration file"""
    config_path = Path("config.yaml")
    if config_path.exists():
        print("✅ Configuration file found")
        
        # Check for Bing API key
        bing_key = os.getenv("BING_API_KEY")
        if bing_key:
            print("✅ Bing API key found in environment")
        else:
            print("⚠️  No Bing API key found")
            print("   Web search will be disabled")
            print("   Set BING_API_KEY environment variable or edit config.yaml")
        
        return True
    else:
        print("⚠️  Configuration file not found")
    print("   Creating default config.yaml...")

    # Create default config
    from skynet.config import Config
    config = Config()
    config.create_default_config_file()
    return True


def pull_ollama_model():
    """Pull the Mistral model if needed"""
    print("🤖 Checking Ollama models...")
    try:
        # Check if mistral is available
        result = subprocess.run(
            ["ollama", "list"], 
            capture_output=True, 
            text=True, 
            timeout=10
        )
        
        if "mistral" in result.stdout:
            print("✅ Mistral model is available")
            return True
        else:
            print("📥 Pulling Mistral model (this may take a while)...")
            subprocess.run(["ollama", "pull", "mistral"], check=True)
            print("✅ Mistral model pulled successfully")
            return True
            
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
        print("❌ Failed to check/pull Ollama models")
        print("   Make sure Ollama is running: ollama serve")
        return False


def main():
    """Main setup function"""
    print("🚀 Setting up Skynet Lite...")
    print("=" * 40)
    
    # Check requirements
    checks = [
        check_python_version(),
        check_ollama(),
        install_dependencies(),
        check_config(),
        pull_ollama_model()
    ]
    
    print("\n" + "=" * 40)
    
    if all(checks):
        print("🎉 Setup complete! Skynet Lite is ready to run.")
        print("\n📝 To start chatting:")
        print("   python main.py")
        print("\n🔧 Optional: Set up Bing Search")
        print("   export BING_API_KEY='your-api-key'")
    else:
        print("❌ Setup incomplete. Please resolve the issues above.")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
