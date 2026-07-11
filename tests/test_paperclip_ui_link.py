from fastapi.testclient import TestClient

from app.main import app


def test_frontend_workforce_log_nav_links_to_dashboard_redirect():
    client = TestClient(app)

    for route in ["/", "/team"]:
        response = client.get(route)
        assert response.status_code == 200
        assert "Workforce Log" in response.text
        assert 'href="/paperclip-ui"' in response.text
        assert "Paperclip Dashboard" not in response.text


def test_paperclip_ui_redirect_is_exposed(monkeypatch):
    monkeypatch.setenv("PAPERCLIP_PUBLIC_URL", "https://paperclip.example.com")
    client = TestClient(app)

    response = client.get("/paperclip-ui", follow_redirects=False)

    assert response.status_code in {302, 307}
    assert response.headers["location"] == "https://paperclip.example.com"
