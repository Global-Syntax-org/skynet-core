"""
Main Orchestrator Entry Point
Semantic Kernel-based skill orchestrator for Skynet Core (Phase 1)
"""

import asyncio
import logging
import signal
import sys
from pathlib import Path

# Add the project root to the path
sys.path.append(str(Path(__file__).parent))

from agents.semantic_kernel import SemanticKernelOrchestrator


class MainOrchestrator:
    """
    Main entry point for the Semantic Kernel orchestrator
    Implements Phase 1 goals: skill orchestrator, not chat frontend
    """
    
    def __init__(self):
        self.orchestrator = SemanticKernelOrchestrator()
        self.running = False
        self.setup_logging()
        self.setup_signal_handlers()
    
    def setup_logging(self):
        """Configure logging for the main orchestrator"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('logs/orchestrator.log')
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def setup_signal_handlers(self):
        """Setup graceful shutdown signal handlers"""
        def signal_handler(signum, frame):
            self.logger.info(f"Received signal {signum}, initiating graceful shutdown...")
            self.running = False
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    async def start(self):
        """Start the orchestrator"""
        try:
            self.logger.info("🚀 Starting Skynet Core Semantic Kernel Orchestrator")
            
            # Initialize the semantic kernel
            await self.orchestrator.initialize()
            
            self.running = True
            self.logger.info("✅ Orchestrator started successfully")
            
            # Enter main event loop
            await self.event_loop()
            
        except Exception as error:
            self.logger.error(f"Failed to start orchestrator: {error}")
            raise
    
    async def event_loop(self):
        """Main event loop for the orchestrator"""
        self.logger.info("🔄 Entering main event loop")
        
        while self.running:
            try:
                # Get orchestrator status
                status = self.orchestrator.get_status()
                
                # Log status periodically (every 30 seconds)
                if hasattr(self, '_last_status_log'):
                    import time
                    if time.time() - self._last_status_log > 30:
                        self.log_status(status)
                        self._last_status_log = time.time()
                else:
                    import time
                    self.log_status(status)
                    self._last_status_log = time.time()
                
                # Demonstrate skill execution
                await self.demonstrate_skills()
                
                # Sleep to prevent busy waiting
                await asyncio.sleep(10)
                
            except Exception as error:
                self.logger.error(f"Error in event loop: {error}")
                await asyncio.sleep(5)
        
        self.logger.info("🔒 Exiting main event loop")
    
    def log_status(self, status):
        """Log orchestrator status"""
        self.logger.info(f"📊 Status: {status['skills_loaded']} skills loaded, "
                        f"provider: {status['active_provider']}, "
                        f"environment: {status['environment']}")
    
    async def demonstrate_skills(self):
        """Demonstrate skill execution capabilities"""
        try:
            # Example: Execute HTTP skill to test external connectivity
            result = await self.orchestrator.execute_skill(
                'httpSkill',
                'make_request',
                {
                    'url': 'https://httpbin.org/uuid',
                    'method': 'GET'
                }
            )
            
            if result.get('success'):
                self.logger.info(f"🌐 HTTP skill test successful: {result.get('data', {}).get('uuid', 'N/A')}")
            else:
                self.logger.warning(f"⚠️ HTTP skill test failed: {result.get('error', 'Unknown error')}")
            
        except Exception as error:
            self.logger.error(f"Skill demonstration failed: {error}")
    
    async def shutdown(self):
        """Graceful shutdown"""
        self.logger.info("🔒 Initiating orchestrator shutdown...")
        
        try:
            await self.orchestrator.shutdown()
            self.logger.info("✅ Orchestrator shutdown completed")
        except Exception as error:
            self.logger.error(f"Error during shutdown: {error}")
    
    async def run(self):
        """Main run method"""
        try:
            await self.start()
        except KeyboardInterrupt:
            self.logger.info("Received keyboard interrupt")
        except Exception as error:
            self.logger.error(f"Orchestrator error: {error}")
        finally:
            await self.shutdown()


async def main():
    """Main entry point"""
    orchestrator = MainOrchestrator()
    await orchestrator.run()


if __name__ == "__main__":
    # Ensure logs directory exists
    import os
    os.makedirs('logs', exist_ok=True)
    
    # Run the orchestrator
    asyncio.run(main())
