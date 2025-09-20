"""
Password Management Routes Blueprint
Handles password reset and token verification endpoints
"""

from flask import Blueprint, request, jsonify, render_template
from auth import AuthManager

# Create blueprint for password management routes
password_bp = Blueprint('password', __name__)

# Get the shared auth manager instance
auth_manager = AuthManager()

@password_bp.route('/api/reset-password', methods=['POST'])
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

@password_bp.route('/api/verify-reset-token', methods=['POST'])
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

@password_bp.route('/reset-password')
def reset_password_page():
    """Render reset password page"""
    token = request.args.get('token', '')
    return render_template('reset_password.html', token=token)
