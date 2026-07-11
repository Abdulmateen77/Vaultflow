import json

import httpx

from app.observability import ConvexRedactionLogger
from app.redactor import Detection, RedactionResult


async def test_convex_logger_posts_redaction_to_mutation_endpoint():
    requests = []

    async def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, json={"status": "success", "value": "log123"})

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    logger = ConvexRedactionLogger(
        convex_url="https://example.convex.cloud",
        client=client,
    )

    log_id = await logger.log(
        input_text="Jane Doe email jane@example.com",
        result=RedactionResult(
            redacted_text="[NAME] email [EMAIL]",
            detections=[
                Detection(type="NAME", start=0, end=8, source="llm"),
                Detection(type="EMAIL", start=15, end=31, source="regex"),
            ],
        ),
    )

    assert log_id == "log123"
    assert len(requests) == 1
    request = requests[0]
    assert str(request.url) == "https://example.convex.cloud/api/mutation"
    payload = json.loads(request.content)
    assert payload == {
        "path": "redactions:log",
        "args": {
            "inputText": "Jane Doe email jane@example.com",
            "redactedText": "[NAME] email [EMAIL]",
            "detections": [
                {"type": "NAME", "start": 0, "end": 8, "source": "llm"},
                {"type": "EMAIL", "start": 15, "end": 31, "source": "regex"},
            ],
        },
        "format": "json",
    }


async def test_convex_logger_raises_when_mutation_fails():
    async def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"status": "error", "errorMessage": "boom"})

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    logger = ConvexRedactionLogger(
        convex_url="https://example.convex.cloud",
        client=client,
    )

    result = RedactionResult(redacted_text="ok", detections=[])

    try:
        await logger.log(input_text="x", result=result)
    except RuntimeError as exc:
        assert "boom" in str(exc)
    else:
        raise AssertionError("Expected Convex logging failure")
