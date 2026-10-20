
## 73. Delegated decision on what W1-25 built beyond the decisions' wording (register v0.73, appended by the W1 orchestrator on branch `w1/integrate`)

Decided by the orchestrator on 2026-10-04 under DEC-220, on the points the W1-25 (`DAEO-rrxp`) ticket lead asked to
have confirmed. Each is a detail of the built command, reversible until W1-29 and W1-30 call it; the lead's and the
orchestrator's recommendations agree; confidence high.

### DEC-336 — W1-25: the details of `gov checkpoint` as built are accepted
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** the W1-25 lead's "to confirm" list; confidence high · **Under:** DEC-279 to DEC-282, DEC-317, DEC-320, DEC-321
- **Decision:**
  - A checkpoint also stores `task_status`, the ticket's status when it was written; the watchdog compares it for
    the `ticket-transition` reason. The key is optional in the schema, and a checkpoint without it is judged stale.
  - The file is `docs/checkpoints/<ticket>/CP-<ticket>-<NNNN>.md`; the highest number is the latest.
  - An input's `version` is the short hash of the last commit that changed the file, or `untracked`.
  - The family check's command is `gov checkpoint --resume --json`, tier `G1`, severity `hard-block`.
  - `CHECKPOINT_STALE` and `CHECKPOINT_MISSING` end with exit code 3, for `--watch` and `--resume`. The other
    errors end with 1: `CHECKPOINT_ARGUMENT_MISSING`, `CHECKPOINT_TRIGGER_UNKNOWN`, `TICKET_UNKNOWN`,
    `CHECKPOINT_INPUT_UNREADABLE`, `CHECKPOINT_INVALID`, `GIT_FAILED`.
  - The lead's change to the W1-46 builder test `tests/unit/launch/test_command_modules.py` (the stand-in command
    renamed from `checkpoint` to `pause`, `9c8fec02`) is accepted; it is outside W1-25's paths and is a record.

| Version | Date | Change |
|---|---|---|
| 0.73 | 2026-10-04 | Delegated under DEC-220: DEC-336 (W1-25: `task_status`, the file name, the input version, the family check's command, the exit codes and the builder-test rename are accepted as built). |
