# Vaultflow — Deployment & Run Guide

## Local dev

```bash
# Start FastAPI (port 8000)
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Run tests
uv run pytest tests/ -q
```

## Public URL via ngrok

```bash
# Start server first, then in a second terminal:
ngrok http 8000 --log=stdout

# Tunnel URL appears in ngrok console and at:
curl http://127.0.0.1:4040/api/tunnels
```

## Verify live endpoints

```bash
PUBLIC_URL="<your-ngrok-url>"

# Health check
curl "$PUBLIC_URL/health"
# => {"status":"ok"}

# PII redaction (10 planted items)
curl -X POST "$PUBLIC_URL/redact" \
  -H "Content-Type: application/json" \
  -d '{"text":"SSN 123-45-6789, email john@gmail.com, phone (555) 867-5309, card 4111 1111 1111 1111, SSN 987-65-4321, email jane@company.org, phone 800-555-1234, card 5500-0000-0000-0004, user John Smith at 123 Main St."}'

# Frontend UI
open "$PUBLIC_URL/"
```

## Convex logging

Redaction logs are written to Convex local backend (.convex/local/).
Every /redact call stores: original_text, redacted_text, detections, timestamp.

## Buildathon verification URL (session on 2026-07-11)

Public URL: https://ergonomic-tinwork-stunned.ngrok-free.dev
/health: {"status":"ok"}
/redact: 8 PII items detected and redacted across 2 identities
