import pytest

from app.redactor import Detection, detect_regex_pii, redact_text


class FakeClaudeDetector:
    def __init__(self, detections):
        self._detections = detections

    async def detect(self, text: str):
        return self._detections


# ---------------------------------------------------------------------------
# Composite regex test (all four regex PII types in one pass)
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# SSN — individual coverage
# ---------------------------------------------------------------------------


def test_ssn_detected_individually():
    detections = detect_regex_pii("My SSN is 456-78-9012 please keep it secret.")
    assert len(detections) == 1
    assert detections[0].type == "SSN"
    assert detections[0].source == "regex"


def test_ssn_without_dashes_not_detected():
    # Raw digit string is not a valid SSN format
    detections = detect_regex_pii("123456789")
    assert all(d.type != "SSN" for d in detections)


# ---------------------------------------------------------------------------
# Email — individual coverage
# ---------------------------------------------------------------------------


def test_email_detected_individually():
    detections = detect_regex_pii("Reach me at bob@company.io for details.")
    assert len(detections) == 1
    assert detections[0].type == "EMAIL"


def test_multiple_emails_all_redacted():
    text = "Primary: a@x.com; secondary: b@y.org"
    detections = detect_regex_pii(text)
    emails = [d for d in detections if d.type == "EMAIL"]
    assert len(emails) == 2
    assert {text[d.start:d.end] for d in emails} == {"a@x.com", "b@y.org"}


# ---------------------------------------------------------------------------
# Phone — individual coverage
# ---------------------------------------------------------------------------


def test_phone_detected_dash_format():
    detections = detect_regex_pii("Call me at 415-555-1234 anytime.")
    phones = [d for d in detections if d.type == "PHONE"]
    assert len(phones) == 1


def test_phone_detected_international_format():
    detections = detect_regex_pii("Reach me at +1 (650) 555-0199.")
    phones = [d for d in detections if d.type == "PHONE"]
    assert len(phones) == 1


def test_phone_detected_contiguous_10_digits():
    # Bug regression: 1234567890 (no separators) must be detected as PHONE
    detections = detect_regex_pii("My phone number is 1234567890 please call me.")
    phones = [d for d in detections if d.type == "PHONE"]
    assert len(phones) == 1
    assert detections[0].type == "PHONE"


def test_phone_detected_contiguous_with_leading_1():
    # 11-digit US number with leading country code: 11234567890
    detections = detect_regex_pii("Call 11234567890 to reach support.")
    phones = [d for d in detections if d.type == "PHONE"]
    assert len(phones) == 1


async def test_contiguous_phone_redacted_in_full_sentence():
    # End-to-end redaction: the canonical repro from the bug report
    text = "My name is John Smith. My phone number is 1234567890 and my email is john@example.com."
    llm_detections = [Detection(type="NAME", start=11, end=21, source="llm")]
    result = await redact_text(text, llm_detector=FakeClaudeDetector(llm_detections))

    assert "[PHONE]" in result.redacted_text
    assert "1234567890" not in result.redacted_text
    assert any(d.type == "PHONE" for d in result.detections)


def test_contiguous_phone_not_false_positive_inside_longer_digits():
    # 12+ contiguous digits should NOT be tagged as PHONE (could be card or ID)
    detections = detect_regex_pii("Account number 123456789012.")
    phones = [d for d in detections if d.type == "PHONE"]
    assert len(phones) == 0


def test_phone_without_separators_detected():
    # VAU-6 regression: bare 10-digit number must be caught by regex
    detections = detect_regex_pii("My phone number is 1234567890 ok.")
    phones = [d for d in detections if d.type == "PHONE"]
    assert len(phones) == 1
    assert detections[0].type == "PHONE"


async def test_vau6_full_repro_phone_name_email_all_redacted():
    # Exact repro from VAU-6 issue report (name injected via fake LLM)
    text = "My name is John Smith. My phone number is 1234567890 and my email is john@example.com."
    llm_detections = [Detection(type="NAME", start=11, end=21, source="llm")]
    result = await redact_text(text, llm_detector=FakeClaudeDetector(llm_detections))

    assert "[NAME]" in result.redacted_text
    assert "[PHONE]" in result.redacted_text
    assert "[EMAIL]" in result.redacted_text
    assert "1234567890" not in result.redacted_text
    assert "john@example.com" not in result.redacted_text
    assert "John Smith" not in result.redacted_text


def test_phone_detected_contiguous_10_digit():
    """Regression: 10-digit unseparated number like 1234567890 must be detected."""
    detections = detect_regex_pii("My phone number is 1234567890")
    phones = [d for d in detections if d.type == "PHONE"]
    assert len(phones) == 1
    assert phones[0].source == "regex"


