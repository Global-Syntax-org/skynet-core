# 🌐 Web Interface Architecture Guide

## Overview

The Skynet Core web interface has been completely refactored into a modular Blueprint architecture for better maintainability, scalability, and development experience.

## 🏗️ Modular Architecture

### Main Application (`web/app.py`) - 260 lines
The core application file now focuses on:
- Flask app initialization and configuration
- Blueprint registration
- Background loop management
- Authentication setup
- Database initialization

### Blueprint Modules

#### 1. Authentication Routes (`web/auth_routes.py`) - 99 lines
**Purpose**: User registration, login, logout, and profile management

**Endpoints**:
- `POST /api/register` - User registration
- `POST /api/login` - User authentication
- `POST /api/logout` - User logout
- `GET /api/user` - Get current user info
- `GET /api/user/profile` - Get detailed user profile

#### 2. Chat Routes (`web/chat_routes.py`) - 193 lines
**Purpose**: Chat messaging, conversation history, and session management

**Endpoints**:
- `POST /chat` - Handle chat messages with AI
- `GET /api/history` - Get conversation history
- `POST /clear` - Clear conversation history

**Features**:
- Async chat processing with background loops
- Error recovery and retry logic
- Conversation persistence
- Memory management

#### 3. Document Routes (`web/document_routes.py`) - 164 lines
**Purpose**: Document upload, management, and search functionality

**Endpoints**:
- `POST /api/documents/upload` - Upload new documents
- `GET /api/documents/list` - List user's documents
- `DELETE /api/documents/<id>` - Delete specific document
- `POST /api/documents/search` - Search document content

#### 4. Password Routes (`web/password_routes.py`) - 54 lines
**Purpose**: Password reset and token management

**Endpoints**:
- `POST /api/reset-password` - Handle password reset with token
- `POST /api/verify-reset-token` - Verify reset token validity
- `GET /reset-password` - Render reset password page

#### 5. Static Routes (`web/static_routes.py`) - 33 lines
**Purpose**: Static pages and utility endpoints

**Endpoints**:
- `GET /` - Main chat interface or login redirect
- `GET /login` - Login/registration page
- `GET /health` - Health check endpoint

## 🔧 Configuration and Setup

### Blueprint Registration

In `web/app.py`:
```python
# Register all blueprints
app.register_blueprint(document_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(password_bp)
app.register_blueprint(chat_bp)
app.register_blueprint(static_bp)

# Configure chat blueprint with background functions
from chat_routes import set_background_functions
set_background_functions(ensure_background_loop, init_skynet)
```

### Shared Dependencies

All blueprints share common dependencies:
- **AuthManager**: Centralized authentication and user management
- **Database**: SQLite database for user data and sessions
- **Background Processing**: Async event loops for AI processing

## 🎯 Benefits of Modular Architecture

### 1. **Maintainability** (53% reduction in main file size)
- **Before**: Single 554-line `app.py` file
- **After**: 6 focused modules, largest is 260 lines
- Easier to locate and modify specific functionality

### 2. **Team Collaboration**
- Different developers can work on different functional areas
- Reduced merge conflicts
- Clear ownership boundaries

### 3. **Testing**
- Individual blueprint modules can be tested in isolation
- Easier to mock dependencies for unit tests
- Focused test suites for each functional area

### 4. **Scalability**
- Easy to add new functional areas as separate blueprints
- Clean separation of concerns
- Modular deployment possibilities

## 🔄 Development Workflow

### Adding New Features

1. **Identify functional area**: Determine which blueprint the feature belongs to
2. **Create routes**: Add new routes to the appropriate blueprint
3. **Update tests**: Add tests specific to the blueprint
4. **Documentation**: Update relevant documentation

### Modifying Existing Features

1. **Locate blueprint**: Find the appropriate blueprint file
2. **Make changes**: Modify only the relevant blueprint
3. **Test isolation**: Test the specific blueprint functionality
4. **Integration test**: Verify overall application still works

