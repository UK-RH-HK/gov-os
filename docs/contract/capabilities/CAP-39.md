---
id: CAP-39
type: capability
status: PROPOSED
state_class: DERIVED
title: Governance health scheduler (G0-G6 tiers)
depends_on:
- CONTRACT-v4
---

# CAP-39: Governance health scheduler (G0-G6 tiers)

Generated from `docs/contract/contract.yaml` (Contract v4, version 4.1), which is the authority; this record exists so that the id resolves (DEC-614).

- **Outcome:** Governance checks run at the right tier automatically, and a stale required index blocks close.
- **Acceptance:** `gov close` fails when a required index is stale; the scheduler runs the configured tiers on schedule and records results.
- **Wave:** W3
- **Disposition:** KEPT
- **Covers:** CAP-39.a, CAP-39.b, CAP-39.c, CAP-39.d
