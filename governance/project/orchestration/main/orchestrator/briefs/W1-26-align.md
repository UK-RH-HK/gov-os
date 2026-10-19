You are the independent test designer for ticket `DAEO-fygv` (W1-26), in the worktree `/home/usain/gov-os-worktrees/W1-26` on branch `w1/W1-26`. A short turn, one file, one commit.

`tests/acceptance/W1-07/w1_07_support.py` has been changed both on this branch (this ticket's lines: `check` added to `BUILT_LATER`, and what else `git diff 19d8320a HEAD -- tests/acceptance/W1-07/w1_07_support.py` shows) and on `w1/integrate` since the merge base `19d8320a` (W1-24's lines for `context`; see `git diff 19d8320a w1/integrate -- tests/acceptance/W1-07/w1_07_support.py`). A merge commit has no authority over an acceptance test, so before the branch merges `w1/integrate`, you bring this branch's file to hold exactly `w1/integrate`'s version of the file plus this ticket's own lines in their place (owner decision DEC-412: aligned before the merge).

1. Take `w1/integrate`'s version (`git show w1/integrate:tests/acceptance/W1-07/w1_07_support.py`) as the base and apply this ticket's own lines to it by hand; never rewrite a line another ticket wrote.
2. Check: `git diff w1/integrate -- tests/acceptance/W1-07/w1_07_support.py` (working tree against `w1/integrate`) shows only this ticket's lines. `git merge-tree --write-tree HEAD w1/integrate` is not yours to run; do not merge.
3. Do the same for `tests/acceptance/W1-07/test_w1_07_envelope.py` and `tests/acceptance/W1-07/test_w1_07_check_declarations.py` only if `git diff 19d8320a w1/integrate -- (that file)` is not empty; otherwise leave them.
4. Do not run the W1-07 suite's cases that need `gov context` (it is not in this tree until the merge); run `python3 -m pytest tests/acceptance/W1-26 -q` to its end and report the count. Some W1-07 cases may be red until the merge brings W1-24's code: that is expected; say which, if you run them.
5. Commit: `git commit -m "W1-26: the shared W1-07 support file aligned with w1/integrate before the merge (DEC-412)" --trailer "Task: DAEO-fygv" --trailer "Role: independent-test-designer"`.

Write nothing outside `tests/acceptance/W1-07/` and `tests/acceptance/W1-26/`. Your last message: the commit hash, the diff of the file against `w1/integrate` (the lines only), and the count.
