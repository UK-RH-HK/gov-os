
## 52. Delegated decisions on W1-49's packages DP-1 and DP-2 (register v0.52, appended by the W1 orchestrator on branch `w1/integrate`)

Decided by the orchestrator on 2026-10-04 under DEC-220, on two of the three packages the W1-49 (`DAEO-32n6`) ticket
lead returned from its test design. For each, the designer's, the lead's and the orchestrator's recommendations
agree, the confidence is medium or higher, and the choice is reversible: W1-29 replaces both hook files. DP-3 (the
prompt path injected for a ticket lead) is not decided here: the designer and the lead recommend differently, so it
goes to the owner. Meanwhile the suite stands as the designer wrote it (option (a): in a worktree, the lead
checkpoint's path and its RESUME HERE section only), and the owner's answer may add one assertion.

### DEC-258 — W1-49 DP-1: what "ensures the checkpoint is current" means for a PreCompact hook
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-49 package DP-1 option (a) with measure (i); confidence medium-high on the option, medium on the 30 minutes · **Under:** DEC-248, CAP-37.g
- **Decision:**
  - A hook can check and block; it cannot write the checkpoint's content. The checkpoint is current when its file
    is at most 30 minutes old.
  - On a manual compaction over a checkpoint that is not current, the hook blocks (exit 2) and says why.
  - On an automatic compaction it lets the compaction through and tells the user, and the SessionStart injection
    after it says `CHECKPOINT NOT CURRENT` with the path.
  - **Known gap, told to the owner:** an automatic compaction over a stale checkpoint still proceeds; the session
    is told only afterwards. With auto-compaction replacing the `CONTEXT_CHECKPOINT` stop (DEC-250) that is the
    common case, and it rests on the orchestrator and the leads rewriting their checkpoint after every merge,
    close and stop, as the prompt's section 1 already asks of the orchestrator.

### DEC-259 — W1-49 DP-2: the hooks act only for the orchestrator role
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-49 package DP-2 option (a); confidence high · **Under:** DEC-248, DEC-096, DEC-236
- **Decision:** The PreCompact and SessionStart hooks act only when `GOV_ROLE` is `orchestrator` (the main
  orchestrator and the ticket leads). A worker session gets no injection and is not blocked: the lead's checkpoint
  holds the loop count, which no session inside the loop may see. An unset `GOV_ROLE` is not the orchestrator.

| Version | Date | Change |
|---|---|---|
| 0.52 | 2026-10-04 | Delegated under DEC-220: DEC-258 (W1-49 DP-1: current means at most 30 minutes old; a manual compaction is blocked, an automatic one goes through with a notice and a `CHECKPOINT NOT CURRENT` line after it), DEC-259 (W1-49 DP-2: the hooks act only for `GOV_ROLE=orchestrator`). DP-3 goes to the owner. |
