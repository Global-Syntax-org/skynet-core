"""
API Integration Skill Implementation
Provides REST API calls, GraphQL queries, webhook handling, and API monitoring.
"""

import asyncio
import json
import logging
import time
import hashlib
import hmac
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import httpx
from urllib.parse import urljoin, urlparse
import base64

logger = logging.getLogger(__name__)

@dataclass
class APIResponse:
    """API response data structure"""
    status_code: int
    headers: Dict[str, str]
    content: Any
    response_time: float
    url: str
    method: str
    success: bool

@dataclass
class WebhookEvent:
    """Webhook event data structure"""
    id: str
    url: str
    headers: Dict[str, str]
    payload: Any
    timestamp: str
    verified: bool

@dataclass
class APIHealthCheck:
    """API health check result"""
    url: str
    status: str  # "healthy", "degraded", "unhealthy"
    response_time: float
    status_code: int
    timestamp: str
    error: Optional[str] = None

class APIIntegrationSkill:
    """Advanced API integration with authentication, monitoring, and webhooks"""
    
    def __init__(self):
        """Initialize API integration skill"""
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(30.0),
            limits=httpx.Limits(max_connections=100, max_keepalive_connections=20)
        )
        self.webhook_registrations = {}
        self.api_health_cache = {}
        self.rate_limit_cache = {}
        
        # Default headers
        self.default_headers = {
            "User-Agent": "Skynet-API-Integration/1.0",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
    
    def _prepare_auth(self, auth_config: Optional[Dict[str, Any]]) -> Dict[str, str]:
        """Prepare authentication headers"""
        headers = {}
        
        if not auth_config:
            return headers
        
        auth_type = auth_config.get("type", "").lower()
        
        if auth_type == "bearer":
            token = auth_config.get("token")
            if token:
                headers["Authorization"] = f"Bearer {token}"
        
        elif auth_type == "basic":
            username = auth_config.get("username")
            password = auth_config.get("password")
            if username and password:
                credentials = base64.b64encode(f"{username}:{password}".encode()).decode()
                headers["Authorization"] = f"Basic {credentials}"
        
        elif auth_type == "api_key":
            key = auth_config.get("key")
            value = auth_config.get("value")
            if key and value:
                headers[key] = value
        
        elif auth_type == "custom":
            custom_headers = auth_config.get("headers", {})
            headers.update(custom_headers)
        
        return headers
    
    def _check_rate_limit(self, url: str) -> bool:
        """Check if request is within rate limits"""
        now = time.time()
        cache_key = urlparse(url).netloc
        
        if cache_key in self.rate_limit_cache:
            last_request, count = self.rate_limit_cache[cache_key]
            
            # Reset counter if minute has passed
            if now - last_request > 60:
                self.rate_limit_cache[cache_key] = (now, 1)
                return True
            
            # Check if under rate limit (60 requests per minute)
            if count < 60:
                self.rate_limit_cache[cache_key] = (last_request, count + 1)
                return True
            
            return False
        
        # First request for this domain
        self.rate_limit_cache[cache_key] = (now, 1)
        return True
    
    async def make_api_call(self, url: str, method: str = "GET",
                           headers: Optional[Dict[str, str]] = None,
                           params: Optional[Dict[str, Any]] = None,
                           data: Optional[Dict[str, Any]] = None,
                           auth: Optional[Dict[str, Any]] = None,
                           timeout: Optional[float] = None,
                           follow_redirects: bool = True) -> Dict[str, Any]:
        """Make REST API call with comprehensive error handling"""
        try:
            # Rate limiting check
            if not self._check_rate_limit(url):
                return {
                    "success": False,
                    "error": "Rate limit exceeded (60 requests per minute)",
                    "error_type": "RateLimitError"
                }
            
            # Prepare headers
            request_headers = self.default_headers.copy()
            if headers:
                request_headers.update(headers)
            
            # Add authentication
            auth_headers = self._prepare_auth(auth)
            request_headers.update(auth_headers)
            
            # Prepare request data
            json_data = None
            if data and method.upper() in ["POST", "PUT", "PATCH"]:
                json_data = data
            
            # Make request
            start_time = time.time()
            
            response = await self.client.request(
                method=method.upper(),
                url=url,
                headers=request_headers,
                params=params,
                json=json_data,
                timeout=timeout or 30.0,
                follow_redirects=follow_redirects
            )
            
            response_time = time.time() - start_time
            
            # Parse response content
            try:
                if response.headers.get("content-type", "").startswith("application/json"):
                    content = response.json()
                else:
                    content = response.text
            except Exception:
                content = response.text
            
            # Create response object
            api_response = APIResponse(
                status_code=response.status_code,
                headers=dict(response.headers),
                content=content,
                response_time=response_time,
                url=str(response.url),
                method=method.upper(),
                success=200 <= response.status_code < 300
            )
            
            return {
                "success": True,
                "response": asdict(api_response)
            }
            
        except httpx.TimeoutException:
            return {
                "success": False,
                "error": f"Request timeout for {url}",
                "error_type": "TimeoutError"
            }
        except httpx.ConnectError:
            return {
                "success": False,
                "error": f"Connection failed for {url}",
                "error_type": "ConnectionError"
            }
        except Exception as e:
            logger.error(f"API call failed for {url}: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }
    
    async def graphql_query(self, url: str, query: str,
                           variables: Optional[Dict[str, Any]] = None,
                           operation_name: Optional[str] = None,
                           auth: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute GraphQL query"""
        try:
            # Prepare GraphQL payload
            payload = {
                "query": query
            }
            
            if variables:
                payload["variables"] = variables
            
            if operation_name:
                payload["operationName"] = operation_name
            
            # Make GraphQL request
            result = await self.make_api_call(
                url=url,
                method="POST",
                data=payload,
                auth=auth,
                headers={"Content-Type": "application/json"}
            )
            
            if not result["success"]:
                return result
            
            response_data = result["response"]["content"]
            
            # Check for GraphQL errors
            if isinstance(response_data, dict) and "errors" in response_data:
                return {
                    "success": False,
                    "error": "GraphQL errors",
                    "errors": response_data["errors"],
                    "data": response_data.get("data"),
                    "error_type": "GraphQLError"
                }
            
            return {
                "success": True,
                "data": response_data.get("data") if isinstance(response_data, dict) else response_data,
                "response": result["response"]
            }
            
        except Exception as e:
            logger.error(f"GraphQL query failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }
    
    async def register_webhook(self, url: str, endpoint: str,
                             secret: Optional[str] = None,
                             events: Optional[List[str]] = None,
                             auth: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Register webhook endpoint"""
        try:
            webhook_id = hashlib.md5(f"{url}{endpoint}".encode()).hexdigest()
            
            # Prepare webhook registration payload
            registration_data = {
                "url": endpoint,
                "events": events or ["*"],
                "active": True
            }
            
            if secret:
                registration_data["secret"] = secret
            
            # Register webhook
            result = await self.make_api_call(
                url=url,
                method="POST",
                data=registration_data,
                auth=auth
            )
            
            if result["success"]:
                # Store webhook registration locally
                self.webhook_registrations[webhook_id] = {
                    "url": url,
                    "endpoint": endpoint,
                    "secret": secret,
                    "events": events,
                    "created": datetime.now().isoformat(),
                    "active": True
                }
                
                return {
                    "success": True,
                    "webhook_id": webhook_id,
                    "registration": result["response"]
                }
            
            return result
            
        except Exception as e:
            logger.error(f"Webhook registration failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }
    
    async def verify_webhook(self, webhook_id: str, headers: Dict[str, str],
                           payload: str) -> Dict[str, Any]:
        """Verify webhook signature"""
        try:
            if webhook_id not in self.webhook_registrations:
                return {
                    "success": False,
                    "error": f"Webhook not found: {webhook_id}",
                    "error_type": "WebhookNotFoundError"
                }
            
            webhook_config = self.webhook_registrations[webhook_id]
            secret = webhook_config.get("secret")
            
            if not secret:
                # No secret configured, consider verified
                return {
                    "success": True,
                    "verified": True,
                    "reason": "No secret configured"
                }
            
            # Check for signature headers (GitHub style)
            signature_header = headers.get("x-hub-signature-256") or headers.get("x-signature-256")
            
            if not signature_header:
                return {
                    "success": True,
                    "verified": False,
                    "reason": "No signature header found"
                }
            
            # Verify signature
            expected_signature = hmac.new(
                secret.encode(),
                payload.encode(),
                hashlib.sha256
            ).hexdigest()
            
            # Remove 'sha256=' prefix if present
            received_signature = signature_header.replace("sha256=", "")
            
            verified = hmac.compare_digest(expected_signature, received_signature)
            
            return {
                "success": True,
                "verified": verified,
                "reason": "Signature match" if verified else "Signature mismatch"
            }
            
        except Exception as e:
            logger.error(f"Webhook verification failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }
    
    async def batch_api_calls(self, requests: List[Dict[str, Any]],
                             max_concurrent: int = 5,
                             continue_on_error: bool = True) -> Dict[str, Any]:
        """Execute multiple API calls concurrently"""
        try:
            semaphore = asyncio.Semaphore(max_concurrent)
            
            async def make_request(request_config: Dict[str, Any]) -> Dict[str, Any]:
                async with semaphore:
                    try:
                        return await self.make_api_call(**request_config)
                    except Exception as e:
                        return {
                            "success": False,
                            "error": str(e),
                            "error_type": type(e).__name__,
                            "request": request_config
                        }
            
            # Execute all requests concurrently
            start_time = time.time()
            results = await asyncio.gather(
                *[make_request(req) for req in requests],
                return_exceptions=continue_on_error
            )
            total_time = time.time() - start_time
            
            # Process results
            successful = sum(1 for r in results if isinstance(r, dict) and r.get("success"))
            failed = len(results) - successful
            
            return {
                "success": True,
                "total_requests": len(requests),
                "successful": successful,
                "failed": failed,
                "total_time": total_time,
                "results": results
            }
            
        except Exception as e:
            logger.error(f"Batch API calls failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }
    
    async def monitor_api_health(self, urls: List[str],
                               check_interval: int = 300,
                               timeout: float = 10.0) -> Dict[str, Any]:
        """Monitor API health status"""
        try:
            health_results = []
            
            for url in urls:
                try:
                    start_time = time.time()
                    
                    response = await self.client.get(
                        url,
                        timeout=timeout,
                        follow_redirects=True
                    )
                    
                    response_time = time.time() - start_time
                    
                    # Determine health status
                    if response.status_code == 200:
                        status = "healthy"
                    elif 200 <= response.status_code < 300:
                        status = "healthy"
                    elif 300 <= response.status_code < 500:
                        status = "degraded"
                    else:
                        status = "unhealthy"
                    
                    health_check = APIHealthCheck(
                        url=url,
                        status=status,
                        response_time=response_time,
                        status_code=response.status_code,
                        timestamp=datetime.now().isoformat()
                    )
                    
                except Exception as e:
                    health_check = APIHealthCheck(
                        url=url,
                        status="unhealthy",
                        response_time=timeout,
                        status_code=0,
                        timestamp=datetime.now().isoformat(),
                        error=str(e)
                    )
                
                health_results.append(asdict(health_check))
                
                # Cache result
                self.api_health_cache[url] = health_check
            
            # Calculate overall health
            healthy_count = sum(1 for h in health_results if h["status"] == "healthy")
            degraded_count = sum(1 for h in health_results if h["status"] == "degraded")
            unhealthy_count = sum(1 for h in health_results if h["status"] == "unhealthy")
            
            overall_status = "healthy"
            if unhealthy_count > 0:
                overall_status = "unhealthy"
            elif degraded_count > 0:
                overall_status = "degraded"
            
            return {
                "success": True,
                "overall_status": overall_status,
                "healthy": healthy_count,
                "degraded": degraded_count,
                "unhealthy": unhealthy_count,
                "total": len(urls),
                "checks": health_results,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"API health monitoring failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

# Global instance for skill registration
api_integration_skill = APIIntegrationSkill()

# Skill function exports for orchestrator
async def make_api_call(url: str, **kwargs) -> Dict[str, Any]:
    """Make REST API call"""
    return await api_integration_skill.make_api_call(url, **kwargs)

async def graphql_query(url: str, query: str, **kwargs) -> Dict[str, Any]:
    """Execute GraphQL query"""
    return await api_integration_skill.graphql_query(url, query, **kwargs)

async def register_webhook(url: str, endpoint: str, **kwargs) -> Dict[str, Any]:
    """Register webhook endpoint"""
    return await api_integration_skill.register_webhook(url, endpoint, **kwargs)

async def verify_webhook(webhook_id: str, headers: Dict[str, str], payload: str) -> Dict[str, Any]:
    """Verify webhook signature"""
    return await api_integration_skill.verify_webhook(webhook_id, headers, payload)

async def batch_api_calls(requests: List[Dict[str, Any]], **kwargs) -> Dict[str, Any]:
    """Execute multiple API calls concurrently"""
    return await api_integration_skill.batch_api_calls(requests, **kwargs)

async def monitor_api_health(urls: List[str], **kwargs) -> Dict[str, Any]:
    """Monitor API health status"""
    return await api_integration_skill.monitor_api_health(urls, **kwargs)
