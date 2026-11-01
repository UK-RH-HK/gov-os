# Brief: independent test designer, DAEO-wq2b (W2-97), STANDARD

You are a fresh independent test designer (MR-3). Ticket: `DAEO-wq2b` (`W2-97`, "the local merge queue"), profile STANDARD. You work only in the tests worktree `/home/usain/gov-os-worktrees/W2-97-tests` on branch `w2/W2-97-tests` (DEC-963); you never read or write the ticket's own worktree `/home/usain/gov-os-worktrees/W2-97`. Expect `GOV_ROLE=independent-test-designer` and `GOV_TICKET=DAEO-wq2b`. You write the ticket's acceptance tests from its KPI lines and the specification below, in parallel with an engineer who builds the tool from the same specification; you never read its work, and it never reads yours. You show your tests red.

## Your retrieval (DEC-963)

- Use the integration branch's store only, never the ticket worktree's: `cd /home/usain/gov-os-worktrees/W2-00-store && gov retrieve "<question>" --json`. For what changed on `w2/integrate` since that store's last refresh, read it with `git show w2/integrate:<path>`.
- **P-R1:** drop unread any `gov retrieve` result under the ticket's implementation paths (`governance/project/orchestration/tools/`, `tests/unit/orchestration/`), and name in your return any such result you were served.

## What you read

- The ticket file `.tickets/DAEO-wq2b.md` (read-only): its six success and four failure KPI lines, its `allowed_paths`, its sources.
- The decisions, in `docs/DECISION_REGISTER.md`: DEC-959 (item 1), DEC-968, DEC-979 (item 3), DEC-962 (the test lock ended), DEC-848, DEC-953 (item 4).
- `governance/project/orchestration/packages/ROLES-RESEARCH-1.md` §4 option (c) and §5.3 item 5.
- Existing code the queue follows, as it stands (read, never edit; it is the CTO's, untracked, not this ticket's implementation): `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/close_build.py` (how a close clones, selects, runs, re-runs a red alone, traces a red with and without the change, and finds a batch's culprit) and `select_tests.py` (the selection's JSON output).
- An existing acceptance suite as a pattern for layout (README, conftest, a ticket-prefixed support module): `tests/acceptance/W2-108/`.

## What you write

- Only under `tests/acceptance/W2-97/`, with a `README.md` that maps each KPI line (all six success lines and all four failure lines) to its tests and gives each test's expected red reason today (the tool does not exist on the ticket's base, so every test should fail because the tool file is missing, or say what else).
- **In proportion (STANDARD; DEC-951 item 5: the minimum that shows each line):** every KPI line's success and failure, plus the key edge cases the specification names (a flaky red that passes alone; a red that is not the batch's; a fail-closed batch). No combinatorial expansion. Aim for roughly 10 to 16 tests that run in well under two minutes together.
- **Stand-ins only (the ticket's acceptance line):** each test builds a planted git repository under pytest's `tmp_path` with a fake integration branch (`w2/integrate`, plus a `main` the tests check is never moved), planted ticket branches whose commits carry `Task:` trailers, and stub test, selection and prepare commands (for example small scripts the test writes, or `python3 -m pytest -q -p no:cacheprovider` over planted test files). A stub can record how many times it ran (to show "one run" and "skipped") and can move the planted integration branch during its first run (to show "the head moved while under test"). Strip the environment variables that would leak the outer pytest run into a stub (`PYTEST_ADDOPTS`, `PYTEST_XDIST_*`, `PYTEST_CURRENT_TEST`). Set a git identity for the planted repository's own commits. Always pass `--work` and `--queue` under `tmp_path`. **No test touches this repository's branches, its stores, `~/gov-os-runs/` or the network.**
- The tests run the tool as a subprocess, located relative to the repository root the tests sit in (`governance/project/orchestration/tools/merge_queue.py`), with `sys.executable`, so a run from the ticket worktree exercises that worktree's copy (DEC-732); the README says so.
- Tests check behaviour through the public interface only: the exit code, the integration branch's head (and that it is a merge commit whose parents are the old head and the approved commit, the very commit tested), the files in the queue folder (`approved/`, `ejected/`, `landed/`, `records/`) and their stated fields, and the stubs' own run counts. Never an internal name.
- **Red first:** run your suite to its end from your worktree (`PYTHONPATH=/home/usain/gov-os-worktrees/W2-97-tests/src TMPDIR=/tmp/gov-os-lead-W2-97 python3 -m pytest tests/acceptance/W2-97 -q -p no:cacheprovider -o tmp_path_retention_policy=failed`); every test must fail for the reason your README states. Then run `PYTHONPATH=/home/usain/gov-os-worktrees/W2-97-tests/src python3 -m pytest tests/acceptance/W2-97 --collect-only -q -p no:cacheprovider` and make sure nothing clashes on import with other suites (ticket-prefixed module names).
- An ambiguous KPI line or a point the specification leaves open is never a guess: if it blocks a test, return it as a package (question, why now, options, impact, reversibility, cost, recommendation, confidence); otherwise test only what the specification fixes and name the gap.
- No KPI here asks for an earlier ticket's test to be revised; if you find one does, name it, do not edit it.
- **Your share of the scratch budget:** 3 GB and 150,000 files and folders.

## Commit

Commit only `tests/acceptance/W2-97/`, in one commit, in your worktree:

    git commit -m "W2-97 acceptance tests: the local merge queue (DAEO-wq2b)" --trailer "Task: DAEO-wq2b" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-959, DEC-979, DEC-953, DEC-968" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

In your return, also give: your commit (12 digits), the test count, the KPI lines with their tests, the red reason as you saw it per test, and every point of the specification you found unclear.

