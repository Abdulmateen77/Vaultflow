from fastapi.testclient import TestClient

from app.main import app


def test_api_reference_page_removed_from_frontend():
    client = TestClient(app)

    response = client.get("/api-reference")

    assert response.status_code == 404
