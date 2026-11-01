Your tests are merged into the ticket's worktree. `gov accept DAEO-qzrq --json` there refuses the run before any
test, with `ACCEPT_MAP_UNREADABLE`: "the README of tests/acceptance/W2-123/ has a map row naming no KPI line it can
read". `gov accept` (W2-96, `src/gov/accept/runner.py` as it stands on `w2/integrate`: `NAME`, `line_names`,
`parse_map`) reads a map row's KPI cell only when it begins with a line name such as `S1`, `KPI 1`, `success 1`,
`F1` or `failure 1` (several joined by `,`, `/`, `;` or `and`); your rows begin `1.` to `6.` and `Failure:`, so none
is read.

Do this, in your worktree `/home/usain/gov-os-worktrees/W2-123-tests` only, with every standing rule of your first
brief still in force:

1. Rewrite only the KPI cells of the map in `tests/acceptance/W2-123/README.md` so that each begins with its line
   name: `S1` to `S6` for the six success lines, in the ticket file's order, and `F1` for the failure line, keeping
   the rest of each cell's text. Change no test and nothing else.
2. Check it reads: in your worktree run
   `PYTHONPATH=/home/usain/gov-os-worktrees/W2-123-tests/src python3 -m gov.cli.main accept DAEO-qzrq --json`
   (one process, not a heavy step). On your base code it must report every line (success-1 to success-6 and
   failure-1) with its tests, all red, and no unmapped test; quote its per-line counts.
3. Commit only that file, with the trailers in the final block (a rewrite after the implementer's commit, DEC-491):

       git commit -m "W2-123 acceptance README: the map's KPI cells in gov accept's line names" --trailer "Task: DAEO-qzrq" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-1014, DEC-1017" --trailer "Rewrite-Reason: gov accept's map reader (W2-96) reads no KPI line from cells that begin with a bare number" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

   Then quote `git log --oneline -2` and `git status --short`.

Return as before: one message, your last, the twelve fields first, each as a labelled line (task, status,
work_completed, files_changed, evidence, tests, discoveries, risks, lessons, proposed_decisions, unresolved,
recommended_next_action), any payload after them. Refused twice for the same call: stop and say so.
