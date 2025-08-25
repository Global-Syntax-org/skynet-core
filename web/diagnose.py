#!/usr/bin/env python3
"""
Skynet Core Web UI Diagnostics
Helps troubleshoot web interface issues
"""

import sys
import os
import requests
import time
import subprocess

def check_ollama():
    """Check if Ollama is running"""
    try:
        response = requests.get("http://localhost:11434/api/version", timeout=3)
        if response.status_code == 200:
            version = response.json().get('version', 'unknown')
            print(f"✅ Ollama is running (version: {version})")
            return True
        else:
            print(f"⚠️ Ollama responded with status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Ollama not accessible: {e}")
        print("💡 Start Ollama with: ollama serve")
        return False

def check_models():
    """Check available models"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=3)
        if response.status_code == 200:
            data = response.json()
            models = [model['name'] for model in data.get('models', [])]
            if models:
                print(f"✅ Available models: {', '.join(models)}")
                return True
            else:
                print("❌ No models found")
                print("💡 Pull a model with: ollama pull mistral")
                return False
    except Exception as e:
        print(f"❌ Could not check models: {e}")
        return False

def test_core_functionality():
    """Test core Skynet functionality"""
    print("\n🧪 Testing core Skynet functionality...")
    
    # Add parent directory to path
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    try:
        from main import SkynetLite
        import asyncio
        
        async def test():
            skynet = SkynetLite()
            success = await skynet.initialize()
            if success:
                response = await skynet.chat("test")
                return True, response
            return False, "Initialization failed"
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            success, result = loop.run_until_complete(test())
            if success:
                print(f"✅ Core functionality working: {result[:50]}...")
                return True
            else:
                print(f"❌ Core test failed: {result}")
                return False
        finally:
            loop.close()
            
    except Exception as e:
        print(f"❌ Core test error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_web_endpoint():
    """Test web endpoint"""
    print("\n🌐 Testing web endpoint...")
    
    # Start Flask app in background
    try:
        # Check if Flask is available
        try:
            import flask
            print("✅ Flask is available")
        except ImportError:
            print("❌ Flask not found. Install with: pip install flask")
            return False
        
        print("🚀 Starting test web server...")
        proc = subprocess.Popen([
            sys.executable, "app.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait for server to start
        time.sleep(4)
        
        # Test endpoints
        try:
            # Health check
            health_resp = requests.get("http://localhost:5000/health", timeout=5)
            if health_resp.status_code == 200:
                print("✅ Health endpoint working")
            else:
                print(f"⚠️ Health endpoint returned {health_resp.status_code}")
            
            # Chat endpoint
            chat_resp = requests.post(
                "http://localhost:5000/chat",
                json={"message": "test"},
                timeout=15
            )
            
            if chat_resp.status_code == 200:
                data = chat_resp.json()
                if 'response' in data:
                    print(f"✅ Chat endpoint working: {data['response'][:50]}...")
                    return True
                else:
                    print(f"⚠️ Chat response missing 'response' field: {data}")
            else:
                print(f"❌ Chat endpoint failed: {chat_resp.status_code}")
                try:
                    error_data = chat_resp.json()
                    print(f"Error details: {error_data}")
                except:
                    print(f"Error text: {chat_resp.text}")
            
        except requests.exceptions.ConnectionError:
            print("❌ Could not connect to web server")
        except requests.exceptions.Timeout:
            print("❌ Web server request timed out")
        except Exception as e:
            print(f"❌ Web test error: {e}")
        
        return False
        
    finally:
        # Clean up
        if 'proc' in locals():
            try:
                proc.terminate()
                proc.wait(timeout=3)
            except:
                proc.kill()

def main():
    print("🔧 Skynet Core Web UI Diagnostics")
    print("=" * 50)
    
    # Check prerequisites
    print("\n📋 Checking prerequisites...")
    ollama_ok = check_ollama()
    models_ok = check_models() if ollama_ok else False
    
    # Test core functionality
    core_ok = test_core_functionality()
    
    # Test web interface
    web_ok = test_web_endpoint()
    
    # Summary
    print("\n📊 Diagnostic Summary:")
    print(f"Ollama: {'✅' if ollama_ok else '❌'}")
    print(f"Models: {'✅' if models_ok else '❌'}")
    print(f"Core AI: {'✅' if core_ok else '❌'}")
    print(f"Web Interface: {'✅' if web_ok else '❌'}")
    
    if all([ollama_ok, models_ok, core_ok, web_ok]):
        print("\n🎉 All systems working! Try the web interface at http://localhost:5000")
    else:
        print("\n🔧 Some issues found. Check the details above and:")
        print("1. Ensure Ollama is running: ollama serve")
        print("2. Pull a model: ollama pull mistral")
        print("3. Install Flask: pip install flask")
        print("4. Try clearing browser cache (Ctrl+F5)")

if __name__ == "__main__":
    main()
