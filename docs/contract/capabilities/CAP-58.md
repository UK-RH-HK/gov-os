---
id: CAP-58
type: capability
status: PROPOSED
state_class: DERIVED
title: Path guards as default-deny allow-lists
depends_on:
- CONTRACT-v4
---

# CAP-58: Path guards as default-deny allow-lists

Generated from `docs/contract/contract.yaml` (Contract v4, version 4.1), which is the authority; this record exists so that the id resolves (DEC-614).

- **Outcome:** An agent can write only inside its task's declared paths; everything else is denied. The orchestrator is the one exception: it may write anywhere in the repository except `tests/acceptance/**`.
- **Acceptance:** An Edit, Write or Bash write outside the ticket's `allowed_paths` is refused by the guard, and a Bash form the guard cannot parse is caught by the post-command containment check; in a launched worker session a Bash write outside the repository is stopped by the OS sandbox, and a file-tool write outside it by the permission rules and the guard.
- **Wave:** W1
- **Disposition:** KEPT
- **Covers:** CAP-58.a, CAP-58.b, CAP-58.c, CAP-58.d, CAP-58.e, CAP-58.f, CAP-58.g, CAP-58.h
