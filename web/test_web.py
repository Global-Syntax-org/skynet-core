#!/usr/bin/env python3
"""
Test script for Skynet Core Web UI
Demonstrates the web interface functionality
"""

import os
import sys
import time
import webbrowser
import subprocess
import signal

def main():
    print("🧪 Skynet Core Web UI Test")
    print("=" * 40)
    
    # Check if we're in the right directory
    if not os.path.exists('app.py'):
        print("❌ Please run this script from the web/ directory")
        return 1
    
    # Start the web server
    print("🚀 Starting web server...")
    web_process = None
    
    try:
        # Get the correct Python executable
        python_path = "/home/stux/repos/skynet-lite/.venv/bin/python"
        if not os.path.exists(python_path):
            python_path = sys.executable
        
        # Start Flask app in background
        web_process = subprocess.Popen(
            [python_path, "app.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait a moment for the server to start
        time.sleep(3)
        
        # Check if process is still running
        if web_process.poll() is None:
            print("✅ Web server started successfully")
            print("🌐 Open http://localhost:5000 in your browser")
            print("💬 Try typing: 'hello', 'what is python', or 'latest AI news'")
            print("🛑 Press Ctrl+C to stop the server")
            
            # Optionally open browser
            try:
                webbrowser.open('http://localhost:5000')
                print("🔗 Browser opened automatically")
            except:
                print("💡 Manually open http://localhost:5000")
            
            # Wait for user to stop
            try:
                web_process.wait()
            except KeyboardInterrupt:
                print("\n🛑 Stopping web server...")
        else:
            # Process failed to start
            stdout, stderr = web_process.communicate()
            print("❌ Failed to start web server")
            print(f"Error: {stderr.decode()}")
            return 1
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping web server...")
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    finally:
        # Clean up
        if web_process and web_process.poll() is None:
            web_process.terminate()
            try:
                web_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                web_process.kill()
        print("👋 Test completed")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
