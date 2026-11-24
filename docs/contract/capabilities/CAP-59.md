---
id: CAP-59
type: capability
status: ACCEPTED
state_class: DERIVED
title: Review-repair loop budget
depends_on:
- CONTRACT-v5
---

# CAP-59: Review-repair loop budget

Generated from `docs/contract/contract.yaml` (Contract v5, version 5.1), which is the authority; this record exists so that the id resolves (DEC-614).

- **Outcome:** The owner never sees an endless loop: any review→repair, audit→repair, test→fix or verification loop runs at most two rounds, and then the owner decides once, from an escalation package with options.
- **Acceptance:** After two rounds on the same surface the review tool refuses a third and puts one escalation package in chat (each round's outcome, why it is not converging, options: fix differently, narrow, split, defer, delete, continue); READY is computed from the reviewers' verdict blocks; the round count never appears in the output seen by the looping session.
- **Wave:** W1
- **Disposition:** KEPT
- **Covers:** CAP-59.a, CAP-59.b, CAP-59.c
