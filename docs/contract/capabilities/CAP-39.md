---
id: CAP-39
type: capability
status: ACCEPTED
state_class: DERIVED
title: Governance health tiers and the landing's checks (G1-G5)
depends_on:
- CONTRACT-v5
---

# CAP-39: Governance health tiers and the landing's checks (G1-G5)

Generated from `docs/contract/contract.yaml` (Contract v5, version 5.0), which is the authority; this record exists so that the id resolves (DEC-614).

- **Outcome:** Governance checks run at the right tier automatically, and a stale required index fails the landing.
- **Acceptance:** The landing fails when a required index is stale, and records each check it ran with its tier and its RED, YELLOW or GREEN result; `gov ci` runs the CI tiers.
- **Wave:** W2
- **Disposition:** KEPT
- **Covers:** CAP-39.a, CAP-39.b, CAP-39.c, CAP-39.d, CAP-39.e
