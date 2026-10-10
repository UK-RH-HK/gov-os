---
id: CAP-01
type: capability
status: PROPOSED
state_class: DERIVED
title: Authority precedence and hard invariants
depends_on:
- CONTRACT-v4
---

# CAP-01: Authority precedence and hard invariants

Generated from `docs/contract/contract.yaml` (Contract v4, version 4.1), which is the authority; this record exists so that the id resolves (DEC-614).

- **Outcome:** An agent can tell which of two conflicting records governs, by a deterministic precedence (Charter → Contract → ADRs → specifications → tasks → retrieval → inference) and by supersession status.
- **Acceptance:** Given two conflicting records at different precedence levels, `gov context` puts only the higher one in the authority block and marks the lower one superseded.
- **Wave:** W1
- **Disposition:** KEPT
- **Covers:** CAP-01.a, CAP-01.b, CAP-01.c, CAP-01.d
