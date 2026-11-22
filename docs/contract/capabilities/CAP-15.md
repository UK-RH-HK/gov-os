---
id: CAP-15
type: capability
status: ACCEPTED
state_class: DERIVED
title: The brief carries the ticket's retrieval
depends_on:
- CONTRACT-v5
---

# CAP-15: The brief carries the ticket's retrieval

Generated from `docs/contract/contract.yaml` (Contract v5, version 5.1), which is the authority; this record exists so that the id resolves (DEC-614).

- **Outcome:** An agent starts every task with a brief that carries the ticket's whole retrieval bundle, uncut, with its mandatory inputs by id and hash and the authority record first.
- **Acceptance:** `gov brief <role> <ticket>` writes a brief that holds the ticket's whole retrieval bundle, uncut, every mandatory input by id and sha256 and no unfilled placeholder (no `{QUESTION}`), refuses when a mandatory input is missing or the ticket is not READY, and the memory-use log has a line for it; `gov context` is retired and no packet ceiling exists.
- **Wave:** W2
- **Disposition:** KEPT
- **Covers:** CAP-15.a, CAP-15.b, CAP-15.c, CAP-15.d, CAP-15.e, CAP-15.f, CAP-15.g
