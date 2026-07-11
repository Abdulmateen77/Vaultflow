from fastapi.testclient import TestClient

from app.main import app


def _assert_no_removed_frontend_references(html: str) -> None:
    assert "Paperclip" not in html
    assert "paperclip" not in html
    assert "API Docs" not in html
    assert "API Reference" not in html
    assert "/api-reference" not in html
    assert "/paperclip-ui" not in html
    assert "ticket" not in html.lower()


def test_team_page_serves_five_agent_cards_without_removed_branding():
    client = TestClient(app)

    response = client.get("/team")

    assert response.status_code == 200
    html = response.text
    for role in ["ceo", "cto", "sales", "marketing", "finance"]:
        assert f'data-role="{role}"' in html
        assert f"/agent/{role}" in html
    assert "Autonomous Agents Team" in html
    assert "runs the company app" in html
    assert "Workforce log" in html
    assert "agent-output" in html
    _assert_no_removed_frontend_references(html)


def test_homepage_uses_ai_observance_and_clean_nav_without_removed_branding():
    client = TestClient(app)

    response = client.get("/")

    assert response.status_code == 200
    html = response.text
    assert "Vaultflow AI Observance Tool" in html
    assert "AI Security Gateway + Governance Platform" in html
    assert "Run fully autonomously by agents" in html
    assert 'href="/team"' in html
    assert "Team" in html
    assert "Workforce Log" in html
    _assert_no_removed_frontend_references(html)
