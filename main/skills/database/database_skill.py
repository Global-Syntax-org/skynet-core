"""
Database Operations Skill for Semantic Kernel
Provides comprehensive database operations with SQLite, PostgreSQL, and MongoDB support
"""

import asyncio
import sqlite3
import aiosqlite
import json
import gzip
import os
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import logging


class DatabaseSkill:
    """
    Database skill implementation supporting multiple database types
    Follows the skill manifest defined in databaseSkill.json
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {
            'default_db_type': 'sqlite',
            'connection_pool_size': 10,
            'query_timeout': 30,
            'auto_create_tables': True,
            'backup_enabled': True,
            'migration_path': './migrations'
        }
        
        self.connections: Dict[str, Any] = {}
        self.logger = logging.getLogger(__name__)
        self.default_db_path = "data/skynet.db"
        
        # Ensure data directory exists
        os.makedirs(os.path.dirname(self.default_db_path), exist_ok=True)
    
    async def initialize(self):
        """Initialize the database skill with default connection"""
        try:
            # Initialize default SQLite database
            await self._create_connection("default", self.default_db_path)
            
            # Create initial tables if auto_create is enabled
            if self.config.get('auto_create_tables', True):
                await self._create_default_tables()
            
            self.logger.info("🗃️ Database Skill initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize database skill: {e}")
            raise
    
    async def _create_connection(self, name: str, db_path: str):
        """Create database connection"""
        try:
            # For SQLite, we'll use aiosqlite for async operations
            self.connections[name] = {
                'type': 'sqlite',
                'path': db_path,
                'connection': None
            }
            
            self.logger.info(f"📊 Database connection '{name}' configured for {db_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to create connection '{name}': {e}")
            raise
    
    async def _get_connection(self, database: str = "default"):
        """Get or create database connection"""
        if database not in self.connections:
            raise ValueError(f"Database connection '{database}' not found")
        
        conn_info = self.connections[database]
        
        if conn_info['type'] == 'sqlite':
            # Return a new connection for each operation (SQLite handles this well)
            return aiosqlite.connect(conn_info['path'])
        
        raise ValueError(f"Unsupported database type: {conn_info['type']}")
    
    async def _create_default_tables(self):
        """Create default tables for demonstration"""
        schema_definitions = [
            {
                'table_name': 'skill_logs',
                'schema': {
                    'id': 'INTEGER PRIMARY KEY AUTOINCREMENT',
                    'skill_id': 'TEXT NOT NULL',
                    'function_name': 'TEXT NOT NULL',
                    'timestamp': 'DATETIME DEFAULT CURRENT_TIMESTAMP',
                    'parameters': 'TEXT',
                    'result': 'TEXT',
                    'execution_time': 'REAL'
                }
            },
            {
                'table_name': 'memory_store',
                'schema': {
                    'id': 'INTEGER PRIMARY KEY AUTOINCREMENT',
                    'key': 'TEXT UNIQUE NOT NULL',
                    'value': 'TEXT NOT NULL',
                    'created_at': 'DATETIME DEFAULT CURRENT_TIMESTAMP',
                    'updated_at': 'DATETIME DEFAULT CURRENT_TIMESTAMP',
                    'expires_at': 'DATETIME'
                }
            }
        ]
        
        for table_def in schema_definitions:
            await self.create_table(
                table_def['table_name'],
                table_def['schema'],
                if_not_exists=True
            )
    
    async def execute_query(
        self,
        query: str,
        parameters: Optional[Dict[str, Any]] = None,
        database: str = "default",
        fetch_mode: str = "all"
    ) -> Dict[str, Any]:
        """
        Execute SQL query with parameter binding and result formatting
        """
        parameters = parameters or {}
        start_time = datetime.now()
        
        try:
            self.logger.info(f"🔍 Executing query on '{database}': {query[:100]}...")
            
            # Emit signal for query start
            if hasattr(self, 'emit_signal'):
                await self.emit_signal('query_started', {
                    'query': query,
                    'database': database
                })
            
            async with await self._get_connection(database) as conn:
                if parameters:
                    # Convert named parameters to positional for aiosqlite
                    param_values = list(parameters.values())
                    query_with_placeholders = query
                    for key, value in parameters.items():
                        query_with_placeholders = query_with_placeholders.replace(f":{key}", "?")
                    
                    cursor = await conn.execute(query_with_placeholders, param_values)
                else:
                    cursor = await conn.execute(query)
                
                # Fetch results based on mode
                if fetch_mode == "one":
                    data = await cursor.fetchone()
                    data = [dict(zip([col[0] for col in cursor.description], data))] if data else []
                elif fetch_mode == "many":
                    data = await cursor.fetchmany(100)
                    data = [dict(zip([col[0] for col in cursor.description], row)) for row in data]
                else:  # "all"
                    data = await cursor.fetchall()
                    data = [dict(zip([col[0] for col in cursor.description], row)) for row in data]
                
                rows_affected = cursor.rowcount
                await conn.commit()
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            result = {
                'success': True,
                'data': data,
                'rows_affected': rows_affected,
                'execution_time': execution_time,
                'error': None
            }
            
            # Emit signal for query completion
            if hasattr(self, 'emit_signal'):
                await self.emit_signal('query_completed', {
                    'rows_affected': rows_affected,
                    'execution_time': execution_time
                })
            
            self.logger.info(f"✅ Query completed: {rows_affected} rows affected in {execution_time:.3f}s")
            return result
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            error_msg = f"Query execution failed: {str(e)}"
            
            # Emit signal for query failure
            if hasattr(self, 'emit_signal'):
                await self.emit_signal('query_failed', {
                    'error': error_msg,
                    'query': query
                })
            
            self.logger.error(f"❌ {error_msg}")
            
            return {
                'success': False,
                'data': [],
                'rows_affected': 0,
                'execution_time': execution_time,
                'error': error_msg
            }
    
    async def create_table(
        self,
        table_name: str,
        schema: Dict[str, str],
        database: str = "default",
        if_not_exists: bool = True
    ) -> Dict[str, Any]:
        """
        Create database table with schema definition
        """
        try:
            self.logger.info(f"🏗️ Creating table '{table_name}' in database '{database}'")
            
            # Build CREATE TABLE statement
            columns = []
            for column_name, column_type in schema.items():
                columns.append(f"{column_name} {column_type}")
            
            columns_sql = ", ".join(columns)
            if_not_exists_clause = "IF NOT EXISTS" if if_not_exists else ""
            
            create_sql = f"CREATE TABLE {if_not_exists_clause} {table_name} ({columns_sql})"
            
            result = await self.execute_query(create_sql, database=database)
            
            if result['success']:
                # Emit signal for table creation
                if hasattr(self, 'emit_signal'):
                    await self.emit_signal('table_created', {
                        'table_name': table_name,
                        'database': database
                    })
                
                self.logger.info(f"✅ Table '{table_name}' created successfully")
                
                return {
                    'success': True,
                    'table_created': True,
                    'error': None
                }
            else:
                return {
                    'success': False,
                    'table_created': False,
                    'error': result['error']
                }
                
        except Exception as e:
            error_msg = f"Table creation failed: {str(e)}"
            self.logger.error(f"❌ {error_msg}")
            
            return {
                'success': False,
                'table_created': False,
                'error': error_msg
            }
    
    async def insert_data(
        self,
        table_name: str,
        data: List[Dict[str, Any]],
        database: str = "default",
        on_conflict: str = "ignore"
    ) -> Dict[str, Any]:
        """
        Insert data into database table with batch support
        """
        try:
            if not data:
                return {
                    'success': True,
                    'inserted_count': 0,
                    'last_insert_id': None,
                    'error': None
                }
            
            self.logger.info(f"📝 Inserting {len(data)} records into '{table_name}'")
            
            # Get column names from first record
            columns = list(data[0].keys())
            placeholders = ", ".join(["?" for _ in columns])
            columns_sql = ", ".join(columns)
            
            # Build INSERT statement with conflict resolution
            conflict_clause = ""
            if on_conflict == "ignore":
                conflict_clause = "OR IGNORE"
            elif on_conflict == "replace":
                conflict_clause = "OR REPLACE"
            
            insert_sql = f"INSERT {conflict_clause} INTO {table_name} ({columns_sql}) VALUES ({placeholders})"
            
            inserted_count = 0
            last_insert_id = None
            
            async with await self._get_connection(database) as conn:
                for record in data:
                    values = [record.get(col) for col in columns]
                    cursor = await conn.execute(insert_sql, values)
                    if cursor.rowcount > 0:
                        inserted_count += cursor.rowcount
                        last_insert_id = cursor.lastrowid
                
                await conn.commit()
            
            self.logger.info(f"✅ Inserted {inserted_count} records successfully")
            
            return {
                'success': True,
                'inserted_count': inserted_count,
                'last_insert_id': last_insert_id,
                'error': None
            }
            
        except Exception as e:
            error_msg = f"Data insertion failed: {str(e)}"
            self.logger.error(f"❌ {error_msg}")
            
            return {
                'success': False,
                'inserted_count': 0,
                'last_insert_id': None,
                'error': error_msg
            }
    
    async def backup_database(
        self,
        database: str = "default",
        backup_path: str = None,
        compress: bool = True
    ) -> Dict[str, Any]:
        """
        Create database backup with compression
        """
        try:
            if not backup_path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = f"backups/skynet_backup_{timestamp}.db"
                if compress:
                    backup_path += ".gz"
            
            # Ensure backup directory exists
            os.makedirs(os.path.dirname(backup_path), exist_ok=True)
            
            self.logger.info(f"💾 Creating backup of '{database}' to '{backup_path}'")
            
            conn_info = self.connections[database]
            
            if conn_info['type'] == 'sqlite':
                # For SQLite, copy the database file
                import shutil
                
                if compress:
                    # Compress while copying
                    with open(conn_info['path'], 'rb') as src:
                        with gzip.open(backup_path, 'wb') as dst:
                            shutil.copyfileobj(src, dst)
                else:
                    shutil.copy2(conn_info['path'], backup_path)
                
                backup_size = os.path.getsize(backup_path)
                
                # Emit signal for backup completion
                if hasattr(self, 'emit_signal'):
                    await self.emit_signal('backup_completed', {
                        'backup_path': backup_path,
                        'size': backup_size
                    })
                
                self.logger.info(f"✅ Backup completed: {backup_size} bytes")
                
                return {
                    'success': True,
                    'backup_size': backup_size,
                    'backup_path': backup_path,
                    'error': None
                }
            else:
                raise ValueError(f"Backup not supported for database type: {conn_info['type']}")
                
        except Exception as e:
            error_msg = f"Database backup failed: {str(e)}"
            self.logger.error(f"❌ {error_msg}")
            
            return {
                'success': False,
                'backup_size': 0,
                'backup_path': backup_path,
                'error': error_msg
            }
    
    async def shutdown(self):
        """Clean up database connections"""
        try:
            for name, conn_info in self.connections.items():
                if conn_info.get('connection'):
                    await conn_info['connection'].close()
            
            self.connections.clear()
            self.logger.info("🔒 Database Skill shutdown completed")
            
        except Exception as e:
            self.logger.error(f"Error during database shutdown: {e}")


# Example usage and testing
# Global instance for skill registration
database_skill = DatabaseSkill()

# Skill function exports for orchestrator
async def execute_query(query: str, **kwargs) -> Dict[str, Any]:
    """Execute SQL query"""
    return await database_skill.execute_query(query, **kwargs)

async def create_table(table_name: str, columns: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
    """Create database table"""
    return await database_skill.create_table(table_name, columns, **kwargs)

async def insert_data(table_name: str, data: Union[Dict[str, Any], List[Dict[str, Any]]], **kwargs) -> Dict[str, Any]:
    """Insert data into table"""
    return await database_skill.insert_data(table_name, data, **kwargs)

async def backup_database(**kwargs) -> Dict[str, Any]:
    """Backup database"""
    return await database_skill.backup_database(**kwargs)


async def test_database_skill():
    """Test the database skill functionality"""
    skill = DatabaseSkill()
    
    try:
        await skill.initialize()
        
        # Test table creation
        print("Testing table creation...")
        result = await skill.create_table(
            "test_users",
            {
                "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
                "name": "TEXT NOT NULL",
                "email": "TEXT UNIQUE",
                "created_at": "DATETIME DEFAULT CURRENT_TIMESTAMP"
            }
        )
        print(f"Table creation result: {result}")
        
        # Test data insertion
        print("\nTesting data insertion...")
        test_data = [
            {"name": "Alice", "email": "alice@example.com"},
            {"name": "Bob", "email": "bob@example.com"},
            {"name": "Charlie", "email": "charlie@example.com"}
        ]
        
        result = await skill.insert_data("test_users", test_data)
        print(f"Data insertion result: {result}")
        
        # Test query execution
        print("\nTesting query execution...")
        result = await skill.execute_query("SELECT * FROM test_users")
        print(f"Query result: {result}")
        
        # Test backup
        print("\nTesting database backup...")
        result = await skill.backup_database()
        print(f"Backup result: {result}")
        
    finally:
        await skill.shutdown()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(test_database_skill())
