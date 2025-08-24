#!/usr/bin/env python3
"""
Quick MSSQL setup and test script for Skynet Lite

This script helps you quickly configure and test MSSQL storage.
Run with different arguments to test various configurations.
"""

import sys
import os
import asyncio
import logging
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from skynet.storage import StorageManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def check_dependencies():
    """Check if MSSQL dependencies are installed"""
    try:
        import pyodbc
        import aioodbc
        logger.info("✅ MSSQL dependencies are installed")
        return True
    except ImportError as e:
        logger.error("❌ MSSQL dependencies not found!")
        logger.error("Install with: pip install pyodbc aioodbc")
        logger.error(f"Error: {e}")
        return False


def show_docker_setup():
    """Show Docker SQL Server setup commands"""
    logger.info("\n🐳 Quick SQL Server Docker Setup:")
    logger.info("=" * 40)
    
    docker_commands = [
        "# 1. Run SQL Server in Docker",
        'docker run -e "ACCEPT_EULA=Y" -e "SA_PASSWORD=YourStrong@Passw0rd" \\',
        '   -p 1433:1433 --name sqlserver \\',
        '   -d mcr.microsoft.com/mssql/server:2019-latest',
        "",
        "# 2. Create database (optional)",
        'docker exec -it sqlserver /opt/mssql-tools/bin/sqlcmd \\',
        '   -S localhost -U SA -P "YourStrong@Passw0rd" \\',
        '   -Q "CREATE DATABASE skynet_lite"',
        "",
        "# 3. Check if container is running",
        "docker ps",
        "",
        "# 4. Stop container when done",
        "docker stop sqlserver && docker rm sqlserver"
    ]
    
    for cmd in docker_commands:
        logger.info(cmd)


def get_test_configs():
    """Get test configurations for different scenarios"""
    return {
        "docker": {
            "type": "mssql",
            "config": {
                "server": "localhost",
                "database": "skynet_lite", 
                "username": "sa",
                "password": "YourStrong@Passw0rd",
                "encrypt": True,
                "trust_server_certificate": True,
                "connection_timeout": 30
            }
        },
        "local_express": {
            "type": "mssql",
            "config": {
                "server": "localhost\\SQLEXPRESS",
                "database": "skynet_lite",
                "trusted_connection": True,
                "encrypt": True,
                "trust_server_certificate": True
            }
        },
        "azure": {
            "type": "mssql",
            "config": {
                "server": "your-server.database.windows.net",
                "database": "skynet_lite",
                "username": "your-admin@your-server",
                "password": "YourAzurePassword123!",
                "encrypt": True,
                "trust_server_certificate": False,
                "connection_timeout": 30
            }
        }
    }


async def test_mssql_connection(config_name, config):
    """Test MSSQL connection and basic operations"""
    logger.info(f"\n🧪 Testing {config_name} configuration...")
    logger.info("=" * 50)
    
    try:
        # Create storage adapter
        storage = StorageManager.from_config(config)
        
        # Test connection
        logger.info("Connecting to MSSQL...")
        async with storage:
            logger.info("✅ Connected successfully!")
            
            # Test basic operations
            test_data = {
                "test_type": config_name,
                "timestamp": "2025-08-22T10:30:00Z",
                "data": {"message": "Hello from MSSQL!"}
            }
            
            # Store test data
            logger.info("Storing test data...")
            await storage.store("test", "connection_test", test_data)
            logger.info("✅ Data stored successfully!")
            
            # Retrieve test data
            logger.info("Retrieving test data...")
            retrieved = await storage.retrieve("test", "connection_test")
            logger.info(f"✅ Data retrieved: {retrieved}")
            
            # Query test
            logger.info("Testing query...")
            results = await storage.query("test", {"test_type": config_name})
            logger.info(f"✅ Query results: {len(results)} items found")
            
            # Cleanup
            logger.info("Cleaning up test data...")
            await storage.delete("test", "connection_test")
            logger.info("✅ Test completed successfully!")
            
            return True
            
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        return False


def show_environment_setup(config_name, config):
    """Show environment variable setup for configuration"""
    logger.info(f"\n📝 Environment Variables for {config_name}:")
    logger.info("=" * 50)
    
    env_vars = [
        "export SKYNET_STORAGE_TYPE=mssql",
        f"export MSSQL_SERVER=\"{config['config']['server']}\"",
        f"export MSSQL_DATABASE=\"{config['config']['database']}\""
    ]
    
    if config['config'].get('username'):
        env_vars.append(f"export MSSQL_USERNAME=\"{config['config']['username']}\"")
        env_vars.append(f"export MSSQL_PASSWORD=\"{config['config']['password']}\"")
    
    if config['config'].get('trusted_connection'):
        env_vars.append("export MSSQL_TRUSTED_CONNECTION=true")
    
    if config['config'].get('encrypt'):
        env_vars.append("export MSSQL_ENCRYPT=true")
        
    if config['config'].get('trust_server_certificate'):
        env_vars.append("export MSSQL_TRUST_CERT=true")
    
    for var in env_vars:
        logger.info(var)


async def main():
    """Main function"""
    logger.info("🗃️  Skynet Lite - MSSQL Setup & Test Tool")
    logger.info("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        return
    
    # Get command line argument for configuration type
    config_type = sys.argv[1] if len(sys.argv) > 1 else "docker"
    
    # Show available options
    if config_type == "help" or config_type == "--help":
        logger.info("Usage: python mssql_setup.py [config_type]")
        logger.info("\nAvailable configurations:")
        logger.info("  docker      - Docker SQL Server (default)")
        logger.info("  local_express - Local SQL Server Express")
        logger.info("  azure       - Azure SQL Database") 
        logger.info("  help        - Show this help")
        return
    
    # Get configurations
    configs = get_test_configs()
    
    if config_type not in configs:
        logger.error(f"Unknown configuration: {config_type}")
        logger.info(f"Available: {list(configs.keys())}")
        return
    
    config = configs[config_type]
    
    # Show Docker setup if using docker config
    if config_type == "docker":
        show_docker_setup()
    
    # Show environment setup
    show_environment_setup(config_type, config)
    
    # Ask user if they want to test connection
    logger.info(f"\n🤔 Ready to test {config_type} connection?")
    logger.info("Make sure your SQL Server is running and accessible.")
    
    try:
        response = input("Continue with connection test? (y/N): ").strip().lower()
        if response in ['y', 'yes']:
            success = await test_mssql_connection(config_type, config)
            if success:
                logger.info("\n🎉 MSSQL setup successful!")
                logger.info("You can now use MSSQL with Skynet Lite.")
            else:
                logger.info("\n💡 Setup Tips:")
                logger.info("1. Make sure SQL Server is running")
                logger.info("2. Check connection string parameters")
                logger.info("3. Verify network connectivity")
                logger.info("4. Check authentication credentials")
        else:
            logger.info("Test skipped. Configuration shown above.")
            
    except KeyboardInterrupt:
        logger.info("\nTest cancelled by user.")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
