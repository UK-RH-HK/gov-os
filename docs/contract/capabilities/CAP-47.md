---
id: CAP-47
type: capability
status: PROPOSED
state_class: DERIVED
title: Independent adoption/audit roles and fresh-session independence
depends_on:
- CONTRACT-v4
---

# CAP-47: Independent adoption/audit roles and fresh-session independence

Generated from `docs/contract/contract.yaml` (Contract v4, version 4.1), which is the authority; this record exists so that the id resolves (DEC-614).

- **Outcome:** The owner gets independent verification from fresh sessions that did not build what they check.
- **Acceptance:** A fresh verifier session with only the bounded context pack runs held-out tests and reports; its transcript contains no builder chat.
- **Wave:** W3
- **Disposition:** KEPT
- **Covers:** CAP-47.a, CAP-47.b, CAP-47.c, CAP-47.d
