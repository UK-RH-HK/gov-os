Batch 2 of the same brief, in the same worktree (`/home/usain/gov-os-worktrees/W2-122-tests`, branch
`w2/W2-122-tests`), under the same standing rules (DEC-732 with this worktree's `src/`; never read the ticket's
implementation or anything in `/home/usain/gov-os-worktrees/W2-122`; retrieval only from the W2-00-store; refused twice
for the same call, stop and say so).

The behaviour seen: `gov accept DAEO-blwa --json`, run on the ticket branch with your tests merged, refused before
running any test, exit 1:
`ACCEPT_MAP_UNREADABLE: ticket DAEO-blwa: the README of tests/acceptance/W2-122/ has a map row naming no KPI line it can read`.

`gov accept` (W2-96, `src/gov/accept/runner.py` on `w2/integrate`, which you may read) reads the README's map tables:
every row that lists tests must start its KPI cell with a KPI line's name in a form it takes (`K1`, `S1`,
`success-1`, `F1`, `failure-1`, or several joined by `/`, `,`, `;` or `and`), numbered as the ticket file's `kpis`
block numbers its `success` and `failure` lines. A row whose KPI cell names no numbered line, while it lists tests in
backticks, refuses the whole run.

Do only this:

1. Correct the map in `tests/acceptance/W2-122/README.md` so that every row that lists tests names the KPI line(s)
   it serves in such a form, and the failure line is named as the ticket's first failure line. Change no test and no
   expectation; no other file.
2. Check it yourself: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-122-tests/src TMPDIR=/tmp/gov-os-lead-W2-122 python3 -m gov.cli.main accept DAEO-blwa --json`
   in your worktree (the base code: the tests run red, as before; what matters is that the map is read and each KPI
   line `success-1` to `success-5` and `failure-1` appears in its `lines`). If it would outlive the Bash tool's ten
   minutes, check the map instead with a small script file under `.gov-runtime/scratch/td/` that calls
   `gov.accept.runner.parse_map` on the README, and say which check you ran.
3. Commit only the README, with the trailers in the final block (a rewrite after the implementer's commit, DEC-491):

       git commit -m "W2-122 acceptance README: map rows name their KPI lines for gov accept" --trailer "Task: DAEO-blwa" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-1014, DEC-1015" --trailer "Rewrite-Reason: gov accept refused the map (ACCEPT_MAP_UNREADABLE): two rows named no numbered KPI line" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

   Then quote `git log --oneline -2` and `git status --short`.

Return in the twelve fields first, each as a labelled line (task, status, work_completed, files_changed, evidence,
tests, discoveries, risks, lessons, proposed_decisions, unresolved, recommended_next_action), any payload after them.
