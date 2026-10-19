
## 82. Delegated decisions on W1-28's packages DP-4 and DP-7 (register v0.82, appended by the W1 orchestrator on branch `w1/integrate`)

Decided by the orchestrator on 2026-10-05 under DEC-220, on two of the eight packages the W1-28 (`DAEO-9279`)
ticket lead returned. The test designer's, the lead's and the orchestrator's recommendations agree, the confidence
is medium-high, and both are reversible. The other six (DP-1, DP-2, DP-3, DP-5, DP-6, DP-8) touch KPI lines, the
freeze flag or what a rollback does to history, and go to the owner.

### DEC-357 — W1-28 DP-4 and DP-7: `--cancel-agents` releases locks only, and "the same result on repeat" means the same state
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-05) · **Basis:** W1-28 packages DP-4 option (a) and DP-7 option (a); confidence medium-high · **Under:** CAP-05.b, CAP-05.d, DEC-292
- **Decision:**
  - `gov pause --cancel-agents` releases the claim locks under `.tickets/.claims/` and records the sessions that
    held them. It does not change a ticket's status: a ticket left `in_progress` is set back by hand, which is a
    residual. The command cannot stop a process.
  - "The same result on repeat" means the same state: a repeat succeeds and leaves the project as the first run
    did. The two `result` objects need not be equal field for field.

| Version | Date | Change |
|---|---|---|
| 0.82 | 2026-10-05 | Delegated under DEC-220: DEC-357 (W1-28 DP-4: `--cancel-agents` releases locks only; DP-7: a repeat leaves the same state). Six W1-28 packages go to the owner. |
