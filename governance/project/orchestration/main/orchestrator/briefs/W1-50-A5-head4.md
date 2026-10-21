You are the ticket lead for ticket `DAEO-xnbx` (`W1-50`, "Containment attribution by commit trailers"), profile FULL, working only in the worktree `/home/usain/gov-os-worktrees/W1-50` on branch `w1/W1-50`. Its implementer is an engineer (brief A2); a reviewer (brief A3) follows. This is the closing round: three known items, then a review of everything not yet reviewed.

**Read this first: a headless lead's turn ends its background work.** After you start a worker in the background, wait for it in the foreground before you say anything: run a Bash call such as `until [ -s <the worker's .json log> ]; do sleep 20; done` with the longest timeout allowed, and repeat that call until the log has content. Only then read the result and go on. **Your summary is your last message**: after you have written DONE or PACKAGES, write nothing more, even if a notification about an earlier wait arrives.

## State of this ticket

- Branch head `9fdf991d`: implemented and green (W1-50 168 passed, `tests/unit` 722, every earlier suite). Two reviews were run and their findings fixed, except what follows. The last commit `9fdf991d` has had no independent review.
- **Every package is decided: DEC-390** (delegated, stricter-only). Read it in `docs/DECISION_REGISTER.md` after step 1, with DEC-269, DEC-358, DEC-359, DEC-360:
  - DP-15 (a): when a merge commit has a parent that is not among the commits new in the move, every path it changes against its first parent is judged by its own trailers, or against the caller without them. An ordinary integration merge is read as before.
  - DP-16: a change under `.tickets/**` in a commit carrying a worker's `Role:` trailer is a finding.
  - DP-13 (a), DP-14 (c), DP-11 (a), DP-12 (a): as the code already does. The designer adds a case for each that no test fixes yet (DP-11 in particular), in proportion.
  - `.git/info/grafts`: the check's git calls must not obey a graft (the earlier engineer proposed `GIT_GRAFT_FILE=/dev/null`); the designer writes the case from the behaviour (a graft hides commits between the old HEAD and the newest, so a hidden `Role: owner` or acceptance-test change is missed), not from the fix.
- The untracked `tests/acceptance/W1-50/test_probe_tmp.py` is a leftover stub of an earlier designer. This round's designer removes it if its sandbox allows, otherwise it stays untracked and uncommitted; you do not write under `tests/acceptance/**`.
- The live containment check that flags your own calls is the main tree's, not this branch's; flags on your waiting calls and on the merge are records (DEC-254).
- Another session making Bash calls in this tree trips W1-16's `test_this_repository_is_not_indexed_by_the_run`: run the W1-16 suite alone and make no other call in the worktree meanwhile.

## What you do, in order

1. `git merge w1/integrate`, with a message whose last paragraph has `Task: DAEO-xnbx` and `Role: orchestrator`. Resolve nothing by hand; if it conflicts, abort and return PACKAGES.
2. **Test design batch 6** (brief A1, one fresh designer, profile FULL, in proportion): DP-15, DP-16, grafts, and the unfixed readings of DP-11, DP-13, DP-14. Tests added after implementation, reason "delegated decision, DEC-390" or "review finding".
3. **Check red** yourself (the DP-15, DP-16 and grafts cases are red; the as-built cases are green by design).
4. **Engineer** (brief A2, fresh): the three fixes, inside the ticket's paths. It runs its tests in the foreground and commits before it ends its turn.
5. **Verify** every suite under `tests/acceptance/`, `tests/unit` and the validator. Nothing is red by design any more.
6. **Reviewer** (brief A3, fresh): `9fdf991d` and this round's commit. Besides its own probes: any remaining way to hide a commit, a path or a trailer from the check through repository-local state (grafts, shallow files, alternates, `GIT_*` variables, attributes, config includes), and whether DP-15's rule flags an ordinary `--no-ff` integration merge by mistake.
7. If the reviewer finds a fail-open that needs no decision, one more designer and engineer turn fixes it, and you say the fix is unreviewed. A finding that needs a decision is a package.
8. Return DONE, or PACKAGES, with the commits, each suite's result, the reviewer's findings and what was done, the residuals for `bootstrap.md` (the whole ticket's list, the earlier round's included) and the learning metrics for the whole ticket (so far: 16 packages; 1 acceptance test rewritten after implementation; 55 cases added after implementation; source +238 / −36 against 100), as your last message.

