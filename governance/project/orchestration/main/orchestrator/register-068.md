
## 68. Delegated decision on W1-50's package DP-10 (register v0.68, appended by the W1 orchestrator on branch `w1/integrate`)

Decided by the orchestrator on 2026-10-04 under DEC-220 and the stricter-only rule of the orchestrator prompt v4.1
(section 6), on one of the three packages W1-50's second test design batch returned. The designer's, the lead's and
the orchestrator's recommendations agree, the confidence is medium, the choice is reversible, and it only makes the
containment check report more. DP-8 (how the check finds a ticket's close commit) and DP-9 (an orchestrator commit
that names a closed or never-started ticket) interpret the owner's DEC-318 and go to the owner.

### DEC-327 — W1-50 DP-10: a worker's call is judged commit by commit against the caller
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, stricter-only, 2026-10-04) · **Basis:** W1-50 package DP-10 option (a), the fail-closed reading; confidence medium · **Under:** DEC-319, DEC-255, CAP-58.h
- **Decision:** In a worker's call, a forward HEAD move is judged commit by commit against the caller, not by its
  two ends. A worker's commit outside its paths is a finding even when a later commit of the same call undoes it.

| Version | Date | Change |
|---|---|---|
| 0.68 | 2026-10-04 | Delegated under DEC-220 (stricter-only): DEC-327 (W1-50 DP-10: a worker's call is judged commit by commit against the caller). DP-8 and DP-9 go to the owner. |
