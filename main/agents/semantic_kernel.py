"""
Semantic Kernel Orchestrator for Skynet Lite
Implements Microsoft Semantic Kernel patterns for skill-based AI orchestration
"""

import os
import json
import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
import httpx
from collections import defaultdict


@dataclass
class AIModelConfig:
    """Configuration for AI model providers"""
    provider: str
    model: str
    api_key_env: str
    endpoint: str
    max_tokens: int = 4096
    temperature: float = 0.7
    timeout: int = 30


@dataclass
class SkillFunction:
    """Definition of a skill function"""
    name: str
    description: str
    parameters: Dict[str, Any]
    returns: Dict[str, Any]


@dataclass
class SignalDefinition:
    """Definition of a signal that can be emitted"""
    description: str
    data: Dict[str, str]


@dataclass
class RoutingOptions:
    """Routing configuration for skills"""
    fallback_enabled: bool = True
    cache_responses: bool = False
    rate_limiting: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SkillManifest:
    """Complete skill manifest definition"""
    skillId: str
    name: str
    description: str
    version: str
    category: str
    priority: int
    capabilities: List[str]
    functions: List[SkillFunction]
    signals: Dict[str, SignalDefinition]
    routing: RoutingOptions
    metadata: Dict[str, Any] = field(default_factory=dict)


