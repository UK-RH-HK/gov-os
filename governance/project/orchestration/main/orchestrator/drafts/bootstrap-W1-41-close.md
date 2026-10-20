
## DAEO-cdoi (W1-41) closed after the round of DEC-694, with the ticket tool, by the owner's decision (2026-10-14; for the exit auditor; DEC-703)

`gov close DAEO-cdoi` at `718738d6` refused (exit 3, `CHECK_FAILED`, log `close-W1-41R.json`) on three parts:

- `PROBE_INVALID` on `b87ac775` (2026-10-11), before this repository's trailers base `1c33dd28`, the same finding as DAEO-emkd's close (DEC-690);
- a containment finding on the merge `803f731c` (2026-10-09), before the base;
- adapter-portability RED on `.claude/skills/adopt/SKILL.md` (`GENERATED_DIFFERS`): the generated copy waiting for the operator's apply (DEC-616). The operator applied it at `75b57d40`. At `de9389fc`, after `gov rebuild --no-embeddings`, `gov check` exited 0 with adapter-portability GREEN and no RED family (yellow: decision citations, openspec, audit reproducibility, as before; log `check-W1-41-close.json`). A first `gov check` without the rebuild and the close script's environment was red on index freshness, secrets indexing and recovery/rebuild (the index stale after two commits), and green on adapter-portability.

Its repair ticket (DAEO-52q7) was moved out of `.tickets/` to the orchestrator's scratch log, as earlier repair tickets of pre-base refusals were.

- **Tests:** every test run of the close green (acceptance 242; regression 12,926 parallel and 263 serial); the regression after the merge `945643ec` green (13,168 and 263, validator ALL PASS); the 127 rulesync-pair cases green after `a8cf8867`.
- **Probe:** PASS, `docs/probes/DAEO-cdoi/PR-DAEO-cdoi-round-DEC-694.md` (reviewer `687d031c…`, probed commit `dc14bf4e`).
- **Learning metrics of the round:** KPI disputes 0; 119 cases rewritten before implementation, 0 after; 36 cases added (12 controls); source lines +50 against an estimate of 80.
- The worktree `W1-41` and its branch `w1/W1-41` were removed after the close.
