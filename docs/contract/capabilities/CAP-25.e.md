---
id: CAP-25.e
type: capability
status: PROPOSED
state_class: DERIVED
title: 'The research role may install only inside its own experiment folder (a venv or local prefix within its ticket''s `allowed_paths`); a system-wide install is denied to it; the sandbox''s write fence enforces this: the sandbox stops a write outside the repository, and the generated `Edit` deny rules of `CAP-61.c` stop one to a path that existed at launch elsewhere inside it; a path created later is covered by the guard''s per-ticket allow-list. It is the one exception to the denial in CAP-25.b'
depends_on:
- CAP-25
---

# CAP-25.e: The research role may install only inside its own experiment folder (a venv or local prefix within its ticket's `allowed_paths`); a system-wide install is denied to it; the sandbox's write fence enforces this: the sandbox stops a write outside the repository, and the generated `Edit` deny rules of `CAP-61.c` stop one to a path that existed at launch elsewhere inside it; a path created later is covered by the guard's per-ticket allow-list. It is the one exception to the denial in CAP-25.b

A covers item of CAP-25 (Tool registry and capability memory (lite)). Generated from `docs/contract/contract.yaml` (Contract v4, version 4.1), which is the authority (DEC-614).

- **Item:** The research role may install only inside its own experiment folder (a venv or local prefix within its ticket's `allowed_paths`); a system-wide install is denied to it; the sandbox's write fence enforces this: the sandbox stops a write outside the repository, and the generated `Edit` deny rules of `CAP-61.c` stop one to a path that existed at launch elsewhere inside it; a path created later is covered by the guard's per-ticket allow-list. It is the one exception to the denial in CAP-25.b
- **Wave:** W1
