# Vaultflow — Deployment & Run Guide

## Prerequisites

- Python 3.11+ with `uv` installed
- Node.js 18+ (for Convex local backend)
- `cloudflared` binary (Windows AMD64) — see step 3

---

## 1. Start Convex local backend

```bash
# In the repo root — starts Convex on http://127.0.0.1:3210
npx convex dev
```

CONVEX_URL is already set in `.env.local`:

```
CONVEX_URL=http://127.0.0.1:3210
```

Convex logs every /redact call to its `redactionLogs` table via `redactions:log` (inputText, redactedText, detections, createdAt).

---

## 2. Start FastAPI

```bash
# From repo root
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000

# Verify locally
curl http://127.0.0.1:8000/health
# => {"status":"ok"}
```

---

## 3. Expose a public URL via Cloudflare Tunnel (trycloudflare.com)

No Cloudflare account required — trycloudflare.com issues anonymous quick tunnels.

Use the npm-distributed Cloudflare Tunnel binary (used for this verification):

```bash
npx cloudflared tunnel --url http://127.0.0.1:8000
```

Alternative Windows AMD64 download:

```bash
curl -L -o cloudflared.exe \
  "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe"
./cloudflared.exe tunnel --url http://127.0.0.1:8000 --no-autoupdate
```

cloudflared prints the public URL in its startup log, e.g.:

```
INF | Your quick Tunnel has been created! Visit it at:
INF | https://<random-slug>.trycloudflare.com
```

---

## 4. Verify live endpoints from public URL

```bash
PUBLIC_URL="https://<your-slug>.trycloudflare.com"

# Health check
curl "$PUBLIC_URL/health"
# => {"status":"ok"}

# PII redaction — 10 planted items across 2 identities
curl -X POST "$PUBLIC_URL/redact" \
  -H "Content-Type: application/json" \
  -d '{"text":"SSN 123-45-6789, email john@gmail.com, phone (555) 867-5309, card 4111 1111 1111 1111, SSN 987-65-4321, email jane@company.org, phone 800-555-1234, card 5500-0000-0000-0004, user John Smith at 123 Main St."}'

# Frontend UI
open "$PUBLIC_URL/"
```

---

## 5. Convex log verification

```bash
# List stored redaction events (Convex local backend must be running)
curl -s http://127.0.0.1:3210/api/query \
  -H "Content-Type: application/json" \
  -d '{"path":"redactions:list","args":{},"format":"json"}' | python -m json.tool
```

---

## Verified session evidence (2026-07-11)

Public Cloudflare URL:

```text
https://king-til-aqua-editorials.trycloudflare.com
```

Verified responses:

```text
GET /health -> {"status":"ok"}
GET / -> served minimal paste-and-redact frontend
POST /redact -> redacted regex + Claude-detected PII
```

Sample public `/redact` response:

```json
{
  "redacted_text": "[NAME] lives at [ADDRESS]. Email [EMAIL]. SSN [SSN].",
  "detections": [
    {"type": "NAME", "source": "llm"},
    {"type": "ADDRESS", "source": "llm"},
    {"type": "EMAIL", "source": "regex"},
    {"type": "SSN", "source": "regex"}
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

Frontend: HTML served at `/` (paste-and-redact UI).

Convex backend: redaction events are logged through `redactions:log` and queryable with `redactions:list`.
