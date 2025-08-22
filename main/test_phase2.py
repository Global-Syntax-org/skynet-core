"""
Phase 2 Test Suite - Advanced Skills Testing
Tests database, filesystem, API integration, and memory skills
"""

import asyncio
import pytest
import json
import tempfile
import shutil
from pathlib import Path
import sys
import os

# Add skills to path
sys.path.append("main/skills")
sys.path.append("main/skills/database")
sys.path.append("main/skills/filesystem")
sys.path.append("main/skills/api")
sys.path.append("main/skills/memory")

# Test configuration
TEST_CONFIG = {
    "database": {
        "test_db": "test_memory.db"
    },
    "filesystem": {
        "test_dir": "test_sandbox"
    },
    "api": {
        "test_server": "https://httpbin.org"
    },
    "memory": {
        "test_memories": [
            "The weather is sunny today",
            "Python is a programming language",
            "Machine learning requires data",
            "Robots can perform automated tasks",
            "Neural networks learn from examples"
        ]
    }
}

class TestPhase2Skills:
    """Phase 2 Skills Testing Suite"""
    
    @pytest.fixture(autouse=True)
    async def setup_and_teardown(self):
        """Setup and teardown for tests"""
        # Setup
        self.test_dir = Path(TEST_CONFIG["filesystem"]["test_dir"])
        self.test_dir.mkdir(exist_ok=True)
        
        # Cleanup old test files
        test_db = Path(TEST_CONFIG["database"]["test_db"])
        if test_db.exists():
            test_db.unlink()
        
        yield
        
        # Teardown
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
        if test_db.exists():
            test_db.unlink()
    
    @pytest.mark.asyncio
    async def test_database_skill(self):
        """Test database operations"""
        try:
            from database_skill import create_table, insert_data, execute_query, backup_database
            
            # Test table creation
            result = await create_table(
                table_name="test_users",
                columns=[
                    {"name": "id", "type": "INTEGER PRIMARY KEY"},
                    {"name": "name", "type": "TEXT NOT NULL"},
                    {"name": "email", "type": "TEXT UNIQUE"}
                ],
                database=TEST_CONFIG["database"]["test_db"]
            )
            assert result["success"], f"Table creation failed: {result}"
            
            # Test data insertion
            result = await insert_data(
                table_name="test_users",
                data={"name": "John Doe", "email": "john@example.com"},
                database=TEST_CONFIG["database"]["test_db"]
            )
            assert result["success"], f"Data insertion failed: {result}"
            
            # Test query execution
            result = await execute_query(
                query="SELECT * FROM test_users WHERE name = ?",
                parameters=["John Doe"],
                database=TEST_CONFIG["database"]["test_db"]
            )
            assert result["success"], f"Query execution failed: {result}"
            assert len(result["results"]) == 1, "Expected 1 result"
            assert result["results"][0]["name"] == "John Doe", "Name mismatch"
            
            # Test backup
            result = await backup_database(
                database=TEST_CONFIG["database"]["test_db"],
                backup_path="test_backup.sql"
            )
            assert result["success"], f"Database backup failed: {result}"
            
            print("✅ Database skill tests passed")
            return True
            
        except ImportError as e:
            print(f"⚠️ Database skill not available: {e}")
            return False
        except Exception as e:
            print(f"❌ Database skill test failed: {e}")
            return False
    
    @pytest.mark.asyncio
    async def test_filesystem_skill(self):
        """Test filesystem operations"""
        try:
            from filesystem_skill import write_file, read_file, list_directory, search_files, compress_files
            
            test_content = "This is a test file for Phase 2 filesystem skill testing."
            test_file = self.test_dir / "test_file.txt"
            
            # Test file writing
            result = await write_file(
                path=str(test_file),
                content=test_content,
                create_dirs=True
            )
            assert result["success"], f"File writing failed: {result}"
            
            # Test file reading
            result = await read_file(path=str(test_file))
            assert result["success"], f"File reading failed: {result}"
            assert result["content"] == test_content, "Content mismatch"
            
            # Test directory listing
            result = await list_directory(path=str(self.test_dir))
            assert result["success"], f"Directory listing failed: {result}"
            assert len(result["items"]) >= 1, "Expected at least 1 file"
            
            # Create additional test files
            for i in range(3):
                await write_file(
                    path=str(self.test_dir / f"file_{i}.txt"),
                    content=f"Content for file {i}"
                )
            
            # Test file search
            result = await search_files(
                root_path=str(self.test_dir),
                query="test",
                search_content=True
            )
            assert result["success"], f"File search failed: {result}"
            assert result["count"] > 0, "Expected search results"
            
            # Test compression
            source_files = [str(self.test_dir / f"file_{i}.txt") for i in range(3)]
            result = await compress_files(
                source_paths=source_files,
                output_path=str(self.test_dir / "archive.zip"),
                format="zip"
            )
            assert result["success"], f"File compression failed: {result}"
            
            print("✅ Filesystem skill tests passed")
            return True
            
        except ImportError as e:
            print(f"⚠️ Filesystem skill not available: {e}")
            return False
        except Exception as e:
            print(f"❌ Filesystem skill test failed: {e}")
            return False
    
    @pytest.mark.asyncio
    async def test_api_integration_skill(self):
        """Test API integration operations"""
        try:
            from api_integration_skill import make_api_call, batch_api_calls, monitor_api_health
            
            # Test simple API call
            result = await make_api_call(
                url=f"{TEST_CONFIG['api']['test_server']}/get",
                method="GET",
                params={"test": "value"}
            )
            assert result["success"], f"API call failed: {result}"
            assert result["response"]["status_code"] == 200, "Expected status 200"
            
            # Test POST request
            result = await make_api_call(
                url=f"{TEST_CONFIG['api']['test_server']}/post",
                method="POST",
                data={"message": "Hello from Phase 2 test"}
            )
            assert result["success"], f"POST request failed: {result}"
            
            # Test batch API calls
            requests = [
                {"url": f"{TEST_CONFIG['api']['test_server']}/get", "method": "GET"},
                {"url": f"{TEST_CONFIG['api']['test_server']}/status/200", "method": "GET"},
                {"url": f"{TEST_CONFIG['api']['test_server']}/json", "method": "GET"}
            ]
            
            result = await batch_api_calls(
                requests=requests,
                max_concurrent=2
            )
            assert result["success"], f"Batch API calls failed: {result}"
            assert result["successful"] >= 2, "Expected at least 2 successful calls"
            
            # Test API health monitoring
            urls = [
                f"{TEST_CONFIG['api']['test_server']}/status/200",
                f"{TEST_CONFIG['api']['test_server']}/status/404",
                f"{TEST_CONFIG['api']['test_server']}/delay/1"
            ]
            
            result = await monitor_api_health(urls=urls, timeout=5.0)
            assert result["success"], f"API health monitoring failed: {result}"
            assert result["total"] == 3, "Expected 3 health checks"
            
            print("✅ API Integration skill tests passed")
            return True
            
        except ImportError as e:
            print(f"⚠️ API Integration skill not available: {e}")
            return False
        except Exception as e:
            print(f"❌ API Integration skill test failed: {e}")
            return False
    
    @pytest.mark.asyncio
    async def test_memory_skill(self):
        """Test memory management operations"""
        try:
            from memory_skill import store_memory, search_memories, get_memory_stats, compress_memories
            
            # Store test memories
            stored_memories = []
            for i, content in enumerate(TEST_CONFIG["memory"]["test_memories"]):
                result = await store_memory(
                    content=content,
                    memory_type="fact",
                    metadata={"source": "test", "index": i},
                    tags=["test", "phase2"]
                )
                assert result["success"], f"Memory storage failed: {result}"
                stored_memories.append(result["memory_id"])
            
            # Test memory search
            result = await search_memories(
                query="programming language",
                limit=5
            )
            assert result["success"], f"Memory search failed: {result}"
            assert result["count"] > 0, "Expected search results"
            
            # Test specific search
            result = await search_memories(
                query="Python",
                memory_types=["fact"],
                min_similarity=0.1
            )
            assert result["success"], f"Specific memory search failed: {result}"
            
            # Test memory statistics
            result = await get_memory_stats()
            assert result["success"], f"Memory stats failed: {result}"
            assert result["total_memories"] >= len(TEST_CONFIG["memory"]["test_memories"]), "Memory count mismatch"
            
            # Test memory compression
            result = await compress_memories(target_size=3)
            assert result["success"], f"Memory compression failed: {result}"
            
            print("✅ Memory skill tests passed")
            return True
            
        except ImportError as e:
            print(f"⚠️ Memory skill not available: {e}")
            return False
        except Exception as e:
            print(f"❌ Memory skill test failed: {e}")
            return False

