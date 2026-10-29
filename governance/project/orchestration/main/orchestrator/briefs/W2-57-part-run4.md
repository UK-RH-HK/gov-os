You are the ticket lead for ticket `DAEO-cy5o` (`W2-57`, "the rulesync probe, the doctor probes, the serial pass and its route to the nightly"), profile FULL, working only in the worktree `/home/usain/gov-os-worktrees/W2-57` on branch `w2/W2-57`.

**This is run 4: a judgement-only re-probe (DEC-895), not a new round.** `git rev-parse --short=12 HEAD` must show `d0cb962998b5`, and `git status --short` must show nothing. Anything else: stop and return PACKAGES naming it.

## Why you start now

- W2-57 is merged into `w2/integrate` and pinned (re-pin 2, `5c401220`); it waits for its close. Its last probe record (`docs/probes/DAEO-cy5o/PR-DAEO-cy5o-reprobe-1.md`, judgement pass, probed commit `8d9d78d93529`) is now **stale**.
- W2-68's merge (`848f5ab3`, 2026-10-29) changed one file that probe judged: `src/gov/close/command.py`, 31 lines in and 11 out. W2-68 adds the batch's calls and the close record's lines: `scope: reused`, the `reused` block with its skip count, both fingerprints, the red-run hold. W2-68's own review passed, and its full run was green (16,536 passed).
- The owner's standing rule (DEC-895) schedules a fresh probe at once.

## The decisions for this run

1. **Merge `w2/integrate` into `w2/W2-57`** (`git merge --no-ff w2/integrate`, with `Task: DAEO-cy5o`, `Implements: DEC-895` and `Role: orchestrator` in the final trailer block). If git reports a conflict, stop: `git merge --abort`, and return PACKAGES naming each file.
2. **A fresh FULL reviewer** (brief A3 with `governance/project/briefs/JUDGEMENT.md` word for word, `--effort max`, read-only, launched sandboxed) on the merged head.
   - **Its scope is judgement-only:** every file the earlier probe judged that changed between `8d9d78d93529` and the merged head, above all `src/gov/close/command.py`.
   - **Its question:** does W2-68's change alter what the probe found, or let a close pass something W2-57's change refused? In particular: the serial phase's entries, the nightly route, a reused run's skips (the nightly-routed entries run in neither a close nor a batch: W2-68's reviewer's F3), and the order of the commit gates before any test.
   - The earlier records' findings and classification stand unless a change touches them.
3. **Commit a new probe record** under `docs/probes/DAEO-cy5o/` (beside the earlier ones), only if it passes. Its `probed_commit` is the merged head.
4. **Verification, scoped to what changed:**
   - `tests/acceptance/W2-57/` and `tests/unit/close/` in the close's form;
   - `pytest --collect-only -q` over `tests` (DEC-868).
   - No full run: this run adds no code, and W2-68's run verified the same code in full.
   - **The nightly:** while `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/NIGHTLY-RUNNING` exists, run no suite. A close queue may be running in the main tree; run your suites only when the 1-minute load is under 20.
   - **Known:** `test_w2_57_designer_read_p95.py` fails under load from other sessions (row W2-L450). If it is red, re-run it alone and report both.
5. **Your trailers** (LEAD-w2-common, DEC-927 item 2): run `trailer_gate.py` on your worktree before you return.
6. **Return** DONE (the new probe passed; ready to merge), or PACKAGES.

**Estimate:** about 1 to 1.5 hours.

---
