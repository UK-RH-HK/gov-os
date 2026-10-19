
## 55. Delegated decisions on W1-50's test design packages (register v0.55, appended by the W1 orchestrator on branch `w1/integrate`)

Decided by the orchestrator on 2026-10-04 under DEC-220, on five of the seven packages the W1-50 (`DAEO-xnbx`)
ticket lead returned with its test design batch. For each, the designer's, the lead's and the orchestrator's
recommendations agree, the confidence is medium or higher, the choice is reversible, and it never lets through
something today's containment check flags without the commit's own trailers allowing it. DP-4 (trailers naming a
ticket that is closed or not started) and DP-5 (a worker's call that makes a commit carrying another role's
trailers) are not decided here: they set how strong containment is, and on DP-4 the confidence is low. They go to
the owner.

### DEC-266 — W1-50 DP-1: only a merge in the orchestrator's own call is judged commit by commit
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-50 package DP-1 option (a); confidence high · **Under:** DEC-255, CAP-58.h
- **Decision:** A non-fast-forward merge is judged commit by commit only when it is made in an orchestrator
  session's own call (the main orchestrator's integration merge, or a lead taking `w1/integrate` into its ticket
  branch). A merge in any other caller's call stays flagged, as W1-03 tests it.

### DEC-267 — W1-50 DP-2: own-trailer judging needs both trailers in the final block
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-50 package DP-2 option (a); confidence medium-high · **Under:** DEC-255, DEC-182
- **Decision:** A commit is judged by its own trailers only when its final trailer block carries both `Role` and
  `Task`. A commit with one of the two, or with `Role:` and `Task:` lines only in the message body, is judged
  against the caller, as today.

### DEC-268 — W1-50 DP-3: trailers that name nothing valid allow nothing
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-50 package DP-3 option (a), the fail-closed reading; confidence medium · **Under:** DEC-255
- **Decision:** When a commit's trailers name an unknown role, an unknown ticket, a role that is not the ticket's,
  or several different `Role` or `Task` values, the commit has no allowed paths and every path it changes is a
  finding. A ticket is found by its `id` or its `wbs_id`, as the guard does.

### DEC-269 — W1-50 DP-6: a path the merge commit itself changes is judged by the merge commit's trailers
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-50 package DP-6 option (a); confidence medium-high · **Under:** DEC-255, DEC-156, DEC-253
- **Decision:** A path a merge commit changes beyond what its parents hold (a conflict resolution, a hand edit) is
  judged by the merge commit's own trailers, or against the caller when it has none. An orchestrator's conflict
  resolution under `tests/acceptance/**` is therefore a finding, and elsewhere it is not.

### DEC-270 — W1-50 DP-7: the finding record keeps the caller's role and ticket
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-50 package DP-7 option (a); confidence medium · **Under:** DEC-122, DEC-255
- **Decision:** In a finding for a commit judged by its trailers, `role` and `ticket` hold the caller's values, as
  today; the commit id and its trailers are named in `reason`.

| Version | Date | Change |
|---|---|---|
| 0.55 | 2026-10-04 | Delegated under DEC-220: DEC-266 (W1-50 DP-1: only the orchestrator's own merge is judged commit by commit), DEC-267 (DP-2: both trailers, in the final block), DEC-268 (DP-3: invalid trailers allow nothing), DEC-269 (DP-6: a merge commit's own changes are judged by its trailers), DEC-270 (DP-7: the finding keeps the caller's role and ticket). DP-4 and DP-5 go to the owner. |
