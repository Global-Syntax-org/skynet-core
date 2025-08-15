#!/usr/bin/env python3
"""
Skynet Lite Web Interface
Simple Flask web UI for chatting with Skynet Lite
"""

import sys
import os
import time
import asyncio
from flask import Flask, render_template, request, jsonify, session
from datetime import datetime
import uuid

# Add parent directory to path so we can import skynet modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import SkynetLite
from concurrent.futures import ThreadPoolExecutor

# Background asyncio loop and executor for running Skynet coroutines
_bg_loop = None
_bg_thread_executor = None

def start_background_loop():
    global _bg_loop, _bg_thread_executor
    if _bg_loop and _bg_loop.is_running():
        return _bg_loop

    def _run_loop(loop):
        asyncio.set_event_loop(loop)
        loop.run_forever()

    _bg_loop = asyncio.new_event_loop()
    _bg_thread_executor = ThreadPoolExecutor(max_workers=1)
    # Start loop in a background thread
    _bg_thread_executor.submit(_run_loop, _bg_loop)
    print(f"🔁 Started background event loop id={id(_bg_loop)}")
    return _bg_loop


def ensure_background_loop():
    """Ensure a running background loop is available and return it.

    This will try to recreate the loop if the existing one is stopped/closed.
    """
    global _bg_loop
    loop = start_background_loop()
    # If the returned loop is not running for any reason, recreate it.
    if not loop.is_running():
        print(f"⚠️ Background loop not running (id={id(loop)}). Recreating...")
        try:
            # attempt to stop and replace
            if loop.is_closed():
                print(f"⚠️ Old loop (id={id(loop)}) is closed")
        except Exception:
            pass
        _bg_loop = None
        loop = start_background_loop()
    return loop

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Add CORS headers for development
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# Global skynet instance
skynet = None

async def init_skynet():
    """Initialize Skynet Lite instance - reuse global for conversation continuity"""
    global skynet
    # Ensure we're running on an event loop (should be the background loop)
    current_loop = asyncio.get_running_loop()

    recreate = False
    if skynet is None:
        recreate = True
        print("🚀 Creating new Skynet instance (no existing instance)")
    else:
        # If skynet was created on a different/closed loop, recreate it
        skynet_loop = getattr(skynet, '_event_loop', None)
        if skynet_loop is None:
            recreate = True
            print("🚀 Recreating Skynet instance (no loop tagged)")
        else:
            try:
                if skynet_loop.is_closed() or not skynet_loop.is_running():
                    recreate = True
                    print("🚀 Recreating Skynet instance (loop closed/stopped)")
            except Exception:
                recreate = True
                print("🚀 Recreating Skynet instance (loop exception)")

    if recreate:
        print("🚀 Initializing new Skynet instance on current loop...")
        skynet = SkynetLite()
        # tag the instance with the loop it runs on
        skynet._event_loop = current_loop
        success = await skynet.initialize()
        if success:
            print("✅ Skynet initialized successfully")
            # Diagnostic: report memory manager type
            try:
                mm = getattr(skynet, 'memory_manager', None)
                print(f"🧠 Skynet memory manager type: {type(mm)}")
                print(f"🧠 Memory manager conversation history length: {len(mm.conversation_history) if hasattr(mm, 'conversation_history') else 'N/A'}")
                # If the memory manager exposes a load_from_file or memory_file, report it
                if hasattr(mm, 'load_from_file'):
                    print("🧾 memory manager supports load_from_file()")
                if hasattr(mm, 'memory_file'):
                    print(f"📄 memory manager configured file: {getattr(mm, 'memory_file')}")
            except Exception:
                pass
        else:
            print("❌ Skynet initialization failed")
            skynet = None
    else:
        print("♻️ Reusing existing Skynet instance")

    return skynet

@app.route('/')
def index():
    """Render the main chat interface."""
    timestamp = int(time.time())  # Unix timestamp for cache busting
    return render_template('index.html', timestamp=timestamp)

@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        
        print(f"📝 Received message: {user_message}")
        
        if not user_message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Run async skynet response using a persistent background loop
        try:
            print("🔄 Getting Skynet instance on background loop...")
            loop = ensure_background_loop()

            # Ensure skynet is initialized on the background loop
            init_future = asyncio.run_coroutine_threadsafe(init_skynet(), loop)
            skynet_instance = init_future.result(timeout=30)
            if skynet_instance is None:
                raise Exception('Failed to initialize AI system')

            # Diagnostic: log loop identities
            skynet_loop = getattr(skynet_instance, '_event_loop', None)
            print(f"🔎 Background loop id={id(loop)} running={loop.is_running()} | skynet._event_loop id={id(skynet_loop) if skynet_loop else None}")

            # If the skynet instance appears bound to a different/closed loop, re-init it
            need_reinit = False
            try:
                if skynet_loop is None:
                    need_reinit = True
                elif skynet_loop is not loop or skynet_loop.is_closed() or not skynet_loop.is_running():
                    need_reinit = True
            except Exception:
                need_reinit = True

            if need_reinit:
                print("♻️ Skynet instance loop mismatch or stopped - reinitializing on background loop...")
                init_future = asyncio.run_coroutine_threadsafe(init_skynet(), loop)
                skynet_instance = init_future.result(timeout=30)
                if skynet_instance is None:
                    raise Exception('Failed to re-initialize AI system')

            print('🤖 Submitting chat coroutine to background loop...')

            # Try chat, if it fails with a closed-loop error, try to recover once
            try:
                chat_future = asyncio.run_coroutine_threadsafe(skynet_instance.chat(user_message), loop)
                response = chat_future.result(timeout=120)
            except Exception as e:
                print(f"⚠️ Chat invocation raised: {e}")
                import traceback
                traceback.print_exc()
                msg = str(e)
                if 'Event loop is closed' in msg or 'closed' in msg.lower():
                    print("🔁 Detected closed event loop during chat generation — attempting one reinitialize+retry")
                    try:
                        init_future = asyncio.run_coroutine_threadsafe(init_skynet(), loop)
                        skynet_instance = init_future.result(timeout=30)
                        if skynet_instance is None:
                            raise Exception('Failed to reinitialize after loop-closed')
                        chat_future = asyncio.run_coroutine_threadsafe(skynet_instance.chat(user_message), loop)
                        response = chat_future.result(timeout=120)
                    except Exception as e2:
                        print(f"❌ Retry after reinit failed: {e2}")
                        import traceback
                        traceback.print_exc()
                        return jsonify({'response': f'Sorry, I encountered an error: {str(e2)}'}), 200
                else:
                    return jsonify({'response': f'Sorry, I encountered an error: {str(e)}'}), 200

            return jsonify({
                'response': response,
                'timestamp': datetime.now().isoformat(),
                'session_id': session.get('session_id')
            })

        except Exception as e:
            print(f"💥 Error in async processing: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({'error': f'Processing error: {str(e)}'}), 500
            
    except Exception as e:
        print(f"💥 Error in chat endpoint: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Internal error: {str(e)}'}), 500

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'service': 'skynet-lite-web'})

