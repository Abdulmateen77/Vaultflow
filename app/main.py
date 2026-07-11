from __future__ import annotations

import pathlib

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, field_validator
from dotenv import load_dotenv

from app.observability import log_redaction
from app.redactor import Detection, redact_text

load_dotenv()
load_dotenv(".env.local", override=False)

app = FastAPI(title="Vaultflow PII Redaction Gateway", version="0.1.0")

_STATIC_DIR = pathlib.Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=_STATIC_DIR), name="static")


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


@app.get("/", include_in_schema=False)
def root() -> FileResponse:
    return FileResponse(_STATIC_DIR / "index.html")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/redact", response_model=RedactResponse)
async def redact(request: RedactRequest) -> RedactResponse:
    result = await redact_text(request.text)
    try:
        await log_redaction(request.text, result)
    except Exception as exc:
        raise HTTPException(status_code=502, detail="redaction log write failed") from exc

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
