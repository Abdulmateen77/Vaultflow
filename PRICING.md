# Vaultflow PII Redaction Gateway — Pricing Tiers

**Version:** 1.0 (Proposal — Pending Board Approval)
**Author:** CEO Agent (VAU-19)
**Date:** 2026-07-11
**Status:** DRAFT — Do not publish until board-approved

---

## Executive Summary

Proposed 4-tier pricing model optimized for:
1. Low-friction developer acquisition (freemium)
2. Startup / team conversions that generate near-term MRR
3. Enterprise compliance deals with high ACV and sticky retention
4. Path to $1K MRR within 60 days via 3-4 Pro tier conversions

---

## Competitive Benchmarks

| Competitor         | Closest Tier       | Price         | Calls/Month | Notes                            |
|--------------------|--------------------|---------------|-------------|----------------------------------|
| Protecto.ai        | Starter            | $250/mo       | 5,000       | Direct PII redaction API comp    |
| Protecto.ai        | Growth             | $500/mo       | 12,000      | Direct PII redaction API comp    |
| CaseGuard          | Doc Suite          | $279/user/mo  | Unlimited   | Desktop-only, not API-first      |
| CaseGuard          | Ultimate Suite     | $379/user/mo  | Unlimited   | Desktop-only, not API-first      |
| Prediction Guard   | Enterprise         | Custom        | N/A         | AI governance platform, sales-led|
| Strac              | Enterprise         | Custom        | N/A         | DLP suite, not API-first PII     |

Key insight: Protecto is the closest direct analog. We can undercut them significantly on the
entry and mid tiers while offering more call volume — a deliberate land-and-expand wedge.

---

## Proposed Pricing Table

### Tier 1 — Dev (Free)

**Price:** $0 / month  
**Positioning:** Zero-friction entry for developers and compliance evaluators  
**Limits:** 500 requests/month | 10 req/min rate limit

**Included:**
- All core PII detection: name, email, phone, SSN, DOB, credit card numbers
- Basic audit log (last 30 days, read-only via API)
- 1 API key
- Community support (Discord)
- No credit card required

**Does NOT include:**
- Audit log export
- SLA commitments
- Data Processing Agreement (DPA)

**Why free matters:** Every paid SaaS tool in this category (Protecto, CaseGuard) requires a
sales call or credit card for trials. Offering a real working free tier with no friction lets
developers evaluate against actual data and reduces the time-to-value to under 5 minutes.

---

### Tier 2 — Builder ($49/month)

**Price:** $49 / month (annual: $39/month billed yearly)  
**Positioning:** Indie developers, small startups, early-stage products  
**Limits:** 15,000 requests/month | 60 req/min rate limit

**Included:**
- Everything in Dev, plus:
- Audit log access + export (CSV / JSON)
- 2 API keys
- Email support (48-hour response SLA)
- Monthly usage dashboard (basic)

**Why $49:** Sets a low commitment threshold for first conversion. Protecto's cheapest paid
tier is $250/mo for fewer calls. We offer 3x the volume at 20% of the price. Goal: minimize
friction to first dollar and build conversion data.

---

### Tier 3 — Pro ($299/month)

**Price:** $299 / month (annual: $249/month billed yearly)  
**Positioning:** Compliance-conscious startups, mid-size teams, CTOs who need an audit trail  
**Limits:** 100,000 requests/month | 300 req/min rate limit

**Included:**
- Everything in Builder, plus:
- Full audit log export + 90-day retention
- Up to 10 API keys / team members
- Webhook notifications on detection events
- Data Processing Agreement (DPA) — GDPR/HIPAA-aligned usage terms
- Priority email support (8-hour response SLA)
- Monthly usage report (detailed, exportable)

**Why $299:** This is the primary MRR driver tier. 3-4 Pro customers reaches the $897-$1,196
MRR target. Priced below Protecto's Starter ($250) at 20x the call volume — compelling value
for any startup that has passed the "let's evaluate" stage and is integrating into production.

**Note to board:** DPA is a standard document; CTO can produce a template in <1 day.
Webhook notifications and 90-day log retention need a 1-week sprint estimate before we commit.
Flag before publishing.

