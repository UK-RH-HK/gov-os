---
id: CAP-21
type: capability
status: PROPOSED
state_class: DERIVED
title: Owner-only approval facts (lite of L0-L5 authority levels)
depends_on:
- CONTRACT-v4
---

# CAP-21: Owner-only approval facts (lite of L0-L5 authority levels)

Generated from `docs/contract/contract.yaml` (Contract v4, version 4.1), which is the authority; this record exists so that the id resolves (DEC-614).

- **Outcome:** The owner can trust that no agent makes a decision ACTIVE on its own.
- **Acceptance:** `gov check` (and CI) fails a change that sets a decision ACTIVE unless the change carries an owner approval fact from git.
- **Wave:** W1
- **Disposition:** LITE
- **Covers:** CAP-21.a, CAP-21.b
