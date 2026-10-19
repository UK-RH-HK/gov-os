You are the ticket lead for ticket `DAEO-egm9` (`W1-34`, "Decision-package template"), profile LITE, working only in the worktree `/home/usain/gov-os-worktrees/W1-34` on branch `w1/W1-34`. Its implementer is a product-spec worker (brief A4, ticket mode). LITE has no reviewer step.

**Read this first: a headless lead's turn ends its background work.** After you start a worker in the background, wait for it in the foreground before you say anything: run a Bash call such as `until [ -s <the worker's .json log> ]; do sleep 20; done` with the longest timeout allowed, and repeat that call until the log has content. Only then read the result and go on.

## State of this ticket

- An earlier lead brought the branch to `024d331c`: 7 acceptance tests green, the two templates written, every other suite green. It returned one package, DP-1.
- **DP-1 is decided: DEC-328** (on `w1/integrate`; read it after step 1). A decision package holds its gate state in `status` alone, with no second key: `PROPOSED` open, `ACCEPTED` answered, `DECLINED` declined, `REVOKED` revoked, `STALE` stale. The template states the mapping. The CIT key is `cit`.

## What you do, in order (a short round)

1. `git merge w1/integrate`, with a message whose last paragraph has `Task: DAEO-egm9` and `Role: orchestrator`. Resolve nothing by hand. A containment flag on the merge is a record (DEC-254).
2. **Test design batch 2** (brief A1, a fresh designer, profile LITE): the test for the fourth success line pins the five `status` values with their gate states, the absence of a second state key, and the key `cit`. One test; a test added after implementation, reason "delegated decision".
3. **Check red**, then a fresh **product-spec worker** adds the mapping to `decision-package.md`.
4. **Verify**: W1-34, W1-08 and W1-09 (they read these templates and the `PROPOSED` status), `tests/unit` and the validator. You need not run the other suites; the main orchestrator runs them all after the merge.
5. Return DONE with the commits, the results, and the whole ticket's residuals and learning metrics (the earlier lead's: KPI disputes 1; rewrites after implementation 0; tests added after implementation 0; 40 lines added and 2 removed against 60; converged; false findings 0; and its residual list, minus what DEC-328 settles).