## 🛠️ Technical Implementation

### Blueprint Pattern

Each blueprint follows this structure:
```python
from flask import Blueprint

# Create blueprint
feature_bp = Blueprint('feature', __name__)

# Define routes
@feature_bp.route('/api/feature', methods=['POST'])
def feature_endpoint():
    # Implementation
    pass
```

### Shared State Management

**Authentication**:
```python
# Shared auth manager across all blueprints
from auth import AuthManager, login_required

auth_manager = AuthManager()

@feature_bp.route('/protected')
@login_required
def protected_route():
    # Access current user via g.current_user
    pass
```

**Background Processing**:
```python
# Chat routes need access to background functions
def set_background_functions(ensure_loop_func, init_skynet_func):
    global ensure_background_loop, init_skynet
    ensure_background_loop = ensure_loop_func
    init_skynet = init_skynet_func
```

## 📊 Performance Impact

### Load Time
- **Improved**: Smaller individual modules load faster
- **Modular imports**: Only necessary components loaded per request
- **Reduced memory**: Less code in memory per functional area

### Development Speed
- **53% smaller main file**: Faster navigation and editing
- **Focused context**: Developers work in smaller, focused files
- **Clearer debugging**: Easier to trace issues to specific modules

## 🔍 File Structure Comparison

### Before Refactoring
```
web/
├── app.py              # 554 lines - everything
├── auth.py            # Authentication logic
├── run.py             # Launcher
└── templates/         # HTML templates
```

### After Refactoring
```
web/
├── app.py              # 260 lines - core config only
├── auth_routes.py      # 99 lines - auth endpoints
├── chat_routes.py      # 193 lines - chat functionality
├── document_routes.py  # 164 lines - document management
├── password_routes.py  # 54 lines - password management
├── static_routes.py    # 33 lines - static pages
├── auth.py            # Authentication logic (unchanged)
├── run.py             # Launcher (unchanged)
└── templates/         # HTML templates (enhanced)
```

## 🐛 Debugging and Troubleshooting

### Blueprint-Specific Issues

**Authentication Problems**:
- Check `auth_routes.py` for login/register issues
- Verify `auth.py` for session management

**Chat Not Working**:
- Debug `chat_routes.py` for message processing
- Check background loop configuration in main `app.py`

**Document Upload Failures**:
- Investigate `document_routes.py` for file handling
- Verify document processor configuration

### Common Debugging Commands

```bash
# Check syntax across all blueprint files
python -m py_compile web/*.py

# Run specific blueprint tests
python -m pytest tests/test_auth_routes.py
python -m pytest tests/test_chat_routes.py
python -m pytest tests/test_document_routes.py

# Debug specific functionality
python -c "from web.auth_routes import auth_bp; print(auth_bp.url_map)"
```

## 🔮 Future Enhancements

### Planned Blueprint Additions
- **Admin Routes**: Administrative functionality
- **API Routes**: REST API with versioning
- **WebSocket Routes**: Real-time chat functionality
- **Plugin Routes**: Dynamic plugin management

### Architecture Improvements
- **Blueprint Factories**: Dynamic blueprint creation
- **Route Prefixes**: Versioned API endpoints
- **Middleware Integration**: Request/response processing
- **Blueprint Testing**: Automated blueprint validation

## 📝 Migration Guide

### For Existing Deployments

The refactoring maintains full backward compatibility:
1. All existing URLs work unchanged
2. Authentication sessions are preserved
3. Database schema remains the same
4. Configuration files are compatible

### For Developers

**Old approach**:
```python
# Everything in app.py
@app.route('/api/feature')
def feature():
    pass
```

**New approach**:
```python
# In appropriate blueprint file
@feature_bp.route('/api/feature')
def feature():
    pass
```

---

This modular architecture provides a solid foundation for continued development and scaling of the Skynet Core web interface while maintaining simplicity and clarity.
