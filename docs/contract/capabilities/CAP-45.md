---
id: CAP-45
type: capability
status: PROPOSED
state_class: DERIVED
title: gov update lifecycle
depends_on:
- CONTRACT-v5
---

# CAP-45: gov update lifecycle

Generated from `docs/contract/contract.yaml` (Contract v5, version 5.0), which is the authority; this record exists so that the id resolves (DEC-614).

- **Outcome:** The owner can update the Gov OS in a repository without losing his overlay or his own edits, and without re-adopting.
- **Acceptance:** `gov update --check` reports the version change and migrations; `gov update` installs the pinned, hash-verified release and applies it with a three-way merge that keeps the owner's own edits and the overlay files, and `gov doctor` is green, with no re-adopt.
- **Wave:** W2
- **Disposition:** KEPT
- **Covers:** CAP-45.a, CAP-45.b
