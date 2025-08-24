"""
Base storage abstraction interface for Skynet Lite

Defines the common interface that all storage adapters must implement.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
import asyncio


class StorageError(Exception):
    """Base exception for storage operations"""
    pass


class ConnectionError(StorageError):
    """Raised when storage connection fails"""
    pass


class DataError(StorageError):
    """Raised when data operation fails"""
    pass


class StorageAdapter(ABC):
    """Abstract base class for all storage adapters"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self._connected = False
    
    @abstractmethod
    async def connect(self) -> bool:
        """Establish connection to storage backend"""
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """Close connection to storage backend"""
        pass
    
    @abstractmethod
    async def store(self, collection: str, key: str, data: Dict[str, Any]) -> bool:
        """Store data in the specified collection with given key"""
        pass
    
    @abstractmethod
    async def retrieve(self, collection: str, key: str) -> Optional[Dict[str, Any]]:
        """Retrieve data from collection by key"""
        pass
    
    @abstractmethod
    async def update(self, collection: str, key: str, data: Dict[str, Any]) -> bool:
        """Update existing data in collection"""
        pass
    
    @abstractmethod
    async def delete(self, collection: str, key: str) -> bool:
        """Delete data from collection by key"""
        pass
    
    @abstractmethod
    async def list_keys(self, collection: str) -> List[str]:
        """List all keys in a collection"""
        pass
    
    @abstractmethod
    async def exists(self, collection: str, key: str) -> bool:
        """Check if key exists in collection"""
        pass
    
    @abstractmethod
    async def query(self, collection: str, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Query collection with filters"""
        pass
    
    @abstractmethod
    async def bulk_store(self, collection: str, items: List[Dict[str, Any]]) -> bool:
        """Store multiple items efficiently"""
        pass
    
    @abstractmethod
    async def create_collection(self, collection: str, schema: Optional[Dict] = None) -> bool:
        """Create a new collection/table"""
        pass
    
    @abstractmethod
    async def drop_collection(self, collection: str) -> bool:
        """Drop a collection/table"""
        pass
    
    @property
    def is_connected(self) -> bool:
        """Check if adapter is connected"""
        return self._connected
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.disconnect()
