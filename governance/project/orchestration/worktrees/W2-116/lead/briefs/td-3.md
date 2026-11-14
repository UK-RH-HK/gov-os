# Brief: independent test designer (fix batch 2), W2-116 (DAEO-f58b) pass 2b: one README map item `gov accept` cannot match

You are the independent test designer (MR-3) for ticket DAEO-f58b (W2-116). One small fix in your own suite's README.

## Where you work
- Worktree /home/usain/gov-os-worktrees/W2-116-tests, branch w2/W2-116-tests (at 862bc5b54). Write only
  `tests/acceptance/W2-116/README.md`. Commit there; never merge, never push.

## The failing output (the lead's `gov accept W2-116` on 862bc5b54)
Every line passes but success-2: `{"kpi": "success-2", "outcome": "fail", "passed": 22, "failed": 0, "skipped": 0}`;
totals 60 passed, 0 failed. A line fails when one of its map items names a test that no collected case matches.

The lead's check (`src/gov/accept/runner.py`, `matches`, lines 204-214, and `names_a_test`, 217-220): README line 186
lists the item `test_w2_116_s2_config.py::test_s2_failure_a_missing_or_invalid_setting_refuses_by_name_and_builds_nothing[<id>]`.
An item with `[` must equal a case's full name exactly, so `[<id>]` matches no case, and the line fails. Every other
item of success-2 matches or names no test.

## What to do
- On line 186, name the test without the placeholder:
  `test_w2_116_s2_config.py::test_s2_failure_a_missing_or_invalid_setting_refuses_by_name_and_builds_nothing` (it
  matches every parametrised row), keeping the list of ids as prose. Change nothing else.
- Check it (it must print `[]`):
  ```
  env PYTHONPATH=/home/usain/gov-os-worktrees/W2-116-tests/src python3 -c "from gov.accept.runner import parse_map; m=parse_map(open('/home/usain/gov-os-worktrees/W2-116-tests/tests/acceptance/W2-116/README.md').read()); print([i for items in m.values() for i in items if '[' in i])"
  ```
- Commit:
  ```
  git -C /home/usain/gov-os-worktrees/W2-116-tests commit -m "W2-116 pass 2b (DAEO-f58b): README map: the config refusal test named without the [<id>] placeholder, so gov accept matches it" --trailer "Task: DAEO-f58b" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-983, DEC-982, DEC-966, DEC-963, DEC-1087" -- tests/acceptance/W2-116/README.md
  ```

## Rules
- No pytest run is needed. Refused twice for the same call by the guard, the sandbox or a hook: stop and say so; never
  work around it (DEC-1142 (9)). No `gov retrieve` or `gov context` in the sandbox (DEC-1065).

## Return (your last message; only it is read)
The twelve fields, each a labelled line ("none" where nothing): task / status / work_completed / files_changed /
evidence (the check's printed line) / tests / discoveries / risks / lessons / proposed_decisions / unresolved /
recommended_next_action. Then `commits:` with hash12 and subject.
