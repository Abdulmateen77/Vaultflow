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
# Serves the Paperclip Team page with CEO, CTO, Sales, Marketing, Finance cards.

curl -X POST https://king-til-aqua-editorials.trycloudflare.com/redact \
  -H 'Content-Type: application/json' \
  -d '{"text":"Cloud check: Jane Doe, jane@example.com, 1234567890."}'
# {"redacted_text":"Cloud check: [NAME], [EMAIL], [PHONE].", ...}
```

### Public Paperclip UI URL

```text
https://presidential-rna-habits-tiles.trycloudflare.com
```

The frontend links to this through:

```text
/paperclip-ui
```

Verified redirect:

```bash
curl -I https://king-til-aqua-editorials.trycloudflare.com/paperclip-ui
# Location: https://presidential-rna-habits-tiles.trycloudflare.com
```

Verified Paperclip public health:

```bash
curl https://presidential-rna-habits-tiles.trycloudflare.com/api/health
# {"status":"ok", ...}
```

Paperclip hostname allowlist was updated with:

```bash
npx paperclipai allowed-hostname presidential-rna-habits-tiles.trycloudflare.com
```

Paperclip was restarted afterward so the hostname allowlist took effect.

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

### Paperclip backend/UI

```bash
npx paperclipai run
```

## Cloudflare quick tunnels

FastAPI/frontend tunnel:

```bash
npx cloudflared tunnel --url http://127.0.0.1:8000
```

Paperclip UI tunnel:

```bash
npx cloudflared tunnel --url http://127.0.0.1:3100
```

If the Paperclip tunnel slug changes, allowlist the new hostname and update `.env`:

```bash
npx paperclipai allowed-hostname <new-slug>.trycloudflare.com
# restart Paperclip
# update PAPERCLIP_PUBLIC_URL=https://<new-slug>.trycloudflare.com
# restart FastAPI
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
npx cloudflared tunnel create vaultflow-paperclip
npx cloudflared tunnel route dns vaultflow-api <api-hostname>
npx cloudflared tunnel route dns vaultflow-paperclip <paperclip-hostname>
```

Then update:

```text
PAPERCLIP_PUBLIC_URL=https://<paperclip-hostname>
```

and restart FastAPI.

## Full verification checklist

```bash
uv run pytest -q

curl https://king-til-aqua-editorials.trycloudflare.com/health
curl https://king-til-aqua-editorials.trycloudflare.com/team
curl -I https://king-til-aqua-editorials.trycloudflare.com/paperclip-ui
curl https://presidential-rna-habits-tiles.trycloudflare.com/api/health

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
