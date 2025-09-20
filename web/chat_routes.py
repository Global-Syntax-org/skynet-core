"""
Chat and History Routes Blueprint
Handles chat messaging, conversation history, and session clearing
"""

import asyncio
import traceback
from datetime import datetime
from flask import Blueprint, request, jsonify, g
from auth import AuthManager, login_required

# Create blueprint for chat routes
chat_bp = Blueprint('chat', __name__)

# Get the shared auth manager instance
auth_manager = AuthManager()

# Global skynet instance reference (will be set by main app)
skynet = None

def set_skynet_instance(skynet_instance):
    """Set the global skynet instance reference"""
    global skynet
    skynet = skynet_instance

def set_background_functions(ensure_loop_func, init_skynet_func):
    """Set the background loop functions from main app"""
    global ensure_background_loop, init_skynet
    ensure_background_loop = ensure_loop_func
    init_skynet = init_skynet_func

@chat_bp.route('/chat', methods=['POST'])
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
                chat_future = asyncio.run_coroutine_threadsafe(skynet_instance.chat(user_message, g.current_user.id), loop)
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
                        chat_future = asyncio.run_coroutine_threadsafe(skynet_instance.chat(user_message, g.current_user.id), loop)
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

@chat_bp.route('/api/history', methods=['GET'])
@login_required
def get_conversation_history():
    """Get user's conversation history"""
    try:
        limit = request.args.get('limit', 20, type=int)
        # limit=0 => return all history
        if limit == 0:
            history = auth_manager.get_user_conversation_history(g.current_user.id, limit=0)
        else:
            history = auth_manager.get_user_conversation_history(g.current_user.id, limit)
        return jsonify({'success': True, 'history': history})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@chat_bp.route('/clear', methods=['POST'])
@login_required
def clear_session():
    """Clear user's conversation history"""
    try:
        # Clear user's conversation history from database
        auth_manager.clear_user_conversation_history(g.current_user.id)
        
        # Also clear in-memory conversation history for the running Skynet instance
        try:
            loop = ensure_background_loop()

            def _clear_memory():
                try:
                    global skynet
                    if skynet and hasattr(skynet, 'memory_manager'):
                        mm = skynet.memory_manager
                        # Try common memory shapes
                        if hasattr(mm, 'conversation_history'):
                            mm.conversation_history.clear()
                        if hasattr(mm, 'clear_history'):
                            try:
                                mm.clear_history()
                            except Exception:
                                pass
                        print('🧹 Cleared in-memory conversation history for current Skynet instance')
                except Exception as e:
                    print(f'⚠️ Error while clearing in-memory history: {e}')

            # Schedule on the background loop thread
            try:
                loop.call_soon_threadsafe(_clear_memory)
            except Exception:
                # If scheduling fails, attempt a safe reinit to ensure fresh memory
                try:
                    asyncio.run_coroutine_threadsafe(init_skynet(), loop)
                except Exception as ex:
                    print(f'⚠️ Could not schedule memory clear or reinit: {ex}')
        except Exception:
            pass
        
        return jsonify({
            'status': 'cleared', 
            'user_id': g.current_user.id,
            'message': 'Conversation history cleared'
        })
        
    except Exception as e:
        print(f"⚠️ Failed to clear conversation history: {e}")
        return jsonify({'error': 'Failed to clear history'}), 500
