import os
import logging
import asyncio
from typing import Optional, Dict, Any
import httpx

logger = logging.getLogger(__name__)


class MicrosoftCopilotLoader:
    """Microsoft Copilot integration for Skynet Core.
    
    Uses Microsoft's Copilot API (formerly Bing Chat) for AI completions.
    Requires Microsoft API credentials and access to Copilot services.
    """

    def __init__(self):
        self.api_key = os.getenv("MICROSOFT_COPILOT_API_KEY")
        self.endpoint = os.getenv("MICROSOFT_COPILOT_ENDPOINT", 
                                "https://api.cognitive.microsoft.com/copilot/v1/chat/completions")
        self.model = os.getenv("MICROSOFT_COPILOT_MODEL", "copilot")
        self.client: Optional[httpx.AsyncClient] = None
        self.conversation_id: Optional[str] = None

    async def initialize(self) -> bool:
        """Initialize the Microsoft Copilot client."""
        if not self.api_key:
            logger.info("Microsoft Copilot API key not configured; MS Copilot loader disabled")
            return False
            
        if not self.endpoint:
            logger.error("Microsoft Copilot endpoint not configured")
            return False
            
        self.client = httpx.AsyncClient(
            timeout=60.0,
            headers={
                "Ocp-Apim-Subscription-Key": self.api_key,
                "Content-Type": "application/json",
                "User-Agent": "SkynetLite/1.0"
            }
        )
        
        # Test connection
        try:
            await self._test_connection()
            logger.info("Microsoft Copilot loader initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Microsoft Copilot: {e}")
            if self.client:
                await self.client.aclose()
                self.client = None
            return False

    async def _test_connection(self) -> bool:
        """Test the connection to Microsoft Copilot API."""
        test_payload = {
            "messages": [{"role": "user", "content": "Hello"}],
            "model": self.model,
            "max_tokens": 10,
            "temperature": 0.1
        }
        
        response = await self.client.post(self.endpoint, json=test_payload)
        response.raise_for_status()
        return True

    async def ensure_model_available(self, model_name: Optional[str] = None) -> bool:
        """Microsoft Copilot models are always available if API is accessible."""
        return self.client is not None

    async def generate_completion(self, prompt: str, model_name: Optional[str] = None) -> str:
        """Generate completion using Microsoft Copilot."""
        if not self.client:
            if not await self.initialize():
                return ""

        # Prepare the conversation payload
        messages = [
            {
                "role": "system",
                "content": "You are a helpful AI assistant powered by Microsoft Copilot. "
                          "Provide accurate, helpful, and concise responses."
            },
            {
                "role": "user", 
                "content": prompt
            }
        ]

        payload = {
            "messages": messages,
            "model": model_name or self.model,
            "max_tokens": 2048,
            "temperature": 0.7,
            "top_p": 0.9,
            "frequency_penalty": 0.0,
            "presence_penalty": 0.0,
            "stream": False
        }

        # Add conversation ID if available for context continuity
        if self.conversation_id:
            payload["conversation_id"] = self.conversation_id

        backoff = 1.0
        for attempt in range(3):
            try:
                response = await self.client.post(self.endpoint, json=payload)
                response.raise_for_status()
                
                data = response.json()
                
                # Extract conversation ID for future requests
                if "conversation_id" in data:
                    self.conversation_id = data["conversation_id"]
                
                # Extract the completion text
                if "choices" in data and len(data["choices"]) > 0:
                    choice = data["choices"][0]
                    if "message" in choice and "content" in choice["message"]:
                        return choice["message"]["content"].strip()
                    elif "text" in choice:
                        return choice["text"].strip()
                
                # Fallback extraction methods
                if "response" in data:
                    return data["response"].strip()
                elif "content" in data:
                    return data["content"].strip()
                elif "text" in data:
                    return data["text"].strip()
                
                logger.warning(f"Unexpected response format from Microsoft Copilot: {data}")
                return ""

            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429:  # Rate limited
                    logger.warning(f"Microsoft Copilot rate limited, attempt {attempt + 1}")
                    if attempt < 2:
                        await asyncio.sleep(backoff)
                        backoff *= 2
                        continue
                elif e.response.status_code == 401:
                    logger.error("Microsoft Copilot authentication failed - check API key")
                    return ""
                elif e.response.status_code == 403:
                    logger.error("Microsoft Copilot access forbidden - check permissions")
                    return ""
                else:
                    logger.error(f"Microsoft Copilot HTTP error {e.response.status_code}: {e}")
                    return ""
                    
            except httpx.RequestError as e:
                logger.warning(f"Microsoft Copilot request failed, attempt {attempt + 1}: {e}")
                if attempt < 2:
                    await asyncio.sleep(backoff)
                    backoff *= 2
                    continue
                    
            except Exception as e:
                logger.error(f"Unexpected error with Microsoft Copilot: {e}")
                return ""

        logger.error("Microsoft Copilot failed after all retry attempts")
        return ""

    async def reset_conversation(self) -> None:
        """Reset the conversation context."""
        self.conversation_id = None
        logger.info("Microsoft Copilot conversation context reset")

    async def close(self) -> None:
        """Clean up the HTTP client."""
        if self.client:
            await self.client.aclose()
            self.client = None
            logger.info("Microsoft Copilot client closed")
