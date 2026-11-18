---
id: CAP-58
type: capability
status: PROPOSED
state_class: DERIVED
title: Containment judged at the landing
depends_on:
- CONTRACT-v5
---

# CAP-58: Containment judged at the landing

Generated from `docs/contract/contract.yaml` (Contract v5, version 5.0), which is the authority; this record exists so that the id resolves (DEC-614).

- **Outcome:** An agent works inside its task's declared paths. A change outside them is a notice in the landing's record; only a change that breaks test authorship is refused (MR-3).
- **Acceptance:** At the landing, each commit's paths are judged against the allowed paths of its `Role` and `Task` trailers: a path outside them is a notice in the land record and never a refusal; a commit that changes `tests/acceptance/` without `Role: independent-test-designer` (or the owner's `Role: owner`) is refused, naming the commit. Nothing is refused at write time.
- **Wave:** W1
- **Disposition:** KEPT
- **Covers:** CAP-58.a, CAP-58.b, CAP-58.c, CAP-58.d, CAP-58.e, CAP-58.f, CAP-58.g, CAP-58.h
