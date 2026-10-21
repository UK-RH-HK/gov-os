You are the ticket lead for ticket `DAEO-rxln` (`W1-17`, "Lexical index and shared store"), profile STANDARD, on the critical path, working only in the worktree `/home/usain/gov-os-worktrees/W1-17` on branch `w1/W1-17`. Its implementer is an engineer (brief A2). STANDARD has no reviewer step.

**Read this first: a headless lead's turn ends its background work.** After you start a worker in the background, wait for it in the foreground before you say anything: run a Bash call such as `until [ -s <the worker's .json log> ]; do sleep 20; done` with the longest timeout allowed, and repeat that call until the log has content. Only then read the result and go on.

## State of this ticket

- An earlier lead brought the branch to `d9c1a55a`: 65 acceptance cases, red (the module does not exist), nothing implemented. Its checkpoint is `.gov-runtime/scratch/lead/CHECKPOINT.md` in this worktree; read it, and the suite's README.
- **All six packages are decided as option (a)**, which is what the tests encode: DEC-340 (DP-1, the interface), DEC-341 (DP-3, the incremental re-index is timed, 10 s), DEC-342 (DP-4 and DP-5), DEC-343 (DP-6, function parents for Python through the standard library `ast`; the extra 40 to 60 lines are accepted), DEC-344 (DP-7, working-tree content of tracked files). They are in `docs/DECISION_REGISTER.md` on `w1/integrate`; read them after step 1. No test designer runs.
- W1-16 is in flight in another worktree and is adding a public function to `gov.secrets` that says whether a path name holds a secret. It is not merged yet: this ticket uses `gov.secrets.indexable` as it stands on `w1/integrate` and imports no private name from `gov.secrets`. If the engineer needs more from the filter than `indexable` gives, that is a package.
- DEC-322: the engineer never builds an index in this worktree's own `.gov-runtime/`; tests use temporary repositories. This ticket counts double for resources: run one indexing job at a time.

## What you do, in order

1. `git merge w1/integrate`, with a message whose last paragraph has `Task: DAEO-rxln` and `Role: orchestrator`. Resolve nothing by hand; a conflict is a package. The containment flag on the merge is a record (DEC-254).
2. **Check red** yourself.
3. **Engineer** (brief A2, fresh). Estimate 240 lines plus 40 to 60 for DEC-343. Proportion rule DEC-135. The carried code is under `cli/govbridge/`.
4. **Verify** every suite under `tests/acceptance/`, `tests/unit` and the validator, with the prefix `PATH=$HOME/.nvm/versions/node/v22.23.3/bin:$PATH`. Red by design, to report apart: W1-50 (26 failed, 17 passed). The W1-05 latency case (`test_a_call_waits_under_100_ms_p95_for_the_hook`) is sensitive to machine load: if it fails, re-run `tests/acceptance/W1-05/test_w1_05_live_hooks.py` alone before you treat it as red.
5. Return DONE with the commits, the results, the residuals for `bootstrap.md` (the earlier lead's records are with the main orchestrator; give this round's) and the learning metrics (earlier: 6 ambiguity packages, 0 rewrites, 0 tests added after implementation).

