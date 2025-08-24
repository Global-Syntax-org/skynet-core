"""
Test suite for storage abstraction layer

Tests all storage adapters: SQLite, MSSQL, File, Memory
"""

import pytest
import asyncio
import tempfile
import os
from unittest.mock import AsyncMock, patch

from skynet.storage import StorageManager, get_storage_adapter
from skynet.storage.base import StorageAdapter, StorageError
from skynet.storage.sqlite_adapter import SQLiteAdapter
from skynet.storage.memory_adapter import MemoryAdapter


class TestStorageManager:
    """Test storage manager functionality"""
    
    def test_create_sqlite_adapter(self):
        """Test creating SQLite adapter"""
        config = {"database_path": ":memory:"}
        adapter = StorageManager.create_adapter("sqlite", config)
        assert isinstance(adapter, SQLiteAdapter)
    
    def test_create_memory_adapter(self):
        """Test creating memory adapter"""
        config = {"persist_to_file": False}
        adapter = StorageManager.create_adapter("memory", config)
        assert isinstance(adapter, MemoryAdapter)
    
    def test_unknown_adapter_type(self):
        """Test error for unknown adapter type"""
        with pytest.raises(ValueError, match="Unknown storage type"):
            StorageManager.create_adapter("unknown", {})
    
    def test_default_config(self):
        """Test default configuration generation"""
        sqlite_config = StorageManager.get_default_config("sqlite")
        assert "database_path" in sqlite_config
        
        mssql_config = StorageManager.get_default_config("mssql")
        assert "server" in mssql_config
        assert "database" in mssql_config
    
    def test_from_config(self):
        """Test creating adapter from config dict"""
        config = {
            "type": "memory",
            "config": {"persist_to_file": False}
        }
        adapter = StorageManager.from_config(config)
        assert isinstance(adapter, MemoryAdapter)


class TestMemoryAdapter:
    """Test memory storage adapter"""
    
    @pytest.mark.asyncio
    async def test_store_and_retrieve(self):
        """Test basic store and retrieve operations"""
        config = {"persist_to_file": False}
        adapter = MemoryAdapter(config)
        await adapter.connect()
        
        try:
            test_data = {"name": "test", "value": 42}
            
            # Store data
            result = await adapter.store("test_collection", "test_key", test_data)
            assert result is True
            
            # Retrieve data
            retrieved = await adapter.retrieve("test_collection", "test_key")
            assert retrieved == test_data
        finally:
            await adapter.disconnect()
    
    @pytest.mark.asyncio
    async def test_update(self):
        """Test update operation"""
        adapter = MemoryAdapter({})
        await adapter.connect()
        try:
            original_data = {"name": "test", "value": 42}
            updated_data = {"name": "test", "value": 84}

            # Store original
            await adapter.store("test_collection", "test_key", original_data)
            
            # Update
            await adapter.update("test_collection", "test_key", updated_data)
            
            # Verify update
            retrieved = await adapter.retrieve("test_collection", "test_key")
            assert retrieved == updated_data
        finally:
            await adapter.disconnect()

    @pytest.mark.asyncio
    async def test_delete(self):
        """Test delete operation"""
        adapter = MemoryAdapter({})
        await adapter.connect()
        try:
            test_data = {"name": "test"}

            # Store data
            await adapter.store("test_collection", "test_key", test_data)
            
            # Verify exists
            exists = await adapter.exists("test_collection", "test_key")
            assert exists

            # Delete
            await adapter.delete("test_collection", "test_key")
            
            # Verify deleted
            exists = await adapter.exists("test_collection", "test_key")
            assert not exists
        finally:
            await adapter.disconnect()

    @pytest.mark.asyncio
    async def test_list_keys(self):
        """Test listing keys in collection"""
        adapter = MemoryAdapter({})
        await adapter.connect()
        try:
            # Store multiple items
            await adapter.store("test_collection", "key1", {"data": 1})
            await adapter.store("test_collection", "key2", {"data": 2})
            await adapter.store("other_collection", "key3", {"data": 3})

            # List keys in test_collection
            keys = await adapter.list_keys("test_collection")
            assert set(keys) == {"key1", "key2"}

            # List keys in other_collection
            keys = await adapter.list_keys("other_collection")
            assert keys == ["key3"]
        finally:
            await adapter.disconnect()

    @pytest.mark.asyncio
    async def test_query(self):
        """Test query with filters"""
        adapter = MemoryAdapter({})
        await adapter.connect()
        try:
            # Store test data
            await adapter.store("users", "user1", {"name": "Alice", "age": 25})
            await adapter.store("users", "user2", {"name": "Bob", "age": 30})
            await adapter.store("users", "user3", {"name": "Charlie", "age": 25})

            # Query by age
            results = await adapter.query("users", {"age": 25})
            assert len(results) == 2
            assert results[0]["name"] in ["Alice", "Charlie"]
            assert results[1]["name"] in ["Alice", "Charlie"]

            # Query by name
            results = await adapter.query("users", {"name": "Bob"})
            assert len(results) == 1
            assert results[0]["name"] == "Bob"
        finally:
            await adapter.disconnect()

    @pytest.mark.asyncio
    async def test_bulk_store(self):
        """Test bulk store operation"""
        adapter = MemoryAdapter({})
        await adapter.connect()
        try:
            items = [
                {"_key": "item1", "name": "Item 1", "value": 10},
                {"_key": "item2", "name": "Item 2", "value": 20},
                {"_key": "item3", "name": "Item 3", "value": 30}
            ]

            result = await adapter.bulk_store("items", items)
            assert result is True

            # Verify items were stored
            item1 = await adapter.retrieve("items", "item1")
            assert item1["name"] == "Item 1"
        finally:
            await adapter.disconnect()

    @pytest.mark.asyncio
    async def test_collection_operations(self):
        """Test collection create and drop"""
        adapter = MemoryAdapter({})
        await adapter.connect()
        try:
            # Create collection
            result = await adapter.create_collection("new_collection")
            assert result is True

            # Store something in it
            await adapter.store("new_collection", "test", {"data": "test"})
            assert await adapter.exists("new_collection", "test")

            # Drop collection
            result = await adapter.drop_collection("new_collection")
            assert result is True

            # Verify collection is gone
            keys = await adapter.list_keys("new_collection")
            assert len(keys) == 0
        finally:
            await adapter.disconnect()


