# The lift's map fixes, fix round: W2-05's edge rows name tests the reader cannot match (W2-96, DAEO-ouet)

You are a fresh **independent test designer**, launched under W2-96's ticket (`.tickets/DAEO-ouet.md`).

## The behaviour to fix (a described behaviour, DEC-136)
At `ba5cf0f87` (branch `w2/W2-96-maps-lift-tests`), W2-05's map (`tests/acceptance/W2-05/README.md`) reads, and its
three edge rows now name a KPI line each (lines 132-134: `**F1**, edge:`, `**S2**, edge:`, `**S1**, edge:`). But rows
133 and 134 list tests by an **elided** name: `test_a_declared_check_..._lands_as_staged[a linked worktree, a plain
commit]`, `test_install_from_a_linked_worktree_...`, `test_the_guard_hook_refuses_within_its_own_limit_...` and
`test_gov_close_runs_...`. `gov accept` treats an item that begins `test_` (or holds `::`) as naming a test, and a named
test that matches no collected case fails its line. So `gov accept W2-05` would now fail S2 and S1 with no red case.
An item matches a case only as `file.py::test_name`, `file.py::test_name[row id]`, `file.py`, or a bare whole function
name (no brackets, no dots); you may read `matches` and `names_a_test` in `src/gov/accept/runner.py`.

## The task (DEC-866: wording only, the mapping kept)
1. In rows 133 and 134, write each elided item as the full name of the one test it stands for, in a form the reader
   matches (e.g. `test_w2_05_planted.py::test_gov_close_runs_its_subprocesses_and_the_ticket_tests_with_a_sanitised_environment`).
   Each must match exactly the test(s) the elided name meant, from W2-05's own test files; if one is ambiguous, say so
   and leave it out of the row's backticks as prose rather than guess.
2. Change nothing else: no other row, no other cell's meaning, no test file. Row 132 stays as it is.
3. Check with the reader itself (names only, no suite run): `parse_map` raises nothing and its line set is unchanged;
   and for each backticked item of rows 132-134 that `names_a_test` accepts, show that the function it names exists in
   `tests/acceptance/W2-05/` (a `grep -n "def <name>"`), and for a `[row id]` item that the id is one of the test's
   parametrize ids.
4. One commit with `--trailer "Task: DAEO-ouet" --trailer "Implements: DEC-1112" --trailer "Role: independent-test-designer"`
   `--trailer "Rewrite-Reason: DEC-866: W2-05's edge rows named tests by elided names gov accept cannot match; written in full, the mapping kept"`
   `--trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`. Never merge, push, amend or rebase.

## Where you work
- Worktree `/home/usain/gov-os-worktrees/W2-96-maps-lift-tests`, branch `w2/W2-96-maps-lift-tests`, at `ba5cf0f87`.
- Write only `tests/acceptance/W2-05/README.md`. `TMPDIR` a folder of your own under the sandbox's TMPDIR.

## Rules
- `EMG-common.md` holds, its hidden-half rule included. No GPU, no installs, no test runs. Never `git worktree prune`.
  Single simple Bash commands.
- Estimate: 10 minutes. Return the twelve fields, short: each item's old and new text, the step 3 evidence, the head.
