You are the ticket lead for ticket `DAEO-ebmh` (`W2-75`, "W2-54's green-here fixture reads the close's own check result"), profile LITE, a test-revision ticket, working only in the worktree `/home/usain/gov-os-worktrees/W2-75` on branch `w2/W2-75`.

**This is run 1.** `git rev-parse --short=12 HEAD` must show `3eef001d08dd`, and `git status --short` must show nothing. Anything else: stop and return PACKAGES naming it. Read the ticket file (`.tickets/DAEO-ebmh.md`), its card in `docs/plan/WAVE_2_WBS.md` §2, row W2-L429 in `docs/plan/WAVE_2_LIST.md`, and DEC-937 first.

## Why you start now

- **Every full close is refused.** W2-58's close (2026-10-28 21:31, count 1, repair ticket DAEO-pr0y) ran 15,672 regression cases with 0 failed and 3 errors, all of them W2-54's green-here cases: "failed on setup with Timeout (>900.0s) from pytest-timeout".
- **The cause:** their shared fixture `gov_check_here` (`tests/acceptance/W2-54/conftest.py`) runs `gov check` on this repository. That takes about six minutes alone, and over the close's 900 s per-test limit under a full close's parallel load.
- **What waits on you:** W2-58, W2-63, W2-07 and W2-57 all close in full, so the queue holds until you merge.

## The decisions for this run (DEC-937, delegated; row W2-L429 names the fix)

- **A fresh independent test designer** (launched sandboxed, `--effort high`; its brief must not set `TMPDIR`) revises W2-54's green-here fixture and cases, within the ticket's allowed paths, each change with `Rewrite-Reason: W2-L429` and described in the README:
  1. **Inside a close,** `gov_check_here` reads the result the pinned close hands its runs instead of running `gov check`. That is the environment variable `GOV_CLOSE_CHECK_RESULT`: the path of the JSON envelope of gate (b)'s `gov check`, run on the same commit after the rebuild. See how W2-66's tests read it (`tests/acceptance/W2-66/w2_66_support.py`, `test_w2_66_followed_couplings.py`) and the pinned close's `CHECK_RESULT_VARIABLE` in `gov/close/command.py`.
  2. **Outside a close** (the variable unset), the fixture runs `gov check` in this tree exactly as now.
  3. **A result that is missing, unreadable, or not gov check's envelope with its checks** is never read as green. The fixture runs `gov check` itself, or the cases fail naming the file.
  4. **Each of the three cases keeps its meaning** (context-reproducibility GREEN here, core-schema GREEN here, the W1-43 audit report untouched) and asserts nothing less. Where a case needs `gov check` to have run in this tree, it and the README say how gate (b)'s run stands for it.
- **Red first:** the test designer shows the old fixture with `GOV_CLOSE_CHECK_RESULT` set still running `gov check` (a spy, or the time taken), and the new one not.

## Your checks (a script file under `.gov-runtime/scratch/lead/`; never `python3 -c` with braces, DEC-409)

- **Both routes, run alone:**
  - the three cases with `GOV_CLOSE_CHECK_RESULT` set to a `gov check --json` result you produce first in this worktree: green, without running `gov check` again;
  - the three cases with the variable unset: green, running it.
- **A planted bad result is not read as green:** a missing file, a non-JSON file, and an envelope whose context-reproducibility check is RED.
- `pytest --collect-only -q` over `tests`: no collection error.

## Verification

The full run in the close's form, under the lock, with the retention option and the disk gate first.
- In that run the variable is unset, so the green-here cases still run `gov check` and may time out under load. If they do, re-run them alone and report both (row W2-L429). The point of the ticket is the close's route, which your check above proves.
- **Known:** the nightly route (W2-57, now pinned) is not in a plain pytest run. W1-46's and W1-19's cases run in your serial phase.
- **The nightly (owner, DEC-933, DEC-936):** while `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/NIGHTLY-RUNNING` exists (from 02:00 most nights), run no suite and no full run. Wait, and go on the moment it is gone. Your full run also waits for the verification lock.
- Any other red is named with its cause.

**No review (LITE).**

## This run's order

1. The test designer.
2. Your checks.
3. Rebuild and verify in full.
4. **Return** DONE (it merges at once, and the queue restarts with W2-58), or PACKAGES.

**Estimate:** about 30 lines, about 2 hours with the full run.

**Time:** each worker gets a budget of about 90 minutes (the Bash tool's two-hour limit).

---