@app.route('/clear', methods=['POST'])
def clear_session():
    """Clear chat session"""
    global skynet
    session.clear()
    new_id = str(uuid.uuid4())
    session['session_id'] = new_id
    print(f"🔁 Clearing session and starting new session: {new_id}")
    
    # Force complete Skynet instance reset - this ensures no memory carries over
    try:
        if skynet:
            print("🔄 Forcing complete Skynet instance reset...")
            # Try to shutdown current instance cleanly
            try:
                import asyncio
                loop = ensure_background_loop()
                shutdown_future = asyncio.run_coroutine_threadsafe(skynet.shutdown(), loop)
                shutdown_future.result(timeout=5)
                print("✅ Current Skynet instance shut down cleanly")
            except Exception as e:
                print(f"⚠️ Error during Skynet shutdown: {e}")
            
            # Clear memory manager if it exists
            if hasattr(skynet, 'memory_manager') and skynet.memory_manager:
                mm = skynet.memory_manager
                print(f"🧠 Clearing memory for manager type: {type(mm)}")
                
                # Prefer clear_history() when available
                if hasattr(mm, 'clear_history') and callable(mm.clear_history):
                    try:
                        mm.clear_history()
                        print("🧹 Called clear_history() on memory manager")
                    except Exception as e:
                        print(f"⚠️ clear_history() raised: {e}")
                
                # Fallback: directly clear conversation_history list
                if hasattr(mm, 'conversation_history'):
                    try:
                        mm.conversation_history = []
                        print("🧹 Cleared conversation_history attribute on memory manager")
                    except Exception as e:
                        print(f"⚠️ Failed to clear conversation_history attribute: {e}")

                # If memory manager saves to a file, try to remove or overwrite it
                try:
                    mem_file = None
                    # Check common locations: attribute or env var
                    if hasattr(mm, 'memory_file'):
                        mem_file = getattr(mm, 'memory_file')
                    import os
                    if not mem_file:
                        mem_file = os.environ.get('MEMORY_FILE')
                    if not mem_file:
                        # Check for default files in workspace
                        possible_files = ['conversation_history.json', 'memory.json', 'chat_history.json']
                        for pf in possible_files:
                            if os.path.exists(pf):
                                mem_file = pf
                                break
                    
                    if mem_file:
                        # Only delete if file exists in workspace or absolute path
                        if os.path.isabs(mem_file):
                            path_to_check = mem_file
                        else:
                            path_to_check = os.path.join(os.getcwd(), mem_file)
                        if os.path.exists(path_to_check):
                            try:
                                os.remove(path_to_check)
                                print(f"🗑️ Removed persisted memory file: {path_to_check}")
                            except Exception as e:
                                print(f"⚠️ Failed to remove memory file {path_to_check}: {e}")
                        else:
                            print(f"ℹ️ Memory file not found at: {path_to_check}")
                    else:
                        print("ℹ️ No memory files found to remove")
                except Exception as e:
                    print(f"⚠️ Error while handling persisted memory file: {e}")
            
            # Force skynet instance to None - next request will create fresh instance
            skynet = None
            print("♻️ Skynet instance cleared - next request will create fresh instance")
            
    except Exception as e:
        print(f"⚠️ Failed to clear Skynet memory: {e}")

    return jsonify({'status': 'cleared', 'session_id': new_id})

if __name__ == '__main__':
    print("🌐 Starting Skynet Lite Web Interface...")
    print("🔗 Open http://localhost:5000 in your browser")
    print("💡 Tip: Make sure Ollama is running with 'ollama serve'")
    
    # Run Flask app
    # Note: disable the Werkzeug reloader to avoid starting a new process
    # which can close the background asyncio loop unexpectedly.
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        threaded=True,
        use_reloader=False
    )


import atexit

@atexit.register
def _shutdown_background():
    global _bg_loop, _bg_thread_executor
    try:
        if _bg_loop and _bg_loop.is_running():
            print('Shutting down background loop...')
            _bg_loop.call_soon_threadsafe(_bg_loop.stop)
        if _bg_thread_executor:
            _bg_thread_executor.shutdown(wait=False)
    except Exception:
        pass
