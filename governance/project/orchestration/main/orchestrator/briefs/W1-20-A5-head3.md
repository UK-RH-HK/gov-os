You are the ticket lead for ticket `DAEO-jozo` (`W1-20`, "gov closure"), profile STANDARD, working only in the worktree `/home/usain/gov-os-worktrees/W1-20` on branch `w1/W1-20`. This is the ticket's last, short round.

**Read this first: a headless lead's turn ends its background work.** After you start a worker in the background, wait for it in the foreground before you say anything: run a Bash call such as `until [ -s <the worker's .json log> ]; do sleep 20; done` with the longest timeout allowed, and repeat that call until the log has content. Only then read the result and go on. **Your summary is your last message**: after you have written DONE or PACKAGES, write nothing more, even if a notification about an earlier wait arrives.

## State of this ticket

- Branch head `92d2346a`: `gov closure` built; W1-20 46 of 49. The three failures stop only on `stopping_reason in REASONS`: the tests' support file `w1_20_support.py` has a fixed list of five values.
- **Decided by the owner: DEC-396.** The stopping reason when unresolved ids are the only gaps is `UNRESOLVED_IDS`, the sixth value; ADR-0002 §4 is amended (`13a3f8ba`). A test designer adds the value to the tests' list. The constant `UNRESOLVED_ALONE` in `src/gov/closure/__init__.py` already has that spelling.
- **Decided, delegated: DEC-393.** DP-A (a): the order is `FACET_UNAVAILABLE`, then `DEPTH_LIMIT_REACHED`, then `UNRESOLVED_IDS`, then `CLOSURE_COMPLETE`. DP-B (a): `facets.code` is `not_asked` when the facet was never asked. Both are what is built.
- Read DEC-391, DEC-393 and DEC-396 in `docs/DECISION_REGISTER.md` after step 1.
- A launched worker's scratchpad is removed when its session ends (DEC-386, merged): a worker returns what you need in its final message.
- The real code tool cannot run inside a launched worker's sandbox: you run the W1-20 suite yourself, alone.

## What you do, in order

1. `git merge w1/integrate`, with a message whose last paragraph has `Task: DAEO-jozo` and `Role: orchestrator`. Resolve nothing by hand; if it conflicts, abort and return PACKAGES. A containment flag on the merge is a record (DEC-254).
2. **Test designer** (brief A1, one fresh designer, a short turn): adds `UNRESOLVED_IDS` to `REASONS` (a revision of cases that have never passed, reason "owner decision, DEC-396"); where a case can now say more than "not `CLOSURE_COMPLETE`" for unresolved ids alone, it asserts `UNRESOLVED_IDS`; one case each for DEC-393's two points (a depth cut together with unresolved ids gives `DEPTH_LIMIT_REACHED`; a closure of records alone says `not_asked`) if none holds them; the README's readings are brought in line. Nothing else changes.
3. **Verify**: W1-20 alone (all green), then W1-07, `tests/unit` and the validator, then every other suite under `tests/acceptance/` (W1-16 alone, with no other call in the worktree meanwhile). Red by design, to report apart: W1-50.
4. If a new case is red for a reason in the code, one engineer turn (brief A2) fixes it inside the ticket's paths; say so.
5. Return DONE with the commits, each suite's result, the residuals for `bootstrap.md` (the whole ticket's list) and the learning metrics for the whole ticket (so far: 10 ambiguity packages, 0 KPI disputes; 17 W1-07 cases "planned: command implemented"; 1 acceptance case and 7 builder cases added after implementation; source +119 / −1 against 100), as your last message.

