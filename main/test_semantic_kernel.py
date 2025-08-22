"""
Test Script for Semantic Kernel Phase 1 Implementation
Validates core functionality without external dependencies
"""

import asyncio
import sys
import json
from pathlib import Path

# Add the project root to the path
sys.path.append(str(Path(__file__).parent))

from agents.semantic_kernel import SemanticKernelOrchestrator


async def test_kernel_initialization():
    """Test basic kernel initialization"""
    print("🧪 Testing Semantic Kernel initialization...")
    
    orchestrator = SemanticKernelOrchestrator()
    
    try:
        await orchestrator.initialize()
        
        status = orchestrator.get_status()
        print(f"✅ Kernel initialized successfully")
        print(f"   - Active provider: {status['active_provider']}")
        print(f"   - Skills loaded: {status['skills_loaded']}")
        print(f"   - Available skills: {status['available_skills']}")
        
        return True
        
    except Exception as error:
        print(f"❌ Kernel initialization failed: {error}")
        return False
    
    finally:
        await orchestrator.shutdown()


async def test_skill_discovery():
    """Test skill discovery and loading"""
    print("\n🧪 Testing skill discovery...")
    
    orchestrator = SemanticKernelOrchestrator()
    
    try:
        await orchestrator.initialize()
        
        skills = orchestrator.skills
        print(f"✅ Discovered {len(skills)} skills:")
        
        for skill_id, skill in skills.items():
            print(f"   - {skill.name} ({skill_id})")
            print(f"     Category: {skill.category}, Priority: {skill.priority}")
            print(f"     Functions: {[f.name for f in skill.functions]}")
        
        return len(skills) > 0
        
    except Exception as error:
        print(f"❌ Skill discovery failed: {error}")
        return False
    
    finally:
        await orchestrator.shutdown()


async def test_http_skill_execution():
    """Test HTTP skill execution"""
    print("\n🧪 Testing HTTP skill execution...")
    
    orchestrator = SemanticKernelOrchestrator()
    
    try:
        await orchestrator.initialize()
        
        # Test HTTP skill if available
        if 'httpSkill' in orchestrator.skills:
            print("   Testing make_request function...")
            
            result = await orchestrator.execute_skill(
                'httpSkill',
                'make_request',
                {
                    'url': 'https://httpbin.org/json',
                    'method': 'GET'
                }
            )
            
            if result.get('success'):
                print(f"   ✅ HTTP request successful: {result['status_code']}")
                return True
            else:
                print(f"   ⚠️ HTTP request failed: {result.get('error', 'Unknown error')}")
                return False
        else:
            print("   ⚠️ HTTP skill not found")
            return False
            
    except Exception as error:
        print(f"   ❌ HTTP skill execution failed: {error}")
        return False
    
    finally:
        await orchestrator.shutdown()


async def test_signal_system():
    """Test signal emission and handling"""
    print("\n🧪 Testing signal system...")
    
    orchestrator = SemanticKernelOrchestrator()
    
    # Track received signals
    received_signals = []
    
    def signal_handler(data):
        received_signals.append(data)
    
    try:
        # Register test signal handler
        orchestrator.on_signal('test_signal', signal_handler)
        
        # Emit test signal
        await orchestrator.emit_signal('test_signal', {'test': 'data'})
        
        # Check if signal was received
        if received_signals:
            print(f"   ✅ Signal system working: received {len(received_signals)} signals")
            return True
        else:
            print("   ❌ Signal not received")
            return False
            
    except Exception as error:
        print(f"   ❌ Signal system test failed: {error}")
        return False


async def test_configuration_loading():
    """Test configuration loading"""
    print("\n🧪 Testing configuration loading...")
    
    try:
        # Check if kernel settings file exists
        config_path = Path("main/config/kernelSettings.json")
        if not config_path.exists():
            print(f"   ❌ Configuration file not found: {config_path}")
            return False
        
        # Load and validate configuration
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        required_sections = ['kernel', 'ai_models', 'plugins', 'skill_discovery']
        
        for section in required_sections:
            if section not in config:
                print(f"   ❌ Missing configuration section: {section}")
                return False
        
        print("   ✅ Configuration file valid")
        print(f"   - Environment: {config['kernel']['environment']}")
        print(f"   - Primary provider: {config['ai_models']['primary']['provider']}")
        print(f"   - Fallback providers: {len(config['ai_models']['fallback_chain'])}")
        
        return True
        
    except Exception as error:
        print(f"   ❌ Configuration loading failed: {error}")
        return False


async def test_skill_manifest_validation():
    """Test skill manifest validation"""
    print("\n🧪 Testing skill manifest validation...")
    
    try:
        # Check if HTTP skill manifest exists
        manifest_path = Path("main/skills/httpSkill.json")
        if not manifest_path.exists():
            print(f"   ❌ Skill manifest not found: {manifest_path}")
            return False
        
        # Load and validate manifest
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)
        
        required_fields = ['skillId', 'name', 'description', 'functions', 'signals']
        
        for field in required_fields:
            if field not in manifest:
                print(f"   ❌ Missing manifest field: {field}")
                return False
        
        print("   ✅ Skill manifest valid")
        print(f"   - Skill ID: {manifest['skillId']}")
        print(f"   - Functions: {len(manifest['functions'])}")
        print(f"   - Signals: {len(manifest['signals'])}")
        
        return True
        
    except Exception as error:
        print(f"   ❌ Skill manifest validation failed: {error}")
        return False


async def run_all_tests():
    """Run all tests and report results"""
    print("🚀 Running Semantic Kernel Phase 1 Tests\n")
    
    tests = [
        ("Configuration Loading", test_configuration_loading),
        ("Skill Manifest Validation", test_skill_manifest_validation),
        ("Signal System", test_signal_system),
        ("Kernel Initialization", test_kernel_initialization),
        ("Skill Discovery", test_skill_discovery),
        ("HTTP Skill Execution", test_http_skill_execution),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results[test_name] = result
        except Exception as error:
            print(f"❌ Test '{test_name}' crashed: {error}")
            results[test_name] = False
    
    # Print summary
    print("\n" + "="*50)
    print("🏁 TEST SUMMARY")
    print("="*50)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Semantic Kernel Phase 1 is ready.")
        return True
    else:
        print("⚠️ Some tests failed. Please check the implementation.")
        return False


if __name__ == "__main__":
    # Ensure required directories exist
    import os
    os.makedirs('logs', exist_ok=True)
    
    # Run tests
    asyncio.run(run_all_tests())
