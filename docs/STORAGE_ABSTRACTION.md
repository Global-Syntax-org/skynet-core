# Storage Abstraction Layer

## Overview

The Skynet Core project now includes a comprehensive storage abstraction layer that provides a unified interface for multiple storage backends. This abstraction allows the system to work with different storage solutions without changing application code.

## Architecture

### Core Components

1. **StorageAdapter (Base Class)**: Abstract interface defining all storage operations
2. **Storage Adapters**: Concrete implementations for different backends
3. **StorageManager**: Factory and configuration management
4. **Configuration System**: Environment variable and programmatic configuration

### Available Storage Backends

1. **SQLite Adapter** (`sqlite_adapter.py`)
   - Default/fallback storage option
   - Uses aiosqlite for async operations
   - Automatic schema creation
   - File-based persistence

2. **MSSQL Adapter** (`mssql_adapter.py`)
   - Microsoft SQL Server support
   - Windows Authentication and SQL Authentication
   - Connection string building
   - Enterprise-ready with connection pooling

3. **File Adapter** (`file_adapter.py`)
   - JSON file-based storage
   - Uses aiofiles for async file operations
   - Collection-based directory structure
   - Human-readable storage format

4. **Memory Adapter** (`memory_adapter.py`)
   - In-memory storage using dictionaries
   - Optional file persistence
   - Fast performance for testing/caching
   - Deep copy data isolation

## Usage Examples

### Basic Usage

```python
from skynet.storage import StorageManager

# Create storage manager
manager = StorageManager()

# Get adapter (auto-detects from environment)
async with manager.get_adapter() as storage:
    # Store data
    await storage.store("users", "user1", {"name": "Alice", "age": 25})
    
    # Retrieve data
    user = await storage.retrieve("users", "user1")
    print(user)  # {"name": "Alice", "age": 25}
```

### Configuration via Environment Variables

```bash
# SQLite (default)
export SKYNET_STORAGE_TYPE=sqlite
export SKYNET_STORAGE_DATABASE_PATH=/path/to/database.db

# MSSQL with Windows Authentication
export SKYNET_STORAGE_TYPE=mssql
export SKYNET_STORAGE_SERVER=myserver
export SKYNET_STORAGE_DATABASE=mydatabase
export SKYNET_STORAGE_TRUSTED_CONNECTION=true

# MSSQL with SQL Authentication
export SKYNET_STORAGE_TYPE=mssql
export SKYNET_STORAGE_SERVER=myserver
export SKYNET_STORAGE_DATABASE=mydatabase
export SKYNET_STORAGE_USERNAME=myuser
export SKYNET_STORAGE_PASSWORD=mypassword

# File storage
export SKYNET_STORAGE_TYPE=file
export SKYNET_STORAGE_BASE_PATH=/path/to/storage/directory

# Memory storage
export SKYNET_STORAGE_TYPE=memory
export SKYNET_STORAGE_PERSIST_TO_FILE=true
export SKYNET_STORAGE_FILE_PATH=/path/to/memory_backup.json
```

### Programmatic Configuration

```python
from skynet.storage import StorageManager

# SQLite configuration
sqlite_config = {
    "type": "sqlite",
    "database_path": "/tmp/test.db"
}

# MSSQL configuration
mssql_config = {
    "type": "mssql",
    "server": "localhost",
    "database": "testdb",
    "trusted_connection": True,
    "encrypt": True
}

manager = StorageManager()
async with manager.get_adapter(sqlite_config) as storage:
    await storage.store("test", "key", {"data": "value"})
```

## Storage Operations

All adapters support the following operations:

- `store(collection, key, data)`: Store a document
- `retrieve(collection, key)`: Retrieve a document
- `update(collection, key, data)`: Update a document
- `delete(collection, key)`: Delete a document
- `exists(collection, key)`: Check if document exists
- `list_keys(collection)`: List all keys in collection
- `query(collection, filters)`: Query documents with filters
- `bulk_store(collection, items)`: Store multiple documents efficiently
- `create_collection(collection, schema=None)`: Create a new collection
- `drop_collection(collection)`: Drop a collection

## Testing

The storage system includes comprehensive tests:

```bash
# Run all storage tests
pytest tests/test_storage.py -v

# Run specific adapter tests
pytest tests/test_storage.py::TestMemoryAdapter -v
pytest tests/test_storage.py::TestSQLiteAdapter -v
pytest tests/test_storage.py::TestStorageManager -v
```

## Dependencies

### Required Dependencies
- `aiosqlite`: SQLite async support
- `aiofiles`: File async operations

### Optional Dependencies
- `pyodbc`: MSSQL support (system ODBC driver required)
- `aioodbc`: Async MSSQL support

### Installation

```bash
# Basic installation
pip install aiosqlite aiofiles

# With MSSQL support
pip install aiosqlite aiofiles pyodbc aioodbc
```

## Error Handling

The storage system includes comprehensive error handling:

- `ConnectionError`: Connection-related issues
- `DataError`: Data operation failures
- `ConfigurationError`: Configuration problems
- Graceful fallback from MSSQL to SQLite when dependencies unavailable

## Integration Examples

### Migrating Existing Code

Before (direct SQLite):
```python
import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()
cursor.execute("INSERT INTO users VALUES (?, ?)", ("user1", "Alice"))
conn.commit()
```

After (storage abstraction):
```python
from skynet.storage import StorageManager

manager = StorageManager()
async with manager.get_adapter() as storage:
    await storage.store("users", "user1", {"name": "Alice"})
```

### Using with Existing Skynet Components

The storage abstraction can be integrated with existing Skynet components:

1. **Memory Plugin**: Replace direct file I/O with storage abstraction
2. **Web Application**: Use for user data, session storage
3. **Authentication**: Store user credentials and tokens
4. **Configuration**: Store application settings

## Performance Considerations

- **Memory Adapter**: Fastest for temporary data, limited by RAM
- **SQLite Adapter**: Good balance of performance and persistence
- **File Adapter**: Good for human-readable data, slower for large datasets
- **MSSQL Adapter**: Best for enterprise applications with high concurrency

## Production Deployment

For production use:

1. **Use MSSQL** for enterprise applications requiring high availability
2. **Use SQLite** for single-instance applications or development
3. **Configure proper connection pooling** for MSSQL
4. **Set up backup strategies** for file-based storage
5. **Monitor storage performance** and adjust configurations as needed

## Future Enhancements

Potential future additions:
- PostgreSQL adapter
- Redis adapter for caching
- MongoDB adapter for document storage
- Encryption at rest
- Automatic schema migration
- Connection pooling for all adapters
- Distributed storage support
