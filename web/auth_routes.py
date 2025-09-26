"""
Authentication Routes Blueprint
Handles user registration, login, logout, and user profile endpoints
"""

from flask import Blueprint, request, jsonify, session, g
from auth import AuthManager, login_required

# Create blueprint for authentication routes
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/api/register', methods=['POST'])
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
        
        result = g.auth_manager.create_user(username, password, email)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Registration error: {str(e)}'}), 500

@auth_bp.route('/api/login', methods=['POST'])
def login():
    """Handle user login"""
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        result = g.auth_manager.authenticate_user(username, password)
        
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

@auth_bp.route('/api/logout', methods=['POST'])
@login_required
def logout():
    """Handle user logout"""
    session.clear()
    return jsonify({'success': True, 'message': 'Logged out successfully'})

@auth_bp.route('/api/user', methods=['GET'])
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

@auth_bp.route('/api/user/profile', methods=['GET'])
@login_required  
def get_user_profile():
    """Get current user profile"""
    user = g.current_user
    return jsonify({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'created_at': user.created_at.isoformat(),
        'message_count': g.auth_manager.get_user_message_count(user.id)
    })

@auth_bp.route('/api/debug/session', methods=['GET'])
def debug_session():
    """Debug endpoint to check session contents"""
    from flask import session
    return jsonify({
        'session_data': dict(session),
        'has_user_id': 'user_id' in session,
        'user_id': session.get('user_id'),
        'username': session.get('username')
    })
