---
id: CAP-15
type: capability
status: PROPOSED
state_class: DERIVED
title: Context packet compilation
depends_on:
- CONTRACT-v4
---

# CAP-15: Context packet compilation

Generated from `docs/contract/contract.yaml` (Contract v4, version 4.1), which is the authority; this record exists so that the id resolves (DEC-614).

- **Outcome:** An agent starts every task with a compiled context packet: mandatory inputs by id and hash, an authority block first, under a ceiling.
- **Acceptance:** `gov context <ticket>` writes a packet that contains every mandatory input by id and sha256, stays under the configured ceiling (default ~6k tokens), carries its own hash, and is delivered as a file path plus a summary of at most ~2.5k tokens; when the ticket's evidence exceeds the ceiling, the packet carries synthesis notes that cite source ids and sha256, pass the validator, disclose unresolved evidence and are invalidated when a cited source changes.
- **Wave:** W1
- **Disposition:** KEPT
- **Covers:** CAP-15.a, CAP-15.b, CAP-15.c, CAP-15.d, CAP-15.e, CAP-15.f, CAP-15.g
