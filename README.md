# Vaultflow

PII Redaction Gateway MVP for the Hermes Buildathon AI as Agency track.

The app exposes one core feature: detect and redact sensitive data from text before it reaches an AI model.

## Current scope

- FastAPI backend
- `/redact` endpoint
- Regex PII detection for email, phone, SSN, and credit cards
- Claude API detector for names and physical addresses
- Convex logging for every successful redaction request
- Cloudflare public URL is next in the build order

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

## Convex observability

Convex stores every successful redaction request and result in `redactionLogs`.

```bash
npm install
npx convex dev
```

Convex writes `CONVEX_URL` to `.env.local`; the FastAPI app loads `.env.local` as a fallback.

Query the latest logs:

```bash
CONVEX_URL=$(grep '^CONVEX_URL=' .env.local | cut -d= -f2-)
curl -s "$CONVEX_URL/api/query" \
  -H 'Content-Type: application/json' \
  -d '{"path":"redactions:list","args":{"limit":10},"format":"json"}'
```

## API

```bash
curl -s http://127.0.0.1:8000/redact \
  -H 'Content-Type: application/json' \
  -d '{"text":"Jane Doe lives at 221B Baker Street. Email jane@example.com."}'
```