class TestSQLiteAdapter:
    """Test SQLite storage adapter"""
    
    @pytest.mark.asyncio
    async def test_sqlite_store_retrieve(self):
        """Test SQLite store and retrieve"""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
            db_path = tmp.name
        
        try:
            config = {"database_path": db_path}
            adapter = SQLiteAdapter(config)
            await adapter.connect()
            
            try:
                test_data = {"message": "Hello SQLite", "count": 42}
                
                # Store
                result = await adapter.store("messages", "msg1", test_data)
                assert result is True
                
                # Retrieve
                retrieved = await adapter.retrieve("messages", "msg1")
                assert retrieved == test_data
            finally:
                await adapter.disconnect()
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)
    
    @pytest.mark.asyncio
    async def test_sqlite_persistence(self):
        """Test data persists across connections"""
        import tempfile
        import os
        
        # Create temporary database file
        db_fd, db_path = tempfile.mkstemp(suffix='.db')
        os.close(db_fd)
        
        try:
            test_data = {"persistent": True}

            # Create first adapter and store data
            config = {"database_path": db_path}
            adapter1 = SQLiteAdapter(config)
            await adapter1.connect()
            
            await adapter1.store("persistent", "test", test_data)
            await adapter1.disconnect()

            # Create new adapter with same database
            adapter2 = SQLiteAdapter(config)
            await adapter2.connect()

            try:
                # Retrieve data
                retrieved = await adapter2.retrieve("persistent", "test")
                assert retrieved == test_data
            finally:
                await adapter2.disconnect()
        finally:
            # Clean up
            if os.path.exists(db_path):
                os.unlink(db_path)
@pytest.mark.asyncio
async def test_context_manager():
    """Test storage adapter as async context manager"""
    config = {"persist_to_file": False}
    
    async with MemoryAdapter(config) as storage:
        assert storage.is_connected
        
        # Use storage
        await storage.store("test", "key", {"data": "value"})
        data = await storage.retrieve("test", "key")
        assert data["data"] == "value"
    
    # Should be disconnected after context
    assert not storage.is_connected


class TestMSSQLAdapter:
    """Test MSSQL adapter (mocked since we don't have SQL Server in CI)"""
    
    @pytest.mark.asyncio
    async def test_mssql_adapter_import_error(self):
        """Test MSSQL adapter handles missing dependencies gracefully"""
        
        # Mock the import to fail
        with patch.dict('sys.modules', {'pyodbc': None, 'aioodbc': None}):
            with patch('skynet.storage.mssql_adapter.MSSQL_AVAILABLE', False):
                from skynet.storage.mssql_adapter import MSSQLAdapter
                
                with pytest.raises(ImportError, match="MSSQL dependencies not available"):
                    MSSQLAdapter({})
    
    def test_connection_string_building(self):
        """Test MSSQL connection string construction"""
        # Skip if MSSQL not available
        try:
            from skynet.storage.mssql_adapter import MSSQLAdapter, MSSQL_AVAILABLE
            if not MSSQL_AVAILABLE:
                pytest.skip("MSSQL dependencies not available")
        except ImportError:
            pytest.skip("MSSQL dependencies not available")

        # Test Windows auth
        config = {
            "server": "testserver",
            "database": "testdb",
            "trusted_connection": True,
            "encrypt": True
        }

        adapter = MSSQLAdapter(config)
        conn_str = adapter._build_connection_string()
        
        assert "testserver" in conn_str
        assert "testdb" in conn_str
        assert "Trusted_Connection=yes" in conn_str
        assert "Encrypt=yes" in conn_str

        # Test SQL auth
        config = {
            "server": "testserver",
            "database": "testdb",
            "username": "testuser",
            "password": "testpass",
            "driver": "ODBC Driver 17 for SQL Server"
        }

        adapter = MSSQLAdapter(config)
        conn_str = adapter._build_connection_string()
        
        assert "testserver" in conn_str
        assert "testdb" in conn_str
        assert "testuser" in conn_str
        assert "testpass" in conn_str
        assert "ODBC Driver 17 for SQL Server" in conn_str