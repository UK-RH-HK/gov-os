Batch 2 of the same brief. The lead has merged the acceptance tests into this worktree:
`/home/usain/gov-os-worktrees/W2-122/.gov-runtime/scratch/lead/TESTS-READY` now exists. Your standing rules are those of
your batch-1 brief, unchanged (DEC-732: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-122/src` per command; never read
`tests/acceptance/W2-122/`; refused twice for the same call, stop and say so).

Do only this:

1. Run `printenv GOV_ROLE GOV_TICKET` and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `engineer`,
   `DAEO-blwa`, `/home/usain/gov-os-worktrees/W2-122`, `w2/W2-122`) and `git log --oneline -3`.
2. Run the acceptance tests once, reading results only, through
   `PYTHONPATH=/home/usain/gov-os-worktrees/W2-122/src TMPDIR=/tmp/gov-os-lead-W2-122 python3 -m gov.cli.main accept DAEO-blwa --json`
   only (never `pytest` on `tests/acceptance/`). If it would outlive the Bash tool's ten minutes, say so and return.
3. Report pass or fail per KPI line and the counts. `docs/changes/W2-122-evidence.md` (KPI 3) is not yet written: a
   red on it is expected and you do not write it in this batch. For any other red, describe the failing behaviour as
   `gov accept` reports it (names and messages only); change no code in this batch and commit nothing.

Return in the twelve fields first, each as a labelled line (task, status, work_completed, files_changed, evidence,
tests, discoveries, risks, lessons, proposed_decisions, unresolved, recommended_next_action), any payload after them.
