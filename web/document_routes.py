#!/usr/bin/env python3
"""
Document management routes for Skynet Core Web Interface
Handles document upload, listing, deletion, and search endpoints
"""

import os
import sys
import logging
from flask import Blueprint, request, jsonify, g
from datetime import datetime

# Add parent directory to path so we can import skynet modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from skynet.document_processor import document_processor
from auth import login_required

logger = logging.getLogger(__name__)

# Create Blueprint for document routes
document_bp = Blueprint('documents', __name__, url_prefix='/api/documents')


# Helper function to wrap async functions for Flask
def async_route(f):
    """Decorator to handle async functions in Flask routes"""
    import asyncio
    from functools import wraps
    
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            # Try to get the current event loop
            loop = asyncio.get_event_loop()
        except RuntimeError:
            # No loop is running, create a new one
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        if loop.is_running():
            # If loop is already running, we need to use run_coroutine_threadsafe
            # This should not happen in normal Flask operation, but just in case
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, f(*args, **kwargs))
                return future.result()
        else:
            # Run the coroutine
            return loop.run_until_complete(f(*args, **kwargs))
    
    return wrapper


@document_bp.route('/upload', methods=['POST'])
@login_required
@async_route
async def upload_document():
    """Handle document upload"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Read file data
        file_data = file.read()
        
        # Upload document using the document processor
        result = await document_processor.upload_document(
            file_data, 
            file.filename, 
            str(g.current_user.id)
        )
        
        if result.get('success'):
            return jsonify({
                'success': True,
                'message': result.get('message', 'Document uploaded successfully'),
                'document_id': result.get('document_id'),
                'filename': file.filename
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Upload failed')
            }), 400
            
    except Exception as e:
        logger.error(f"Document upload error: {e}")
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500


@document_bp.route('/list', methods=['GET'])
@login_required
@async_route
async def list_documents():
    """List user's documents"""
    try:
        documents = await document_processor.list_user_documents(str(g.current_user.id))
        return jsonify({
            'success': True,
            'documents': documents
        })
        
    except Exception as e:
        logger.error(f"Document listing error: {e}")
        return jsonify({'error': f'Failed to list documents: {str(e)}'}), 500


@document_bp.route('/<document_id>', methods=['DELETE'])
@login_required
@async_route
async def delete_document(document_id):
    """Delete a specific document"""
    try:
        success = await document_processor.delete_document(document_id, str(g.current_user.id))
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Document deleted successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Document not found or permission denied'
            }), 404
            
    except Exception as e:
        logger.error(f"Document deletion error: {e}")
        return jsonify({'error': f'Failed to delete document: {str(e)}'}), 500


@document_bp.route('/search', methods=['GET'])
@login_required
@async_route
async def search_documents():
    """Search documents for specific content"""
    try:
        query = request.args.get('q', '').strip()
        if not query:
            return jsonify({'error': 'Search query is required'}), 400
        
        max_results = request.args.get('max_results', 10, type=int)
        
        results = await document_processor.search_documents(
            query, 
            str(g.current_user.id), 
            max_results=max_results
        )
        
        return jsonify({
            'success': True,
            'query': query,
            'results': results,
            'count': len(results)
        })
        
    except Exception as e:
        logger.error(f"Document search error: {e}")
        return jsonify({'error': f'Search failed: {str(e)}'}), 500
