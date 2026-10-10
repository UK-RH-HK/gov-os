---
id: CAP-43
type: capability
status: PROPOSED
state_class: DERIVED
title: Canonical OS repo separation and immutable releases
depends_on:
- CONTRACT-v4
---

# CAP-43: Canonical OS repo separation and immutable releases

Generated from `docs/contract/contract.yaml` (Contract v4, version 4.1), which is the authority; this record exists so that the id resolves (DEC-614).

- **Outcome:** The owner can tell exactly which Gov OS version a repository runs; releases never change once tagged.
- **Acceptance:** `framework.lock` records the template tag, commit and file-hash manifest, and `gov doctor` fails when any of them disagrees with the installed kernel.
- **Wave:** W1
- **Disposition:** KEPT
- **Covers:** CAP-43.a, CAP-43.b, CAP-43.c
