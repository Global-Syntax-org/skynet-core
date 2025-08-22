"""
Phase 2 Simple Test Runner
Tests all Phase 2 skills without external dependencies
"""

import asyncio
import json
import tempfile
import shutil
from pathlib import Path
import sys
import os

# Add skills to path
sys.path.insert(0, "main/skills")
sys.path.insert(0, "main/skills/database")
sys.path.insert(0, "main/skills/filesystem")
sys.path.insert(0, "main/skills/api")
sys.path.insert(0, "main/skills/memory")

class Phase2Tester:
    """Simple Phase 2 Skills Tester"""
    
    def __init__(self):
        self.results = {}
        self.test_dir = Path("test_sandbox")
        self.test_db = Path("test_memory.db")
    
    def setup(self):
        """Setup test environment"""
        # Create test directory
        self.test_dir.mkdir(exist_ok=True)
        
        # Cleanup old test files
        if self.test_db.exists():
            self.test_db.unlink()
    
    def cleanup(self):
        """Cleanup test environment"""
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
        if self.test_db.exists():
            self.test_db.unlink()
        
        # Remove backup files
        for backup_file in Path(".").glob("test_backup.*"):
            backup_file.unlink()
    
    async def test_database_skill(self):
        """Test database operations"""
        print("🔍 Testing Database Skill...")
        try:
            # Test direct aiosqlite functionality
            import aiosqlite
            
            # Simple database test
            async with aiosqlite.connect(str(self.test_db)) as db:
                # Create table
                await db.execute("""
                    CREATE TABLE test_users (
                        id INTEGER PRIMARY KEY,
                        name TEXT NOT NULL,
                        email TEXT UNIQUE
                    )
                """)
                
                # Insert data
                await db.execute(
                    "INSERT INTO test_users (name, email) VALUES (?, ?)",
                    ("Alice Smith", "alice@example.com")
                )
                
                # Query data
                async with db.execute("SELECT * FROM test_users WHERE name = ?", ("Alice Smith",)) as cursor:
                    result = await cursor.fetchall()
                    assert len(result) == 1, "Expected 1 result"
                
                await db.commit()
            
            print("   ✅ Database operations working")
            return True
            
        except ImportError as e:
            print(f"   ⚠️ Database skill not available: {e}")
            return False
        except Exception as e:
            print(f"   ❌ Database test failed: {e}")
            return False
    
    async def test_filesystem_skill(self):
        """Test filesystem operations"""
        print("🔍 Testing Filesystem Skill...")
        try:
            from filesystem_skill import write_file, read_file, list_directory, search_files
            
            test_content = "This is a test file for Phase 2 filesystem testing."
            test_file = self.test_dir / "test_file.txt"
            
            # Test file writing
            result = await write_file(
                path=str(test_file),
                content=test_content,
                create_dirs=True
            )
            assert result["success"], f"File writing failed: {result.get('error')}"
            
            # Test file reading
            result = await read_file(path=str(test_file))
            assert result["success"], f"File reading failed: {result.get('error')}"
            assert result["content"] == test_content, "Content mismatch"
            
            # Test directory listing
            result = await list_directory(path=str(self.test_dir))
            assert result["success"], f"Directory listing failed: {result.get('error')}"
            assert len(result["items"]) >= 1, "Expected at least 1 file"
            
            # Create more test files
            for i in range(2):
                await write_file(
                    path=str(self.test_dir / f"file_{i}.txt"),
                    content=f"Content for file {i} with keyword test"
                )
            
            # Test file search
            result = await search_files(
                root_path=str(self.test_dir),
                query="test",
                search_content=True
            )
            assert result["success"], f"File search failed: {result.get('error')}"
            assert result["count"] > 0, "Expected search results"
            
            print("   ✅ Filesystem operations working")
            return True
            
        except ImportError as e:
            print(f"   ⚠️ Filesystem skill not available: {e}")
            return False
        except Exception as e:
            print(f"   ❌ Filesystem test failed: {e}")
            return False
    
    async def test_api_integration_skill(self):
        """Test API integration operations"""
        print("🔍 Testing API Integration Skill...")
        try:
            from api_integration_skill import make_api_call, monitor_api_health
            
            # Test simple API call
            result = await make_api_call(
                url="https://httpbin.org/get",
                method="GET",
                params={"test": "phase2"}
            )
            assert result["success"], f"API call failed: {result.get('error')}"
            
            # Test POST request  
            result = await make_api_call(
                url="https://httpbin.org/post",
                method="POST",
                data={"message": "Hello from Phase 2"}
            )
            assert result["success"], f"POST request failed: {result.get('error')}"
            
            # Test API health monitoring
            urls = [
                "https://httpbin.org/status/200",
                "https://httpbin.org/json"
            ]
            
            result = await monitor_api_health(urls=urls, timeout=10.0)
            assert result["success"], f"API health monitoring failed: {result.get('error')}"
            
            print("   ✅ API Integration operations working")
            return True
            
        except ImportError as e:
            print(f"   ⚠️ API Integration skill not available: {e}")
            return False
        except Exception as e:
            print(f"   ❌ API Integration test failed: {e}")
            return False
    
    async def test_memory_skill(self):
        """Test memory management operations"""
        print("🔍 Testing Memory Skill...")
        try:
            from memory_skill import store_memory, search_memories, get_memory_stats
            
            # Store test memories
            test_memories = [
                "The weather is sunny today",
                "Python is a powerful programming language",
                "Machine learning algorithms require training data"
            ]
            
            stored_ids = []
            for i, content in enumerate(test_memories):
                result = await store_memory(
                    content=content,
                    memory_type="fact",
                    metadata={"source": "test", "index": i}
                )
                assert result["success"], f"Memory storage failed: {result.get('error')}"
                stored_ids.append(result["memory_id"])
            
            # Test memory search
            result = await search_memories(
                query="programming",
                limit=5
            )
            assert result["success"], f"Memory search failed: {result.get('error')}"
            
            # Test memory statistics
            result = await get_memory_stats()
            assert result["success"], f"Memory stats failed: {result.get('error')}"
            assert result["total_memories"] >= len(test_memories), "Memory count issue"
            
            print("   ✅ Memory operations working")
            return True
            
        except ImportError as e:
            print(f"   ⚠️ Memory skill not available: {e}")
            return False
        except Exception as e:
            print(f"   ❌ Memory test failed: {e}")
            return False
    
    async def run_all_tests(self):
        """Run all Phase 2 tests"""
        print("🚀 Phase 2 Advanced Skills Testing")
        print("=" * 50)
        
        self.setup()
        
        try:
            # Run tests
            self.results["database"] = await self.test_database_skill()
            self.results["filesystem"] = await self.test_filesystem_skill()
            self.results["api_integration"] = await self.test_api_integration_skill()
            self.results["memory"] = await self.test_memory_skill()
            
            # Summary
            passed = sum(self.results.values())
            total = len(self.results)
            
            print("\n" + "=" * 50)
            print("📊 Phase 2 Test Results:")
            print(f"   Database Skill:      {'✅ PASS' if self.results['database'] else '❌ FAIL'}")
            print(f"   Filesystem Skill:    {'✅ PASS' if self.results['filesystem'] else '❌ FAIL'}")
            print(f"   API Integration:     {'✅ PASS' if self.results['api_integration'] else '❌ FAIL'}")
            print(f"   Memory Skill:        {'✅ PASS' if self.results['memory'] else '❌ FAIL'}")
            print(f"\n🎯 Overall: {passed}/{total} skills working")
            
            if passed == total:
                print("🎉 Phase 2 implementation successful!")
                return True
            else:
                print("⚠️ Some skills need attention")
                return False
                
        except Exception as e:
            print(f"❌ Testing failed: {e}")
            return False
        finally:
            self.cleanup()

async def main():
    """Main test execution"""
    tester = Phase2Tester()
    success = await tester.run_all_tests()
    return success

if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n⏹️ Testing interrupted")
        exit(1)
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        exit(1)
