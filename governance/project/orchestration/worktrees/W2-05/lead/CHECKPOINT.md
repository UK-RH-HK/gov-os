# W2-05 (DAEO-0z8c) lead checkpoint — 2026-10-19, end of run 2 (after DEC-783, DEC-789, DEC-793)

## State: PACKAGES. The second and last review (DEC-413) failed on a lost-work case (F-A) and a fail-open case (F-B). No third round without the owner. Not held as DONE. No probe record committed.

- Branch `w2/W2-05`, cut from `w2/integrate` at `c94e1507`, head `f19f156e` (the head rev2 probed). `git status` clean.
- The `gov launch` trial (DEC-789) WORKS: 4 workers (rev1, td3, eng3, rev2) started through it. Sandbox check (a) refused each time; `.sandbox-trial-DAEO-0z8c` was never created. (b) worked each time. Every later worker of this ticket starts through `gov launch`.

## Commits of run 2

- `3b2e6468` td2, independent-test-designer: the 4 S3 cases per DEC-783 (b), Rewrite-Reason x4 (before DEC-789, no tripwire).
- `0983be4c` CP-DAEO-0z8c-0010, orchestrator (the hold next-action), probed by rev1 (FAIL: F1, F2).
- `68055fa3` td3, independent-test-designer: F1 (3 cases rewritten, stricter, Rewrite-Reason x3; 4 new), F2 (2 new). 35 cases.
- `2e108d85` eng3, engineer: `gitenv.foreign_index`; `gov ci staged-secrets` refuses a foreign inherited index (CI_NOT_MEASURED, naming it); codeintel `_env` from `git_env(root)`; sweep rows 43–45, row 9 and row 13 corrected; 2 unit tests.
- `f19f156e` CP-DAEO-0z8c-0014, orchestrator (the hold next-action), probed by rev2 (FAIL: F-A, F-B).

## Verification at 2e108d85 (and f19f156e, same src)

rebuild exit 0 (codeintel recreated). gov.__file__ in this worktree. All 52 suites plus unit green, except W2-05's 5 reds that wait on another ticket (4 on W2-50, 1 on W2-53) and W1-42's 2 accepted reds. W2-05: 30 passed, 5 failed. W1-16: 167 passed. W1-40: 74 passed. W1-46: 493 passed. unit: 2143 passed, 1 skipped. gov check: adapter-portability GREEN; RED context-reproducibility (W2-54), core-schema (W1-43 audit report); YELLOW decision-citations (82, DEC-783 unrecorded), openspec absent.

## Drafts (not committed): `.gov-runtime/scratch/lead/probes/PR-DAEO-0z8c-round-1.md`, `PR-DAEO-0z8c-round-2.md`

## What the next lead does (once the owner answers P-R2)

- (a) If a third round is authorised: td (gov launch) for F-A, F-B (and D-1 if folded in) as described behaviours, then a red check, then eng (gov launch), then full verification, then gov checkpoint (hold), then a fresh review (the third, with the owner's leave), then the probe record if it passes, then the hold.
- At the resume after W2-53 and W2-50 close: merge w2/integrate (merge commit with Task: DAEO-0z8c and Role: orchestrator; never -s ours), the freeze look-up's 15 s in decide.py, the marked calls (sweep rows 32–42), one full rebuild, every suite, a fresh probe.
