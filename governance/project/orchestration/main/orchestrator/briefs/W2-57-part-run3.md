You are the ticket lead for ticket `DAEO-cy5o` (`W2-57`, "the rulesync probe, the doctor probes, the serial pass and its route to the nightly"), profile FULL, working only in the worktree `/home/usain/gov-os-worktrees/W2-57` on branch `w2/W2-57`.

**This is run 3: a judgement-only re-probe (DEC-895), not a new round.** `git rev-parse --short=12 HEAD` must show `da0240e0563e`, and `git status --short` must show nothing. Anything else: stop and return PACKAGES naming it.

## Why you start now

- W2-57 is merged into `w2/integrate` (`57e363c5`, 2026-10-28) and waits for its close, after the second re-pin, which carries its code (DEC-933 item 1). Its probe record (`docs/probes/DAEO-cy5o/PR-DAEO-cy5o-review-2.md`, judgement pass, probed commit `8f61bda0eb5c`) is now **stale**.
- W2-07 round 2's merge (`8555aafc`, 2026-10-28) changed one file that probe judged: `src/gov/close/command.py`, one line, gate (h)'s (the `recorded` subtraction before `_check_unmeasured`). git merged it beside your serial phase's line in `_run_tests` with no conflict. W2-07's run 5 verified the merged tree in full: 16,479 passed, 0 failed; serial 180 passed.
- The close's probe gate would refuse W2-57 on it, and the second re-pin pins this code. The owner's standing rule (DEC-895) schedules a fresh probe at once.

## The decisions for this run

1. **Merge `w2/integrate` into `w2/W2-57`** (`git merge --no-ff w2/integrate`, with `Task: DAEO-cy5o`, `Implements: DEC-895` and `Role: orchestrator` in the final trailer block). If git reports a conflict, stop: `git merge --abort`, and return PACKAGES naming each file.
2. **A fresh FULL reviewer** (brief A3 with `governance/project/briefs/JUDGEMENT.md` word for word, `--effort max`, read-only, launched sandboxed) on the merged head.
   - **Its scope is judgement-only:** every file the earlier probe judged that changed between `8f61bda0eb5c` and the merged head (`git diff --name-only 8f61bda0eb5c HEAD` against that probe's list), above all `src/gov/close/command.py`.
   - **Its question:** does any change alter what the probe found, or let the close pass something W2-57's change refused (in particular: the serial phase's entries, the nightly route, and the order of the commit gates before any test)?
   - The earlier record's findings and classification stand unless a change touches them.
3. **Commit a new probe record** under `docs/probes/DAEO-cy5o/` (beside the earlier ones, which you leave as they are), only if it passes. Its `probed_commit` is the merged head.
4. **Verification, scoped to what changed:**
   - `tests/acceptance/W2-57/` and `tests/unit/close/` in the close's form;
   - `pytest --collect-only -q` over `tests` (DEC-868).
   - No full run: this run adds no code, and W2-07's run 5 verified the same merged code in full.
   - **The nightly (DEC-933 item 2.4):** while `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/NIGHTLY-RUNNING` exists, run no suite; wait.
   - **Known:** `tests/acceptance/W2-57/test_w2_57_designer_read_p95.py` fails under load from other sessions (W2-07's run 5: 245 to 256 ms per round at load 20 to 32; passed alone at load 6). If it is red, re-run it alone and report both.
5. **Your trailers** (LEAD-w2-common, DEC-927 item 2): run `trailer_gate.py` on your worktree before you return.
6. **Return** DONE (the new probe passed; ready to merge), or PACKAGES.

**Estimate:** about 1 to 1.5 hours.

---
