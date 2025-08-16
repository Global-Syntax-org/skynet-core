#!/usr/bin/env python3
"""
Privacy-First Authentication System for Skynet Lite
Minimal data collection with secure session management
"""

import sqlite3
import bcrypt
import secrets
import os
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from dataclasses import dataclass
from functools import wraps
from flask import session, request, jsonify, g


@dataclass
class User:
    """User model with minimal privacy-respecting fields"""
    id: int
    username: str
    email: Optional[str]  # Optional for privacy
    created_at: datetime
    last_login: Optional[datetime] = None


class AuthManager:
    """Privacy-first authentication manager"""
    
    def __init__(self, db_path: str = "users.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database with privacy-focused schema"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    email TEXT,  -- Optional for account recovery
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP
                )
            """)
            
            # Password reset tokens table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS password_reset_tokens (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    token TEXT NOT NULL UNIQUE,
                    expires_at TIMESTAMP NOT NULL,
                    used BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS user_conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    message_type TEXT NOT NULL,  -- 'user' or 'assistant'
                    content TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                )
            """)
            
            # Create index for better performance
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_user_conversations_user_id 
                ON user_conversations(user_id, timestamp DESC)
            """)
            
            conn.commit()
    
    def hash_password(self, password: str) -> str:
        """Securely hash password using bcrypt"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    
    def create_user(self, username: str, password: str, email: Optional[str] = None) -> Dict[str, Any]:
        """Create new user with minimal required information"""
        
        # Basic validation
        if not username or len(username) < 3:
            return {"success": False, "error": "Username must be at least 3 characters"}
        
        if not password or len(password) < 6:
            return {"success": False, "error": "Password must be at least 6 characters"}
        
        # Optional email validation (only if provided)
        if email and "@" not in email:
            return {"success": False, "error": "Invalid email format"}
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Check if username exists
                cursor = conn.execute("SELECT id FROM users WHERE username = ?", (username,))
                if cursor.fetchone():
                    return {"success": False, "error": "Username already exists"}
                
                # Hash password and create user
                password_hash = self.hash_password(password)
                cursor = conn.execute("""
                    INSERT INTO users (username, password_hash, email) 
                    VALUES (?, ?, ?)
                """, (username, password_hash, email))
                
                user_id = cursor.lastrowid
                conn.commit()
                
                return {
                    "success": True, 
                    "user_id": user_id,
                    "message": "Account created successfully"
                }
                
        except sqlite3.Error as e:
            return {"success": False, "error": f"Database error: {str(e)}"}
    
    def authenticate_user(self, username: str, password: str) -> Dict[str, Any]:
        """Authenticate user and return user info if successful"""
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT id, username, password_hash, email, created_at, last_login 
                    FROM users WHERE username = ?
                """, (username,))
                
                row = cursor.fetchone()
                if not row:
                    return {"success": False, "error": "Invalid username or password"}
                
                user_id, username, password_hash, email, created_at, last_login = row
                
                # Verify password
                if not self.verify_password(password, password_hash):
                    return {"success": False, "error": "Invalid username or password"}
                
                # Debugging: Log password verification success
                print(f"Password verified for user: {username}")
                
                # Update last login
                conn.execute("""
                    UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?
                """, (user_id,))
                conn.commit()
                
                user = User(
                    id=user_id,
                    username=username,
                    email=email,
                    created_at=datetime.fromisoformat(created_at) if created_at else None,
                    last_login=datetime.fromisoformat(last_login) if last_login else None
                )
                
                return {
                    "success": True,
                    "user": user,
                    "message": "Login successful"
                }
                
        except sqlite3.Error as e:
            return {"success": False, "error": f"Database error: {str(e)}"}
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT id, username, email, created_at, last_login 
                    FROM users WHERE id = ?
                """, (user_id,))
                
                row = cursor.fetchone()
                if row:
                    user_id, username, email, created_at, last_login = row
                    return User(
                        id=user_id,
                        username=username,
                        email=email,
                        created_at=datetime.fromisoformat(created_at) if created_at else None,
                        last_login=datetime.fromisoformat(last_login) if last_login else None
                    )
                
        except sqlite3.Error:
            pass
        
        return None
    
    def save_conversation_message(self, user_id: int, message_type: str, content: str):
        """Save conversation message to user's history"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO user_conversations (user_id, message_type, content) 
                    VALUES (?, ?, ?)
                """, (user_id, message_type, content))
                conn.commit()
        except sqlite3.Error as e:
            print(f"Error saving conversation: {e}")
    
    def get_user_conversation_history(self, user_id: int, limit: int = 20) -> list:
        """Get user's conversation history"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                if limit and limit > 0:
                    cursor = conn.execute("""
                        SELECT message_type, content, timestamp 
                        FROM user_conversations 
                        WHERE user_id = ? 
                        ORDER BY timestamp DESC 
                        LIMIT ?
                    """, (user_id, limit))
                else:
                    # limit == 0 or falsy => return all history
                    cursor = conn.execute("""
                        SELECT message_type, content, timestamp 
                        FROM user_conversations 
                        WHERE user_id = ? 
                        ORDER BY timestamp DESC
                    """, (user_id,))
                
                messages = []
                for message_type, content, timestamp in cursor.fetchall():
                    messages.append({
                        "type": message_type,
                        "content": content,
                        "timestamp": timestamp
                    })
                
                # Reverse to get chronological order
                return list(reversed(messages))
                
        except sqlite3.Error:
            return []
    
    def clear_user_conversation_history(self, user_id: int) -> bool:
        """Clear all conversation history for a user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            # Table name is `user_conversations` (not `conversations`) — delete user's rows
            cursor.execute("DELETE FROM user_conversations WHERE user_id = ?", (user_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"❌ Error clearing conversation history: {e}")
            return False
    
    def get_user_message_count(self, user_id: int) -> int:
        """Get the total number of messages for a user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            # Count messages from the user_conversations table
            cursor.execute("SELECT COUNT(*) FROM user_conversations WHERE user_id = ?", (user_id,))
            count = cursor.fetchone()[0]
            conn.close()
            return count
        except Exception as e:
            print(f"❌ Error getting message count: {e}")
            return 0
    
    def delete_user_account(self, user_id: int) -> bool:
        """Delete user account and all associated data (GDPR compliance)"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Delete user conversations first (foreign key constraint)
                conn.execute("DELETE FROM user_conversations WHERE user_id = ?", (user_id,))
                
                # Delete user
                cursor = conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
                
                conn.commit()
                return cursor.rowcount > 0
                
        except sqlite3.Error:
            return False

    def generate_reset_token(self, email: str) -> Dict[str, Any]:
        """Generate a password reset token for the given email"""
        if not email:
            return {"success": False, "error": "Email is required"}
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Check if user exists with this email
                cursor = conn.execute("SELECT id, username FROM users WHERE email = ?", (email,))
                user_row = cursor.fetchone()
                
                if not user_row:
                    # For security, don't reveal if email exists or not
                    return {"success": True, "message": "If an account with that email exists, a reset link has been sent."}
                
                user_id, username = user_row
                
                # Generate secure token
                reset_token = secrets.token_urlsafe(32)
                expires_at = datetime.now() + timedelta(hours=24)  # 24-hour expiry
                
                # Invalidate any existing tokens for this user
                conn.execute("UPDATE password_reset_tokens SET used = TRUE WHERE user_id = ? AND used = FALSE", (user_id,))
                
                # Insert new reset token
                conn.execute("""
                    INSERT INTO password_reset_tokens (user_id, token, expires_at)
                    VALUES (?, ?, ?)
                """, (user_id, reset_token, expires_at))
                
                conn.commit()
                
                # Send reset email
                email_sent = self.send_reset_email(email, username, reset_token)
                
                if email_sent:
                    return {"success": True, "message": "If an account with that email exists, a reset link has been sent."}
                else:
                    return {"success": False, "error": "Failed to send reset email. Please try again."}
                
        except sqlite3.Error as e:
            print(f"Database error in generate_reset_token: {e}")
            return {"success": False, "error": "Database error occurred"}

    def send_reset_email(self, email: str, username: str, reset_token: str) -> bool:
        """Send password reset email"""
        try:
            # Email configuration from environment variables
            smtp_server = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
            smtp_port = int(os.environ.get('SMTP_PORT', '587'))
            sender_email = os.environ.get('SENDER_EMAIL')
            sender_password = os.environ.get('SENDER_PASSWORD')
            app_url = os.environ.get('APP_URL', 'http://localhost:5000')
            
            if not sender_email or not sender_password:
                print("Warning: SENDER_EMAIL and SENDER_PASSWORD environment variables not set")
                # For development, just log the reset token
                print(f"🔑 Password reset token for {username}: {reset_token}")
                print(f"🔗 Reset URL: {app_url}/reset-password?token={reset_token}")
                return True
            
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = "Skynet Lite - Password Reset"
            message["From"] = sender_email
            message["To"] = email
            
            # Create reset URL
            reset_url = f"{app_url}/reset-password?token={reset_token}"
            
            # Email content
            text = f"""
Hello {username},

You have requested a password reset for your Skynet Lite account.

Click the following link to reset your password:
{reset_url}

This link will expire in 24 hours.

If you did not request this reset, please ignore this email.

Best regards,
The Skynet Lite Team
            """
            
            html = f"""
<html>
  <body>
    <h2>Password Reset Request</h2>
    <p>Hello <strong>{username}</strong>,</p>
    
    <p>You have requested a password reset for your Skynet Lite account.</p>
    
    <p><a href="{reset_url}" style="background-color: #667eea; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Reset Your Password</a></p>
    
    <p>Or copy and paste this link into your browser:</p>
    <p><a href="{reset_url}">{reset_url}</a></p>
    
    <p><em>This link will expire in 24 hours.</em></p>
    
    <p>If you did not request this reset, please ignore this email.</p>
    
    <p>Best regards,<br>The Skynet Lite Team</p>
  </body>
</html>
            """
            
            # Add parts to message
            part1 = MIMEText(text, "plain")
            part2 = MIMEText(html, "html")
            message.attach(part1)
            message.attach(part2)
            
            # Send email
            context = ssl.create_default_context()
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls(context=context)
                server.login(sender_email, sender_password)
                server.sendmail(sender_email, email, message.as_string())
            
            return True
            
        except Exception as e:
            print(f"Error sending reset email: {e}")
            return False

    def verify_reset_token(self, token: str) -> Dict[str, Any]:
        """Verify a password reset token"""
        if not token:
            return {"success": False, "error": "Reset token is required"}
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT rt.user_id, rt.expires_at, u.username, u.email
                    FROM password_reset_tokens rt
                    JOIN users u ON rt.user_id = u.id
                    WHERE rt.token = ? AND rt.used = FALSE
                """, (token,))
                
                row = cursor.fetchone()
                if not row:
                    return {"success": False, "error": "Invalid or expired reset token"}
                
                user_id, expires_at_str, username, email = row
                expires_at = datetime.fromisoformat(expires_at_str)
                
                # Check if token is expired
                if datetime.now() > expires_at:
                    return {"success": False, "error": "Reset token has expired"}
                
                return {
                    "success": True,
                    "user_id": user_id,
                    "username": username,
                    "email": email
                }
                
        except sqlite3.Error as e:
            print(f"Database error in verify_reset_token: {e}")
            return {"success": False, "error": "Database error occurred"}

    def reset_password(self, token: str, new_password: str) -> Dict[str, Any]:
        """Reset password using a valid token"""
        if not token or not new_password:
            return {"success": False, "error": "Token and new password are required"}
        
        if len(new_password) < 6:
            return {"success": False, "error": "Password must be at least 6 characters"}
        
        # Verify token first
        token_result = self.verify_reset_token(token)
        if not token_result["success"]:
            return token_result
        
        user_id = token_result["user_id"]
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Hash new password
                new_password_hash = self.hash_password(new_password)
                
                # Update user password
                conn.execute("UPDATE users SET password_hash = ? WHERE id = ?", (new_password_hash, user_id))
                
                # Mark token as used
                conn.execute("UPDATE password_reset_tokens SET used = TRUE WHERE token = ?", (token,))
                
                conn.commit()
                
                return {"success": True, "message": "Password reset successfully"}
                
        except sqlite3.Error as e:
            print(f"Database error in reset_password: {e}")
            return {"success": False, "error": "Database error occurred"}

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email address"""
        if not email:
            return None
            
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT id, username, email, created_at, last_login 
                    FROM users WHERE email = ?
                """, (email,))
                
                row = cursor.fetchone()
                if row:
                    user_id, username, email, created_at, last_login = row
                    return User(
                        id=user_id,
                        username=username,
                        email=email,
                        created_at=datetime.fromisoformat(created_at) if created_at else None,
                        last_login=datetime.fromisoformat(last_login) if last_login else None
                    )
                
        except sqlite3.Error:
            pass
        
        return None


def login_required(f):
    """Decorator to require authentication for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        
        # Load current user into g
        auth_manager = getattr(g, 'auth_manager', None)
        if not auth_manager:
            return jsonify({'error': 'Authentication system error'}), 500
        
        g.current_user = auth_manager.get_user_by_id(session['user_id'])
        if not g.current_user:
            session.clear()  # Clear invalid session
            return jsonify({'error': 'Invalid session'}), 401
        
        return f(*args, **kwargs)
    
    return decorated_function


def optional_auth(f):
    """Decorator for routes that work with or without authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' in session:
            auth_manager = getattr(g, 'auth_manager', None)
            if auth_manager:
                g.current_user = auth_manager.get_user_by_id(session['user_id'])
        
        if not hasattr(g, 'current_user'):
            g.current_user = None
        
        return f(*args, **kwargs)
    
    return decorated_function


# Privacy-focused session configuration
def configure_session_security(app):
    """Configure Flask session for security and privacy"""
    
    # Generate secure secret key if not provided
    if not app.config.get('SECRET_KEY'):
        app.config['SECRET_KEY'] = secrets.token_hex(32)
        print("⚠️  Generated temporary secret key. Set SECRET_KEY environment variable for production.")
    
    # Session configuration
    app.config.update(
        SESSION_COOKIE_SECURE=False,  # Set to True in production with HTTPS
        SESSION_COOKIE_HTTPONLY=True,  # Prevent XSS
        SESSION_COOKIE_SAMESITE='Lax',  # CSRF protection
        PERMANENT_SESSION_LIFETIME=timedelta(days=30),  # 30-day sessions
    )
