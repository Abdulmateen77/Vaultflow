from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import Protocol

from anthropic import AsyncAnthropic


@dataclass(frozen=True)
class Detection:
    type: str
    start: int
    end: int
    source: str


@dataclass(frozen=True)
class RedactionResult:
    redacted_text: str
    detections: list[Detection]


class LLMDetector(Protocol):
    async def detect(self, text: str) -> list[Detection]: ...


EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
SSN_RE = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
PHONE_RE = re.compile(
    r"(?<!\d)"
    r"(?:\+?1[\s.-]?)?"
    r"(?:"
    r"(?:\(\d{3}\)|\d{3})[\s.-]\d{3}[\s.-]\d{4}"  # formatted: (123) 456-7890 or 123-456-7890
    r"|\d{10}"                                       # raw 10-digit: 1234567890 (VAU-6)
    r")"
    r"(?!\d)"
)
CREDIT_CARD_CANDIDATE_RE = re.compile(r"(?<!\d)(?:\d[ -]?){13,19}(?!\d)")

PLACEHOLDERS = {
    "EMAIL": "[EMAIL]",
    "PHONE": "[PHONE]",
    "SSN": "[SSN]",
    "CREDIT_CARD": "[CREDIT_CARD]",
    "NAME": "[NAME]",
    "ADDRESS": "[ADDRESS]",
}


def detect_regex_pii(text: str) -> list[Detection]:
    detections: list[Detection] = []
    for pii_type, pattern in (
        ("EMAIL", EMAIL_RE),
        ("PHONE", PHONE_RE),
        ("SSN", SSN_RE),
    ):
        for match in pattern.finditer(text):
            detections.append(
                Detection(type=pii_type, start=match.start(), end=match.end(), source="regex")
            )

    for match in CREDIT_CARD_CANDIDATE_RE.finditer(text):
        value = match.group(0)
        digits = re.sub(r"\D", "", value)
        if 13 <= len(digits) <= 19 and _passes_luhn(digits):
            detections.append(
                Detection(
                    type="CREDIT_CARD",
                    start=match.start(),
                    end=match.end(),
                    source="regex",
                )
            )

    return _merge_overlapping(detections)


async def redact_text(text: str, llm_detector: LLMDetector | None = None) -> RedactionResult:
    detections = detect_regex_pii(text)
    if llm_detector is None:
        llm_detector = ClaudePIIDetector()

    llm_detections = await llm_detector.detect(text)
    detections = _merge_overlapping([*detections, *llm_detections])
    redacted_text = _apply_redactions(text, detections)
    return RedactionResult(redacted_text=redacted_text, detections=detections)


def _apply_redactions(text: str, detections: list[Detection]) -> str:
    parts: list[str] = []
    cursor = 0
    for detection in detections:
        parts.append(text[cursor : detection.start])
        parts.append(PLACEHOLDERS.get(detection.type, "[PII]"))
        cursor = detection.end
    parts.append(text[cursor:])
    return "".join(parts)


def _merge_overlapping(detections: list[Detection]) -> list[Detection]:
    valid = [d for d in detections if 0 <= d.start < d.end]
    ranked = sorted(valid, key=lambda d: (d.start, -(d.end - d.start), d.source != "regex"))
    merged: list[Detection] = []

    for detection in ranked:
        if not merged:
            merged.append(detection)
            continue

        last = merged[-1]
        if detection.start >= last.end:
            merged.append(detection)
            continue

        last_len = last.end - last.start
        detection_len = detection.end - detection.start
        if detection_len > last_len:
            merged[-1] = detection

    return sorted(merged, key=lambda d: d.start)


def _passes_luhn(digits: str) -> bool:
    total = 0
    parity = len(digits) % 2
    for index, char in enumerate(digits):
        value = int(char)
        if index % 2 == parity:
            value *= 2
            if value > 9:
                value -= 9
        total += value
    return total % 10 == 0


class ClaudePIIDetector:
    def __init__(self, api_key: str | None = None, model: str | None = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.model = model or os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-5")
        self.client = AsyncAnthropic(api_key=self.api_key) if self.api_key else None

    async def detect(self, text: str) -> list[Detection]:
        if not self.client or not text.strip():
            return []

        response = await self.client.messages.create(
            model=self.model,
            max_tokens=800,
            temperature=0,
            system=(
                "You detect PII in user-provided text. Return only JSON, no prose. "
                "Detect names and physical addresses only. Do not include emails, phone "
                "numbers, SSNs, or credit cards because regex handles those."
            ),
            messages=[
                {
                    "role": "user",
                    "content": (
                        "Find personal names and physical addresses in this text. "
                        "Return a JSON array like "
                        '[{"type":"NAME","text":"Jane Doe"},'
                        '{"type":"ADDRESS","text":"221B Baker Street"}]. '
                        "Only use type NAME or ADDRESS. Text:\n\n" + text
                    ),
                }
            ],
        )
        payload = _message_text(response)
        return _detections_from_llm_payload(text, payload)


def _message_text(response) -> str:
    chunks: list[str] = []
    for block in response.content:
        if getattr(block, "type", None) == "text":
            chunks.append(block.text)
    return "".join(chunks)


def _detections_from_llm_payload(text: str, payload: str) -> list[Detection]:
    try:
        parsed = json.loads(payload)
    except json.JSONDecodeError:
        return []

    detections: list[Detection] = []
    if not isinstance(parsed, list):
        return detections

    for item in parsed:
        if not isinstance(item, dict):
            continue
        pii_type = str(item.get("type", "")).upper()
        pii_text = str(item.get("text", ""))
        if pii_type not in {"NAME", "ADDRESS"} or not pii_text:
            continue
        start = text.find(pii_text)
        while start != -1:
            detections.append(
                Detection(
                    type=pii_type,
                    start=start,
                    end=start + len(pii_text),
                    source="llm",
                )
            )
            start = text.find(pii_text, start + len(pii_text))
    return _merge_overlapping(detections)
