#!/usr/bin/env python3
"""
Skynet Lite Web Interface with Privacy-First Authentication
Simple Flask web UI for chatting with Skynet Lite including user accounts
"""

import sys
import os
import time
import asyncio
import traceback
import uuid
import sqlite3
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, g
from datetime import datetime

# Add parent directory to path so we can import skynet modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Add current directory to path for local imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import SkynetLite
from auth import AuthManager, login_required, optional_auth, configure_session_security
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

# Configure authentication and security
configure_session_security(app)

# Initialize authentication manager
auth_manager = AuthManager()

# Add CORS headers for development
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# Make auth manager available to all requests
@app.before_request
def before_request():
    g.auth_manager = auth_manager

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
@optional_auth
def index():
    """Render the main chat interface or login page."""
    if not g.current_user:
        return redirect(url_for('login_page'))
    
    timestamp = int(time.time())  # Unix timestamp for cache busting
    return render_template('index.html', 
                         timestamp=timestamp, 
                         username=g.current_user.username)

@app.route('/login')
def login_page():
    """Render the login/registration page."""
    return render_template('login.html')

@app.route('/api/register', methods=['POST'])
def register():
    """Handle user registration"""
    try:
        data = request.get_json()
        if not data:
            raise ValueError("Invalid JSON payload")
        
        username = data.get('username', '').strip()
        password = data.get('password', '')
        print(f"📩 Registration payload: {data}")
        email = data.get('email', '')
        email = email.strip() if isinstance(email, str) else None
        print(f"📩 Processed email: {email}")
        
        result = auth_manager.create_user(username, password, email)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Registration error: {str(e)}'}), 500

@app.route('/api/login', methods=['POST'])
def login():
    """Handle user login"""
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        result = auth_manager.authenticate_user(username, password)
        
        if result['success']:
            # Set session
            user = result['user']
            session['user_id'] = user.id
            session['username'] = user.username
            session.permanent = True
            
            return jsonify({
                'success': True,
                'message': 'Login successful',
                'user': {
                    'id': user.id,
                    'username': user.username
                }
            })
        else:
            return jsonify(result)
            
    except Exception as e:
        return jsonify({'success': False, 'error': f'Login error: {str(e)}'}), 500

@app.route('/api/logout', methods=['POST'])
@login_required
def logout():
    """Handle user logout"""
    session.clear()
    return jsonify({'success': True, 'message': 'Logged out successfully'})

@app.route('/api/user', methods=['GET'])
@login_required
def get_user():
    """Get current user info"""
    return jsonify({
        'success': True,
        'user': {
            'id': g.current_user.id,
            'username': g.current_user.username,
            'email': g.current_user.email,
            'created_at': g.current_user.created_at.isoformat() if g.current_user.created_at else None
        }
    })

@app.route('/chat', methods=['POST'])
@login_required
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
                
                # Save conversation to user's history
                auth_manager.save_conversation_message(g.current_user.id, 'user', user_message)
                auth_manager.save_conversation_message(g.current_user.id, 'assistant', response)
                
            except Exception as e:
                print(f"⚠️ Chat invocation raised: {e}")
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
                        
                        # Save conversation to user's history
                        auth_manager.save_conversation_message(g.current_user.id, 'user', user_message)
                        auth_manager.save_conversation_message(g.current_user.id, 'assistant', response)
                        
                    except Exception as e2:
                        print(f"❌ Retry after reinit failed: {e2}")
                        traceback.print_exc()
                        return jsonify({'response': f'Sorry, I encountered an error: {str(e2)}'}), 200
                else:
                    return jsonify({'response': f'Sorry, I encountered an error: {str(e)}'}), 200

            return jsonify({
                'response': response,
                'timestamp': datetime.now().isoformat(),
                'user_id': g.current_user.id
            })

        except Exception as e:
            print(f"💥 Error in async processing: {e}")
            traceback.print_exc()
            return jsonify({'error': f'Processing error: {str(e)}'}), 500
            
    except Exception as e:
        print(f"💥 Error in chat endpoint: {e}")
        traceback.print_exc()
        return jsonify({'error': f'Internal error: {str(e)}'}), 500

@app.route('/api/history', methods=['GET'])
@login_required
def get_conversation_history():
    """Get user's conversation history"""
    try:
        limit = request.args.get('limit', 20, type=int)
        history = auth_manager.get_user_conversation_history(g.current_user.id, limit)
        return jsonify({'success': True, 'history': history})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/forgot-password', methods=['POST'])
def forgot_password():
    """Handle password reset request"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip()
        
        if not email:
            return jsonify({'success': False, 'error': 'Email is required'}), 400
        
        result = auth_manager.generate_reset_token(email)
        return jsonify(result)
        
    except Exception as e:
        print(f"Error in forgot password: {e}")
        return jsonify({'success': False, 'error': 'Internal server error'}), 500

@app.route('/api/reset-password', methods=['POST'])
def reset_password():
    """Handle password reset with token"""
    try:
        data = request.get_json()
        token = data.get('token', '').strip()
        new_password = data.get('password', '').strip()
        
        if not token or not new_password:
            return jsonify({'success': False, 'error': 'Token and password are required'}), 400
        
        result = auth_manager.reset_password(token, new_password)
        return jsonify(result)
        
    except Exception as e:
        print(f"Error in reset password: {e}")
        return jsonify({'success': False, 'error': 'Internal server error'}), 500

@app.route('/api/verify-reset-token', methods=['POST'])
def verify_reset_token():
    """Verify if a reset token is valid"""
    try:
        data = request.get_json()
        token = data.get('token', '').strip()
        
        if not token:
            return jsonify({'success': False, 'error': 'Token is required'}), 400
        
        result = auth_manager.verify_reset_token(token)
        return jsonify(result)
        
    except Exception as e:
        print(f"Error in verify reset token: {e}")
        return jsonify({'success': False, 'error': 'Internal server error'}), 500

@app.route('/forgot-password')
def forgot_password_page():
    """Render forgot password page"""
    return render_template('forgot_password.html')

@app.route('/reset-password')
def reset_password_page():
    """Render reset password page"""
    token = request.args.get('token', '')
    return render_template('reset_password.html', token=token)

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'service': 'skynet-lite-web'})

@app.route('/clear', methods=['POST'])
@login_required
def clear_session():
    """Clear user's conversation history"""
    try:
        # Clear user's conversation history from database
        auth_manager.clear_user_conversation_history(g.current_user.id)
        
        return jsonify({
            'status': 'cleared', 
            'user_id': g.current_user.id,
            'message': 'Conversation history cleared'
        })
        
    except Exception as e:
        print(f"⚠️ Failed to clear conversation history: {e}")
        return jsonify({'error': 'Failed to clear history'}), 500

@app.route('/api/user/profile', methods=['GET'])
@login_required  
def get_user_profile():
    """Get current user profile"""
    user = g.current_user
    return jsonify({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'created_at': user.created_at.isoformat(),
        'message_count': auth_manager.get_user_message_count(user.id)
    })

def init_db():
    """Initialize the SQLite database."""
    db_path = os.path.join(os.path.dirname(__file__), 'skynet_lite.db')
    conn = sqlite3.connect(db_path)
    with open(os.path.join(os.path.dirname(__file__), 'schema.sql'), 'r') as f:
        conn.executescript(f.read())
    conn.close()

# Initialize the database
init_db()

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
