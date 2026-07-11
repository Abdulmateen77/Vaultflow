from __future__ import annotations

import os
from typing import Any

import httpx

from app.redactor import RedactionResult


class ConvexRedactionLogger:
    def __init__(self, convex_url: str, client: httpx.AsyncClient | None = None):
        self.convex_url = convex_url.rstrip("/")
        self.client = client

    async def log(self, input_text: str, result: RedactionResult) -> Any:
        payload = {
            "path": "redactions:log",
            "args": {
                "inputText": input_text,
                "redactedText": result.redacted_text,
                "detections": [
                    {
                        "type": detection.type,
                        "start": detection.start,
                        "end": detection.end,
                        "source": detection.source,
                    }
                    for detection in result.detections
                ],
            },
            "format": "json",
        }

        if self.client is not None:
            response = await self.client.post(f"{self.convex_url}/api/mutation", json=payload)
        else:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.post(f"{self.convex_url}/api/mutation", json=payload)

        response.raise_for_status()
        body = response.json()
        if body.get("status") != "success":
            raise RuntimeError(body.get("errorMessage", "Convex mutation failed"))
        return body.get("value")


async def log_redaction(input_text: str, result: RedactionResult) -> Any:
    convex_url = os.getenv("CONVEX_URL")
    if not convex_url:
        raise RuntimeError("CONVEX_URL is not configured")
    return await ConvexRedactionLogger(convex_url=convex_url).log(input_text, result)
