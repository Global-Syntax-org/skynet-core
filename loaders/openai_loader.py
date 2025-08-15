import os
import logging
import asyncio
from typing import Optional, Dict, Any
import httpx

logger = logging.getLogger(__name__)


class OpenAIModelLoader:
    """Async OpenAI (ChatGPT) client using the HTTP API.

    Uses `OPENAI_API_KEY` and optional `OPENAI_API_BASE` environment variables.
    Falls back to api.openai.com when no custom base is provided.
    """

    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.api_base = os.getenv("OPENAI_API_BASE", "https://api.openai.com")
        self.default_model = os.getenv("OPENAI_MODEL", "gpt-4o")
        self.client: Optional[httpx.AsyncClient] = None

    async def initialize(self) -> bool:
        if not self.api_key:
            logger.info("OpenAI API key not found; OpenAI loader disabled")
            return False
        self.client = httpx.AsyncClient(timeout=30.0)
        logger.info("OpenAI loader initialized")
        return True

    async def ensure_model_available(self, model_name: Optional[str] = None) -> bool:
        # Best-effort: don't query models endpoint (may require admin access)
        return True

    async def generate_completion(self, prompt: str, model_name: Optional[str] = None) -> str:
        model = model_name or self.default_model
        if not self.client:
            await self.initialize()

        url = f"{self.api_base.rstrip('/')}/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload: Dict[str, Any] = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2,
            "max_tokens": 1024
        }

        # Simple retry with backoff
        backoff = 1.0
        for attempt in range(3):
            try:
                resp = await self.client.post(url, headers=headers, json=payload)
                resp.raise_for_status()
                try:
                    data = resp.json()
                except Exception:
                    data = {}

                # Parse response for chat completion
                choices = data.get("choices") or []
                if choices:
                    message = choices[0].get("message") or {}
                    return message.get("content") or choices[0].get("text", "")
                # Fallback to top-level text
                return data.get("text", "")

            except httpx.HTTPError as e:
                logger.warning(f"OpenAI API attempt {attempt + 1} failed: {e}")
                if attempt < 2:
                    await asyncio.sleep(backoff)
                    backoff *= 2
                    continue
                logger.error("OpenAI API failed after retries")
                return ""
            except Exception as e:
                logger.error(f"Unexpected error calling OpenAI: {e}")
                return ""

    async def close(self) -> None:
        if self.client:
            await self.client.aclose()
