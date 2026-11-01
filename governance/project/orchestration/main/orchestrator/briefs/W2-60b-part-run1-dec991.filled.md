You are the ticket lead for ticket `DAEO-ecac` (`W2-60b`, "One record per session: model, effort, window, tokens, cost, minutes, turns, subagents"). It is profile STANDARD, on the roles stream (DEC-979 item 4), and you work only in the worktree `/home/usain/gov-os-worktrees/W2-60b` on branch `w2/W2-60b`.

**This is run 1.** `git rev-parse --short=12 HEAD` must show `@@HEAD@@`, and `git status --short` must show nothing. Anything else: stop and return PACKAGES naming it.

**Definition of Ready (checked by the CTO at claim, DEC-944 item 2):** sources resolve (DEC-946, DEC-838, DEC-839, DEC-826, DEC-655, DEC-495, DEC-392, DEC-786, DEC-941, DEC-954, DEC-957, DEC-959, DEC-983); allowed paths, KPIs, profile and the acceptance path (`tests/acceptance/W2-60b/`) are set; **its dependencies are W2-60a (`DAEO-cv58`) and W2-07 (`DAEO-r9ss`): W2-07 is closed; it starts only once W2-60a is closed** (they share `src/gov/launch/launcher.py`, and W2-60a's launch record is what your record joins).

**Read first:**
- the ticket file (`.tickets/DAEO-ecac.md`) and its card in `docs/plan/WAVE_2_WBS.md` §2 ("#### W2-60b");
- W2-60a's merged launcher and launch record (`src/gov/launch/role.py`, `record.py`, `launcher.py`) and its CIT-E; W1-31's session-log reader (`src/gov/telemetry/sessionlog.py`);
- DEC-838 items 1 to 3 (the window, compactions), DEC-495 (counts only, never content), DEC-392 (exit codes, signals), DEC-946 (W3-P09: launchable roles read from the role files), DEC-959 item 3 (the QA engineer, rule 5), DEC-963 (one writer per worktree; `--tests-worktree`).

## The decisions for this run
- **The work order (DEC-957, DEC-959 item 7, DEC-963):** a fresh independent test designer (sandboxed, effort high) in `/home/usain/gov-os-worktrees/W2-60b-tests`, retrieving only from the integration branch's store; in parallel a fresh engineer (sandboxed, effort high) to the spec and KPIs; one acceptance run through `gov accept` once merged, results only.
- **`qa-engineer` in the guard's `KNOWN_ROLES` (`src/gov/guard/decide.py`, that set only):** this repository's own live hook's reviewer line is an owner ACT prepared beside it, never changed here; name the line in your return for the CTO.
- **Running beside you:** W2-05 (merged) holds `src/gov/**/*.py` broadly for its git-environment sweep only, no lead running. Any other ticket's file you need: return PACKAGES.
- **Fail closed:** a value the log does not hold reported as measured, a zero for not measured, log text in a record, a changed exit code, a session with no record, a fixed role list left in code.
- **Verification (DEC-968, DEC-983):** the scoped set, once, in the close's form, through `verify_lock.sh`. **No review (STANDARD).**
- **One merge per ticket (DEC-988, DEC-989):** return DONE with the exact head you verified; the CTO lands it through the merge queue, which merges and closes it in one step.

**Estimate:** about 160 lines of code; about 5 hours. Scratch budget (DEC-898): 20 GB and 1,000,000 files and folders for you and your workers, outside the tracked tree; `TMPDIR=/tmp/gov-os-lead-W2-60b`.

**Time:** each worker gets a budget of about 90 minutes (the Bash tool's two-hour limit).

---
