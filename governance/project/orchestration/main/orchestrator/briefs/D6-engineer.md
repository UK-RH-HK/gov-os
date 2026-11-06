# D-6, the code tidy-up, part 1 (DEC-1039 (2), DEC-1040 (1), DEC-1052; started by DEC-1079): one engineer

You are a senior engineer for the CTO. Read `.gov-runtime/scratch/orchestrator/briefs/EMG-common.md` first (the
common rules: the heavy slot for every test run, your own worktree only, the commit form, the return).
**Your worktree:** `/home/usain/gov-os-worktrees/D-6` (branch `emg/d6`, today's `w2/integrate`). Commit only there.

**What to do** (`governance/project/orchestration/packages/LIFT-1/P1-PLAN.md` §A P1-6 and §D "Code tidy-up", item 2):
1. **One frontmatter parser** for the five byte-identical copies in `src/gov/check/{mutation,authority,claims,runner,graph}.py`
   plus `audit_validator` and `skill_validator`; then `schema.py`, `close/traceability.py`, `adopt/project.py`,
   `tasks/tickets.py`. **Not** `guard/decide.py` (the guard's hot path), and **not** `src/gov/store/loader.py` in this
   part.
2. `_ids` (×3), SQLite `_open` (×2), sha256 (×3): one each.
3. `close/evidence.py:junit_rel` deleted if nothing calls it.
4. The git wrappers merged only where their return types match (`store/loader._git` and `retrieval/lexical._git`) —
   **leave this one for part 2**.

**Do not touch** `src/gov/retrieval/retrieve.py`, `src/gov/retrieval/measure.py`, `src/gov/retrieve/command.py`,
`src/gov/store/loader.py` or anything under `tests/acceptance/`: memory work lands there now (W2-32 S11, W2-61h S7).
E-2's four coupling edges are part 2, after those land.

**The rule:** public calls unchanged, so no acceptance test changes; unit tests move with their helpers. **Verify:** the
unit and acceptance suites of every touched package pass unchanged, through the heavy slot, outside the real-model
cases (`-m "not local_only" -k "not real and not green_here and not time_limit"`); then the scoped set from
`select_tests.py` (as `EMG-common.md` says). Name every red you did not cause.

**Commits:** `Task: DAEO-sdxk`, `Implements: DEC-1039, DEC-1040`, `Role: engineer`, `Co-Authored-By: Claude Opus 5.5
<noreply@anthropic.com>`. **Return:** the twelve labelled fields; in `evidence` the before-and-after line counts and each
suite's result. One independent review follows. Est.: half a day.
