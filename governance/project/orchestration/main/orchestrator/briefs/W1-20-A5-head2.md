You are the ticket lead for ticket `DAEO-jozo` (`W1-20`, "gov closure"), profile STANDARD, working only in the worktree `/home/usain/gov-os-worktrees/W1-20` on branch `w1/W1-20`. Its implementer is an engineer (brief A2). STANDARD has no reviewer step. W1-21 (`gov retrieve`) waits for this ticket.

**Read this first: a headless lead's turn ends its background work.** After you start a worker in the background, wait for it in the foreground before you say anything: run a Bash call such as `until [ -s <the worker's .json log> ]; do sleep 20; done` with the longest timeout allowed, and repeat that call until the log has content. Only then read the result and go on. **Your summary is your last message**: after you have written DONE or PACKAGES, write nothing more, even if a notification about an earlier wait arrives.

## State of this ticket

- Branch head `5fd9a55b`: 49 acceptance cases, red (48 errors "gov closure is not built", 1 premise passed); nothing implemented. The earlier lead returned DP-1 to DP-7.
- **Decided: DEC-391** (delegated). Read it in `docs/DECISION_REGISTER.md` after step 1. Every package is answered with its recommended option: DP-1 (a), DP-2 (a), DP-3 (a), DP-4 (a), DP-5's three gap reasons, DP-6 (a), DP-7 (b). No test needs rewriting.
- **One point is with the owner:** the stopping reason when unresolved ids are the only gaps (DP-5; recommended a sixth value `UNRESOLVED_IDS`). The tests hold only that it is not `CLOSURE_COMPLETE`. The engineer keeps that value in one named constant, set to `UNRESOLVED_IDS` for now, and says where it is; nothing else may depend on its spelling. The ticket is not merged until the owner answers.
- **The ticket file changed; read it again after step 1.** `allowed_paths` now also hold `src/gov/codeintel/**` and `tests/unit/codeintel/**`, for one thing only: `callees(root, name)` beside `callers` in `gov.codeintel` (DP-6), in a commit of its own with a unit case, before the closure commit. Nothing else in the wrapper changes; read "W1-16 residuals" in `governance/project/bootstrap.md`.
- A closure never calls `gov.store.load` or `gov.codeintel.index`, starts no model, and never indexes this repository or a worktree of it.
- **The real code tool cannot run inside a launched worker's sandbox:** the engineer runs the tool-free cases and its unit tests in the foreground, says what it could not run, and you run the whole W1-20 suite (the 10 `local_only` code cases included) and the W1-16 suite yourself, each alone, making no other call in the worktree while W1-16 runs.
- If a `local_only` code case fails for a reason in the test and not in the code (nine of them have never run against an implementation), that is a test designer's turn (a fresh designer, a revision before the case has ever passed, reason stated), not an engineer's workaround.
- `/tmp/cbm-daemon-1000` and `/tmp/gov-cbm-1000` are not leftovers: nobody removes them.

## What you do, in order

1. `git merge w1/integrate`, with a message whose last paragraph has `Task: DAEO-jozo` and `Role: orchestrator`. Resolve nothing by hand; if it conflicts, abort and return PACKAGES. A containment flag on the merge is a record (DEC-254).
2. **Engineer** (brief A2, fresh): the `callees` commit, then `gov closure` (`src/gov/closure/command.py` alone builds the command, DEC-317). Estimate 100 lines. It commits before it ends its turn.
3. **Verify**: W1-20 alone, W1-16 alone, then every other suite under `tests/acceptance/`, `tests/unit` and the validator. Red by design, to report apart: W1-50.
4. Return DONE beginning with the sentence "not to be merged before the owner's answer on DP-5's stopping reason", or PACKAGES, with the commits, each suite's result, where the constant is, the residuals for `bootstrap.md` (the earlier round's included) and the learning metrics for the whole ticket (so far: 7 ambiguity packages, 0 KPI disputes), as your last message.

