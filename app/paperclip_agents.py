from __future__ import annotations

import asyncio
import os
import time
from dataclasses import dataclass
from typing import Any

import httpx

from app.observability import log_agent_response


@dataclass(frozen=True)
class AgentRoleConfig:
    role: str
    display_name: str
    paperclip_agent_name: str
    prompt: str


@dataclass(frozen=True)
class AgentRunResult:
    role: str
    ticket_id: str
    ticket_identifier: str
    output: str


TASK_PROMPTS: dict[str, AgentRoleConfig] = {
    "ceo": AgentRoleConfig(
        role="ceo",
        display_name="CEO",
        paperclip_agent_name="CEO",
        prompt=(
            "Act as company strategist. Give company vision, current strategy, "
            "and next steps for the agentic SaaS business. First shipped unit is "
            "a PII redaction gateway."
        ),
    ),
    "cto": AgentRoleConfig(
        role="cto",
        display_name="CTO",
        paperclip_agent_name="Chief Technology Officer",
        prompt=(
            "Report current tech features built (list /redact endpoint, "
            "regex+LLM detection, Convex logging) and the broader agentic SaaS roadmap."
        ),
    ),
    "sales": AgentRoleConfig(
        role="sales",
        display_name="Sales",
        paperclip_agent_name="Sales",
        prompt=(
            "Use Linkup to find real companies + decision makers in regulated "
            "industries (healthcare/legal/finance) who need PII redaction. Return "
            "company, contact name/title, why they fit."
        ),
    ),
    "marketing": AgentRoleConfig(
        role="marketing",
        display_name="Marketing",
        paperclip_agent_name="Marketing",
        prompt=(
            "Write landing page copy (headline, subhead, 3 bullets, CTA) and one "
            "social launch post."
        ),
    ),
    "finance": AgentRoleConfig(
        role="finance",
        display_name="Finance",
        paperclip_agent_name="Finance",
        prompt=(
            "Propose a pricing model for the PII redaction gateway (tiers, "
            "per-request or subscription pricing) and a basic operating budget for "
            "running this as a company unit."
        ),
    ),
}


class UnknownAgentRoleError(ValueError):
    pass