async def run_phase2_tests():
    """Run all Phase 2 skill tests"""
    print("🚀 Starting Phase 2 Advanced Skills Testing")
    print("=" * 60)
    
    test_suite = TestPhase2Skills()
    await test_suite.setup_and_teardown().__anext__()
    
    results = {
        "database": False,
        "filesystem": False,
        "api_integration": False,
        "memory": False
    }
    
    try:
        # Run all tests
        results["database"] = await test_suite.test_database_skill()
        results["filesystem"] = await test_suite.test_filesystem_skill()
        results["api_integration"] = await test_suite.test_api_integration_skill()
        results["memory"] = await test_suite.test_memory_skill()
        
        # Summary
        passed = sum(results.values())
        total = len(results)
        
        print("\n" + "=" * 60)
        print("🎯 Phase 2 Test Summary:")
        print(f"   Database Skill:      {'✅ PASS' if results['database'] else '❌ FAIL'}")
        print(f"   Filesystem Skill:    {'✅ PASS' if results['filesystem'] else '❌ FAIL'}")
        print(f"   API Integration:     {'✅ PASS' if results['api_integration'] else '❌ FAIL'}")
        print(f"   Memory Skill:        {'✅ PASS' if results['memory'] else '❌ FAIL'}")
        print(f"\n📊 Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All Phase 2 skills are working correctly!")
            return True
        else:
            print("⚠️ Some Phase 2 skills need attention")
            return False
            
    except Exception as e:
        print(f"❌ Phase 2 testing failed: {e}")
        return False

if __name__ == "__main__":
    try:
        result = asyncio.run(run_phase2_tests())
        exit(0 if result else 1)
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        exit(1)
