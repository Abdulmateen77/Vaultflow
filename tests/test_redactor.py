from app.redactor import Detection, redact_text


class FakeClaudeDetector:
    def __init__(self, detections):
        self._detections = detections

    async def detect(self, text: str):
        return self._detections


async def test_regex_redacts_email_phone_ssn_and_credit_card():
    text = (
        "Email alice@example.com or call (415) 555-2671. "
        "SSN 123-45-6789. Card 4111 1111 1111 1111."
    )

    result = await redact_text(text, llm_detector=FakeClaudeDetector([]))

    assert result.redacted_text == (
        "Email [EMAIL] or call [PHONE]. "
        "SSN [SSN]. Card [CREDIT_CARD]."
    )
    assert [(d.type, text[d.start:d.end]) for d in result.detections] == [
        ("EMAIL", "alice@example.com"),
        ("PHONE", "(415) 555-2671"),
        ("SSN", "123-45-6789"),
        ("CREDIT_CARD", "4111 1111 1111 1111"),
    ]


async def test_llm_detections_are_merged_with_regex_detections():
    text = "Jane Doe lives at 221B Baker Street and uses jane@example.com."
    llm_detections = [
        Detection(type="NAME", start=0, end=8, source="llm"),
        Detection(type="ADDRESS", start=18, end=35, source="llm"),
    ]

    result = await redact_text(text, llm_detector=FakeClaudeDetector(llm_detections))

    assert result.redacted_text == "[NAME] lives at [ADDRESS] and uses [EMAIL]."
    assert [d.type for d in result.detections] == ["NAME", "ADDRESS", "EMAIL"]


async def test_overlapping_detections_keep_longest_span():
    text = "Contact Jane Doe at jane@example.com."
    llm_detections = [
        Detection(type="NAME", start=8, end=16, source="llm"),
        Detection(type="EMAIL", start=20, end=36, source="llm"),
    ]

    result = await redact_text(text, llm_detector=FakeClaudeDetector(llm_detections))

    assert result.redacted_text == "Contact [NAME] at [EMAIL]."
    assert len([d for d in result.detections if d.type == "EMAIL"]) == 1