class PaperclipAgentClient:
    def __init__(
        self,
        api_base: str | None = None,
        company_id: str | None = None,
        client: httpx.AsyncClient | None = None,
        poll_interval_seconds: float = 2.0,
        timeout_seconds: float | None = None,
    ):
        self.api_base = (api_base or os.getenv("PAPERCLIP_API_BASE", "http://127.0.0.1:3100/api")).rstrip("/")
        self.company_id = company_id or os.getenv(
            "PAPERCLIP_COMPANY_ID",
            "85168c9b-e804-4657-90e4-ac16de06d1ba",
        )
        self.client = client
        self.poll_interval_seconds = poll_interval_seconds
        self.timeout_seconds = timeout_seconds or float(os.getenv("PAPERCLIP_AGENT_TIMEOUT_SECONDS", "180"))

    async def run_role(self, role: str) -> AgentRunResult:
        config = self._role_config(role)
        async with self._client_context() as client:
            agent = await self._find_agent(client, config.paperclip_agent_name)
            await self._resume_agent_if_paused(client, agent)
            issue = await self._create_ticket(client, config, agent["id"])
            await self._invoke_agent(client, agent["id"])
            output = await self._poll_agent_comment(client, issue["id"], agent["id"])
            return AgentRunResult(
                role=config.role,
                ticket_id=issue["id"],
                ticket_identifier=issue.get("identifier", issue["id"]),
                output=output,
            )

    def _role_config(self, role: str) -> AgentRoleConfig:
        normalized = role.lower().strip()
        if normalized not in TASK_PROMPTS:
            raise UnknownAgentRoleError(f"Unknown agent role: {role}")
        return TASK_PROMPTS[normalized]

    def _client_context(self):
        if self.client is not None:
            return _ExistingClientContext(self.client)
        return httpx.AsyncClient(timeout=30)

    async def _find_agent(self, client: httpx.AsyncClient, name: str) -> dict[str, Any]:
        response = await client.get(f"{self.api_base}/companies/{self.company_id}/agents")
        response.raise_for_status()
        agents = response.json()
        for agent in agents:
            if agent.get("name") == name:
                return agent
        raise RuntimeError(f"Paperclip agent not found: {name}")

    async def _resume_agent_if_paused(self, client: httpx.AsyncClient, agent: dict[str, Any]) -> None:
        if agent.get("status") == "paused":
            response = await client.post(f"{self.api_base}/agents/{agent['id']}/resume")
            response.raise_for_status()

    async def _create_ticket(
        self,
        client: httpx.AsyncClient,
        config: AgentRoleConfig,
        agent_id: str,
    ) -> dict[str, Any]:
        response = await client.post(
            f"{self.api_base}/companies/{self.company_id}/issues",
            json={
                "title": f"Team page: {config.display_name}",
                "description": self._ticket_description(config),
                "status": "todo",
                "priority": "high" if config.role in {"ceo", "cto", "sales"} else "medium",
                "assigneeAgentId": agent_id,
                "requestDepth": 0,
            },
        )
        response.raise_for_status()
        return response.json()

    def _ticket_description(self, config: AgentRoleConfig) -> str:
        return (
            f"Team page request for {config.display_name}.\n\n"
            f"Task prompt:\n{config.prompt}\n\n"
            "Paperclip execution requirements:\n"
            "- Complete this ticket using your Paperclip agent identity.\n"
            "- Do not call Claude, Linkup, or other model/search tools from FastAPI; use your Paperclip runtime.\n"
            "- If a required tool such as Linkup is unavailable, explain the blocker in the ticket response.\n"
            "- When done, post the final answer as an agent comment on this ticket and mark the ticket done.\n"
            "- If you post comments through the Paperclip API yourself, POST to /api/issues/{issueId}/comments with JSON {\"body\": \"...\"}; do not use {\"comment\": \"...\"} for that endpoint.\n"
            "- Keep the answer concise and useful for display in the Vaultflow Team page output panel.\n"
        )

    async def _invoke_agent(self, client: httpx.AsyncClient, agent_id: str) -> None:
        response = await client.post(f"{self.api_base}/agents/{agent_id}/heartbeat/invoke")
        response.raise_for_status()

    async def _poll_agent_comment(
        self,
        client: httpx.AsyncClient,
        issue_id: str,
        agent_id: str,
    ) -> str:
        deadline = time.monotonic() + self.timeout_seconds
        last_status = "unknown"
        while time.monotonic() < deadline:
            comment = await self._latest_agent_comment(client, issue_id, agent_id)
            if comment:
                return comment

            issue_response = await client.get(f"{self.api_base}/issues/{issue_id}")
            issue_response.raise_for_status()
            issue = issue_response.json()
            last_status = issue.get("status", last_status)
            if last_status in {"blocked", "cancelled"}:
                raise RuntimeError(f"Paperclip ticket {issue_id} ended with status {last_status}")
            await asyncio.sleep(self.poll_interval_seconds)

        raise TimeoutError(f"Timed out waiting for Paperclip agent response on ticket {issue_id}; last status={last_status}")

    async def _latest_agent_comment(
        self,
        client: httpx.AsyncClient,
        issue_id: str,
        agent_id: str,
    ) -> str | None:
        response = await client.get(f"{self.api_base}/issues/{issue_id}/comments")
        response.raise_for_status()
        comments = response.json()
        for comment in comments:
            if (
                comment.get("authorType") == "agent"
                and comment.get("authorAgentId") == agent_id
                and comment.get("body")
            ):
                return str(comment["body"])
        return None


class _ExistingClientContext:
    def __init__(self, client: httpx.AsyncClient):
        self.client = client

    async def __aenter__(self) -> httpx.AsyncClient:
        return self.client

    async def __aexit__(self, exc_type, exc, tb) -> None:
        return None


async def run_agent_role(
    role: str,
    client: PaperclipAgentClient | None = None,
) -> AgentRunResult:
    runner = client or PaperclipAgentClient()
    result = await runner.run_role(role)
    await log_agent_response(role=result.role, ticket_id=result.ticket_id, output=result.output)
    return result
