import asyncio
import tempfile
import os
import shutil
import json
import pytest

from skynet.storage.memory_adapter import MemoryAdapter
from skynet.storage.file_adapter import FileAdapter
from skynet.storage.sqlite_adapter import SQLiteAdapter, SQLITE_AVAILABLE
from skynet.storage.manager import StorageManager, set_storage_adapter, get_storage_adapter, close_storage
from skynet.storage.base import ConnectionError


@pytest.mark.asyncio
async def test_memory_adapter_basic_ops(tmp_path):
    cfg = {"persist_to_file": False}
    adapter = MemoryAdapter(cfg)

    assert not adapter.is_connected
    await adapter.connect()
    assert adapter.is_connected

    await adapter.create_collection("users")
    await adapter.store("users", "alice", {"name": "Alice", "age": 30})
    data = await adapter.retrieve("users", "alice")
    assert data["name"] == "Alice"

    exists = await adapter.exists("users", "alice")
    assert exists

    keys = await adapter.list_keys("users")
    assert "alice" in keys

    results = await adapter.query("users", {"name": "Alice"})
    assert len(results) == 1

    await adapter.delete("users", "alice")
    assert not await adapter.exists("users", "alice")

    await adapter.disconnect()
    assert not adapter.is_connected


@pytest.mark.asyncio
async def test_file_adapter_basic_ops(tmp_path):
    storage_dir = tmp_path / "file_storage"
    cfg = {"storage_directory": str(storage_dir), "file_extension": ".json"}
    adapter = FileAdapter(cfg)

    await adapter.connect()

    await adapter.create_collection("notes")
    await adapter.store("notes", "n1", {"title": "Note 1", "body": "Hello"})

    data = await adapter.retrieve("notes", "n1")
    assert data["title"] == "Note 1"

    keys = await adapter.list_keys("notes")
    assert "n1" in keys

    assert await adapter.exists("notes", "n1")

    results = await adapter.query("notes", {"body": "Hello"})
    assert len(results) == 1

    await adapter.delete("notes", "n1")
    assert not await adapter.exists("notes", "n1")

    # bulk_store
    items = [{"_key": "a", "v": 1}, {"_key": "b", "v": 2}]
    await adapter.bulk_store("numbers", items)
    keys = await adapter.list_keys("numbers")
    assert set(keys) == {"a", "b"}

    await adapter.drop_collection("numbers")
    assert await adapter.list_keys("numbers") == []

    await adapter.disconnect()


@pytest.mark.asyncio
async def test_sqlite_adapter_basic_ops(tmp_path):
    if not SQLITE_AVAILABLE:
        pytest.skip("aiosqlite not installed in the environment")

    db_path = tmp_path / "test_skynet.db"
    cfg = {"database_path": str(db_path)}
    adapter = SQLiteAdapter(cfg)

    await adapter.connect()

    await adapter.create_collection("items")

    await adapter.store("items", "i1", {"name": "Item 1", "price": 9.99})
    data = await adapter.retrieve("items", "i1")
    assert data["name"] == "Item 1"

    assert await adapter.exists("items", "i1")

    keys = await adapter.list_keys("items")
    assert "i1" in keys

    results = await adapter.query("items", {"name": "Item 1"})
    assert len(results) == 1

    # bulk_store
    items = [{"_key": "x", "name": "X"}, {"_key": "y", "name": "Y"}]
    await adapter.bulk_store("items", items)
    keys = await adapter.list_keys("items")
    assert "x" in keys and "y" in keys

    await adapter.delete("items", "i1")
    assert not await adapter.exists("items", "i1")

    await adapter.drop_collection("items")

    await adapter.disconnect()


@pytest.mark.asyncio
async def test_storage_manager_and_global_adapter(tmp_path):
    # Create a memory adapter via manager
    cfg = {"type": "memory", "config": {"persist_to_file": False}}
    adapter = StorageManager.from_config(cfg)
    await set_storage_adapter(adapter)

    global_adapter = await get_storage_adapter()
    assert global_adapter is adapter

    await global_adapter.connect()
    await global_adapter.store("test", "k1", {"v": 1})
    data = await global_adapter.retrieve("test", "k1")
    assert data["v"] == 1

    await close_storage()


@pytest.mark.asyncio
async def test_invalid_adapter_type():
    with pytest.raises(ValueError):
        StorageManager.create_adapter("unknown", {})


# Cleanup hook for when tests create files
@pytest.fixture(scope="session", autouse=True)
def cleanup_tmp_dirs():
    yield
    # no-op: tmp_path will be removed by pytest
