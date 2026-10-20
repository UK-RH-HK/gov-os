You are the independent test designer for ticket `DAEO-8nue` (W1-22), in the worktree `/home/usain/gov-os-worktrees/W1-22` on branch `w1/W1-22`. A short turn, one change.

`tests/acceptance/W1-22/test_w1_22_canary_unit.py` is a copy of the unit tests that now live in `tests/unit/validate/test_canary.py` (its own docstring says it was placed there only until the engineer moved it). Check with `diff` that the two files differ only in that docstring note. If so:

1. `git rm tests/acceptance/W1-22/test_w1_22_canary_unit.py`.
2. In `tests/acceptance/W1-22/README.md`, correct any line that names that file so that it names `tests/unit/validate/test_canary.py` instead; change nothing else.
3. Run `python3 -m pytest tests/acceptance/W1-22 tests/unit/validate -q` to its end and report the counts.
4. Commit with: `git commit -m "W1-22: the duplicate of the canary unit tests removed from the acceptance folder" --trailer "Task: DAEO-8nue" --trailer "Role: independent-test-designer"`.

If the files differ in anything else, change nothing and say what differs. Write nothing outside `tests/acceptance/W1-22/`. Your last message: the commit hash, the counts, and what you changed in the README.
