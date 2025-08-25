#!/usr/bin/env python3
"""
Quick demo of storage abstraction with MSSQL configuration

This script shows how to configure MSSQL storage for Skynet Core
without requiring an actual SQL Server instance.
"""

import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import asyncio
import logging
from skynet.storage import StorageManager

# Configure logging  
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def demo_mssql_config():
    """Demonstrate MSSQL configuration options"""
    
    logger.info("🔧 MSSQL Configuration Examples")
    logger.info("=" * 40)
    
    # Example 1: Windows Authentication
    windows_auth_config = {
        "type": "mssql",
        "config": {
            "server": "localhost\\SQLEXPRESS",
            "database": "skynet_core", 
            "trusted_connection": True,
            "encrypt": True,
            "trust_server_certificate": True  # For dev environments
        }
    }
    
    logger.info("Windows Authentication Config:")
    logger.info(f"  Server: {windows_auth_config['config']['server']}")
    logger.info(f"  Database: {windows_auth_config['config']['database']}")
    logger.info(f"  Trusted Connection: {windows_auth_config['config']['trusted_connection']}")
    
    # Example 2: SQL Server Authentication
    # Prefer pulling sensitive values from the environment. Example shows placeholders only.
    sql_auth_config = {
        "type": "mssql",
        "config": {
            "server": os.getenv("SKYNET_MSSQL_SERVER", "sqlserver.company.com"),
            "database": os.getenv("SKYNET_MSSQL_DATABASE", "skynet_production"),
            "username": os.getenv("SKYNET_MSSQL_USERNAME", "skynet_app"),
            # Never hard-code passwords in source. Use environment or a secrets manager.
            "password": os.getenv("SKYNET_MSSQL_PASSWORD"),
            "trusted_connection": False,
            "encrypt": True,
            "trust_server_certificate": False,
            "connection_timeout": 30
        }
    }

    logger.info("\nSQL Server Authentication Config (sensitive fields masked):")
    logger.info(f"  Server: {sql_auth_config['config']['server']}")
    logger.info(f"  Database: {sql_auth_config['config']['database']}")
    logger.info(f"  Username: {sql_auth_config['config']['username']}")
    pwd = sql_auth_config['config'].get('password')
    logger.info(f"  Password: {'***' if pwd else '(not set)'}")
    
    # Example 3: Azure SQL Database
    azure_config = {
        "type": "mssql",
        "config": {
            "server": "skynet-server.database.windows.net",
            "database": "skynet-db",
            "username": "skynet-admin",
            "password": "AzurePassword123!",
            "driver": "ODBC Driver 17 for SQL Server", 
            "encrypt": True,
            "trust_server_certificate": False,
            "connection_timeout": 30
        }
    }
    
    logger.info("\nAzure SQL Database Config:")
    logger.info(f"  Server: {azure_config['config']['server']}")
    logger.info(f"  Database: {azure_config['config']['database']}")
    logger.info(f"  Driver: {azure_config['config']['driver']}")
    
    return windows_auth_config, sql_auth_config, azure_config


def demo_connection_strings():
    """Show what connection strings would be generated"""
    
    logger.info("\n🔗 Generated Connection Strings")
    logger.info("=" * 40)
    
    try:
        from skynet.storage.mssql_adapter import MSSQLAdapter
        
        # Test connection string building 
        configs = [
            {
                "server": "localhost",
                "database": "skynet_core", 
                "trusted_connection": True,
                "encrypt": True
            },
        {
            "server": os.getenv("SKYNET_MSSQL_SERVER", "remote.database.com"),
            "database": os.getenv("SKYNET_MSSQL_DATABASE", "production_db"),
            "username": os.getenv("SKYNET_MSSQL_USERNAME", "app_user"),
            "password": os.getenv("SKYNET_MSSQL_PASSWORD"),
            "trusted_connection": False,
            "encrypt": True,
            "trust_server_certificate": False
            }
        ]
        
        for i, config in enumerate(configs, 1):
            try:
                adapter = MSSQLAdapter(config)
                conn_str = adapter._connection_string
                
                # Mask password in output
                display_str = conn_str
                if "PWD=" in display_str:
                    import re
                    display_str = re.sub(r'PWD=[^;]+', 'PWD=***', display_str)
                
                logger.info(f"\nConfig {i} Connection String:")
                logger.info(f"  {display_str}")
                
            except ImportError:
                logger.info(f"\nConfig {i}: MSSQL dependencies not available")
                
    except ImportError:
        logger.warning("MSSQL adapter not available - install dependencies:")
        logger.warning("  pip install pyodbc aioodbc")


async def demo_fallback_behavior():
    """Demonstrate storage fallback from MSSQL to SQLite"""
    
    logger.info("\n🔄 Fallback Behavior Demo")
    logger.info("=" * 40)
    
    # Try MSSQL first (will fail), then SQLite
    storage_configs = [
        {
            "type": "mssql",
            "config": {
                "server": "nonexistent.server.com",
                "database": "test_db",
                "trusted_connection": True
            }
        },
        {
            "type": "sqlite",
            "config": {
                "database_path": ":memory:"  # In-memory for demo
            }
        }
    ]
    
    for config in storage_configs:
        try:
            logger.info(f"Attempting {config['type']} storage...")
            storage = StorageManager.from_config(config)
            
            async with storage:
                # Test basic operation
                test_data = {"demo": True, "timestamp": "2025-08-22"}
                await storage.store("demo", "test", test_data)
                retrieved = await storage.retrieve("demo", "test")
                
                logger.info(f"✅ {config['type']} storage successful!")
                logger.info(f"   Stored and retrieved: {retrieved}")
                break
                
        except Exception as e:
            logger.warning(f"❌ {config['type']} storage failed: {e}")


def main():
    """Main demo function"""
    logger.info("🗃️  Skynet Core Storage Abstraction - MSSQL Demo")
    logger.info("=" * 50)
    
    # Show configuration examples
    demo_mssql_config()
    
    # Show connection string generation
    demo_connection_strings()
    
    # Show fallback behavior
    asyncio.run(demo_fallback_behavior())
    
    logger.info("\n📚 To use MSSQL storage:")
    logger.info("1. Install dependencies: pip install pyodbc aioodbc")
    logger.info("2. Set SKYNET_STORAGE_TYPE=mssql in .env")
    logger.info("3. Configure MSSQL_* environment variables")
    logger.info("4. Ensure SQL Server is accessible and database exists")
    
    logger.info("\n🔧 For troubleshooting:")
    logger.info("- Check ODBC driver installation")
    logger.info("- Verify network connectivity to SQL Server")
    logger.info("- Test connection with SQL Server Management Studio")
    logger.info("- Check firewall settings and SQL Server configuration")


if __name__ == "__main__":
    main()
