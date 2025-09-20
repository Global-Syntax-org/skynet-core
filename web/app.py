#!/usr/bin/env python3
"""
Skynet Core Web Interface with Privacy-First Authentication
Simple Flask web UI for chatting with Skynet Core including user accounts
"""

import sys
import os
import time
import asyncio
import traceback
import uuid
import sqlite3
import glob
import logging

# If a local .venv exists in the project, add its site-packages to sys.path so
# the app can be started with the system Python (without activating the venv).
# This is a best-effort convenience for development; production should use a
# properly activated environment or a process manager.
try:
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    venv_root = os.path.join(project_root, '.venv')
    if os.path.isdir(venv_root):
        # Typical layouts:
        #  - .venv/lib/pythonX.Y/site-packages
        #  - .venv/lib64/pythonX.Y/site-packages
        #  - .venv/lib/pythonX.Y/dist-packages
        patterns = [
            os.path.join(venv_root, 'lib', 'python*', 'site-packages'),
            os.path.join(venv_root, 'lib64', 'python*', 'site-packages'),
            os.path.join(venv_root, 'lib', 'python*', 'dist-packages'),
        ]
        for pat in patterns:
            for p in glob.glob(pat):
                if os.path.isdir(p) and p not in sys.path:
                    sys.path.insert(0, p)
        # Also ensure the venv's 'site-packages' is preferred for imports
        # (no-op if already present)
except Exception:
    # Fail silently — we don't want startup to break if enrichment fails
    pass

from flask import Flask, render_template, request, jsonify, session, redirect, url_for, g
from datetime import datetime

# Add parent directory to path so we can import skynet modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Add current directory to path for local imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from skynet.assistant import SkynetLite
from skynet.document_processor import document_processor
from auth import AuthManager, login_required, optional_auth, configure_session_security
from concurrent.futures import ThreadPoolExecutor
from document_routes import document_bp
from auth_routes import auth_bp
from password_routes import password_bp
from chat_routes import chat_bp
from static_routes import static_bp

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

# Register all blueprints
app.register_blueprint(document_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(password_bp)
app.register_blueprint(chat_bp)
app.register_blueprint(static_bp)

# Set up logging
logger = logging.getLogger(__name__)

# Configure authentication and security
configure_session_security(app)

# Use a single, canonical SQLite database file inside the web/ directory
DB_PATH = os.path.join(os.path.dirname(__file__), 'skynet_core.db')

# Backward compatibility: migrate legacy database filename if present
LEGACY_DB_PATH = os.path.join(os.path.dirname(__file__), 'skynet_lite.db')
if os.path.exists(LEGACY_DB_PATH) and not os.path.exists(DB_PATH):
    try:
        import shutil
        shutil.copy2(LEGACY_DB_PATH, DB_PATH)
        print("📦 Migrated legacy database skynet_lite.db -> skynet_core.db")
    except Exception as e:
        print(f"⚠️ Failed to migrate legacy database file: {e}")


# Initialize the database (ensure schema exists before creating AuthManager)
def init_db():
    """Initialize the SQLite database at the canonical DB_PATH."""
    conn = sqlite3.connect(DB_PATH)
    with open(os.path.join(os.path.dirname(__file__), 'schema.sql'), 'r') as f:
        conn.executescript(f.read())
    conn.close()


init_db()

# Initialize authentication manager using the same DB file
auth_manager = AuthManager(db_path=DB_PATH)

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
    """Initialize Skynet Core instance - reuse global for conversation continuity"""
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

# Configure chat blueprint with background functions
from chat_routes import set_background_functions
set_background_functions(ensure_background_loop, init_skynet)

# Routes moved to blueprints - keeping only route handling logic

# Authentication routes moved to auth_routes.py

# Chat routes moved to chat_routes.py

# Password management routes moved to password_routes.py
# History routes moved to chat_routes.py  
# Health and utility routes moved to static_routes.py
# User profile routes moved to auth_routes.py


if __name__ == '__main__':
    print("🌐 Starting Skynet Core Web Interface...")
    print("🔗 Open http://localhost:5005 in your browser")
    print("💡 Tip: Make sure Ollama is running with 'ollama serve'")
    
    # Run Flask app
    # Note: disable the Werkzeug reloader to avoid starting a new process
    # which can close the background asyncio loop unexpectedly.
    app.run(
        host='0.0.0.0',
        port=5005,
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
