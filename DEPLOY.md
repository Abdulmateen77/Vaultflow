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

Convex logs every /redact call to its `redactions` table (inputText, redactedText, detections, timestamp).

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

Download cloudflared (Windows AMD64):

```bash
curl -L -o cloudflared.exe \
  "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe"
```

Start the tunnel (run from the directory containing cloudflared.exe):

```bash
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

## Verified session evidence (2026-07-11 — session 2)

Public URL: https://pine-colin-dept-cord.trycloudflare.com

All three services confirmed running:
- Convex backend: port 3210 (local SQLite, 30+ redaction events logged)
- FastAPI: port 8000 (uvicorn)
- cloudflared tunnel: PID 4567 — cmd: `cloudflared.exe tunnel --url http://127.0.0.1:8000 --no-autoupdate`

/health response:
```json
{"status":"ok"}
```

/redact response (10 PII items detected and redacted):
```json
{
  "redacted_text": "SSN [SSN], email [EMAIL], phone [PHONE], card [CREDIT_CARD], SSN [SSN], email [EMAIL], phone [PHONE], card [CREDIT_CARD], user [NAME] at [ADDRESS].",
  "detections": [
    {"type":"SSN","start":4,"end":15,"source":"regex"},
    {"type":"EMAIL","start":23,"end":37,"source":"regex"},
    {"type":"PHONE","start":45,"end":59,"source":"regex"},
    {"type":"CREDIT_CARD","start":66,"end":85,"source":"regex"},
    {"type":"SSN","start":91,"end":102,"source":"regex"},
    {"type":"EMAIL","start":110,"end":126,"source":"regex"},
    {"type":"PHONE","start":134,"end":146,"source":"regex"},
    {"type":"CREDIT_CARD","start":153,"end":172,"source":"regex"},
    {"type":"NAME","start":179,"end":189,"source":"llm"},
    {"type":"ADDRESS","start":193,"end":204,"source":"llm"}
  ]
}
```

Detection summary: SSN×2, EMAIL×2, PHONE×2, CREDIT_CARD×2, NAME×1, ADDRESS×1 = 10 total

Frontend: HTML served at / (paste-and-redact UI) — confirmed via HTTP 200 + HTML body.

Convex backend: 30+ redaction events logged and queryable at http://127.0.0.1:3210/api/query.
