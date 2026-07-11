import json

import httpx
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.paperclip_agents import PaperclipAgentClient, run_agent_role


@pytest.mark.asyncio
async def test_paperclip_client_creates_invokes_polls_and_returns_agent_comment():
    requests: list[httpx.Request] = []
    issue = {
        "id": "ticket-123",
        "identifier": "VAU-123",
        "status": "todo",
        "assigneeAgentId": "ceo-agent",
        "title": "Team page: CEO",
    }

    async def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        if request.method == "GET" and str(request.url).endswith("/companies/company-1/agents"):
            return httpx.Response(
                200,
                json=[
                    {"id": "ceo-agent", "name": "CEO", "role": "ceo", "status": "idle"},
                ],
            )
        if request.method == "POST" and str(request.url).endswith("/companies/company-1/issues"):
            payload = json.loads(request.content)
            assert payload["assigneeAgentId"] == "ceo-agent"
            assert payload["status"] == "todo"
            assert "Act as company strategist" in payload["description"]
            assert "post the final answer as an agent comment" in payload["description"]
            return httpx.Response(201, json=issue)
        if request.method == "POST" and str(request.url).endswith("/agents/ceo-agent/heartbeat/invoke"):
            return httpx.Response(201, json={"id": "run-1", "status": "queued"})
        if request.method == "GET" and str(request.url).endswith("/issues/ticket-123/comments"):
            return httpx.Response(
                200,
                json=[
                    {"authorType": "user", "body": "created"},
                    {
                        "authorType": "agent",
                        "authorAgentId": "ceo-agent",
                        "body": "Vision: build the agentic SaaS company around privacy automation.",
                    },
                ],
            )
        if request.method == "GET" and str(request.url).endswith("/issues/ticket-123"):
            return httpx.Response(200, json={**issue, "status": "done"})
        return httpx.Response(404, json={"error": str(request.url)})

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    paperclip = PaperclipAgentClient(
        api_base="http://paperclip.local/api",
        company_id="company-1",
        client=client,
        poll_interval_seconds=0,
        timeout_seconds=1,
    )

    result = await paperclip.run_role("ceo")

    assert result.role == "ceo"
    assert result.ticket_id == "ticket-123"
    assert result.ticket_identifier == "VAU-123"
    assert "Vision:" in result.output
    assert any(req.method == "POST" and "/heartbeat/invoke" in str(req.url) for req in requests)


@pytest.mark.asyncio
async def test_run_agent_role_logs_output_to_convex(monkeypatch):
    captured = {}

    class FakePaperclip:
        async def run_role(self, role: str):
            from app.paperclip_agents import AgentRunResult

            return AgentRunResult(
                role=role,
                ticket_id="ticket-sales",
                ticket_identifier="VAU-777",
                output="Prospects found",
            )

    async def fake_log(role: str, ticket_id: str, output: str):
        captured["role"] = role
        captured["ticket_id"] = ticket_id
        captured["output"] = output
        return "convex-log-id"

    monkeypatch.setattr("app.paperclip_agents.log_agent_response", fake_log)

    result = await run_agent_role("sales", client=FakePaperclip())

    assert result.output == "Prospects found"
    assert captured == {
        "role": "sales",
        "ticket_id": "ticket-sales",
        "output": "Prospects found",
    }


def test_agent_endpoint_returns_ticket_response_and_rejects_unknown_role(monkeypatch):
    async def fake_run_agent_role(role: str):
        from app.paperclip_agents import AgentRunResult

        return AgentRunResult(
            role=role,
            ticket_id="ticket-marketing",
            ticket_identifier="VAU-888",
            output="Headline: Stop leaking PII into AI tools.",
        )

    monkeypatch.setattr("app.main.run_agent_role", fake_run_agent_role)
    client = TestClient(app)

    response = client.post("/agent/marketing")

    assert response.status_code == 200
    assert response.json() == {
        "role": "marketing",
        "ticket_id": "ticket-marketing",
        "ticket_identifier": "VAU-888",
        "output": "Headline: Stop leaking PII into AI tools.",
    }

    bad = client.post("/agent/not-a-role")
    assert bad.status_code == 404
