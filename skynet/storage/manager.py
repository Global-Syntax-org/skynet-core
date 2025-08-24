"""
Storage manager for Skynet Lite

Centralized management of storage adapters and configuration.
"""

import os
import logging
from typing import Dict, Any, Optional

from .base import StorageAdapter
from .sqlite_adapter import SQLiteAdapter
from .mssql_adapter import MSSQLAdapter
from .file_adapter import FileAdapter
from .memory_adapter import MemoryAdapter

logger = logging.getLogger(__name__)

# Global storage adapter instance
_storage_adapter: Optional[StorageAdapter] = None


class StorageManager:
    """Manages storage configuration and adapter selection"""
    
    ADAPTERS = {
        "sqlite": SQLiteAdapter,
        "mssql": MSSQLAdapter,
        "file": FileAdapter,
        "memory": MemoryAdapter,
    }
    
    @classmethod
    def create_adapter(cls, storage_type: str, config: Dict[str, Any]) -> StorageAdapter:
        """Create a storage adapter instance"""
        if storage_type not in cls.ADAPTERS:
            raise ValueError(f"Unknown storage type: {storage_type}. Available: {list(cls.ADAPTERS.keys())}")
        
        adapter_class = cls.ADAPTERS[storage_type]
        return adapter_class(config)
    
    @classmethod
    def get_default_config(cls, storage_type: str) -> Dict[str, Any]:
        """Get default configuration for storage type"""
        defaults = {
            "sqlite": {
                "database_path": os.path.join(os.getcwd(), "data", "skynet_storage.db")
            },
            "mssql": {
                "server": "localhost",
                "database": "skynet_lite",
                "driver": "ODBC Driver 17 for SQL Server",
                # Do not assume Windows trusted auth by default; prefer explicit opt-in
                "trusted_connection": False,
                "encrypt": True,
                "trust_server_certificate": False,
                "connection_timeout": 30,
                "command_timeout": 30
            },
            "file": {
                "storage_directory": os.path.join(os.getcwd(), "data", "storage"),
                "file_extension": ".json"
            },
            "memory": {
                "persist_to_file": False,
                "file_path": os.path.join(os.getcwd(), "data", "memory_storage.json")
            }
        }
        
        return defaults.get(storage_type, {})
    
    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> StorageAdapter:
        """Create adapter from configuration dictionary"""
        storage_type = config.get("type", "sqlite")
        adapter_config = config.get("config", {})
        
        # Merge with defaults
        default_config = cls.get_default_config(storage_type)
        final_config = {**default_config, **adapter_config}
        
        return cls.create_adapter(storage_type, final_config)
    
    @classmethod
    def from_env(cls) -> StorageAdapter:
        """Create adapter from environment variables"""
        storage_type = os.getenv("SKYNET_STORAGE_TYPE", "sqlite").lower()
        
        if storage_type == "mssql":
            config = {
                "server": os.getenv("MSSQL_SERVER", "localhost"),
                "database": os.getenv("MSSQL_DATABASE", "skynet_lite"),
                "username": os.getenv("MSSQL_USERNAME"),
                "password": os.getenv("MSSQL_PASSWORD"),
                "driver": os.getenv("MSSQL_DRIVER", "ODBC Driver 17 for SQL Server"),
                "trusted_connection": os.getenv("MSSQL_TRUSTED_CONNECTION", "false").lower() == "true",
                "encrypt": os.getenv("MSSQL_ENCRYPT", "true").lower() == "true",
                "trust_server_certificate": os.getenv("MSSQL_TRUST_CERT", "false").lower() == "true",
                "connection_timeout": int(os.getenv("MSSQL_CONN_TIMEOUT", "30")),
                "command_timeout": int(os.getenv("MSSQL_CMD_TIMEOUT", "30"))
            }
        else:  # sqlite default
            config = {
                "database_path": os.getenv("SQLITE_DATABASE_PATH", 
                                         os.path.join(os.getcwd(), "data", "skynet_storage.db"))
            }
        
        return cls.create_adapter(storage_type, config)


async def get_storage_adapter() -> StorageAdapter:
    """Get the global storage adapter instance"""
    global _storage_adapter
    
    if _storage_adapter is None:
        # Try to get from skynet config first
        try:
            from skynet.config import Config
            config = Config()
            
            storage_config = getattr(config, 'storage', {})
            if storage_config:
                _storage_adapter = StorageManager.from_config(storage_config)
            else:
                _storage_adapter = StorageManager.from_env()
                
        except (ImportError, AttributeError):
            # Fallback to environment variables
            _storage_adapter = StorageManager.from_env()
        
        # Connect the adapter
        if not _storage_adapter.is_connected:
            await _storage_adapter.connect()
    
    return _storage_adapter


async def set_storage_adapter(adapter: StorageAdapter) -> None:
    """Set the global storage adapter instance"""
    global _storage_adapter
    
    # Disconnect old adapter if exists
    if _storage_adapter and _storage_adapter.is_connected:
        await _storage_adapter.disconnect()
    
    _storage_adapter = adapter
    
    # Connect new adapter if not connected
    if not adapter.is_connected:
        await adapter.connect()


async def close_storage() -> None:
    """Close the global storage adapter"""
    global _storage_adapter
    
    if _storage_adapter and _storage_adapter.is_connected:
        await _storage_adapter.disconnect()
        _storage_adapter = None
