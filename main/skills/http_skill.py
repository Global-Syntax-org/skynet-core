"""
HTTP Skill Implementation for Semantic Kernel
Provides HTTP request capabilities with retry logic and error handling
"""

import asyncio
import httpx
from typing import Dict, Any, Optional
from datetime import datetime
import logging


class HttpSkill:
    """
    HTTP Skill implementation for making web requests
    Follows the skill manifest defined in httpSkill.json
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {
            'timeout': 30,
            'max_retries': 3,
            'retry_delay': 1.0,
            'user_agent': 'SkynetLite-HttpSkill/1.0',
            'follow_redirects': True,
            'verify_ssl': True
        }
        
        self.session: Optional[httpx.AsyncClient] = None
        self.logger = logging.getLogger(__name__)
    
    async def initialize(self):
        """Initialize the HTTP skill with session"""
        self.session = httpx.AsyncClient(
            timeout=self.config['timeout'],
            limits=httpx.Limits(max_connections=20),
            headers={'User-Agent': self.config['user_agent']},
            follow_redirects=self.config['follow_redirects'],
            verify=self.config['verify_ssl']
        )
        
        self.logger.info("🌐 HTTP Skill initialized")
    
    async def make_request(
        self,
        url: str,
        method: str = "GET",
        headers: Optional[Dict[str, str]] = None,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute HTTP request with automatic retry and error handling
        
        Args:
            url: Target URL for the HTTP request
            method: HTTP method (GET, POST, PUT, DELETE, PATCH)
            headers: HTTP headers to include
            data: Request payload for POST/PUT operations
            params: URL parameters for GET requests
            
        Returns:
            Dict containing status_code, data, headers, success, and error fields
        """
        if not self.session:
            await self.initialize()
        
        headers = headers or {}
        params = params or {}
        
        # Retry logic
        for attempt in range(self.config['max_retries']):
            try:
                self.logger.info(f"🔄 Making {method} request to {url} (attempt {attempt + 1})")
                
                response = await self.session.request(
                    method=method.upper(),
                    url=url,
                    headers=headers,
                    json=data if method.upper() in ['POST', 'PUT', 'PATCH'] and data else None,
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
                
                result = {
                    'status_code': response.status_code,
                    'data': response_data,
                    'headers': dict(response.headers),
                    'success': response.status_code < 400,
                    'error': None
                }
                
                if result['success']:
                    self.logger.info(f"✅ Request successful: {response.status_code}")
                    return result
                else:
                    # For 4xx errors, don't retry
                    if 400 <= response.status_code < 500:
                        result['error'] = f"Client error: {response.status_code}"
                        return result
                    
                    # For 5xx errors, retry
                    if attempt < self.config['max_retries'] - 1:
                        self.logger.warning(f"⚠️ Server error {response.status_code}, retrying...")
                        await asyncio.sleep(self.config['retry_delay'])
                        continue
                    else:
                        result['error'] = f"Server error: {response.status_code}"
                        return result
            
            except httpx.RequestError as e:
                error_msg = f"Request failed: {str(e)}"
                
                if attempt < self.config['max_retries'] - 1:
                    self.logger.warning(f"⚠️ {error_msg}, retrying...")
                    await asyncio.sleep(self.config['retry_delay'])
                    continue
                else:
                    return {
                        'status_code': 0,
                        'data': None,
                        'headers': {},
                        'success': False,
                        'error': error_msg
                    }
            
            except Exception as e:
                error_msg = f"Unexpected error: {str(e)}"
                self.logger.error(f"🚨 {error_msg}")
                
                return {
                    'status_code': 0,
                    'data': None,
                    'headers': {},
                    'success': False,
                    'error': error_msg
                }
        
        # Should not reach here, but just in case
        return {
            'status_code': 0,
            'data': None,
            'headers': {},
            'success': False,
            'error': 'Max retries exceeded'
        }
    
    async def download_file(
        self,
        url: str,
        destination: str,
        chunk_size: int = 8192
    ) -> Dict[str, Any]:
        """
        Download file from URL with progress tracking
        
        Args:
            url: URL of file to download
            destination: Local path to save the file
            chunk_size: Download chunk size in bytes
            
        Returns:
            Dict containing success, file_size, download_time, and error fields
        """
        if not self.session:
            await self.initialize()
        
        try:
            start_time = datetime.now()
            file_size = 0
            
            self.logger.info(f"📥 Downloading file from {url} to {destination}")
            
            async with self.session.get(url) as response:
                response.raise_for_status()
                
                # Create destination directory if it doesn't exist
                import os
                os.makedirs(os.path.dirname(destination), exist_ok=True)
                
                with open(destination, 'wb') as f:
                    async for chunk in response.content.iter_chunked(chunk_size):
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
            
            self.logger.info(f"✅ Download completed: {file_size} bytes in {download_time:.2f}s")
            
            return {
                'success': True,
                'file_size': file_size,
                'download_time': download_time,
                'error': None
            }
            
        except Exception as e:
            error_msg = f"Download failed: {str(e)}"
            self.logger.error(f"🚨 {error_msg}")
            
            return {
                'success': False,
                'file_size': 0,
                'download_time': 0,
                'error': error_msg
            }
    
    async def shutdown(self):
        """Clean up resources"""
        if self.session:
            await self.session.aclose()
            self.session = None
        
        self.logger.info("🔒 HTTP Skill shutdown completed")


# Example usage and testing
async def test_http_skill():
    """Test the HTTP skill functionality"""
    skill = HttpSkill()
    
    try:
        await skill.initialize()
        
        # Test GET request
        print("Testing GET request...")
        result = await skill.make_request(
            url="https://httpbin.org/json",
            method="GET"
        )
        print(f"GET Result: {result}")
        
        # Test POST request
        print("\nTesting POST request...")
        result = await skill.make_request(
            url="https://httpbin.org/post",
            method="POST",
            data={"test": "data", "timestamp": datetime.now().isoformat()}
        )
        print(f"POST Result: {result}")
        
        # Test error handling
        print("\nTesting error handling...")
        result = await skill.make_request(
            url="https://httpbin.org/status/404",
            method="GET"
        )
        print(f"Error Result: {result}")
        
    finally:
        await skill.shutdown()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(test_http_skill())
