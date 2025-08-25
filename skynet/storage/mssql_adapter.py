"""
Microsoft SQL Server storage adapter for Skynet Core

Implements storage interface using MSSQL database with async support.
Supports both SQL Server Authentication and Windows Authentication.

Configuration:
    {
        "server": "localhost",
    "database": "skynet_core", 
        "username": "skynet_user",  # Optional for Windows auth
        "password": "password",     # Optional for Windows auth
        "driver": "ODBC Driver 17 for SQL Server",  # Optional
        "trusted_connection": False,  # True for Windows auth
        "encrypt": True,
        "trust_server_certificate": False,
        "connection_timeout": 30,
        "command_timeout": 30
    }
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional, Union
import json
from datetime import datetime

try:
    import pyodbc
    import aioodbc
    MSSQL_AVAILABLE = True
except ImportError:
    MSSQL_AVAILABLE = False

from .base import StorageAdapter, StorageError, ConnectionError, DataError

logger = logging.getLogger(__name__)


class MSSQLAdapter(StorageAdapter):
    """Microsoft SQL Server storage adapter"""
    
    def __init__(self, config: Dict[str, Any]):
        if not MSSQL_AVAILABLE:
            raise ImportError(
                "MSSQL dependencies not available. Install with: "
                "pip install pyodbc aioodbc"
            )
        
        super().__init__(config)
        self.connection = None
        self._connection_string = self._build_connection_string()
    
    def _build_connection_string(self) -> str:
        """Build MSSQL connection string from config"""
        server = self.config.get("server", "localhost")
        database = self.config.get("database", "skynet_core")
        driver = self.config.get("driver", "ODBC Driver 17 for SQL Server")
        
        conn_parts = [
            f"Driver={{{driver}}}",
            f"Server={server}",
            f"Database={database}"
        ]
        
        # Authentication
        if self.config.get("trusted_connection", False):
            conn_parts.append("Trusted_Connection=yes")
        else:
            username = self.config.get("username")
            password = self.config.get("password")
            if username and password:
                conn_parts.append(f"UID={username}")
                conn_parts.append(f"PWD={password}")
        
        # Security settings
        if self.config.get("encrypt", True):
            conn_parts.append("Encrypt=yes")
        
        if self.config.get("trust_server_certificate", False):
            conn_parts.append("TrustServerCertificate=yes")
        
        # Timeouts
        conn_timeout = self.config.get("connection_timeout", 30)
        conn_parts.append(f"Connection Timeout={conn_timeout}")
        
        return ";".join(conn_parts)
    
    async def connect(self) -> bool:
        """Establish connection to MSSQL database"""
        try:
            self.connection = await aioodbc.connect(
                dsn=self._connection_string,
                autocommit=True
            )
            self._connected = True
            
            # Initialize storage schema
            await self._initialize_schema()
            
            logger.info("Connected to MSSQL database successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to MSSQL: {e}")
            raise ConnectionError(f"MSSQL connection failed: {e}")
    
    async def disconnect(self) -> None:
        """Close connection to MSSQL database"""
        if self.connection:
            try:
                await self.connection.close()
                logger.info("Disconnected from MSSQL database")
            except Exception as e:
                logger.error(f"Error disconnecting from MSSQL: {e}")
            finally:
                self.connection = None
                self._connected = False
    
    async def _initialize_schema(self) -> None:
        """Initialize the storage schema if it doesn't exist"""
        create_table_sql = """
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='skynet_storage' AND xtype='U')
        CREATE TABLE skynet_storage (
            id BIGINT IDENTITY(1,1) PRIMARY KEY,
            collection NVARCHAR(255) NOT NULL,
            key_name NVARCHAR(255) NOT NULL,
            data NVARCHAR(MAX) NOT NULL,
            created_at DATETIME2 DEFAULT GETDATE(),
            updated_at DATETIME2 DEFAULT GETDATE(),
            UNIQUE(collection, key_name)
        );
        
        IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_collection_key')
        CREATE INDEX idx_collection_key ON skynet_storage(collection, key_name);
        """
        
        try:
            async with self.connection.cursor() as cursor:
                await cursor.execute(create_table_sql)
        except Exception as e:
            raise DataError(f"Failed to initialize MSSQL schema: {e}")
    
    async def store(self, collection: str, key: str, data: Dict[str, Any]) -> bool:
        """Store data in MSSQL database"""
        if not self._connected:
            raise ConnectionError("Not connected to MSSQL database")
        
        try:
            json_data = json.dumps(data, default=str)
            
            sql = """
            MERGE skynet_storage AS target
            USING (SELECT ? AS collection, ? AS key_name, ? AS data) AS source
            ON target.collection = source.collection AND target.key_name = source.key_name
            WHEN MATCHED THEN
                UPDATE SET data = source.data, updated_at = GETDATE()
            WHEN NOT MATCHED THEN
                INSERT (collection, key_name, data) VALUES (source.collection, source.key_name, source.data);
            """
            
            async with self.connection.cursor() as cursor:
                await cursor.execute(sql, (collection, key, json_data))
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to store data in MSSQL: {e}")
            raise DataError(f"MSSQL store operation failed: {e}")
    
    async def retrieve(self, collection: str, key: str) -> Optional[Dict[str, Any]]:
        """Retrieve data from MSSQL database"""
        if not self._connected:
            raise ConnectionError("Not connected to MSSQL database")
        
        try:
            sql = "SELECT data FROM skynet_storage WHERE collection = ? AND key_name = ?"
            
            async with self.connection.cursor() as cursor:
                await cursor.execute(sql, (collection, key))
                row = await cursor.fetchone()
                
                if row:
                    return json.loads(row[0])
                return None
                
        except Exception as e:
            logger.error(f"Failed to retrieve data from MSSQL: {e}")
            raise DataError(f"MSSQL retrieve operation failed: {e}")
    
    async def update(self, collection: str, key: str, data: Dict[str, Any]) -> bool:
        """Update existing data in MSSQL database"""
        return await self.store(collection, key, data)  # MERGE handles updates
    
    async def delete(self, collection: str, key: str) -> bool:
        """Delete data from MSSQL database"""
        if not self._connected:
            raise ConnectionError("Not connected to MSSQL database")
        
        try:
            sql = "DELETE FROM skynet_storage WHERE collection = ? AND key_name = ?"
            
            async with self.connection.cursor() as cursor:
                await cursor.execute(sql, (collection, key))
                return cursor.rowcount > 0
                
        except Exception as e:
            logger.error(f"Failed to delete data from MSSQL: {e}")
            raise DataError(f"MSSQL delete operation failed: {e}")
    
    async def list_keys(self, collection: str) -> List[str]:
        """List all keys in a collection"""
        if not self._connected:
            raise ConnectionError("Not connected to MSSQL database")
        
        try:
            sql = "SELECT key_name FROM skynet_storage WHERE collection = ? ORDER BY key_name"
            
            async with self.connection.cursor() as cursor:
                await cursor.execute(sql, (collection,))
                rows = await cursor.fetchall()
                return [row[0] for row in rows]
                
        except Exception as e:
            logger.error(f"Failed to list keys from MSSQL: {e}")
            raise DataError(f"MSSQL list_keys operation failed: {e}")
    
    async def exists(self, collection: str, key: str) -> bool:
        """Check if key exists in collection"""
        if not self._connected:
            raise ConnectionError("Not connected to MSSQL database")
        
        try:
            sql = "SELECT 1 FROM skynet_storage WHERE collection = ? AND key_name = ?"
            
            async with self.connection.cursor() as cursor:
                await cursor.execute(sql, (collection, key))
                row = await cursor.fetchone()
                return row is not None
                
        except Exception as e:
            logger.error(f"Failed to check existence in MSSQL: {e}")
            raise DataError(f"MSSQL exists operation failed: {e}")
    
    async def query(self, collection: str, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Query collection with filters (basic JSON query support)"""
        if not self._connected:
            raise ConnectionError("Not connected to MSSQL database")
        
        try:
            # Basic implementation - for complex queries, consider using JSON functions
            sql = "SELECT data FROM skynet_storage WHERE collection = ?"
            params = [collection]
            
            async with self.connection.cursor() as cursor:
                await cursor.execute(sql, params)
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
            logger.error(f"Failed to query MSSQL: {e}")
            raise DataError(f"MSSQL query operation failed: {e}")
    
    async def bulk_store(self, collection: str, items: List[Dict[str, Any]]) -> bool:
        """Store multiple items efficiently using bulk insert"""
        if not self._connected:
            raise ConnectionError("Not connected to MSSQL database")
        
        try:
            # Prepare bulk insert data
            values = []
            for item in items:
                key = item.get("_key", str(datetime.now().timestamp()))
                data = {k: v for k, v in item.items() if k != "_key"}
                json_data = json.dumps(data, default=str)
                values.append((collection, key, json_data))
            
            sql = """
            INSERT INTO skynet_storage (collection, key_name, data)
            VALUES (?, ?, ?)
            """
            
            async with self.connection.cursor() as cursor:
                await cursor.executemany(sql, values)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to bulk store in MSSQL: {e}")
            raise DataError(f"MSSQL bulk_store operation failed: {e}")
    
    async def create_collection(self, collection: str, schema: Optional[Dict] = None) -> bool:
        """Create a new collection (no-op for MSSQL - uses single table)"""
        # MSSQL adapter uses a single table with collection as a column
        # So this is essentially a no-op, but we can validate the collection name
        if not collection or not isinstance(collection, str):
            raise DataError("Invalid collection name")
        return True
    
    async def drop_collection(self, collection: str) -> bool:
        """Drop a collection (delete all records for the collection)"""
        if not self._connected:
            raise ConnectionError("Not connected to MSSQL database")
        
        try:
            sql = "DELETE FROM skynet_storage WHERE collection = ?"
            
            async with self.connection.cursor() as cursor:
                await cursor.execute(sql, (collection,))
                return cursor.rowcount > 0
                
        except Exception as e:
            logger.error(f"Failed to drop collection from MSSQL: {e}")
            raise DataError(f"MSSQL drop_collection operation failed: {e}")
