#!/usr/bin/env python3
"""
Skynet Lite Web UI Launcher
Simple script to run the Flask web interface
"""

import os
import sys
import subprocess
import time

def check_requirements():
    """Check if Flask is installed"""
    try:
        import flask
        print("✅ Flask is available")
        return True
    except ImportError:
        print("❌ Flask not found. Installing...")
        return False

def install_flask():
    """Install Flask using pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "flask"])
        print("✅ Flask installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install Flask")
        return False

def check_ollama():
    """Check if Ollama service is running"""
    try:
        import httpx
        response = httpx.get("http://localhost:11434/api/version", timeout=2.0)
        if response.status_code == 200:
            print("✅ Ollama is running")
            return True
        else:
            print("⚠️  Ollama may not be running properly")
            return False
    except Exception:
        print("⚠️  Ollama doesn't appear to be running at localhost:11434")
        print("💡 Start Ollama with: ollama serve")
        return False

def main():
    print("🚀 Skynet Lite Web UI Launcher")
    print("=" * 40)
    
    # Check Flask
    if not check_requirements():
        if not install_flask():
            print("❌ Cannot proceed without Flask")
            return 1
    
    # Check Ollama (warning only)
    check_ollama()
    
    print("\n🌐 Starting web interface...")
    print("🔗 Open http://localhost:5000 in your browser")
    print("🛑 Press Ctrl+C to stop")
    print("-" * 40)
    
    # Change to web directory and run Flask app
    web_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(web_dir)
    
    try:
        # Run the Flask app
        os.system(f"{sys.executable} app.py")
    except KeyboardInterrupt:
        print("\n👋 Shutting down...")
        return 0

if __name__ == "__main__":
    sys.exit(main())
