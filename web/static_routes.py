"""
Static and Utility Routes Blueprint
Handles static pages and utility endpoints
"""

import time
from flask import Blueprint, render_template, redirect, url_for, g, jsonify
from auth import optional_auth

# Create blueprint for static/utility routes
static_bp = Blueprint('static', __name__)

@static_bp.route('/')
@optional_auth
def index():
    """Render the main chat interface or login page."""
    if not g.current_user:
        return redirect(url_for('static.login_page'))
    
    timestamp = int(time.time())  # Unix timestamp for cache busting
    return render_template('index.html', 
                         timestamp=timestamp, 
                         username=g.current_user.username)

@static_bp.route('/login')
def login_page():
    """Render the login/registration page."""
    return render_template('login.html')

@static_bp.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'service': 'skynet-core-web'})
