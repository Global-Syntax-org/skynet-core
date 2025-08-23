"""
In-memory storage adapter for Skynet Lite

Implements storage interface using in-memory dictionaries.
Useful for testing and temporary storage.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional
from collections import defaultdict
import copy

from .base import StorageAdapter, StorageError, ConnectionError, DataError

logger = logging.getLogger(__name__)


class MemoryAdapter(StorageAdapter):
    """In-memory storage adapter"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.storage: Dict[str, Dict[str, Dict[str, Any]]] = defaultdict(dict)
        self.persist_to_file = config.get("persist_to_file", False)
        self.file_path = config.get("file_path", "memory_storage.json")
    
    async def connect(self) -> bool:
        """Initialize memory storage"""
        try:
            self._connected = True
            
            # Load from file if persistence is enabled
            if self.persist_to_file:
                await self._load_from_file()
            
            logger.info("Memory storage initialized")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize memory storage: {e}")
            raise ConnectionError(f"Memory storage initialization failed: {e}")
    
    async def disconnect(self) -> None:
        """Save to file if persistence is enabled"""
        try:
            if self.persist_to_file and self._connected:
                await self._save_to_file()
            
            self._connected = False
            logger.info("Memory storage disconnected")
            
        except Exception as e:
            logger.error(f"Error during memory storage disconnect: {e}")
    
    async def _load_from_file(self) -> None:
        """Load storage from file"""
        try:
            import json
            import aiofiles
            
            async with aiofiles.open(self.file_path, 'r', encoding='utf-8') as f:
                content = await f.read()
                data = json.loads(content)
                self.storage = defaultdict(dict, data)
                
        except FileNotFoundError:
            # File doesn't exist yet, start with empty storage
            pass
        except Exception as e:
            logger.warning(f"Failed to load memory storage from file: {e}")
    
    async def _save_to_file(self) -> None:
        """Save storage to file"""
        try:
            import json
            import aiofiles
            
            # Convert defaultdict to regular dict for JSON serialization
            data = {k: dict(v) for k, v in self.storage.items()}
            
            async with aiofiles.open(self.file_path, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(data, indent=2, default=str))
                
        except Exception as e:
            logger.error(f"Failed to save memory storage to file: {e}")
    
    async def store(self, collection: str, key: str, data: Dict[str, Any]) -> bool:
        """Store data in memory"""
        if not self._connected:
            raise ConnectionError("Memory storage not connected")
        
        try:
            self.storage[collection][key] = copy.deepcopy(data)
            return True
            
        except Exception as e:
            logger.error(f"Failed to store data in memory: {e}")
            raise DataError(f"Memory store operation failed: {e}")
    
    async def retrieve(self, collection: str, key: str) -> Optional[Dict[str, Any]]:
        """Retrieve data from memory"""
        if not self._connected:
            raise ConnectionError("Memory storage not connected")
        
        try:
            if collection in self.storage and key in self.storage[collection]:
                return copy.deepcopy(self.storage[collection][key])
            return None
                
        except Exception as e:
            logger.error(f"Failed to retrieve data from memory: {e}")
            raise DataError(f"Memory retrieve operation failed: {e}")
    
    async def update(self, collection: str, key: str, data: Dict[str, Any]) -> bool:
        """Update data in memory (same as store)"""
        return await self.store(collection, key, data)
    
    async def delete(self, collection: str, key: str) -> bool:
        """Delete data from memory"""
        if not self._connected:
            raise ConnectionError("Memory storage not connected")
        
        try:
            if collection in self.storage and key in self.storage[collection]:
                del self.storage[collection][key]
                return True
            return False
                
        except Exception as e:
            logger.error(f"Failed to delete data from memory: {e}")
            raise DataError(f"Memory delete operation failed: {e}")
    
    async def list_keys(self, collection: str) -> List[str]:
        """List all keys in a collection"""
        if not self._connected:
            raise ConnectionError("Memory storage not connected")
        
        try:
            if collection in self.storage:
                return list(self.storage[collection].keys())
            return []
                
        except Exception as e:
            logger.error(f"Failed to list keys from memory: {e}")
            raise DataError(f"Memory list_keys operation failed: {e}")
    
    async def exists(self, collection: str, key: str) -> bool:
        """Check if key exists in collection"""
        if not self._connected:
            raise ConnectionError("Memory storage not connected")
        
        try:
            return collection in self.storage and key in self.storage[collection]
                
        except Exception as e:
            logger.error(f"Failed to check existence in memory: {e}")
            raise DataError(f"Memory exists operation failed: {e}")
    
    async def query(self, collection: str, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Query collection with filters"""
        if not self._connected:
            raise ConnectionError("Memory storage not connected")
        
        try:
            if collection not in self.storage:
                return []
            
            results = []
            for key, data in self.storage[collection].items():
                # Simple filter matching
                match = all(
                    str(data.get(k, "")).lower().find(str(v).lower()) >= 0
                    for k, v in filters.items()
                )
                if match:
                    results.append(copy.deepcopy(data))
            
            return results
                
        except Exception as e:
            logger.error(f"Failed to query memory storage: {e}")
            raise DataError(f"Memory query operation failed: {e}")
    
    async def bulk_store(self, collection: str, items: List[Dict[str, Any]]) -> bool:
        """Store multiple items efficiently"""
        if not self._connected:
            raise ConnectionError("Memory storage not connected")
        
        try:
            for i, item in enumerate(items):
                key = item.get("_key", str(i))
                data = {k: v for k, v in item.items() if k != "_key"}
                await self.store(collection, key, data)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to bulk store in memory: {e}")
            raise DataError(f"Memory bulk_store operation failed: {e}")
    
    async def create_collection(self, collection: str, schema: Optional[Dict] = None) -> bool:
        """Create a new collection"""
        if not self._connected:
            raise ConnectionError("Memory storage not connected")
        
        try:
            if collection not in self.storage:
                self.storage[collection] = {}
            
            # Store schema if provided
            if schema:
                self.storage[f"_schema_{collection}"] = {"_schema": schema}
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to create collection in memory: {e}")
            raise DataError(f"Memory create_collection operation failed: {e}")
    
    async def drop_collection(self, collection: str) -> bool:
        """Drop a collection"""
        if not self._connected:
            raise ConnectionError("Memory storage not connected")
        
        try:
            if collection in self.storage:
                del self.storage[collection]
                # Also remove schema if exists
                schema_key = f"_schema_{collection}"
                if schema_key in self.storage:
                    del self.storage[schema_key]
                return True
            return False
                
        except Exception as e:
            logger.error(f"Failed to drop collection from memory: {e}")
            raise DataError(f"Memory drop_collection operation failed: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get storage statistics"""
        stats = {
            "collections": len(self.storage),
            "total_items": sum(len(collection) for collection in self.storage.values()),
            "collections_detail": {}
        }
        
        for collection_name, collection_data in self.storage.items():
            if not collection_name.startswith("_schema_"):
                stats["collections_detail"][collection_name] = len(collection_data)
        
        return stats
