from __future__ import annotations

import os
from typing import Any
from datetime import datetime, timezone

import httpx

from app.redactor import RedactionResult


class ConvexMutationClient:
    def __init__(self, convex_url: str, client: httpx.AsyncClient | None = None):
        self.convex_url = convex_url.rstrip("/")
        self.client = client

    async def mutation(self, path: str, args: dict[str, Any]) -> Any:
        payload = {"path": path, "args": args, "format": "json"}

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


class ConvexRedactionLogger:
    def __init__(self, convex_url: str, client: httpx.AsyncClient | None = None):
        self.mutations = ConvexMutationClient(convex_url=convex_url, client=client)

    async def log(self, input_text: str, result: RedactionResult) -> Any:
        return await self.mutations.mutation(
            "redactions:log",
            {
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
        )


class ConvexAgentLogger:
    def __init__(self, convex_url: str, client: httpx.AsyncClient | None = None):
        self.mutations = ConvexMutationClient(convex_url=convex_url, client=client)

    async def log(self, role: str, ticket_id: str, output: str) -> Any:
        return await self.mutations.mutation(
            "agentLogs:log",
            {
                "role": role,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "ticketId": ticket_id,
                "output": output,
            },
        )


def _convex_url() -> str:
    convex_url = os.getenv("CONVEX_URL")
    if not convex_url:
        raise RuntimeError("CONVEX_URL is not configured")
    return convex_url


async def log_redaction(input_text: str, result: RedactionResult) -> Any:
    return await ConvexRedactionLogger(convex_url=_convex_url()).log(input_text, result)


async def log_agent_response(role: str, ticket_id: str, output: str) -> Any:
    return await ConvexAgentLogger(convex_url=_convex_url()).log(role, ticket_id, output)
