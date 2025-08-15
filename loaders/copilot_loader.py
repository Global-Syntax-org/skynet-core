import os
import logging
import asyncio
from typing import Optional, Dict, Any
import httpx

logger = logging.getLogger(__name__)


class CopilotModelLoader:
    """Minimal Copilot-compatible client using a configurable endpoint.

    GitHub Copilot doesn't offer a simple public REST API for completions; if
    you have an internal endpoint or a proxy that accepts token-based requests,
    set `COPILOT_API_URL` and `GITHUB_COPILOT_TOKEN` in the environment.
    """

    def __init__(self):
        self.token = os.getenv("GITHUB_COPILOT_TOKEN")
        self.api_url = os.getenv("COPILOT_API_URL")
        self.model = os.getenv("COPILOT_MODEL", "copilot")
        self.client: Optional[httpx.AsyncClient] = None

    async def initialize(self) -> bool:
        if not self.token or not self.api_url:
            logger.info("Copilot token or API URL not configured; Copilot loader disabled")
            return False
        self.client = httpx.AsyncClient(timeout=30.0)
        logger.info("Copilot loader initialized")
        return True

    async def ensure_model_available(self, model_name: Optional[str] = None) -> bool:
        return True

    async def generate_completion(self, prompt: str, model_name: Optional[str] = None) -> str:
        if not self.client:
            await self.initialize()

        headers = {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}
        payload: Dict[str, Any] = {"model": model_name or self.model, "prompt": prompt, "max_tokens": 1024}

        backoff = 1.0
        for attempt in range(3):
            try:
                resp = await self.client.post(self.api_url, headers=headers, json=payload)
                resp.raise_for_status()
                try:
                    data = resp.json()
                except Exception:
                    data = {}

                # Expecting {"text": "..."} or a similar structure
                return data.get("text") or data.get("output") or ""

            except httpx.HTTPError as e:
                logger.warning(f"Copilot API attempt {attempt + 1} failed: {e}")
                if attempt < 2:
                    await asyncio.sleep(backoff)
                    backoff *= 2
                    continue
                logger.error("Copilot API failed after retries")
                return ""
            except Exception as e:
                logger.error(f"Unexpected error calling Copilot endpoint: {e}")
                return ""

    async def close(self) -> None:
        if self.client:
            await self.client.aclose()