class SemanticKernelOrchestrator:
    """
    Main orchestrator for Semantic Kernel-based skill execution
    Implements declarative, signal-rich architecture for AI skill coordination
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or "main/config/kernelSettings.json"
        self.skills_path = Path("main/skills")
        
        # Core state
        self.settings: Optional[Dict[str, Any]] = None
        self.skills: Dict[str, SkillManifest] = {}
        self.active_provider: str = ""
        self.signal_handlers: Dict[str, List[Callable]] = defaultdict(list)
        
        # Runtime state
        self.initialized = False
        self.session: Optional[httpx.AsyncClient] = None
        self.memory_store: Dict[str, Any] = {}
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        self.setup_logging()
        
        # Setup core signal handlers
        self.setup_signal_handlers()

    def setup_logging(self):
        """Configure logging for the orchestrator"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('logs/semantic_kernel.log')
            ]
        )

    async def initialize(self) -> None:
        """
        Initialize the Semantic Kernel with configuration and skills
        """
        try:
            # Create necessary directories
            os.makedirs('logs', exist_ok=True)
            
            # Load kernel settings
            await self.load_kernel_settings()
            
            # Initialize HTTP session
            await self.initialize_session()
            
            # Initialize AI model with fallback chain
            await self.initialize_ai_models()
            
            # Discover and load skills
            await self.discover_skills()
            
            # Setup memory management
            await self.setup_memory_skill()
            
            self.initialized = True
            
            await self.emit_signal('kernel_initialized', {
                'provider': self.active_provider,
                'skills_count': len(self.skills),
                'timestamp': datetime.now().isoformat()
            })
            
            self.logger.info(f"🚀 Semantic Kernel initialized with {len(self.skills)} skills")
            
        except Exception as error:
            await self.emit_signal('kernel_error', {'error': str(error)})
            raise Exception(f"Failed to initialize Semantic Kernel: {error}")

    async def load_kernel_settings(self) -> None:
        """Load kernel settings from configuration file"""
        try:
            with open(self.config_path, 'r') as f:
                content = f.read()
                self.settings = json.loads(content)
            
            await self.emit_signal('settings_loaded', {
                'environment': self.settings['kernel']['environment']
            })
            
            self.logger.info("✅ Kernel settings loaded successfully")
            
        except Exception as error:
            raise Exception(f"Failed to load kernel settings: {error}")

    async def initialize_session(self) -> None:
        """Initialize HTTP session for API calls"""
        self.session = httpx.AsyncClient(
            timeout=30.0,
            limits=httpx.Limits(max_connections=20),
            headers={'User-Agent': 'SkynetLite-SemanticKernel/1.0'}
        )

    async def initialize_ai_models(self) -> None:
        """Initialize AI models with fallback chain"""
        if not self.settings:
            raise Exception('Settings not loaded')

        primary_config = AIModelConfig(**self.settings['ai_models']['primary'])
        
        # Try primary model first
        try:
            await self.configure_ai_model(primary_config)
            self.active_provider = primary_config.provider
            self.logger.info(f"✅ Primary model configured: {primary_config.provider}")
            
        except Exception as error:
            self.logger.warning(f"Primary model failed, trying fallback chain: {error}")
            
            # Try fallback models
            for fallback_data in self.settings['ai_models']['fallback_chain']:
                try:
                    fallback_config = AIModelConfig(**fallback_data)
                    await self.configure_ai_model(fallback_config)
                    self.active_provider = fallback_config.provider
                    
                    await self.emit_signal('model_fallback', {
                        'failed_provider': primary_config.provider,
                        'active_provider': self.active_provider
                    })
                    
                    self.logger.info(f"✅ Fallback model configured: {fallback_config.provider}")
                    break
                    
                except Exception as fallback_error:
                    self.logger.warning(f"Fallback model {fallback_data['provider']} failed: {fallback_error}")
            
            if not self.active_provider:
                raise Exception('All AI models failed to initialize')

    async def configure_ai_model(self, config: AIModelConfig) -> None:
        """Configure a specific AI model"""
        api_key = os.getenv(config.api_key_env)
        
        # In development test mode, allow operation without API keys
        if self.settings and self.settings.get('development', {}).get('test_mode', False):
            self.logger.info(f"🧪 Mock mode: Configuring {config.provider} without API key")
            api_key = "mock_key_for_testing"
        elif not api_key:
            raise Exception(f"API key not found in environment: {config.api_key_env}")

        # Test the model configuration with a simple request
        await self.test_model_connection(config, api_key)

    async def test_model_connection(self, config: AIModelConfig, api_key: str) -> None:
        """Test connection to AI model"""
        # In development mode, allow mock testing without API keys
        if self.settings and self.settings.get('development', {}).get('test_mode', False):
            self.logger.info(f"🧪 Mock testing {config.provider} model: {config.model}")
            await asyncio.sleep(0.1)  # Simulate test delay
            return
        
        # This is a placeholder for actual model testing
        # In real implementation, this would make a test API call
        self.logger.info(f"Testing connection to {config.provider} model: {config.model}")
        
        # Mock test for now
        if config.provider in ['openai', 'claude', 'github_copilot', 'microsoft_copilot', 'gemini']:
            # Simulate successful connection test
            await asyncio.sleep(0.1)
        else:
            raise Exception(f"Unsupported AI provider: {config.provider}")

    async def discover_skills(self) -> None:
        """Discover and load skills from the skills directory"""
        if not self.settings:
            return

        try:
            skills_path = Path(self.skills_path)
            if not skills_path.exists():
                self.logger.warning(f"Skills directory not found: {skills_path}")
                return
            
            # Load skill manifests from main skills directory and subdirectories
            manifest_files = list(skills_path.glob("*.json")) + list(skills_path.glob("*/*.json"))
            
            for manifest_file in manifest_files:
                try:
                    skill_manifest = await self.load_skill_manifest(manifest_file)
                    await self.register_skill(skill_manifest)
                    
                    await self.emit_signal('skill_loaded', {
                        'skillId': skill_manifest.skillId,
                        'category': skill_manifest.category
                    })
                    
                except Exception as error:
                    self.logger.error(f"Failed to load skill {manifest_file.name}: {error}")
                    await self.emit_signal('skill_error', {
                        'file': str(manifest_file),
                        'error': str(error)
                    })
            
            # Initialize skill implementations
            await self.initialize_skill_implementations()
            
            self.logger.info(f"📦 Loaded {len(self.skills)} skills")
            
        except Exception as error:
            raise Exception(f"Failed to discover skills: {error}")
    
    async def initialize_skill_implementations(self) -> None:
        """Initialize all skill implementations"""
        try:
            import sys
            
            # Initialize HTTP skill
            try:
                sys.path.append("main/skills")
                from http_skill import make_request, download_file
                self.skill_functions.update({
                    "http_request": make_request,
                    "download_file": download_file
                })
                self.logger.info("✅ HTTP skill functions registered")
            except ImportError as e:
                self.logger.warning(f"Could not import HTTP skill: {e}")
            
            # Initialize Database skill
            try:
                sys.path.append("main/skills/database")
                from database_skill import execute_query, create_table, insert_data, backup_database
                self.skill_functions.update({
                    "execute_query": execute_query,
                    "create_table": create_table,
                    "insert_data": insert_data,
                    "backup_database": backup_database
                })
                self.logger.info("✅ Database skill functions registered")
            except ImportError as e:
                self.logger.warning(f"Could not import Database skill: {e}")
            
            # Initialize Filesystem skill
            try:
                sys.path.append("main/skills/filesystem")
                from filesystem_skill import read_file, write_file, list_directory, search_files, compress_files
                self.skill_functions.update({
                    "read_file": read_file,
                    "write_file": write_file,
                    "list_directory": list_directory,
                    "search_files": search_files,
                    "compress_files": compress_files
                })
                self.logger.info("✅ Filesystem skill functions registered")
            except ImportError as e:
                self.logger.warning(f"Could not import Filesystem skill: {e}")
            
            # Initialize API Integration skill
            try:
                sys.path.append("main/skills/api")
                from api_integration_skill import (make_api_call, graphql_query, register_webhook, 
                                                 verify_webhook, batch_api_calls, monitor_api_health)
                self.skill_functions.update({
                    "make_api_call": make_api_call,
                    "graphql_query": graphql_query,
                    "register_webhook": register_webhook,
                    "verify_webhook": verify_webhook,
                    "batch_api_calls": batch_api_calls,
                    "monitor_api_health": monitor_api_health
                })
                self.logger.info("✅ API Integration skill functions registered")
            except ImportError as e:
                self.logger.warning(f"Could not import API Integration skill: {e}")
            
            # Initialize Memory skill
            try:
                sys.path.append("main/skills/memory")
                from memory_skill import (store_memory, search_memories, create_knowledge_graph, 
                                        compress_memories, get_memory_stats)
                self.skill_functions.update({
                    "store_memory": store_memory,
                    "search_memories": search_memories,
                    "create_knowledge_graph": create_knowledge_graph,
                    "compress_memories": compress_memories,
                    "get_memory_stats": get_memory_stats
                })
                self.logger.info("✅ Memory skill functions registered")
            except ImportError as e:
                self.logger.warning(f"Could not import Memory skill: {e}")
            
            self.logger.info(f"🎯 Total skill functions registered: {len(self.skill_functions)}")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize skill implementations: {e}")

    async def load_skill_manifest(self, manifest_path: Path) -> SkillManifest:
        """Load skill manifest from JSON file"""
        with open(manifest_path, 'r') as f:
            content = f.read()
            data = json.loads(content)
        
        # Convert functions to SkillFunction objects
        functions = [
            SkillFunction(
                name=func['name'],
                description=func['description'],
                parameters=func['parameters'],
                returns=func['returns']
            )
            for func in data.get('functions', [])
        ]
        
        # Convert signals to SignalDefinition objects
        signals = {
            name: SignalDefinition(
                description=signal['description'],
                data=signal['data']
            )
            for name, signal in data.get('signals', {}).items()
        }
        
        # Convert routing options
        routing_data = data.get('routing', {})
        routing = RoutingOptions(
            fallback_enabled=routing_data.get('fallback_enabled', True),
            cache_responses=routing_data.get('cache_responses', False),
            rate_limiting=routing_data.get('rate_limiting', {})
        )
        
        # Create manifest
        manifest = SkillManifest(
            skillId=data['skillId'],
            name=data['name'],
            description=data['description'],
            version=data['version'],
            category=data['category'],
            priority=data['priority'],
            capabilities=data['capabilities'],
            functions=functions,
            signals=signals,
            routing=routing,
            metadata=data.get('metadata', {})
        )
        
        # Validate required fields
        if not all([manifest.skillId, manifest.name, manifest.functions]):
            raise Exception('Invalid skill manifest: missing required fields')
        
        return manifest

    async def register_skill(self, manifest: SkillManifest) -> None:
        """Register a skill with the orchestrator"""
        self.skills[manifest.skillId] = manifest
        self.logger.info(f"✅ Registered skill: {manifest.name} ({manifest.skillId})")

    async def setup_memory_skill(self) -> None:
        """Setup memory management for context storage"""
        if not self.settings:
            return

        try:
            memory_config = self.settings['plugins']['memory']
            
            # Initialize in-memory storage for now
            self.memory_store = {
                'conversations': {},
                'context': {},
                'embeddings': {}
            }
            
            await self.emit_signal('memory_initialized', {
                'provider': memory_config['provider']
            })
            
            self.logger.info('🧠 Memory skill initialized')
            
        except Exception as error:
            self.logger.error(f"Failed to setup memory skill: {error}")

    async def execute_skill(
        self, 
        skill_id: str, 
        function_name: str, 
        parameters: Dict[str, Any]
    ) -> Any:
        """Execute a skill function with intelligent routing"""
        if not self.initialized:
            raise Exception('Kernel not initialized')

        skill = self.skills.get(skill_id)
        if not skill:
            raise Exception(f"Skill not found: {skill_id}")

        skill_function = next(
            (f for f in skill.functions if f.name == function_name), 
            None
        )
        if not skill_function:
            raise Exception(f"Function not found: {function_name} in skill {skill_id}")

        await self.emit_signal('skill_execution_started', {
            'skillId': skill_id,
            'functionName': function_name,
            'parameters': list(parameters.keys())
        })

        try:
            # Execute the skill function
            result = await self.execute_skill_function(skill, skill_function, parameters)
            
            await self.emit_signal('skill_execution_completed', {
                'skillId': skill_id,
                'functionName': function_name,
                'success': True
            })
            
            return result
            
        except Exception as error:
            await self.emit_signal('skill_execution_failed', {
                'skillId': skill_id,
                'functionName': function_name,
                'error': str(error)
            })
            
            raise error

    async def execute_skill_function(
        self,
        skill: SkillManifest,
        skill_function: SkillFunction,
        parameters: Dict[str, Any]
    ) -> Any:
        """Execute skill function implementation"""
        self.logger.info(f"🔧 Executing {skill.skillId}.{skill_function.name}")
        
        # Route to specific skill implementations
        if skill.skillId == 'httpSkill':
            return await self.execute_http_skill(skill_function.name, parameters)
        
        # Default mock execution
        return {
            'success': True,
            'skillId': skill.skillId,
            'function': skill_function.name,
            'result': 'Mock execution completed',
            'timestamp': datetime.now().isoformat()
        }

    async def execute_http_skill(self, function_name: str, parameters: Dict[str, Any]) -> Any:
        """Execute HTTP skill functions"""
        if not self.session:
            raise Exception("HTTP session not initialized")

        if function_name == 'make_request':
            url = parameters.get('url')
            method = parameters.get('method', 'GET').upper()
            headers = parameters.get('headers', {})
            data = parameters.get('data')
            params = parameters.get('params', {})

            try:
                response = await self.session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=data if method in ['POST', 'PUT', 'PATCH'] else None,
                    params=params
                )
                
                # Try to parse as JSON, fallback to text
                try:
                    if 'application/json' in response.headers.get('content-type', ''):
                        response_data = response.json()
                    else:
                        response_data = response.text
                except Exception:
                    response_data = response.text
                
                return {
                    'status_code': response.status_code,
                    'data': response_data,
                    'headers': dict(response.headers),
                    'success': response.status_code < 400
                }
                    
            except Exception as error:
                return {
                    'status_code': 0,
                    'data': None,
                    'headers': {},
                    'success': False,
                    'error': str(error)
                }

        elif function_name == 'download_file':
            url = parameters.get('url')
            destination = parameters.get('destination')
            chunk_size = parameters.get('chunk_size', 8192)

            try:
                response = await self.session.get(url)
                response.raise_for_status()
                
                file_size = 0
                start_time = datetime.now()
                
                # Create destination directory if it doesn't exist
                os.makedirs(os.path.dirname(destination), exist_ok=True)
                
                with open(destination, 'wb') as f:
                    async for chunk in response.aiter_bytes(chunk_size):
                        f.write(chunk)
                        file_size += len(chunk)
                        
                        # Emit progress signal (would be handled by orchestrator)
                        if hasattr(self, 'emit_signal'):
                            total_size = int(response.headers.get('content-length', 0))
                            if total_size > 0:
                                percentage = (file_size / total_size) * 100
                                await self.emit_signal('download_progress', {
                                    'bytes_downloaded': file_size,
                                    'total_bytes': total_size,
                                    'percentage': percentage
                                })
                
                download_time = (datetime.now() - start_time).total_seconds()
                
                return {
                    'success': True,
                    'file_size': file_size,
                    'download_time': download_time
                }
                    
            except Exception as error:
                return {
                    'success': False,
                    'file_size': 0,
                    'download_time': 0,
                    'error': str(error)
                }

        else:
            raise Exception(f"Unknown HTTP skill function: {function_name}")

    def setup_signal_handlers(self) -> None:
        """Setup default signal handlers"""
        self.on_signal('kernel_error', self._handle_kernel_error)
        self.on_signal('model_fallback', self._handle_model_fallback)
        self.on_signal('skill_error', self._handle_skill_error)

    def _handle_kernel_error(self, data: Dict[str, Any]) -> None:
        """Handle kernel errors"""
        self.logger.error(f"🚨 Kernel Error: {data}")

    def _handle_model_fallback(self, data: Dict[str, Any]) -> None:
        """Handle model fallback events"""
        self.logger.warning(f"🔄 Model Fallback: {data}")

    def _handle_skill_error(self, data: Dict[str, Any]) -> None:
        """Handle skill errors"""
        self.logger.error(f"⚠️ Skill Error: {data}")

    def on_signal(self, signal_name: str, handler: Callable) -> None:
        """Register signal handler"""
        self.signal_handlers[signal_name].append(handler)

    async def emit_signal(self, signal_name: str, data: Any) -> None:
        """Emit signal to registered handlers"""
        handlers = self.signal_handlers.get(signal_name, [])
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(data)
                else:
                    handler(data)
            except Exception as error:
                self.logger.error(f"Signal handler error for {signal_name}: {error}")

    def get_status(self) -> Dict[str, Any]:
        """Get kernel status and metrics"""
        return {
            'initialized': self.initialized,
            'active_provider': self.active_provider,
            'skills_loaded': len(self.skills),
            'available_skills': list(self.skills.keys()),
            'environment': self.settings.get('kernel', {}).get('environment') if self.settings else None,
            'version': self.settings.get('kernel', {}).get('version') if self.settings else None,
            'timestamp': datetime.now().isoformat()
        }

    async def shutdown(self) -> None:
        """Graceful shutdown"""
        await self.emit_signal('kernel_shutdown', {
            'timestamp': datetime.now().isoformat()
        })
        
        # Clean up resources
        if self.session:
            await self.session.aclose()
        
        self.skills.clear()
        self.signal_handlers.clear()
        self.memory_store.clear()
        self.initialized = False
        
        self.logger.info('🔒 Semantic Kernel shutdown completed')


# Factory function for easy instantiation
def create_orchestrator(config_path: Optional[str] = None) -> SemanticKernelOrchestrator:
    """Create and return a SemanticKernelOrchestrator instance"""
    return SemanticKernelOrchestrator(config_path)


# Example usage
async def main():
    """Example usage of the Semantic Kernel Orchestrator"""
    orchestrator = create_orchestrator()
    
    try:
        await orchestrator.initialize()
        
        # Example: Execute HTTP skill
        result = await orchestrator.execute_skill(
            'httpSkill',
            'make_request',
            {
                'url': 'https://httpbin.org/json',
                'method': 'GET'
            }
        )
        
        print("Skill execution result:", result)
        
        # Get status
        status = orchestrator.get_status()
        print("Orchestrator status:", status)
        
    except Exception as error:
        print(f"Error: {error}")
    
    finally:
        await orchestrator.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
