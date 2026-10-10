---
id: CAP-59
type: capability
status: PROPOSED
state_class: DERIVED
title: Review-repair loop budget
depends_on:
- CONTRACT-v4
---

# CAP-59: Review-repair loop budget

Generated from `docs/contract/contract.yaml` (Contract v4, version 4.1), which is the authority; this record exists so that the id resolves (DEC-614).

- **Outcome:** The owner never sees an endless loop: any review→repair, audit→repair, test→fix or verification loop continues until it converges, or until three consecutive iterations fail to converge, and then the owner decides from an escalation package.
- **Acceptance:** After three consecutive non-converging iterations on the same surface, `gov close` stops the loop and puts an escalation package in chat (each iteration's outcome, why it is not converging, options: fix differently, narrow, split, defer, delete, continue); the iteration count never appears in the output seen by the looping session.
- **Wave:** W1
- **Disposition:** KEPT
- **Covers:** CAP-59.a, CAP-59.b, CAP-59.c
