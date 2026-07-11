# Vaultflow — Deployment & Run Guide

## Current live deployment evidence

Date: 2026-07-11

### Public FastAPI + frontend URL

```text
https://king-til-aqua-editorials.trycloudflare.com
```

Live routes verified:

```bash
curl https://king-til-aqua-editorials.trycloudflare.com/health
# {"status":"ok"}

curl https://king-til-aqua-editorials.trycloudflare.com/team
# Serves the Autonomous Agents Team page with CEO, CTO, Sales, Marketing, Finance cards.

curl -I https://king-til-aqua-editorials.trycloudflare.com/paperclip-ui
# Redirects to the Paperclip Dashboard / workforce log backend.

curl -X POST https://king-til-aqua-editorials.trycloudflare.com/redact \
  -H 'Content-Type: application/json' \
  -d '{"text":"Cloud check: Jane Doe, jane@example.com, 1234567890."}'
# {"redacted_text":"Cloud check: [NAME], [EMAIL], [PHONE].", ...}
```

### Convex Cloud deployment

Project:

```text
axleron-ai / vaultflow-3518a
```

Production deployment:

```text
prod:abundant-ferret-758
```

Convex Cloud URL:

```text
https://abundant-ferret-758.convex.cloud
```

Dashboard:

```text
https://dashboard.convex.dev/t/axleron-ai/vaultflow-3518a/abundant-ferret-758
```

Convex tables/functions deployed:

- `redactionLogs`
  - mutation: `redactions:log`
  - query: `redactions:list`
- `agentLogs`
  - mutation: `agentLogs:log`
  - query: `agentLogs:list`

Verified cloud redaction log query:

```bash
curl https://abundant-ferret-758.convex.cloud/api/query \
  -H 'Content-Type: application/json' \
  -d '{"path":"redactions:list","args":{"limit":2},"format":"json"}'
```

Latest verified cloud redaction row included:

```text
inputText:    Cloud check: Jane Doe, jane@example.com, 1234567890.
redactedText: Cloud check: [NAME], [EMAIL], [PHONE].
detections:   NAME(llm), EMAIL(regex), PHONE(regex)
```

Verified cloud Paperclip agent log query:

```bash
curl https://abundant-ferret-758.convex.cloud/api/query \
  -H 'Content-Type: application/json' \
  -d '{"path":"agentLogs:list","args":{"limit":3},"format":"json"}'
```

Latest verified cloud agent row included:

```text
role:     cto
ticketId: 5bf55c03-6f72-412e-8d50-33db47929ca3
output:   CTO tech status report from a real Paperclip ticket
```

## Runtime configuration

Runtime-only secrets/config live in ignored `.env` files and are not committed.

Important runtime values currently set locally:

```text
CONVEX_URL=https://abundant-ferret-758.convex.cloud
CONVEX_DEPLOYMENT=prod:abundant-ferret-758
PAPERCLIP_PUBLIC_URL=https://presidential-rna-habits-tiles.trycloudflare.com
```

The app loads `.env` first and `.env.local` second with `override=False`, so cloud `CONVEX_URL` in `.env` takes precedence over local Convex fallback values in `.env.local`.

## Start services locally

### Convex local fallback

Only needed for local development fallback:

```bash
npx convex dev
```

### FastAPI backend + frontend

```bash
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Agent workforce backend

```bash
npx paperclipai run
```

## Cloudflare quick tunnels

FastAPI/frontend tunnel:

```bash
npx cloudflared tunnel --url http://127.0.0.1:8000
```

## Dedicated-domain blocker

Dedicated Cloudflare hostnames are not configured yet because this machine does not have active Cloudflare browser/cert auth:

```text
wrangler whoami -> not authenticated
~/.cloudflared/cert.pem -> missing
```

To move from quick tunnels to stable dedicated domains, authenticate Cloudflare and create named tunnels:

```bash
npx cloudflared tunnel login
npx cloudflared tunnel create vaultflow-api
npx cloudflared tunnel route dns vaultflow-api <api-hostname>
```

Then restart FastAPI.

## Full verification checklist

```bash
uv run pytest -q

curl https://king-til-aqua-editorials.trycloudflare.com/health
curl https://king-til-aqua-editorials.trycloudflare.com/team

curl -X POST https://king-til-aqua-editorials.trycloudflare.com/redact \
  -H 'Content-Type: application/json' \
  -d '{"text":"My name is John Smith. My phone number is 1234567890 and my email is john@example.com."}'

curl -X POST https://king-til-aqua-editorials.trycloudflare.com/agent/cto

curl https://abundant-ferret-758.convex.cloud/api/query \
  -H 'Content-Type: application/json' \
  -d '{"path":"redactions:list","args":{"limit":2},"format":"json"}'

curl https://abundant-ferret-758.convex.cloud/api/query \
  -H 'Content-Type: application/json' \
  -d '{"path":"agentLogs:list","args":{"limit":3},"format":"json"}'
```
