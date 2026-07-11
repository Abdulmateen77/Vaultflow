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

    async def fake_log_redaction(input_text: str, result: RedactionResult):
        return "log123"

    monkeypatch.setattr("app.main.redact_text", fake_redact_text)
    monkeypatch.setattr("app.main.log_redaction", fake_log_redaction)
    client = TestClient(app)

    response = client.post("/redact", json={"text": "Email alice@example.com"})

    assert response.status_code == 200
    assert response.json() == {
        "redacted_text": "Email [EMAIL]",
        "detections": [
            {"type": "EMAIL", "start": 6, "end": 23, "source": "regex"},
        ],
    }


def test_redact_endpoint_logs_every_successful_redaction(monkeypatch):
    captured = {}

    async def fake_redact_text(text: str):
        return RedactionResult(
            redacted_text="Email [EMAIL]",
            detections=[Detection(type="EMAIL", start=6, end=23, source="regex")],
        )

    async def fake_log_redaction(input_text: str, result: RedactionResult):
        captured["input_text"] = input_text
        captured["result"] = result

    monkeypatch.setattr("app.main.redact_text", fake_redact_text)
    monkeypatch.setattr("app.main.log_redaction", fake_log_redaction)
    client = TestClient(app)

    response = client.post("/redact", json={"text": "Email alice@example.com"})

    assert response.status_code == 200
    assert captured["input_text"] == "Email alice@example.com"
    assert captured["result"].redacted_text == "Email [EMAIL]"


def test_redact_endpoint_fails_closed_if_logging_fails(monkeypatch):
    async def fake_redact_text(text: str):
        return RedactionResult(redacted_text="Email [EMAIL]", detections=[])

    async def fake_log_redaction(input_text: str, result: RedactionResult):
        raise RuntimeError("Convex down")

    monkeypatch.setattr("app.main.redact_text", fake_redact_text)
    monkeypatch.setattr("app.main.log_redaction", fake_log_redaction)
    client = TestClient(app)

    response = client.post("/redact", json={"text": "Email alice@example.com"})

    assert response.status_code == 502
    assert response.json()["detail"] == "redaction log write failed"


def test_redact_endpoint_rejects_empty_text():
    client = TestClient(app)

    response = client.post("/redact", json={"text": "   "})

    assert response.status_code == 422
