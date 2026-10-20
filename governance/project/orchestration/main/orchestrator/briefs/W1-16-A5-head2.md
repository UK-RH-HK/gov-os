You are the ticket lead for ticket `DAEO-lkeb` (`W1-16`, "codebase-memory wrapper"), profile FULL, working only in the worktree `/home/usain/gov-os-worktrees/W1-16` on branch `w1/W1-16`. Its implementer is an engineer (brief A2). This is a short round on decided packages.

**Read this first: a headless lead's turn ends its background work.** After you start a worker in the background, wait for it in the foreground before you say anything: run a Bash call such as `until [ -s <the worker's .json log> ]; do sleep 20; done` with the longest timeout allowed, and repeat that call until the log has content. Only then read the result and go on.

## State of this ticket

- An earlier lead brought the branch to `b31670cc`: implemented, reviewed, 132 acceptance cases green. It left no checkpoint file: read the suite's README and `git log`.
- Its packages, decided in `docs/DECISION_REGISTER.md` on `w1/integrate` (read them after step 1):
  - **DEC-337**: DP-2 (A) and DP-3 (A), as built. Nothing to do.
  - **DEC-338** (DP-4 (C)): the wrapper sets a short per-repository directory of its own for the tool's daemon files (`CBM_RUNTIME_DIR`), outside the repository, and never uses the tool's shared default; a test shows the shared default is not used. The socket path limit is 108 bytes.
  - **DEC-339**: R-1, the token rule also flags a body that begins with `_` or `-` when the rest meets DEC-325; R-3, `gov.secrets` exposes a public function that says whether a path name holds a secret, and the wrapper stops importing private names (`src/gov/secrets/**` and `tests/unit/secrets/**` are in this ticket's paths); R-2, the engineer traces why a token holding the full alphabet run is never flagged when the gitleaks defaults are extended, and reports the cause. It does not fix R-2: the fix is a package.
  - **With the owner, not yours to settle:** DP-1 (the question set for hit@5) and whether the daemon may serve its loopback UI. Change nothing for them.
- Since the earlier lead ran, W1-46 and W1-25 were merged into `w1/integrate` and are green there; W1-17 (the lexical index) is in flight in another worktree and will call the new public function.

## What you do, in order

1. `git merge w1/integrate`, with a message whose last paragraph has `Task: DAEO-lkeb` and `Role: orchestrator`. Resolve nothing by hand; a conflict is a package. The containment flag on the merge is a record (DEC-254).
2. **Test design batch 3** (brief A1, a fresh designer, profile FULL), in proportion (about ten cases): DEC-338 (the daemon directory is per repository, short, outside the repository, and the shared default is untouched by a run); R-1 (bodies beginning with `_` and `-`, flagged and near misses, through the public interface of the secret filter and the gitleaks files; W1-15's cases stand); R-3 (the public function, by the name the designer fixes in the README: a path with a secret in a file or folder name, and one without). Tests added after implementation, reason "delegated decision".
3. **Check red**, then a fresh **engineer** (brief A2). It also does the R-2 trace and puts the cause, with the evidence, in its return.
4. **Verify** every suite under `tests/acceptance/`, `tests/unit` and the validator, with the prefix `PATH=$HOME/.nvm/versions/node/v22.23.3/bin:$PATH`. Run the W1-16 suite alone. W1-15 must stay green. Red by design, to report apart: W1-50 (26 failed, 17 passed). The W1-05 latency case (`test_a_call_waits_under_100_ms_p95_for_the_hook`) is sensitive to machine load: if it fails, re-run `tests/acceptance/W1-05/test_w1_05_live_hooks.py` alone before you treat it as red.
5. No reviewer pass this round. Workers do not write under `/tmp` outside their session scratchpad; say what, if anything, is left behind.
6. Return DONE with this round's commits, the results, the R-2 cause, this round's new residuals (the main orchestrator holds the earlier list) and the learning-metric changes (earlier totals: KPI disputes 4; rewrites after implementation 0; tests added after implementation 8 cases; production code and rules +201 / −6 against 50).

