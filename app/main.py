from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel, Field, field_validator
from dotenv import load_dotenv

from app.redactor import Detection, redact_text

load_dotenv()

app = FastAPI(title="Vaultflow PII Redaction Gateway", version="0.1.0")


class RedactRequest(BaseModel):
    text: str = Field(min_length=1)

    @field_validator("text")
    @classmethod
    def text_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("text must not be blank")
        return value


class DetectionResponse(BaseModel):
    type: str
    start: int
    end: int
    source: str


class RedactResponse(BaseModel):
    redacted_text: str
    detections: list[DetectionResponse]


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/redact", response_model=RedactResponse)
async def redact(request: RedactRequest) -> RedactResponse:
    result = await redact_text(request.text)
    return RedactResponse(
        redacted_text=result.redacted_text,
        detections=[_detection_response(detection) for detection in result.detections],
    )


def _detection_response(detection: Detection) -> DetectionResponse:
    return DetectionResponse(
        type=detection.type,
        start=detection.start,
        end=detection.end,
        source=detection.source,
    )
