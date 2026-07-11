# Vaultflow

PII Redaction Gateway MVP for the Hermes Buildathon AI as Agency track.

The app exposes one core feature: detect and redact sensitive data from text before it reaches an AI model.

## Current scope

- FastAPI backend
- `/redact` endpoint
- Regex PII detection for email, phone, SSN, and credit cards
- Claude API detector for names and physical addresses
- Convex logging and Cloudflare public URL are next in the build order

## Run locally

```bash
uv sync --dev
cp .env.example .env
# Fill ANTHROPIC_API_KEY in .env for Claude name/address detection
uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

## Test

```bash
uv run pytest -q
```

## API

```bash
curl -s http://127.0.0.1:8000/redact \
  -H 'Content-Type: application/json' \
  -d '{"text":"Jane Doe lives at 221B Baker Street. Email jane@example.com."}'
```
