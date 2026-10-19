
## 64. Delegated decisions on W1-09 after its review (register v0.64, appended by the W1 orchestrator on branch `w1/integrate`)

Decided by the orchestrator on 2026-10-04 under DEC-220, on what the W1-09 (`DAEO-topz`) ticket lead returned with
its DONE. Both make the READY rule stricter (they fail closed), the recommendations agree, the confidence is medium
or higher, and both are reversible. W1-09's DP-4 and DP-6 remain with the owner.

### DEC-300 — W1-09: the acceptance tests folder must lie below `tests/acceptance/`
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-09 reviewer finding H2 and its repair; confidence high · **Narrows:** DEC-293 · **Under:** DEC-069, CAP-31.c
- **Decision:** The folder that makes a ticket READY (DEC-293) counts only if, with links resolved, it is a
  directory inside the project and strictly below `tests/acceptance/`. An absolute path, `.`, `..`, `src`, `.git`,
  `tests/acceptance/` itself or a link leading outside the project does not count. A path naming another ticket's
  folder, and an empty folder, still count; both are residuals.

### DEC-301 — W1-09 DP-10: while the claims folder cannot be inspected, every open ticket counts as claimed
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-09 package DP-10 option (a); confidence medium · **Under:** DEC-292, CAP-23.a
- **Decision:** When `.tickets/.claims` cannot be read, every open ticket is `CLAIMED` and the ready queue is empty
  until the folder is repaired. A claim that cannot be inspected counts as a claim.

| Version | Date | Change |
|---|---|---|
| 0.64 | 2026-10-04 | Delegated under DEC-220: DEC-300 (W1-09: the acceptance tests folder must lie strictly below `tests/acceptance/`, inside the project; narrows DEC-293), DEC-301 (W1-09 DP-10: an unreadable claims folder makes every open ticket claimed). |
