from fastapi.testclient import TestClient

from app.main import app
from app.redactor import Detection, RedactionResult


def test_redact_endpoint_returns_redacted_text_and_detections(monkeypatch):
    async def fake_redact_text(text: str):
        assert text == "Email alice@example.com"
        return RedactionResult(
            redacted_text="Email [EMAIL]",
            detections=[Detection(type="EMAIL", start=6, end=23, source="regex")],
        )

    monkeypatch.setattr("app.main.redact_text", fake_redact_text)
    client = TestClient(app)

    response = client.post("/redact", json={"text": "Email alice@example.com"})

    assert response.status_code == 200
    assert response.json() == {
        "redacted_text": "Email [EMAIL]",
        "detections": [
            {"type": "EMAIL", "start": 6, "end": 23, "source": "regex"},
        ],
    }


def test_redact_endpoint_rejects_empty_text():
    client = TestClient(app)

    response = client.post("/redact", json={"text": "   "})

    assert response.status_code == 422
