"""
SQLite storage adapter for Skynet Lite

Implements storage interface using SQLite database with async support.
"""

import asyncio
import logging
import json
import os
from typing import Any, Dict, List, Optional
from datetime import datetime

try:
    import aiosqlite
    SQLITE_AVAILABLE = True
except ImportError:
    SQLITE_AVAILABLE = False

from .base import StorageAdapter, StorageError, ConnectionError, DataError

logger = logging.getLogger(__name__)


class SQLiteAdapter(StorageAdapter):
    """SQLite storage adapter"""
    
    def __init__(self, config: Dict[str, Any]):
        if not SQLITE_AVAILABLE:
            raise ImportError(
                "SQLite async dependencies not available. Install with: "
                "pip install aiosqlite"
            )
        
        super().__init__(config)
        self.db_path = config.get("database_path", "skynet_storage.db")
        self.connection = None
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(os.path.abspath(self.db_path)), exist_ok=True)
    
    async def connect(self) -> bool:
        """Establish connection to SQLite database"""
        try:
            self.connection = await aiosqlite.connect(self.db_path)
            self._connected = True
            
            # Initialize storage schema
            await self._initialize_schema()
            
            logger.info(f"Connected to SQLite database: {self.db_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to SQLite: {e}")
            raise ConnectionError(f"SQLite connection failed: {e}")
    
    async def disconnect(self) -> None:
        """Close connection to SQLite database"""
        if self.connection:
            try:
                await self.connection.close()
                logger.info("Disconnected from SQLite database")
            except Exception as e:
                logger.error(f"Error disconnecting from SQLite: {e}")
            finally:
                self.connection = None
                self._connected = False
    
    async def _initialize_schema(self) -> None:
        """Initialize the storage schema if it doesn't exist"""
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS skynet_storage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            collection TEXT NOT NULL,
            key_name TEXT NOT NULL,
            data TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(collection, key_name)
        );
        
        CREATE INDEX IF NOT EXISTS idx_collection_key 
        ON skynet_storage(collection, key_name);
        """
        
        try:
            await self.connection.executescript(create_table_sql)
            await self.connection.commit()
        except Exception as e:
            raise DataError(f"Failed to initialize SQLite schema: {e}")
    
    async def store(self, collection: str, key: str, data: Dict[str, Any]) -> bool:
        """Store data in SQLite database"""
        if not self._connected:
            raise ConnectionError("Not connected to SQLite database")
        
        try:
            json_data = json.dumps(data, default=str)
            
            sql = """
            INSERT OR REPLACE INTO skynet_storage (collection, key_name, data, updated_at)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            """
            
            await self.connection.execute(sql, (collection, key, json_data))
            await self.connection.commit()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to store data in SQLite: {e}")
            raise DataError(f"SQLite store operation failed: {e}")
    
    async def retrieve(self, collection: str, key: str) -> Optional[Dict[str, Any]]:
        """Retrieve data from SQLite database"""
        if not self._connected:
            raise ConnectionError("Not connected to SQLite database")
        
        try:
            sql = "SELECT data FROM skynet_storage WHERE collection = ? AND key_name = ?"
            
            async with self.connection.execute(sql, (collection, key)) as cursor:
                row = await cursor.fetchone()
                
                if row:
                    return json.loads(row[0])
                return None
                
        except Exception as e:
            logger.error(f"Failed to retrieve data from SQLite: {e}")
            raise DataError(f"SQLite retrieve operation failed: {e}")
    
    async def update(self, collection: str, key: str, data: Dict[str, Any]) -> bool:
        """Update existing data in SQLite database"""
        return await self.store(collection, key, data)  # INSERT OR REPLACE handles updates
    
    async def delete(self, collection: str, key: str) -> bool:
        """Delete data from SQLite database"""
        if not self._connected:
            raise ConnectionError("Not connected to SQLite database")
        
        try:
            sql = "DELETE FROM skynet_storage WHERE collection = ? AND key_name = ?"
            
            cursor = await self.connection.execute(sql, (collection, key))
            await self.connection.commit()
            return cursor.rowcount > 0
                
        except Exception as e:
            logger.error(f"Failed to delete data from SQLite: {e}")
            raise DataError(f"SQLite delete operation failed: {e}")
    
    async def list_keys(self, collection: str) -> List[str]:
        """List all keys in a collection"""
        if not self._connected:
            raise ConnectionError("Not connected to SQLite database")
        
        try:
            sql = "SELECT key_name FROM skynet_storage WHERE collection = ? ORDER BY key_name"
            
            async with self.connection.execute(sql, (collection,)) as cursor:
                rows = await cursor.fetchall()
                return [row[0] for row in rows]
                
        except Exception as e:
            logger.error(f"Failed to list keys from SQLite: {e}")
            raise DataError(f"SQLite list_keys operation failed: {e}")
    
    async def exists(self, collection: str, key: str) -> bool:
        """Check if key exists in collection"""
        if not self._connected:
            raise ConnectionError("Not connected to SQLite database")
        
        try:
            sql = "SELECT 1 FROM skynet_storage WHERE collection = ? AND key_name = ? LIMIT 1"
            
            async with self.connection.execute(sql, (collection, key)) as cursor:
                row = await cursor.fetchone()
                return row is not None
                
        except Exception as e:
            logger.error(f"Failed to check existence in SQLite: {e}")
            raise DataError(f"SQLite exists operation failed: {e}")
    
    async def query(self, collection: str, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Query collection with filters"""
        if not self._connected:
            raise ConnectionError("Not connected to SQLite database")
        
        try:
            sql = "SELECT data FROM skynet_storage WHERE collection = ?"
            params = [collection]
            
            async with self.connection.execute(sql, params) as cursor:
                rows = await cursor.fetchall()
                
                results = []
                for row in rows:
                    data = json.loads(row[0])
                    # Simple filter matching
                    match = all(
                        str(data.get(k, "")).lower().find(str(v).lower()) >= 0
                        for k, v in filters.items()
                    )
                    if match:
                        results.append(data)
                
                return results
                
        except Exception as e:
            logger.error(f"Failed to query SQLite: {e}")
            raise DataError(f"SQLite query operation failed: {e}")
    
    async def bulk_store(self, collection: str, items: List[Dict[str, Any]]) -> bool:
        """Store multiple items efficiently"""
        if not self._connected:
            raise ConnectionError("Not connected to SQLite database")
        
        try:
            # Prepare bulk insert data
            values = []
            for item in items:
                key = item.get("_key", str(datetime.now().timestamp()))
                data = {k: v for k, v in item.items() if k != "_key"}
                json_data = json.dumps(data, default=str)
                values.append((collection, key, json_data))
            
            sql = """
            INSERT OR REPLACE INTO skynet_storage (collection, key_name, data, updated_at)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            """
            
            await self.connection.executemany(sql, values)
            await self.connection.commit()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to bulk store in SQLite: {e}")
            raise DataError(f"SQLite bulk_store operation failed: {e}")
    
    async def create_collection(self, collection: str, schema: Optional[Dict] = None) -> bool:
        """Create a new collection (no-op for SQLite - uses single table)"""
        # SQLite adapter uses a single table with collection as a column
        if not collection or not isinstance(collection, str):
            raise DataError("Invalid collection name")
        return True
    
    async def drop_collection(self, collection: str) -> bool:
        """Drop a collection (delete all records for the collection)"""
        if not self._connected:
            raise ConnectionError("Not connected to SQLite database")
        
        try:
            sql = "DELETE FROM skynet_storage WHERE collection = ?"
            
            cursor = await self.connection.execute(sql, (collection,))
            await self.connection.commit()
            return cursor.rowcount > 0
                
        except Exception as e:
            logger.error(f"Failed to drop collection from SQLite: {e}")
            raise DataError(f"SQLite drop_collection operation failed: {e}")
