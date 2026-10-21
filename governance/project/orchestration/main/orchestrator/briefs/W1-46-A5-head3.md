You are the ticket lead for ticket `DAEO-jdqr` (`W1-46`, "Worker session launcher (gov launch)"), profile FULL, working only in the worktree `/home/usain/gov-os-worktrees/W1-46` on branch `w1/W1-46`. Its implementer is an engineer (brief A2). This is a short closing round.

**Read this first: a headless lead's turn ends its background work.** After you start a worker in the background, wait for it in the foreground before you say anything: run a Bash call such as `until [ -s <the worker's .json log> ]; do sleep 20; done` with the longest timeout allowed, and repeat that call until the log has content. Only then read the result and go on.

## State of this ticket

- An earlier lead brought the branch to `32b5b9df`; it is merged into `w1/integrate` and every suite was green there except one builder test, which the main orchestrator has since corrected on `w1/integrate` (DEC-335). The lead's checkpoint is `.gov-runtime/scratch/lead/CHECKPOINT.md` in this worktree; read it, and the suite's README.
- Its five packages are decided, in `docs/DECISION_REGISTER.md` on `w1/integrate` (read them after step 1): DEC-332 (DP-17 (a), as built), DEC-333 (DP-18 (a), as built), DEC-335 (DP-21, done), and **DEC-334, the work of this round**:
  - the guard refuses `ln` without `-s`, `link` and `cp -l` when the source is a file the role may not write (a later call would write through the hard link and change an acceptance test);
  - the guard treats the destination of `mv --target-directory=<dir>` and of `install` as a write target, as it does for `mv -t` and `cp -t`.

## What you do, in order

1. `git merge w1/integrate`, with a message whose last paragraph has `Task: DAEO-jdqr` and `Role: orchestrator`. Resolve nothing by hand; a conflict is a package. The containment flag on the merge is a record (DEC-254).
2. **Test design batch 6** (brief A1, a fresh designer, profile FULL): refusal and control cases for DEC-334, in proportion (about ten cases): a hard link whose source is an acceptance test, a ticket file or the freeze flag is refused for an engineer, and one whose source is in the role's paths is not; the independent test designer may still hard-link inside the acceptance tests; `mv --target-directory=` and `install` (with `-t`, `-D` and the plain two-operand form) into the acceptance tests and `.tickets/` are refused, and into the role's paths are not. Tests added after implementation, reason "delegated decision".
3. **Check red** yourself, then a fresh **engineer** (brief A2). No guard decision may fail open; a form the guard cannot resolve is refused when its target could be protected, as the existing rules do.
4. **Verify**: W1-46 (the two live sessions included), W1-02, W1-03, W1-04, W1-05, W1-47, `tests/unit` and the validator, with the prefix `PATH=$HOME/.nvm/versions/node/v22.23.3/bin:$PATH`. You need not run the other suites; the main orchestrator runs them all after the merge. The W1-05 latency case (`test_a_call_waits_under_100_ms_p95_for_the_hook`) is sensitive to machine load: if it fails, re-run `tests/acceptance/W1-05/test_w1_05_live_hooks.py` alone before you treat it as red.
5. No reviewer pass this round. Remove the throwaway repository `.gov-runtime/scratch/lead/wt-probe/` if a plain `rm -rf` on that exact path is allowed; if it is refused, leave it and say so.
6. Return DONE with this round's commits, the results, any new residual, and the learning-metric changes against the earlier lead's totals (tests added after implementation 192; LOC outside tests 759 added and 71 removed).

