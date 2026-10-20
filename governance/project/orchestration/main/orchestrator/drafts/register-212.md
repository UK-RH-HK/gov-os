
## 212. Owner answers of 2026-10-14, third set: DEC-700 accepted; the exit clones restored (register v0.212, appended by the W1 orchestrator on branch `w1/integrate`)

### DEC-701 — DEC-700 is accepted by the owner; the restore of the exit clones is recorded
- **Status:** ACCEPTED (owner, 2026-10-14) · **Under:** DEC-694, DEC-698, DEC-699, DEC-700
- **Decision:** the delegated decision DEC-700 stands as recorded: at adoption's path-map stage, a namespace without `embedding_policy` is refused like a namespace with another value; outside adoption DEC-380 and DEC-388 stand.
- **Record of the restore (DEC-699):** the owner restored both clones through the operator with `cp -a` from the archive into `/tmp/claude-1000/-home-usain-gov-os-worktrees-W1-42/1be98491-a02b-4f3c-accf-41da4cc96c6b/scratchpad/clones/`; both targets were absent before, and the archive copies are untouched.
  - `a-dev-exit`, from `live-run4-a-dev-exit`: `feature/dimension-checked-addition` at `30996b6` (checked out), main at `2d3d098`, clean.
  - `b-dev-exit`, from `live/b-dev-exit`: `feature/data-retention-rule` at `fc28272` (checked out), main at `3b1ad56`, clean.
  - The orchestrator checked both heads and both clean trees before starting W1-42 run 7.

| Version | Date | Change |
|---|---|---|
| 0.212 | 2026-10-14 | Owner: DEC-701 (DEC-700 accepted; the restore of both exit clones at the heads of the archive recorded). Next free id: DEC-702. |
