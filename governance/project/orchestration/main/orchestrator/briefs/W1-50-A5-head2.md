You are the ticket lead for ticket `DAEO-xnbx` (`W1-50`, "Containment attribution by commit trailers"), profile FULL, working only in the worktree `/home/usain/gov-os-worktrees/W1-50` on branch `w1/W1-50`.

**This run is test design batch 2 only (owner decision DEC-256).** You run steps 1 and 2 of the loop and then return. You start no engineer and no reviewer: the implementation waits until W1-46, which touches the same guard files, is merged.

**Read this first: a headless lead's turn ends its background work.** After you start a worker in the background, wait for it in the foreground before you say anything: run a Bash call such as `until [ -s <the worker's .json log> ]; do sleep 20; done` with the longest timeout allowed, and repeat that call until the log has content. Only then read the result and go on.

## State of this ticket

- Test design batch 1 is on the branch (`d2ab1147`) and was merged into `w1/integrate`: 43 cases in `tests/acceptance/W1-50/`, 26 failed and 17 passed by design, and the W1-01 history test revised. Read the suite's README.
- All seven packages of batch 1 are decided. Read them in `docs/DECISION_REGISTER.md` after step 1:
  - delegated: DEC-266 (DP-1: only a merge in an orchestrator session's own call is judged commit by commit), DEC-267 (DP-2: own-trailer judging needs both trailers in the final block), DEC-268 (DP-3: trailers that name nothing valid allow nothing), DEC-269 (DP-6: a path the merge commit itself changes is judged by the merge commit's trailers), DEC-270 (DP-7: the finding record keeps the caller's role and ticket);
  - owner: DEC-318 (DP-4: a commit whose trailers name a closed ticket is judged by that ticket's role and `allowed_paths` only if it is an ancestor of the ticket's close commit, otherwise it is a finding; a commit naming a ticket that was never started is a finding) and DEC-319 (DP-5, option (b): in a worker's call, a commit whose `Role` trailer differs from the caller's role is a finding; own-trailer judging applies only in an orchestrator session's own call).

## What you do, in order

1. **Take `w1/integrate` into this branch first**: `git merge w1/integrate` (it should be a fast-forward or a clean merge; for a merge commit, the message's last paragraph has `Task: DAEO-xnbx` and `Role: orchestrator`). Resolve nothing by hand; if it conflicts, abort and return PACKAGES saying so. A containment flag on the merge is a record (DEC-254).
2. **Test design batch 2** (brief A1, one fresh designer, profile FULL, DEC-221). Nothing is implemented, so these are revisions and additions before implementation. The designer:
   - checks every existing case against DEC-266 to DEC-270, DEC-318 and DEC-319, and revises the cases an answer makes wrong;
   - adds the cases the decisions need, in proportion: DEC-319 (a worker's call with another role's trailer is a finding; the same commit in an orchestrator session's own call is judged by its trailers); DEC-318 (a closed ticket's commit that is an ancestor of the close commit passes inside that ticket's paths; one that is not an ancestor is a finding; a ticket never started is a finding); DEC-269 (a merge commit's own change under `tests/acceptance/**` is a finding, elsewhere it is not); DEC-267 and DEC-268 where no case holds them yet;
   - states in the README how a test recognises "the ticket's close commit" (the suite builds its own temporary repository and tickets; the decision does not say how the check finds the close commit, so if the sources leave that open, it is a package with a recommendation, the fail-closed reading preferred);
   - reports the W1-03 case `test_a_merge_that_is_not_a_fast_forward_is_flagged` again: under DEC-266 it stays right and is left unchanged.
3. **Check yourself:** the W1-50 suite is red for the README's reason, with the green cases being those that describe behaviour holding today; W1-01, W1-02, W1-03, W1-45 and W1-47 are unchanged and green (run them). You need not run the other suites in this run.
4. Return `DONE` for the batch (say "test design batch 2 only"), with the commits, the counts, the red reason, and any packages in full.

