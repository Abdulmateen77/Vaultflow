from __future__ import annotations

import os
import pathlib

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, field_validator
from dotenv import load_dotenv

from app.observability import log_redaction
from app.paperclip_agents import AgentRunResult, TASK_PROMPTS, UnknownAgentRoleError, run_agent_role
from app.redactor import Detection, redact_text
from app import waitlist

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


class AgentResponse(BaseModel):
    role: str
    ticket_id: str
    ticket_identifier: str
    output: str


class EarlyAccessRequest(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    email: str = Field(min_length=3, max_length=300)
    company: str = Field(min_length=1, max_length=200)
    use_case: str = Field(default="General", max_length=100)

    @field_validator("email")
    @classmethod
    def email_must_contain_at(cls, value: str) -> str:
        if "@" not in value or "." not in value.split("@")[-1]:
            raise ValueError("must be a valid work email address")
        return value.lower().strip()


class EarlyAccessResponse(BaseModel):
    message: str
    already_registered: bool = False


@app.get("/", include_in_schema=False)
def root() -> FileResponse:
    return FileResponse(_STATIC_DIR / "index.html")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/team", include_in_schema=False)
def team() -> FileResponse:
    return FileResponse(_STATIC_DIR / "team.html")


@app.get("/early-access", include_in_schema=False)
def early_access_page() -> FileResponse:
    return FileResponse(_STATIC_DIR / "early-access.html")


@app.get("/paperclip-ui", include_in_schema=False)
def paperclip_ui() -> RedirectResponse:
    target = os.getenv("PAPERCLIP_PUBLIC_URL", "http://127.0.0.1:3100").rstrip("/")
    return RedirectResponse(target)


@app.post("/agent/{role}", response_model=AgentResponse)
async def run_agent(role: str) -> AgentResponse:
    normalized_role = role.lower().strip()
    if normalized_role not in TASK_PROMPTS:
        raise HTTPException(status_code=404, detail=f"Unknown agent role: {role}")

    try:
        result = await run_agent_role(normalized_role)
    except UnknownAgentRoleError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except TimeoutError as exc:
        raise HTTPException(status_code=504, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Agent run failed: {exc}") from exc

    return _agent_response(result)


@app.post("/waitlist", response_model=EarlyAccessResponse)
async def join_waitlist(request: EarlyAccessRequest) -> EarlyAccessResponse:
    """Store an early-access lead and return a confirmation message."""
    already = waitlist.lead_exists(request.email)
    if not already:
        waitlist.insert_lead(
            name=request.name,
            email=request.email,
            company=request.company,
            use_case=request.use_case,
        )
    return EarlyAccessResponse(
        message="You're on the list. Expect a note from us within 24 hours.",
        already_registered=already,
    )


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


def _agent_response(result: AgentRunResult) -> AgentResponse:
    return AgentResponse(
        role=result.role,
        ticket_id=result.ticket_id,
        ticket_identifier=result.ticket_identifier,
        output=result.output,
    )


def _detection_response(detection: Detection) -> DetectionResponse:
    return DetectionResponse(
        type=detection.type,
        start=detection.start,
        end=detection.end,
        source=detection.source,
    )
