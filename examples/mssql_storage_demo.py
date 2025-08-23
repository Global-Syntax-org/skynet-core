"""
Example usage of the storage abstraction layer with MSSQL

This script demonstrates how to configure and use MSSQL storage
for Skynet Lite data persistence.
"""

import asyncio
import logging
from skynet.storage import StorageManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def demo_mssql_storage():
    """Demonstrate MSSQL storage operations"""
    
    # MSSQL configuration
    mssql_config = {
        "type": "mssql",
        "config": {
            "server": "localhost",  # or your SQL Server instance
            "database": "skynet_lite",
            "username": "skynet_user",  # optional for Windows auth
            "password": "your_password",  # optional for Windows auth
            "trusted_connection": False,  # set to True for Windows auth
            "encrypt": True,
            "trust_server_certificate": True,  # for dev environments
            "connection_timeout": 30
        }
    }
    
    try:
        # Create MSSQL adapter
        logger.info("Creating MSSQL storage adapter...")
        storage = StorageManager.from_config(mssql_config)
        
        # Connect to database
        logger.info("Connecting to MSSQL database...")
        async with storage:
            logger.info("✅ Connected successfully!")
            
            # Store some test data
            conversation_data = {
                "user_id": "user123",
                "messages": [
                    {"role": "user", "content": "Hello"},
                    {"role": "assistant", "content": "Hi there!"}
                ],
                "timestamp": "2025-08-22T10:00:00Z"
            }
            
            logger.info("Storing conversation data...")
            await storage.store("conversations", "conv_001", conversation_data)
            
            # Retrieve data
            logger.info("Retrieving conversation data...")
            retrieved = await storage.retrieve("conversations", "conv_001")
            logger.info(f"Retrieved: {retrieved}")
            
            # Store user data
            user_data = {
                "username": "alice",
                "email": "alice@example.com",
                "preferences": {"theme": "dark", "notifications": True}
            }
            
            logger.info("Storing user data...")
            await storage.store("users", "alice", user_data)
            
            # Query operations
            logger.info("Querying conversations...")
            conversations = await storage.query("conversations", {"user_id": "user123"})
            logger.info(f"Found {len(conversations)} conversations")
            
            # List all keys
            logger.info("Listing conversation keys...")
            keys = await storage.list_keys("conversations")
            logger.info(f"Conversation keys: {keys}")
            
            # Check existence
            exists = await storage.exists("conversations", "conv_001")
            logger.info(f"conv_001 exists: {exists}")
            
            logger.info("✅ MSSQL storage demo completed successfully!")
            
    except ImportError as e:
        logger.error("❌ MSSQL dependencies not installed:")
        logger.error("   pip install pyodbc aioodbc")
        logger.error(f"   Error: {e}")
    except Exception as e:
        logger.error(f"❌ MSSQL storage demo failed: {e}")


async def demo_fallback_storage():
    """Demonstrate fallback to SQLite if MSSQL unavailable"""
    
    logger.info("Demonstrating storage fallback...")
    
    # Try MSSQL first, fallback to SQLite
    configs = [
        {
            "type": "mssql",
            "config": {
                "server": "nonexistent_server",
                "database": "skynet_lite",
                "trusted_connection": True
            }
        },
        {
            "type": "sqlite", 
            "config": {
                "database_path": "demo_storage.db"
            }
        }
    ]
    
    for i, config in enumerate(configs):
        try:
            logger.info(f"Trying {config['type']} storage...")
            storage = StorageManager.from_config(config)
            
            async with storage:
                # Test basic operation
                await storage.store("test", "demo", {"message": "Hello from storage!"})
                data = await storage.retrieve("test", "demo")
                logger.info(f"✅ {config['type']} storage working: {data}")
                break
                
        except Exception as e:
            logger.warning(f"❌ {config['type']} storage failed: {e}")
            if i == len(configs) - 1:
                logger.error("All storage options failed!")


async def main():
    """Main demo function"""
    logger.info("🚀 Skynet Lite Storage Abstraction Demo")
    logger.info("=" * 50)
    
    # Demo MSSQL (if available)
    await demo_mssql_storage()
    
    print()
    
    # Demo fallback behavior
    await demo_fallback_storage()


if __name__ == "__main__":
    asyncio.run(main())
