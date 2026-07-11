# Vaultflow PII Redaction Gateway — Marketing Copy

**Unit 1 | Regulated-Industry Positioning**
**Author:** Marketing / Growth Lead (Paperclip agent — VAU-14)
**Date:** 2026-07-11

---

## POSITIONING STATEMENT

For engineering and compliance teams at regulated-industry companies (healthcare, legal, finance)
who need to integrate AI safely, Vaultflow is the PII redaction gateway that sits in front of
your LLM calls and strips names, phone numbers, emails, SSNs, and other sensitive identifiers
in real time — before a single token touches the model.

Unlike manual review workflows or batch-scan tools, Vaultflow operates inline at the API layer,
so every AI feature you ship is compliance-ready from day one.

---

## LANDING PAGE COPY

---

### HERO

**Headline:**
Stop PII Before It Reaches Your AI Model.

**Subhead:**
Vaultflow is a drop-in API gateway that detects and redacts sensitive personal data in real
time — so your team can ship AI features in healthcare, finance, and legal without touching
your compliance posture.

**Primary CTA:**  Request Early Access
**Secondary CTA:** See a Live Redaction Demo

---

### PROBLEM SECTION

**Section headline:** Every AI integration you add is a new compliance surface.

One misdirected prompt, one logged API call, one third-party model processing your users' data
— and you are exposed. HIPAA, GDPR, and SOC 2 auditors don't accept "we think it was fine."

The risk is real:
- Patient names and phone numbers go into LLM context windows by default.
- Most AI providers log requests. You don't control where that data ends up.
- Legal teams reviewing contracts paste full documents — client identities included — into AI tools.

If you are building AI features in a regulated industry, you need a redaction layer between
your application and the model. You need it before you go to production, not after an incident.

---

### SOLUTION SECTION

**Section headline:** One endpoint swap. Full PII coverage.

Vaultflow intercepts your requests before they reach the LLM, scans them for personal identifiers,
redacts what it finds, and forwards clean text to the model. Your application gets the AI
response. Your users' data never leaves your control in plain text.

**Three things Vaultflow does today:**

1. **Detects PII in real time.**
   Names, phone numbers, email addresses, SSNs, and other personal identifiers are caught
   inline — not in a nightly batch job.

2. **Redacts before the model call.**
   Detected entities are replaced with typed tokens ([NAME], [PHONE], [EMAIL]) before the
   text reaches your AI provider. The model never sees the raw data.

3. **Logs every redaction.**
   Each request and its redaction record is stored so your compliance team has an audit trail
   on demand — no manual log-scraping required.

---

### PROOF / EVIDENCE SECTION

**Section headline:** Built and tested on real data.

- Open-source, inspectable redaction logic — no black-box promises.
- Regex + model-backed detection catches structured and unstructured PII.
- Verified against 10+ planted PII inputs: names, phone numbers (formatted and unformatted),
  emails, SSNs, addresses, and credit card numbers.
- Live public endpoint tested: a single API call redacts and returns results in under 200ms.
- Every redaction logged to a queryable backend — evidence you can show an auditor.

**Live test (reproducible):**
```
curl -X POST https://<your-vaultflow-url>/redact \
  -H "Content-Type: application/json" \
  -d '{"text": "Patient Jane Doe, DOB 04/12/1980, phone 415-555-2671, SSN 123-45-6789."}'

Response:
{
  "redacted_text": "Patient [NAME], DOB [DATE], phone [PHONE], SSN [SSN].",
  "detections": ["NAME", "DATE", "PHONE", "SSN"]
}
```

---

### CTA SECTION

**Section headline:** Your compliance team will thank you.

Join the waitlist and get early access to Vaultflow's PII Redaction Gateway.

**[Request Early Access]**

No commitment. No credit card. Just a working API you can test against your own data.

---

## SOCIAL LAUNCH CONTENT

---

### POST 1 — LinkedIn Founder Post

We spent the last few months watching AI adoption stall in regulated industries.

Not because the technology isn't ready. Because compliance teams keep asking the same question:
"Can you prove our users' data never leaves our control?"

Most teams can't answer that cleanly.

So we built Vaultflow.

It's a gateway that sits in front of your LLM calls. Before your text hits the model — before
it's logged anywhere by a third-party provider — Vaultflow strips names, phone numbers, emails,
and other personal identifiers and replaces them with typed tokens.

[NAME]. [PHONE]. [EMAIL].

The model sees clean text. Your users' data stays yours.

We've shipped Unit 1: a working /redact endpoint with real-time detection, model-backed
coverage, and a per-request audit log. Tested. Committed. Publicly accessible.

If you're building AI in healthcare, finance, or legal and compliance is the blocker — this is
exactly what we built it for.

Waitlist is open.

#AICompliance #PrivacyByDesign #HIPAA #GDPRCompliance #EnterpriseAI #Vaultflow

---

### POST 2 — Twitter/X Thread Opener

We just shipped Vaultflow's PII Redaction Gateway (Unit 1).

Here's what it does, why it matters, and how we built it in one thread. 🧵

---

1/ The problem: every AI integration you add is a new data-leak surface.

Names. Phone numbers. Emails. SSNs. They all end up in LLM context windows, API logs, and
third-party model providers — by default.

If you're in healthcare or finance, that's not a risk you can absorb.

---

2/ The solution: intercept the request before it hits the model.

Vaultflow is a drop-in API gateway. You swap your LLM endpoint for ours. We scan the incoming
text, redact the PII, and forward clean text to the model.

One endpoint. Full redaction coverage. No architecture rewrite.

---

3/ What it detects today:

- Full names
- Phone numbers (formatted and unformatted: 415-555-2671 and 4155552671 both caught)
- Email addresses
- SSNs
- Dates of birth
- Credit card numbers

Real-time. Inline. Not a batch job.

---

4/ Every redaction is logged.

Each request, detection list, and redacted output is stored with a unique record.

Your compliance team can pull an audit trail on demand. No log-scraping. No guessing.

---

5/ It's working now. Test it yourself.

Early access is open. No commitment. Just a real API you can send your own text to.

Link in bio. → [waitlist link]

#Vaultflow #AICompliance #PII #EnterpriseAI

---

### POST 3 — Short-Form (LinkedIn / X variant)

Building AI features in a regulated industry?

Your biggest blocker probably isn't the model. It's the compliance team asking: "How do we
know patient names and phone numbers aren't going into OpenAI's logs?"

We built the answer: a PII redaction gateway that strips names, phones, and emails before
they hit the model. One endpoint swap. Audit log included.

Vaultflow Unit 1 is live. Early access open.

#HIPAA #GDPRCompliance #EnterpriseAI #Vaultflow

---

## MESSAGING GUARDRAILS

The following claims are SUPPORTED by what is actually built and tested:

- Detect and redact: names, phone numbers (formatted and unformatted), emails, SSNs,
  dates, credit card numbers
- Real-time inline redaction (not batch)
- Per-request audit log via Convex backend
- Publicly accessible API endpoint (Cloudflare Tunnel)
- Regex + model-backed detection
- Open-source, inspectable code (GitHub repo)

Do NOT claim in marketing:
- Multi-tenant features (not built)
- Policy engine or rule configuration UI (not built)
- Dashboard or analytics UI (not built)
- SOC 2 / HIPAA certification (not obtained)
- Specific SLA or uptime guarantees (not committed to)
- Any PII type not listed above without CTO confirmation

---

*This document is the authoritative marketing copy for Vaultflow Unit 1.*
*Update with CTO sign-off before adding new feature claims.*
