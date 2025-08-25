"""
Skynet Core Storage Abstraction Layer

This module provides a unified interface for data storage across different backends:
- SQLite databases
- Microsoft SQL Server (MSSQL)
- JSON file storage  
- In-memory storage

Usage:
    from skynet.storage import StorageManager, get_storage_adapter
    
    # Get configured storage adapter
    storage = get_storage_adapter()
    
    # Store and retrieve data
    await storage.store('conversations', user_id, conversation_data)
    data = await storage.retrieve('conversations', user_id)
"""

from .base import StorageAdapter, StorageError
from .sqlite_adapter import SQLiteAdapter
from .mssql_adapter import MSSQLAdapter
from .file_adapter import FileAdapter
from .memory_adapter import MemoryAdapter
from .manager import StorageManager, get_storage_adapter

__all__ = [
    'StorageAdapter',
    'StorageError', 
    'SQLiteAdapter',
    'FileAdapter',
    'MemoryAdapter',
    'StorageManager',
    'get_storage_adapter'
]
