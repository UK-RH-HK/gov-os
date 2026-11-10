Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-116-d10-tests/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# D-10's red-fix list: W2-116's and W1-32's cases against W2-56's cleaned environment and full removal (W2-116, DAEO-f58b)

You are a fresh **independent test designer**, launched under W2-116's ticket (`.tickets/DAEO-f58b.md`). W2-56
changed two behaviours of `gov launch` on purpose, and 13 older cases still expect the old ones. The CTO gave these
to D-10's helper (DEC-1112 (3)).

## The reds (outside the sandbox at integrate, alone and serial)
1. **`tests/acceptance/W2-116/test_w2_116_launch.py`, 6 cases** (`test_s3_every_worker_session_searches_the_integration_store_from_a_worktree_with_none[engineer|independent-auditor|independent-test-designer|product-spec]`,
   `test_s3_failure1_a_designer_never_reads_the_ticket_worktree_s_own_store`,
   `test_s3_guard_the_launched_session_keeps_its_role_and_ticket`).
   - **The failure:** the case's stand-in CLI dies with `KeyError: 'W2_116_SESSION_LOG'`.
   - **The cause:** W2-56's cleaned session environment (`8c399ea3e`; its KPI "A launched session gets a cleaned
     process environment: PATH, HOME, the locale, what the CLI needs to sign in, its identity and the launcher's own
     values …; none of the parent's CLAUDE* and GOV* variables … reach it" [DEC-826 Q5, DEC-877 item 4]) no longer
     passes the case's own variable to the session.
2. **W1-32, 7 cases:**
   - `test_w1_32_launch.py::test_a_failed_removal_keeps_the_sessions_exit_code[0|7]`;
   - `test_w1_32_launch.py::test_a_failed_removal_writes_one_line_to_stderr_that_names_the_folder[0|7]`;
   - `test_w1_32_added_cases.py::test_a_failed_removal_keeps_the_sessions_exit_code_when_stderr_cannot_be_written[stderr-closed-7|stderr-reader-gone-0|stderr-reader-gone-7]`.
   - **The failure:** "the fixture's folder was removed: the removal did not fail".
   - **The cause:** W2-56 (its "a sandboxed worker's temp folder is removed when the worker ends, whatever its exit"
     [W2-M405, DEC-902], built in `8c399ea3e`) restores 0700 before it removes the whole temp folder. So the cases'
     sealed folder no longer resists removal.

The W2-116 ticket's and W2-56's ticket text (`.tickets/DAEO-wnnz.md`, lines 36 and 47) state both behaviours. Read
them; do not read W2-56's or W2-116's implementation (`src/gov/launch/**`): DEC-820 (c).

## The task
1. **W2-116:** the stand-in learns where to write its log by a route the cleaned environment keeps. For example:
   - a path written into the stand-in when the case plants it;
   - a file at a fixed place under the case's planted HOME.
   Assert the same things as before. Lower no expectation.
2. **W1-32:** the failed-removal cases need a removal that still fails under W2-56's removal.
   - For example, a folder whose parent the launcher cannot write: the launcher restores 0700 on the temp folder, not
     on a place it does not own. Or another planted failure you can show the launcher does not undo.
   - If no planted failure can make the removal fail now, so that the cases' premise is gone by design, say so. Then
     return PACKAGES with your recommendation (retire with a record, or keep one case that the folder is gone),
     rather than weakening them.
   - The other assertions (the session's exit code kept, one stderr line naming the folder, stderr closed or gone)
     stay as they are.
3. One README line per suite, and the reason in each changed case's docstring.
4. Every commit carries the matching trailer:
   - `--trailer "Rewrite-Reason: DEC-826 Q5, DEC-877 item 4: W2-56's cleaned session environment passes no parent variable, so the stand-in gets its log path another way"` (W2-116);
   - `--trailer "Rewrite-Reason: DEC-902, W2-M405: W2-56 removes the whole temp folder on every ending, restoring 0700 first, so a sealed folder no longer makes the removal fail"` (W1-32).

## Where you work
- Your worktree: `/home/usain/gov-os-worktrees/W2-116-d10-tests`, branch `w2/W2-116-d10-tests`, at integrate `9ca161a6f`.
- Write only `tests/acceptance/W2-116/**` and `tests/acceptance/W1-32/**`.
- Run through the heavy slot (`EMG-common.md`), with:
  - `PYTHONPATH=/home/usain/gov-os-worktrees/W2-116-d10-tests/src`;
  - `TMPDIR` a folder of your own under the sandbox's TMPDIR;
  - `PYTHONUSERBASE=/home/usain/.local` if HOME is a scratch folder;
  - both suites with `--optin=lifted,breadth`, before and after.
  - Cases that launch need the open gate the suites now plant (merged tonight). If a launch cannot run in your
    sandbox, say which; the CTO's helper runs them outside.

## Rules
- `EMG-common.md` holds. The hidden-half rule: never open anything under `~/gov-os-eval/` or `~/gov-os-runs/`, or
  any `hidden`, `memory-verdict` or `memory-verdict-2` folder. No GPU, no installs, never the full suite. Never run
  `git worktree prune`.
- Commit on `w2/W2-116-d10-tests` only, one commit per suite, with `--trailer "Task: DAEO-f58b"`
  `--trailer "Implements: DEC-1109, DEC-1112" --trailer "Role: independent-test-designer"`
  `--trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"` plus its Rewrite-Reason trailer. Never
  merge, push, amend or rebase.
- Estimate: 40 minutes. Return the twelve fields, short:
  - each suite's change;
  - the counts;
  - what could not run here;
  - the head commit.
