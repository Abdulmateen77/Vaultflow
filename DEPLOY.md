# Vaultflow — Deployment & Run Guide

## Local runtime

Start Convex logging backend:

```bash
npx convex dev
```

Start FastAPI + frontend:

```bash
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Run tests:

```bash
uv run pytest -q
```

## Public URL via Cloudflare Tunnel

This MVP uses a Cloudflare quick tunnel so the FastAPI app remains the backend while Cloudflare provides the public URL.

```bash
npx cloudflared tunnel --url http://127.0.0.1:8000
```

Cloudflare prints a `https://*.trycloudflare.com` URL. Keep the `cloudflared` process running while demoing.

## Live verification commands

```bash
PUBLIC_URL="https://constraint-exactly-basic-portrait.trycloudflare.com"

curl "$PUBLIC_URL/health"

curl -X POST "$PUBLIC_URL/redact" \
  -H "Content-Type: application/json" \
  -d '{"text":"Jane Doe lives at 221B Baker Street. Email jane@example.com and call (415) 555-2671. SSN 123-45-6789. Card 4111 1111 1111 1111."}'

# Frontend UI
# Open in a browser or phone:
# https://constraint-exactly-basic-portrait.trycloudflare.com/
```

## Buildathon verification evidence

Session date: 2026-07-11

Public Cloudflare URL:

```text
https://constraint-exactly-basic-portrait.trycloudflare.com
```

Verified endpoints:

```text
GET /health -> {"status":"ok"}
GET / -> served minimal paste-and-redact frontend
POST /redact -> redacted regex + Claude-detected PII
```

Sample public `/redact` response:

```json
{
  "redacted_text": "[NAME] lives at [ADDRESS]. Email [EMAIL] and call [PHONE]. SSN [SSN]. Card [CREDIT_CARD].",
  "detections": [
    {"type": "NAME", "source": "llm"},
    {"type": "ADDRESS", "source": "llm"},
    {"type": "EMAIL", "source": "regex"},
    {"type": "PHONE", "source": "regex"},
    {"type": "SSN", "source": "regex"},
    {"type": "CREDIT_CARD", "source": "regex"}
  ]
}
```

10 planted public-URL checks all passed:

```text
PASS email
PASS phone-dash
PASS phone-paren
PASS ssn
PASS visa
PASS mastercard
PASS name
PASS address
PASS name-address-email
PASS multi

SUMMARY: 10/10 passed
```

## Observability proof

Every successful `/redact` call writes a Convex log through `redactions:log`.

Query latest logs:

```bash
CONVEX_URL=$(grep '^CONVEX_URL=' .env.local | cut -d= -f2-)
curl -s "$CONVEX_URL/api/query" \
  -H 'Content-Type: application/json' \
  -d '{"path":"redactions:list","args":{"limit":10},"format":"json"}'
```

Each log stores:

- `inputText`
- `redactedText`
- `detections`
- `createdAt`
