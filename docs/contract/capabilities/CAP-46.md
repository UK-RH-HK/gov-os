---
id: CAP-46
type: capability
status: PROPOSED
state_class: DERIVED
title: Cross-machine sync via git
depends_on:
- CONTRACT-v4
---

# CAP-46: Cross-machine sync via git

Generated from `docs/contract/contract.yaml` (Contract v4, version 4.1), which is the authority; this record exists so that the id resolves (DEC-614).

- **Outcome:** The owner can move to another machine with git alone.
- **Acceptance:** A fresh clone followed by `gov doctor` and `gov rebuild` gives a working environment whose derived digest equals the source machine's.
- **Wave:** W1
- **Disposition:** KEPT
- **Covers:** CAP-46.a
