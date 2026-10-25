You are the ticket lead for ticket `DAEO-qty6` (`W2-73`, "W1-03's head-move fixture: an amend that always moves HEAD"), profile LITE, a test-revision ticket, working only in the worktree `/home/usain/gov-os-worktrees/W2-73` on branch `w2/W2-73`.

**This is run 1.** `git log --oneline -1` must show `533c90b1`, and `git status --short` must show nothing. Anything else: stop and return PACKAGES naming it. Read the ticket file (`.tickets/DAEO-qty6.md`) and its card first.

## Why you start now

- **Two cases of `tests/acceptance/W1-03/test_w1_03_head_move_and_acceptance_test.py` fail by chance:**
  - `test_while_another_actor_s_call_is_open_the_test_is_flagged_and_not_restored` fails 6 of 10 alone;
  - `test_the_restore_next_to_a_head_move_takes_back_the_acceptance_tests_and_nothing_else` fails too.
- **The cause:** the fixture's `git commit -q --amend --no-edit` writes an identical commit when it lands in the same second as the commit it replaces, so HEAD does not move. The fixture's own precondition ("did not move HEAD") then fails before containment is judged.
- **Not W2-72's:** it is as frequent before W2-72's merge (7 of 10 at `c60c9704`).
- **Why it matters now:** it fails closed, but a close that runs W1-03 would be refused by chance. The first closes after the first re-pin need it fixed (owner, DEC-921 item 2).

## The decisions for this run

- **A fresh independent test designer** (launched sandboxed, `--effort high`; its brief must not set `TMPDIR`) revises only that file and the folder's README:
  - every amend form that must move HEAD makes a commit that differs whatever the clock (for example a changed message, or an explicit later committer date);
  - no expectation of containment's restore or flag is lowered;
  - each revised case is shown red once under a planted fault in containment's head-move restore;
  - `Rewrite-Reason: DEC-921`.
- **Your check:** the two named cases 30 times in a row alone, green, then the whole of W1-03 alone. Use a script file under `.gov-runtime/scratch/lead/`; never `python3 -c` with braces (DEC-409).
- **Verification:** the full run in the close's form, under the lock, with the retention option and the disk gate first, and the JUnit XML under `/tmp/gov-os-lead-W2-73/`.
  - **Known:** W2-54's green-here case may time out under load (row W2-L429; re-run alone); W1-19's warm-query case is on `load_sensitive`.
  - Any other red is named with its cause.

## This run's order

1. The test designer.
2. Your 30-run check.
3. Rebuild and verify in full.
4. **Return** DONE (it merges at once), or PACKAGES.

**Estimate:** about 15 lines, about 2 hours with the full run.

**Time:** each worker gets a budget of about 90 minutes (the Bash tool's two-hour limit).

---