def test_phone_detected_contiguous_11_digit_with_leading_1():
    """Regression: 11-digit with leading 1 (e.g. 11234567890) must be detected."""
    detections = detect_regex_pii("Call 11234567890 to reach us.")
    phones = [d for d in detections if d.type == "PHONE"]
    assert len(phones) == 1


async def test_redact_contiguous_phone_in_sentence():
    """End-to-end: contiguous phone is redacted to [PHONE] in full sentence."""
    text = "My phone number is 1234567890"
    result = await redact_text(text, llm_detector=FakeClaudeDetector([]))
    assert result.redacted_text == "My phone number is [PHONE]"
    assert any(d.type == "PHONE" for d in result.detections)


async def test_full_pii_sentence_name_phone_email():
    """Integration: name + contiguous phone + email all redacted together."""
    text = "My name is John Smith. My phone number is 1234567890 and my email is john@example.com."
    llm_detections = [Detection(type="NAME", start=11, end=21, source="llm")]
    result = await redact_text(text, llm_detector=FakeClaudeDetector(llm_detections))
    assert "[NAME]" in result.redacted_text
    assert "[PHONE]" in result.redacted_text
    assert "[EMAIL]" in result.redacted_text
    assert "John Smith" not in result.redacted_text
    assert "1234567890" not in result.redacted_text
    assert "john@example.com" not in result.redacted_text


def test_contiguous_phone_does_not_trigger_credit_card():
    """10-digit contiguous number must not produce a CREDIT_CARD detection."""
    detections = detect_regex_pii("My phone number is 1234567890")
    cards = [d for d in detections if d.type == "CREDIT_CARD"]
    assert len(cards) == 0


# ---------------------------------------------------------------------------
# Credit card — individual coverage + Luhn gating
# ---------------------------------------------------------------------------


def test_credit_card_valid_luhn_detected():
    # 4111 1111 1111 1111 is a well-known test Visa number (passes Luhn)
    detections = detect_regex_pii("Pay with 4111 1111 1111 1111.")
    cards = [d for d in detections if d.type == "CREDIT_CARD"]
    assert len(cards) == 1


def test_credit_card_invalid_luhn_not_detected():
    # 1234 5678 9012 3456 fails Luhn — must not be flagged
    detections = detect_regex_pii("Number 1234 5678 9012 3456 is not a card.")
    cards = [d for d in detections if d.type == "CREDIT_CARD"]
    assert len(cards) == 0


# ---------------------------------------------------------------------------
# Name + Address — via LLM detector (unit-tested through FakeClaudeDetector)
# ---------------------------------------------------------------------------


async def test_llm_detections_are_merged_with_regex_detections():
    text = "Jane Doe lives at 221B Baker Street and uses jane@example.com."
    llm_detections = [
        Detection(type="NAME", start=0, end=8, source="llm"),
        Detection(type="ADDRESS", start=18, end=35, source="llm"),
    ]

    result = await redact_text(text, llm_detector=FakeClaudeDetector(llm_detections))

    assert result.redacted_text == "[NAME] lives at [ADDRESS] and uses [EMAIL]."
    assert [d.type for d in result.detections] == ["NAME", "ADDRESS", "EMAIL"]


async def test_name_only_detected_and_redacted():
    text = "The employee John Smith submitted the form."
    llm_detections = [Detection(type="NAME", start=13, end=23, source="llm")]

    result = await redact_text(text, llm_detector=FakeClaudeDetector(llm_detections))

    assert "[NAME]" in result.redacted_text
    assert any(d.type == "NAME" for d in result.detections)


async def test_address_only_detected_and_redacted():
    text = "Ship to 742 Evergreen Terrace, Springfield."
    llm_detections = [Detection(type="ADDRESS", start=8, end=42, source="llm")]

    result = await redact_text(text, llm_detector=FakeClaudeDetector(llm_detections))

    assert "[ADDRESS]" in result.redacted_text
    assert any(d.type == "ADDRESS" for d in result.detections)


# ---------------------------------------------------------------------------
# No PII — must return unchanged text and empty detections
# ---------------------------------------------------------------------------


async def test_no_pii_returns_unchanged_text_and_empty_detections():
    text = "The quick brown fox jumps over the lazy dog."
    result = await redact_text(text, llm_detector=FakeClaudeDetector([]))

    assert result.redacted_text == text
    assert result.detections == []


# ---------------------------------------------------------------------------
# Overlap resolution
# ---------------------------------------------------------------------------


async def test_overlapping_detections_keep_longest_span():
    text = "Contact Jane Doe at jane@example.com."
    llm_detections = [
        Detection(type="NAME", start=8, end=16, source="llm"),
        Detection(type="EMAIL", start=20, end=36, source="llm"),
    ]

    result = await redact_text(text, llm_detector=FakeClaudeDetector(llm_detections))

    assert result.redacted_text == "Contact [NAME] at [EMAIL]."
    assert len([d for d in result.detections if d.type == "EMAIL"]) == 1
