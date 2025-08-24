import os
import pytest

from typing import Dict

try:
    from skynet.storage.mssql_adapter import MSSQLAdapter, MSSQL_AVAILABLE
except Exception:
    MSSQL_AVAILABLE = False


MSSQL_TEST_ENV_VARS = [
    "MSSQL_TEST_SERVER",
    "MSSQL_TEST_DATABASE",
]


def _have_test_env() -> bool:
    # Require server and database; either username+password or trusted connection
    has_core = all(os.getenv(k) for k in MSSQL_TEST_ENV_VARS)
    if not has_core:
        return False

    username = os.getenv("MSSQL_TEST_USERNAME")
    password = os.getenv("MSSQL_TEST_PASSWORD")
    trusted = os.getenv("MSSQL_TEST_TRUSTED_CONNECTION", "false").lower() == "true"

    return trusted or (username and password)


@pytest.mark.asyncio
async def test_mssql_adapter_end_to_end():
    if not MSSQL_AVAILABLE:
        pytest.skip("MSSQL adapter dependencies (pyodbc/aioodbc) not installed")

    if not _have_test_env():
        pytest.skip("MSSQL test environment variables not set. Set MSSQL_TEST_SERVER and MSSQL_TEST_DATABASE and either MSSQL_TEST_USERNAME + MSSQL_TEST_PASSWORD or MSSQL_TEST_TRUSTED_CONNECTION=true")

    config: Dict = {
        "server": os.getenv("MSSQL_TEST_SERVER"),
        "database": os.getenv("MSSQL_TEST_DATABASE"),
        "driver": os.getenv("MSSQL_TEST_DRIVER", "ODBC Driver 17 for SQL Server"),
        "trusted_connection": os.getenv("MSSQL_TEST_TRUSTED_CONNECTION", "false").lower() == "true",
        "encrypt": os.getenv("MSSQL_TEST_ENCRYPT", "true").lower() == "true",
        "trust_server_certificate": os.getenv("MSSQL_TEST_TRUST_CERT", "false").lower() == "true",
        "connection_timeout": int(os.getenv("MSSQL_TEST_CONN_TIMEOUT", "30")),
        "command_timeout": int(os.getenv("MSSQL_TEST_CMD_TIMEOUT", "30"))
    }

    # Optional credentials
    if os.getenv("MSSQL_TEST_USERNAME") and os.getenv("MSSQL_TEST_PASSWORD"):
        config["username"] = os.getenv("MSSQL_TEST_USERNAME")
        config["password"] = os.getenv("MSSQL_TEST_PASSWORD")

    adapter = MSSQLAdapter(config)

    # Connect and exercise basic CRUD
    await adapter.connect()

    # Use a unique test collection name to avoid collisions
    collection = "pytest_test_collection"
    await adapter.create_collection(collection)

    await adapter.store(collection, "k1", {"n": "one"})
    v = await adapter.retrieve(collection, "k1")
    assert v and v.get("n") == "one"

    assert await adapter.exists(collection, "k1")

    keys = await adapter.list_keys(collection)
    assert "k1" in keys

    await adapter.bulk_store(collection, [{"_key": "a", "v": 1}, {"_key": "b", "v": 2}])
    keys = await adapter.list_keys(collection)
    assert set(["a", "b"]).issubset(set(keys))

    await adapter.delete(collection, "k1")
    assert not await adapter.exists(collection, "k1")

    # Cleanup
    await adapter.drop_collection(collection)
    await adapter.disconnect()
