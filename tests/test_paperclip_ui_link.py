from fastapi.testclient import TestClient

from app.main import app


def test_frontend_no_longer_links_to_paperclip_ui():
    client = TestClient(app)

    for route in ["/", "/team"]:
        response = client.get(route)
        assert response.status_code == 200
        assert "/paperclip-ui" not in response.text
        assert "Paperclip" not in response.text
        assert "paperclip" not in response.text
        assert "Paperclip Dashboard" not in response.text


def test_old_paperclip_ui_redirect_is_not_exposed():
    client = TestClient(app)

    response = client.get("/paperclip-ui", follow_redirects=False)

    assert response.status_code == 404
