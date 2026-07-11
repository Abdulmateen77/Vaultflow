from fastapi.testclient import TestClient

from app.main import app


def test_paperclip_ui_redirect_uses_configured_public_url(monkeypatch):
    monkeypatch.setenv("PAPERCLIP_PUBLIC_URL", "https://paperclip.example.com")
    client = TestClient(app)

    response = client.get("/paperclip-ui", follow_redirects=False)

    assert response.status_code in {302, 307}
    assert response.headers["location"] == "https://paperclip.example.com"


def test_team_page_links_to_paperclip_ui():
    client = TestClient(app)

    response = client.get("/team")

    assert response.status_code == 200
    assert 'href="/paperclip-ui"' in response.text
    assert "Open Paperclip dashboard" in response.text