---

### Tier 4 — Enterprise (Custom)

**Price:** Starting at $1,500 / month (custom quote)  
**Positioning:** Healthcare orgs, financial institutions, legal platforms with compliance mandates  
**Limits:** 1M+ requests/month (negotiated) | Custom rate limits

**Included:**
- Everything in Pro, plus:
- Business Associate Agreement (BAA) for HIPAA-covered entities
- 99.9% uptime SLA with credits
- 1-year audit log retention
- SSO / SAML integration
- Dedicated account manager
- Custom entity types and redaction rules
- Quarterly compliance review calls
- On-premises / VPC deployment option (roadmap — not yet available)

**Why custom:** Enterprise compliance buyers have heterogeneous needs. BAA, SLA, and SSO are
non-negotiable requirements in healthcare and finance. Custom pricing lets us capture ACV
proportional to volume and risk. A single Enterprise deal at $1,500-3,000/mo more than covers
the $1K MRR target alone.

**IMPORTANT — Board approval needed on Enterprise commitments:**
The following Enterprise features are NOT yet built and require CTO confirmation before we can
promise them in a sales motion:
- BAA template (1-2 day legal/template task)
- 99.9% SLA (requires infrastructure commitments + monitoring — ~2 week sprint)
- SSO/SAML (multi-week engineering task)
- Custom entity types (roadmap, not committed)
- On-premises deployment (roadmap, not committed)

Recommendation: Launch Enterprise tier as "contact sales" with no public spec sheet until
CTO confirms which features ship in what timeframe.

---

## Revenue Model: Path to $1K MRR in 60 Days

| Scenario          | Mix                               | MRR      |
|-------------------|-----------------------------------|----------|
| Conservative      | 3 × Pro ($299)                    | $897     |
| Target            | 4 × Pro ($299)                    | $1,196   |
| Enterprise-led    | 1 × Enterprise ($1,500)           | $1,500   |
| Mixed             | 2 × Pro + 5 × Builder ($49)       | $843     |

**Recommended path:**
Focus sales energy on converting 3-4 Pro tier customers from the early-access waitlist within
60 days. The free Dev tier seeds the funnel; the $49 Builder tier captures early converts; the
$299 Pro tier is the MRR engine.

---

## Differentiation Rationale

| Feature             | Dev (Free) | Builder ($49) | Pro ($299) | Enterprise (Custom) |
|---------------------|:----------:|:-------------:|:----------:|:-------------------:|
| PII detection        | All types  | All types     | All types  | All types + custom  |
| Requests/month       | 500        | 15,000        | 100,000    | 1M+                 |
| Audit log            | Basic      | Export        | Export+90d | 1-year retention    |
| API keys             | 1          | 2             | 10         | Unlimited           |
| DPA                  | No         | No            | Yes        | Yes                 |
| BAA (HIPAA)          | No         | No            | No         | Yes                 |
| SLA                  | None       | None          | Email 8h   | 99.9% uptime        |
| Support              | Community  | Email 48h     | Priority   | Dedicated manager   |
| SSO/SAML             | No         | No            | No         | Yes                 |

---

## Pricing Guardrails (aligned with MARKETING.md)

The following are NOT commitments until board-approved and CTO-confirmed:
- SOC 2 / HIPAA certification (not obtained — do not imply certification in tier descriptions)
- Specific uptime SLAs on any tier below Enterprise
- Dashboard/analytics UI on Builder tier (not yet built; list as "basic" until confirmed)
- Custom entity types (roadmap — Pro tier flag only)
- On-premises deployment (roadmap — Enterprise note only)

---

## Recommended Next Steps (Post Board Approval)

1. CTO to confirm delivery timeline for: webhook notifications, 90-day log retention, DPA template
2. Legal to draft BAA template for Enterprise
3. Marketing to update landing page with approved pricing table
4. Sales to configure Stripe (or equivalent) for Dev/Builder/Pro self-serve checkout
5. CEO to post pricing page link in early-access waitlist outreach email

---

*This document requires board (user) approval before any public-facing pricing is published.*
*Supersedes any pricing signals in MARKETING.md (which had none as of VAU-14).*
