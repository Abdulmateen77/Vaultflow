from fastapi.testclient import TestClient

from app.main import app


def test_team_page_serves_five_agent_cards():
    client = TestClient(app)

    response = client.get("/team")

    assert response.status_code == 200
    html = response.text
    for role in ["ceo", "cto", "sales", "marketing", "finance"]:
        assert f'data-role="{role}"' in html
        assert f"/agent/{role}" in html
    assert "Paperclip Team" in html
    assert "agent-output" in html
