
## 59. Delegated decisions on W1-49's packages DP-4 and DP-5 (register v0.59, appended by the W1 orchestrator on branch `w1/integrate`)

Decided by the orchestrator on 2026-10-04 under DEC-220, on the two packages the W1-49 (`DAEO-32n6`) test designer
returned in batch 3, after DEC-263 and DEC-264. For each, the lead's recommendation and the orchestrator's agree, the
confidence is medium or higher, and the choice is reversible: W1-29 replaces both hook files. The branch is built
this way. Both read the owner's own words in DEC-264, so each is told to the owner with what it means in practice.
A reviewer finding that could lose written content is not decided here: the prompt says such a finding is fixed,
the lead recommends a residual, and that is the owner's to settle before the ticket is merged.

### DEC-283 — W1-49 DP-4: "older than the block" compares the written part's time with the block's time
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-49 package DP-4 option (a); confidence medium · **Under:** DEC-264
- **Decision:** The SessionStart injection warns when the checkpoint file's time, which the hook sets back to the
  written part's time after it appends, is earlier than the block's `generated:` time. In practice the warning
  shows after every compaction until the session rewrites its checkpoint, and then stops. No tolerance in minutes
  is used (that was DEC-258).

### DEC-284 — W1-49 DP-5: the hook does not invent the pending owner decisions
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-49 package DP-5 option (a); confidence medium-high · **Under:** DEC-264
- **Decision:** A hook is a command and has no source for the pending owner decisions. In the generated block that
  line says `not known to the hook; see the written part of this checkpoint`. The git head, the tickets in
  progress and the worktree list are generated. A file the orchestrator keeps for this, which the hook could read,
  is a matter for W1-29.

| Version | Date | Change |
|---|---|---|
| 0.59 | 2026-10-04 | Delegated under DEC-220: DEC-283 (W1-49 DP-4: the warning compares the written part's time with the block's; it shows after every compaction until the checkpoint is rewritten), DEC-284 (W1-49 DP-5: the block says the pending owner decisions are not known to the hook). |
