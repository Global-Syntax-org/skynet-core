"""
File-based storage adapter for Skynet Lite

Implements storage interface using JSON files on disk.
"""

import asyncio
import aiofiles
import logging
import json
import os
from typing import Any, Dict, List, Optional
from pathlib import Path
import glob

from .base import StorageAdapter, StorageError, ConnectionError, DataError

logger = logging.getLogger(__name__)


class FileAdapter(StorageAdapter):
    """File-based storage adapter using JSON files"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.storage_dir = Path(config.get("storage_directory", "data/storage"))
        self.file_extension = config.get("file_extension", ".json")
    
    async def connect(self) -> bool:
        """Initialize file storage directory"""
        try:
            # Create storage directory if it doesn't exist
            self.storage_dir.mkdir(parents=True, exist_ok=True)
            self._connected = True
            
            logger.info(f"File storage initialized at: {self.storage_dir}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize file storage: {e}")
            raise ConnectionError(f"File storage initialization failed: {e}")
    
    async def disconnect(self) -> None:
        """No-op for file storage"""
        self._connected = False
        logger.info("File storage disconnected")
    
    def _get_file_path(self, collection: str, key: str) -> Path:
        """Get file path for collection and key"""
        collection_dir = self.storage_dir / collection
        collection_dir.mkdir(exist_ok=True)
        return collection_dir / f"{key}{self.file_extension}"
    
    def _get_collection_dir(self, collection: str) -> Path:
        """Get directory path for collection"""
        return self.storage_dir / collection
    
    async def store(self, collection: str, key: str, data: Dict[str, Any]) -> bool:
        """Store data in JSON file"""
        if not self._connected:
            raise ConnectionError("File storage not connected")
        
        try:
            file_path = self._get_file_path(collection, key)
            
            # Ensure collection directory exists
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(data, indent=2, default=str))
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to store data to file: {e}")
            raise DataError(f"File store operation failed: {e}")
    
    async def retrieve(self, collection: str, key: str) -> Optional[Dict[str, Any]]:
        """Retrieve data from JSON file"""
        if not self._connected:
            raise ConnectionError("File storage not connected")
        
        try:
            file_path = self._get_file_path(collection, key)
            
            if not file_path.exists():
                return None
            
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                content = await f.read()
                return json.loads(content)
                
        except FileNotFoundError:
            return None
        except Exception as e:
            logger.error(f"Failed to retrieve data from file: {e}")
            raise DataError(f"File retrieve operation failed: {e}")
    
    async def update(self, collection: str, key: str, data: Dict[str, Any]) -> bool:
        """Update data (same as store for file storage)"""
        return await self.store(collection, key, data)
    
    async def delete(self, collection: str, key: str) -> bool:
        """Delete JSON file"""
        if not self._connected:
            raise ConnectionError("File storage not connected")
        
        try:
            file_path = self._get_file_path(collection, key)
            
            if file_path.exists():
                file_path.unlink()
                return True
            return False
                
        except Exception as e:
            logger.error(f"Failed to delete file: {e}")
            raise DataError(f"File delete operation failed: {e}")
    
    async def list_keys(self, collection: str) -> List[str]:
        """List all keys in a collection"""
        if not self._connected:
            raise ConnectionError("File storage not connected")
        
        try:
            collection_dir = self._get_collection_dir(collection)
            
            if not collection_dir.exists():
                return []
            
            keys = []
            for file_path in collection_dir.glob(f"*{self.file_extension}"):
                key = file_path.stem  # filename without extension
                keys.append(key)
            
            return sorted(keys)
                
        except Exception as e:
            logger.error(f"Failed to list keys from file storage: {e}")
            raise DataError(f"File list_keys operation failed: {e}")
    
    async def exists(self, collection: str, key: str) -> bool:
        """Check if file exists"""
        if not self._connected:
            raise ConnectionError("File storage not connected")
        
        try:
            file_path = self._get_file_path(collection, key)
            return file_path.exists()
                
        except Exception as e:
            logger.error(f"Failed to check file existence: {e}")
            raise DataError(f"File exists operation failed: {e}")
    
    async def query(self, collection: str, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Query collection with filters"""
        if not self._connected:
            raise ConnectionError("File storage not connected")
        
        try:
            collection_dir = self._get_collection_dir(collection)
            
            if not collection_dir.exists():
                return []
            
            results = []
            
            for file_path in collection_dir.glob(f"*{self.file_extension}"):
                try:
                    async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                        content = await f.read()
                        data = json.loads(content)
                        
                        # Simple filter matching
                        match = all(
                            str(data.get(k, "")).lower().find(str(v).lower()) >= 0
                            for k, v in filters.items()
                        )
                        if match:
                            results.append(data)
                            
                except (json.JSONDecodeError, Exception) as e:
                    logger.warning(f"Skipping invalid file {file_path}: {e}")
                    continue
            
            return results
                
        except Exception as e:
            logger.error(f"Failed to query file storage: {e}")
            raise DataError(f"File query operation failed: {e}")
    
    async def bulk_store(self, collection: str, items: List[Dict[str, Any]]) -> bool:
        """Store multiple items efficiently"""
        if not self._connected:
            raise ConnectionError("File storage not connected")
        
        try:
            for item in items:
                key = item.get("_key", str(len(items)))
                data = {k: v for k, v in item.items() if k != "_key"}
                await self.store(collection, key, data)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to bulk store in file storage: {e}")
            raise DataError(f"File bulk_store operation failed: {e}")
    
    async def create_collection(self, collection: str, schema: Optional[Dict] = None) -> bool:
        """Create a new collection directory"""
        if not self._connected:
            raise ConnectionError("File storage not connected")
        
        try:
            collection_dir = self._get_collection_dir(collection)
            collection_dir.mkdir(parents=True, exist_ok=True)
            
            # Optionally store schema metadata
            if schema:
                schema_file = collection_dir / "_schema.json"
                async with aiofiles.open(schema_file, 'w', encoding='utf-8') as f:
                    await f.write(json.dumps(schema, indent=2))
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to create collection directory: {e}")
            raise DataError(f"File create_collection operation failed: {e}")
    
    async def drop_collection(self, collection: str) -> bool:
        """Drop a collection directory and all its files"""
        if not self._connected:
            raise ConnectionError("File storage not connected")
        
        try:
            collection_dir = self._get_collection_dir(collection)
            
            if not collection_dir.exists():
                return False
            
            # Remove all files in the collection
            for file_path in collection_dir.glob("*"):
                if file_path.is_file():
                    file_path.unlink()
            
            # Remove directory if empty
            try:
                collection_dir.rmdir()
            except OSError:
                # Directory not empty, that's okay
                pass
            
            return True
                
        except Exception as e:
            logger.error(f"Failed to drop collection: {e}")
            raise DataError(f"File drop_collection operation failed: {e}")
