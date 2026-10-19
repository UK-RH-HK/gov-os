You are the ticket lead for ticket `DAEO-7nne` (`W1-15`, "Secret rules and pre-index filter"), profile FULL, working only in the worktree `/home/usain/gov-os-worktrees/W1-15` on branch `w1/W1-15`. You run one short round of the ticket loop.

**Read this first.** A headless lead's turn ends its background work. After you start a worker in the background, wait for it in the foreground before you say anything: run a Bash call such as `until [ -s <the worker's .json log> ]; do sleep 20; done` with the longest timeout allowed, and repeat that call until the log has content. Only then read the result and go on.

## State of this ticket

- Two earlier leads brought the branch to head `e9311c8a`: 80 cases green, every other suite green, reviewed, six reviewer findings fixed. The lead checkpoint in `.gov-runtime/scratch/lead/CHECKPOINT.md` describes it; read it.
- One reviewer finding was left for a decision, and it is decided: **DEC-298 (F9)**. DEC-290 made the pre-index filter ignore path allowlists. It also ignores the other ways a project's `.gitleaks.toml` can shelter a secret: allowlist `regexes` and `stopwords`, per-rule allowlists, and disabled rules. A file that holds a secret by the rules never reaches an index, whatever the project's file allows. The decision is on `w1/integrate`; you may `git merge w1/integrate` first (trailers `Task: DAEO-7nne`, `Role: orchestrator` in the last paragraph; a clean merge only; the containment flag on it is a record, DEC-254).

## What you do, in order

1. **A short test design round** (brief A1, a fresh designer, profile FULL) for DEC-298 only, as a described behaviour (DEC-136): a planted secret sheltered in turn by an allowlist regex, a stopword, a per-rule allowlist and a disabled rule is still dropped by `gov.secrets.indexable`; the secrets-indexing check is not made green by them either, if it reads the same file. Tests added after implementation, reason "probe finding".
2. **Check red** yourself.
3. **Engineer** (brief A2, fresh), the smallest change that makes them green without loosening anything.
4. **Verify** every suite and the validator; W1-46 and W1-50 are red on this branch from their own tickets (W1-50 by design); report them apart.
5. Return DONE with the whole ticket's summary: all commits; the residuals of the earlier lead that still stand (its list of thirteen, minus F9); learning metrics for the whole ticket (so far: KPI disputes 0; ambiguity packages 6; rewrites after implementation 0; tests added after implementation 21 cases; code 131 lines against 70, configuration 45, builder tests 82; converged).

