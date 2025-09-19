# Using MSSQL with Skynet Core

This guide shows you how to configure and use Microsoft SQL Server (MSSQL) as the storage backend for Skynet Core.

## Prerequisites

### 1. Install MSSQL Dependencies

```bash
# Install required Python packages
pip install pyodbc aioodbc

# On Ubuntu/Debian, you may need ODBC drivers
sudo apt-get update
sudo apt-get install unixodbc-dev

# Install Microsoft ODBC Driver for SQL Server
curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
curl https://packages.microsoft.com/config/ubuntu/20.04/prod.list > /etc/apt/sources.list.d/mssql-release.list
sudo apt-get update
sudo ACCEPT_EULA=Y apt-get install msodbcsql17
```

### 2. SQL Server Setup

You need access to a SQL Server instance. Options:
- **Local SQL Server Express** (free)
- **Azure SQL Database** (cloud)
- **SQL Server Developer Edition** (free for dev)
- **Docker SQL Server** (quick setup)

#### Quick Docker Setup:
```bash
# Run SQL Server in Docker
docker run -e "ACCEPT_EULA=Y" -e "SA_PASSWORD=$SA_PASSWORD" \
    -p 1433:1433 --name sqlserver \
    -d mcr.microsoft.com/mssql/server:2019-latest

# Create database (optional - adapter will create if needed)
docker exec -it sqlserver /opt/mssql-tools/bin/sqlcmd \
    -S localhost -U SA -P "$SA_PASSWORD" \
    -Q "CREATE DATABASE skynet_core"
```

## Configuration Methods

### Method 1: Environment Variables

```bash
# Set environment variables
export SKYNET_STORAGE_TYPE=mssql
export MSSQL_SERVER=localhost
export MSSQL_DATABASE=skynet_core
export MSSQL_USERNAME=sa
# Do NOT commit real passwords to source control. Set the password in your shell or use a secrets manager.
export MSSQL_PASSWORD=$MSSQL_PASSWORD
export MSSQL_ENCRYPT=true
export MSSQL_TRUST_CERT=true
```

### Method 2: Programmatic Configuration

```python
from skynet.storage import StorageManager

# SQL Server Authentication
mssql_config = {
    "type": "mssql",
    "config": {
        "server": "localhost",
        "database": "skynet_core",
        "username": "sa",
    "password": os.getenv("MSSQL_PASSWORD") or "(set via environment)",
        "encrypt": True,
        "trust_server_certificate": True,  # For dev environments
        "connection_timeout": 30
    }
}

# Windows Authentication (if on Windows)
windows_auth_config = {
    "type": "mssql", 
    "config": {
        "server": "localhost\\SQLEXPRESS",
        "database": "skynet_core",
        "trusted_connection": True,
        "encrypt": True,
        "trust_server_certificate": True
    }
}

# Azure SQL Database
azure_config = {
    "type": "mssql",
    "config": {
        "server": "your-server.database.windows.net",
        "database": "skynet_core",
        "username": "your-admin@your-server",
    "password": os.getenv("AZURE_SQL_PASSWORD") or "(set via environment)",
        "encrypt": True,
        "trust_server_certificate": False,
        "connection_timeout": 30
    }
}
```

## Usage Examples

### Basic Usage

```python
import asyncio
from skynet.storage import StorageManager

async def main():
    # Create storage manager
    manager = StorageManager()
    
    # Method 1: From environment variables
    storage = manager.from_env()
    
    # Method 2: From configuration
    config = {
        "type": "mssql",
        "config": {
            "server": "localhost",
            "database": "skynet_core",
            "username": "sa", 
            "password": os.getenv("MSSQL_PASSWORD") or "(set via environment)",
            "encrypt": True,
            "trust_server_certificate": True
        }
    }
    storage = manager.from_config(config)
    
    # Connect and use storage
    async with storage:
        # Store data
        await storage.store("users", "user1", {
            "name": "Alice",
            "email": "alice@example.com",
            "created": "2025-08-22"
        })
        
        # Retrieve data  
        user = await storage.retrieve("users", "user1")
        print(f"Retrieved user: {user}")
        
        # Query data
        results = await storage.query("users", {"name": "Alice"})
        print(f"Query results: {results}")
        
        # List all keys in collection
        keys = await storage.list_keys("users")
        print(f"All user keys: {keys}")

if __name__ == "__main__":
    asyncio.run(main())
```

### Advanced Usage

```python
import asyncio
from skynet.storage import StorageManager

async def advanced_mssql_demo():
    """Advanced MSSQL storage operations"""
    
    config = {
        "type": "mssql",
        "config": {
            "server": "localhost",
            "database": "skynet_core",
            "username": "sa",
            "password": os.getenv("MSSQL_PASSWORD") or "(set via environment)", 
            "encrypt": True,
            "trust_server_certificate": True,
            "connection_timeout": 30,
            "command_timeout": 30
        }
    }
    
    storage = StorageManager.from_config(config)
    
    async with storage:
        # Bulk store multiple items
        items = [
            {"_key": "conv1", "user": "alice", "messages": 5},
            {"_key": "conv2", "user": "bob", "messages": 3},
            {"_key": "conv3", "user": "alice", "messages": 8}
        ]
        
        result = await storage.bulk_store("conversations", items)
        print(f"Bulk store result: {result}")
        
        # Create collection with schema (optional)
        schema = {
            "user": "string",
            "messages": "integer", 
            "created": "datetime"
        }
        await storage.create_collection("chat_logs", schema)
        
        # Complex query
        alice_convs = await storage.query("conversations", {"user": "alice"})
        print(f"Alice's conversations: {alice_convs}")
        
        # Check if item exists
        exists = await storage.exists("conversations", "conv1")
        print(f"Conv1 exists: {exists}")
        
        # Update item
        await storage.update("conversations", "conv1", {
            "user": "alice",
            "messages": 7,
            "last_updated": "2025-08-22"
        })
        
        # Delete item
        await storage.delete("conversations", "conv2")
        
        # List remaining keys
        remaining = await storage.list_keys("conversations")
        print(f"Remaining conversations: {remaining}")

asyncio.run(advanced_mssql_demo())
```

