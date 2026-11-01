## The repair (this batch's whole task)

The ticket is built and its 76 acceptance tests pass. One measured defect is left, and this batch fixes only it.

**The failing output (the lead's measurements on this worktree, head `0263e8c4e828`, under the same machine load):**

- `gov check --json`: `context reproducibility: RED` — "context-reproducibility did not end within its time limit of 600 seconds". That check computes the context of each of the project's 180 tickets twice (`src/gov/context/context_check.py`).
- One `gov.context.context(root, "DAEO-arrl")` call, profiled: 1.996 s in all; the supplementary part 1.730 s; the retrieval 1.187 s; **the new register filter `leave_out` 0.504 s, of which the register's read and parse at `HEAD` 0.410 s** (`src/gov/decisions/register.py`, `read`). The register is read and parsed again on every call, though it changes only with `HEAD`.
- Ten tickets, two contexts each: 3.44 s per ticket with the base's code, 4.64 s with this branch's code. Over 360 contexts the filter adds about 180 s.

**What to change:** the register's reading must cost its parse once per process for one `HEAD` (and one register file), not once per call: the same `root`, `HEAD` commit and register give the same answer without parsing again; any change of `HEAD` (a new commit) or of the root reads afresh, so no stale register is ever served. Every caller of the read (the filter in `gov context` and `gov retrieve`, `--in-force`, the two register checks) keeps its behaviour exactly. Nothing fails open: a register that cannot be read still refuses as before. Stay in `src/gov/decisions/**` (and `tests/unit/decisions/**` for a builder test of the cache: a second call does not parse again, and a new commit is read afresh). Do not touch `src/gov/retrieval/**`.

**Then:** commit; run `tests/unit/decisions` and the ticket's acceptance tests once (`PYTHONPATH=/home/usain/gov-os-worktrees/W2-55/src python3 -m pytest tests/acceptance/W2-55 -q -p no:cacheprovider --tb=no -rfE -o tmp_path_retention_policy=failed`, results only, never the source); and give, in your return, the same ten-ticket timing as above with your code (`for` the first ten tickets of `gov.context.context_check.project_tickets(root)`, two `context()` calls each, wall time per ticket), and one profiled call's `leave_out` and `read` times.
