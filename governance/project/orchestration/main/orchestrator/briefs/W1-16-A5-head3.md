You are the ticket lead for ticket `DAEO-lkeb` (`W1-16`, "codebase-memory wrapper"), profile FULL, working only in the worktree `/home/usain/gov-os-worktrees/W1-16` on branch `w1/W1-16`. Its implementer is an engineer (brief A2). This is a short round on decided packages.

**Read this first: a headless lead's turn ends its background work.** After you start a worker in the background, wait for it in the foreground before you say anything: run a Bash call such as `until [ -s <the worker's .json log> ]; do sleep 20; done` with the longest timeout allowed, and repeat that call until the log has content. Only then read the result and go on.

## State of this ticket

- Earlier leads brought the branch to `78dfa97f`: implemented, reviewed once, 145 acceptance cases green. Read the suite's README and `git log`.
- Decided since, in `docs/DECISION_REGISTER.md` on `w1/integrate` (read them after step 1):
  - **DEC-346**: DP-5 (a), as built, nothing to do; DP-6 (a) and (c): the daemon directory's leftovers are a residual, and one test shows that no planted secret stands in `daemon_dir(root)` after an index run.
  - **DEC-347, the main work of this round.** gitleaks' built-in defaults carry a global allowlist that `[extend] useDefault = true` merges over the project's rules, so a canary or token that contains the alphabet run in any case, contains `false`, begins with `true`, ends with `null`, or contains the default uuid stopword passes the filter. The pre-index filter (`gov.secrets.indexable`) and the path-name check (`gov.secrets.path_holds_secret`) run a second scan with the project's rules alone, without `extend`, and refuse what either scan flags. The pre-commit hook and a plain `gitleaks` run are not changed in this round.
- With the owner, not yours to settle: DP-1 (the question set for hit@5) and the daemon's loopback UI. For the second, do one thing only: report whether the tool has a documented switch or environment variable that stops the daemon serving its UI on `127.0.0.1:9749` (read the tool's `--help` output; install nothing, change nothing).
- W1-17 (the lexical index) is now merged into `w1/integrate`. Its `src/gov/retrieval/lexical.py` imports `gov.secrets.CONFIG_REL` and calls `gov.secrets.indexable`: keep both names and their behaviour for a clean file. Its suite, `tests/acceptance/W1-17/`, must stay green.

## What you do, in order

1. `git merge w1/integrate`, with a message whose last paragraph has `Task: DAEO-lkeb` and `Role: orchestrator`. Resolve nothing by hand; a conflict is a package. The containment flag on the merge is a record (DEC-254).
2. **Test design batch 4** (brief A1, a fresh designer, profile FULL), in proportion (about twelve cases): DEC-347 through the public interface of the filter (`indexable` and `path_holds_secret`): a canary and a token each sheltered today by the alphabet run (lower and upper case), by `false`, by a leading `true`, by a trailing `null` are refused, in a file's content and in a path name; clean files and names with those words and no secret are still indexable; W1-15's and W1-17's cases stand. DEC-346: the one daemon-directory test. Tests added after implementation, reason "delegated decision". Planted strings are canaries or made-up tokens, never a real credential.
3. **Check red**, then a fresh **engineer** (brief A2). The filter must not fail open: if the second scan cannot run, the file is refused.
4. **Verify** every suite under `tests/acceptance/`, `tests/unit` and the validator, with the prefix `PATH=$HOME/.nvm/versions/node/v22.23.3/bin:$PATH`. Run the W1-16 suite alone. Red by design, to report apart: W1-50 (26 failed, 17 passed). The two 100 ms latency cases (`test_a_call_waits_under_100_ms_p95_for_the_hook` in W1-05 and `test_decision_p95_is_under_100_ms` in W1-02) are sensitive to machine load: if one fails, re-run its file alone before you treat it as red. Report how much longer the W1-15, W1-16 and W1-17 suites take with the second scan.
5. No reviewer pass this round. Workers do not write under `/tmp` outside their session scratchpad and the wrapper's own directory; say what is left behind.
6. Return DONE with this round's commits, the results, the answer on the UI switch, this round's new residuals and the learning-metric changes (earlier totals: tests added after implementation 21 cases; production code and rules +249 / −26 against 50).

