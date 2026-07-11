from fastapi.testclient import TestClient

from app.main import app


def test_api_reference_page_is_served():
    client = TestClient(app)

    response = client.get("/api-reference")

    assert response.status_code == 200
    assert "Vaultflow" in response.text
    assert "API Reference" in response.text
    assert 'href="/api-reference"' in response.text