### Integration with Existing Skynet Components

```python
# Update main.py to use MSSQL storage
import asyncio
from skynet.storage import StorageManager

async def setup_storage():
    """Initialize MSSQL storage for Skynet"""
    config = {
        "type": "mssql",
        "config": {
            "server": "localhost",
            "database": "skynet_core",
            "username": "sa",
            "password": os.getenv("MSSQL_PASSWORD") or "(set via environment)",
            "encrypt": True,
            "trust_server_certificate": True
        }
    }
    
    storage = StorageManager.from_config(config)
    await storage.connect()
    return storage

# In your Skynet application
async def main():
    storage = await setup_storage()
    
    # Store conversation history
    await storage.store("conversations", "session_123", {
        "user_id": "user456",
        "messages": [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"}
        ],
        "created": "2025-08-22T10:30:00Z"
    })
    
    # Retrieve for context
    history = await storage.retrieve("conversations", "session_123")
    print(f"Conversation history: {history}")
```

## Configuration Options

| Parameter | Description | Default | Required |
|-----------|-------------|---------|----------|
| `server` | SQL Server hostname/IP | `localhost` | Yes |
| `database` | Database name | `skynet_core` | Yes |
| `username` | SQL auth username | None | No* |
| `password` | SQL auth password | None | No* |
| `trusted_connection` | Use Windows auth | `False` | No |
| `driver` | ODBC driver name | `ODBC Driver 17 for SQL Server` | No |
| `encrypt` | Encrypt connection | `True` | No |
| `trust_server_certificate` | Trust self-signed certs | `False` | No |
| `connection_timeout` | Connection timeout (seconds) | `30` | No |
| `command_timeout` | Command timeout (seconds) | `30` | No |

*Required for SQL Server authentication, not needed for Windows authentication

## Common Connection Strings

### Local SQL Server Express
```
Driver={ODBC Driver 17 for SQL Server};Server=localhost\SQLEXPRESS;Database=skynet_core;Trusted_Connection=yes;Encrypt=yes;TrustServerCertificate=yes
```

### Remote SQL Server with SQL Auth
```
Driver={ODBC Driver 17 for SQL Server};Server=myserver.com;Database=skynet_core;UID=myuser;PWD=mypass;Encrypt=yes
```

### Azure SQL Database
```
Driver={ODBC Driver 17 for SQL Server};Server=myserver.database.windows.net;Database=skynet_core;UID=myadmin@myserver;PWD=mypass;Encrypt=yes
```

## Troubleshooting

### Common Issues

1. **Import Error**: `MSSQL dependencies not available`
   ```bash
   pip install pyodbc aioodbc
   ```

2. **Connection Timeout**: Increase timeout values
   ```python
   config["connection_timeout"] = 60
   config["command_timeout"] = 60
   ```

3. **SSL Certificate Issues**: For development
   ```python
   config["trust_server_certificate"] = True
   ```

4. **Authentication Failed**: Check credentials and authentication method
   ```python
   # For Windows auth
   config["trusted_connection"] = True
   # Remove username/password
   
   # For SQL auth  
   config["trusted_connection"] = False
   config["username"] = "your_user"
   config["password"] = "your_pass"
   ```

5. **Driver Not Found**: Install ODBC driver
   ```bash
   # Ubuntu/Debian
   sudo ACCEPT_EULA=Y apt-get install msodbcsql17
   
   # Check available drivers
   odbcinst -q -d
   ```

### Fallback Behavior

If MSSQL fails, Skynet automatically falls back to SQLite:

```python
# This will try MSSQL first, then SQLite if it fails
storage = StorageManager.from_env()
```

## Performance Tips

1. **Use connection pooling** for high-traffic applications
2. **Create indexes** on frequently queried columns
3. **Use bulk operations** for multiple items
4. **Configure appropriate timeouts** for your network
5. **Monitor SQL Server performance** with built-in tools

## Production Deployment

For production environments:

1. **Use proper authentication** (not SA account)
2. **Enable SSL encryption** (`encrypt=True`)
3. **Use connection pooling**
4. **Configure backup strategies**
5. **Monitor database performance**
6. **Set up high availability** if needed

```python
# Production configuration example
production_config = {
    "type": "mssql",
    "config": {
        "server": "prod-sql-server.company.com",
        "database": "skynet_production",
        "username": "skynet_app_user",
        "password": os.getenv("SQL_PASSWORD"),  # From environment
        "encrypt": True,
        "trust_server_certificate": False,
        "connection_timeout": 30,
        "command_timeout": 60
    }
}
```
