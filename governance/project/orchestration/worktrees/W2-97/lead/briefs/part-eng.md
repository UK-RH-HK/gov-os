# Brief: engineer, DAEO-wq2b (W2-97), STANDARD

You are a fresh engineer. Ticket: `DAEO-wq2b` (`W2-97`, "the local merge queue"), profile STANDARD. You work only in the worktree `/home/usain/gov-os-worktrees/W2-97` on branch `w2/W2-97`. Expect `GOV_ROLE=engineer` and `GOV_TICKET=DAEO-wq2b`. You build the tool to the specification below and the ticket's KPIs, never to the tests: an independent test designer writes the acceptance tests at the same time in another worktree, from the same specification.

## Your retrieval

This worktree's own store is still being built (the machine's rebuild lock is queued), and until you commit this worktree holds nothing the integration branch does not, so use the integration branch's store: `cd /home/usain/gov-os-worktrees/W2-00-store && gov retrieve "<question>" --json` (a read; for what changed on `w2/integrate` since its refresh, `git show w2/integrate:<path>`). Once `/home/usain/gov-os-worktrees/W2-97/.gov-runtime/scratch/lead/log/rebuild.rc` holds `0`, you may also use this worktree's own: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-97/src python3 -m gov.cli.main retrieve "<question>" --json`, run in this worktree.

## What you read

- The ticket file `.tickets/DAEO-wq2b.md` (read-only): its KPI lines and its `allowed_paths`.
- The decisions, in `docs/DECISION_REGISTER.md`: DEC-959 (item 1), DEC-968, DEC-979 (item 3), DEC-962 (the test lock ended), DEC-848 (agents never push), DEC-953 (item 4).
- `governance/project/orchestration/packages/ROLES-RESEARCH-1.md` §4 option (c) and §5.3 item 5.
- **The CTO's close tool, which the queue's steps follow and later replace** (read it, never edit it; it is untracked): `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/close_build.py` — the clone, the rebuild, the selection, the parallel and serial runs, the alone re-run, the trace with and without the change (`trace_node`, `decisive`, `attribute`) and the culprit search (`assign_culprits`, `explained_without`, `red_alone`, `merge_is_own`); its tests `tools/test_close_build.py` (26 cases, reviewed three times on 2026-10-31); and `tools/select_tests.py` (the one selection, DEC-953 item 4). **Reuse the reviewed functions' logic: copy what you need into the tracked tool (never import from scratch, it is untracked), and carry their test cases into your unit tests.** Where the queue differs (it makes the merges itself, so "without a ticket" can be built by merging the others rather than reverting), keep the same verdicts and the same fail-closed rules.
- **Never read this ticket's acceptance-test code** (DEC-820 (c)): nothing under `tests/acceptance/W2-97/`, by any tool. You may run those tests and read their results (names, pass or fail, failure messages), never their source.

## What you write

- Only inside the ticket's `allowed_paths`: `governance/project/orchestration/tools/merge_queue.py` (the folder does not exist yet: you make it), `governance/project/orchestration/tools/README.md` (what the queue does, how the CTO approves and runs it, the queue folder's files, the record the close cites, the stand-in options, the exit codes) and your unit tests `tests/unit/orchestration/test_w2_97*.py` (no `__init__.py`: it is outside the paths; use ticket-prefixed module names). Nothing under `src/`, nothing under `.gov-runtime/scratch/orchestrator/`, never `tests/acceptance/**`.
- **Size:** about 250 lines of tool and 150 of unit tests is the estimate; the specification is the requirement, not the estimate. Proportion (DEC-135): no code for edge cases beyond the KPI lines and the specification. **Never make a gate fail open:** the branch moves only to a tested commit, only by fast-forward, and every uncertain case (a red no ticket explains, a candidate that cannot be isolated, a run that did not complete) keeps the branch where it was.
- **Unit tests (your test-driven development):** in `tests/unit/orchestration/`, with planted git repositories under pytest's `tmp_path` and stub commands; no test touches this repository's branches, its stores, `~/gov-os-runs/` or the network. Run them with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-97/src TMPDIR=/tmp/gov-os-lead-W2-97 python3 -m pytest tests/unit/orchestration -q -p no:cacheprovider -o tmp_path_retention_policy=failed`, to the end. Also run `PYTHONPATH=/home/usain/gov-os-worktrees/W2-97/src python3 -m pytest tests/unit/orchestration --collect-only -q -p no:cacheprovider` to see no import clash.
- **The acceptance tests arrive while you work (DEC-963):** your lead merges them into this worktree between your batches (your sandbox mounts the acceptance tests read-only). Commit your work first. Then, if `/home/usain/gov-os-worktrees/W2-97/.gov-runtime/scratch/lead/TESTS-READY` exists, run them once, reading results only: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-97/src TMPDIR=/tmp/gov-os-lead-W2-97 python3 -m pytest tests/acceptance/W2-97 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rA`, to the end, and report each test's name and result. A failing acceptance test you believe is wrong is a package, never something to work around. If the file does not exist when you are done, say so and return: your lead starts a fresh session to run them.
- **Your share of the scratch budget:** 5 GB and 250,000 files and folders.
- A point the specification leaves open that you cannot settle inside it: decide it inside the ticket's paths if it is reversible and changes no KPI (say so in your return), else return a package.

## Commit

Commit only your paths, with the trailers in the final block:

    git commit -m "W2-97: the local merge queue (DAEO-wq2b)" --trailer "Task: DAEO-wq2b" --trailer "Role: engineer" --trailer "Implements: DEC-959, DEC-979, DEC-953, DEC-968" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

In your return, also give: your commits (12 digits), the files changed, the lines added and removed, your unit tests' and (if run) the acceptance tests' results by name, and every point of the specification you had to decide.

