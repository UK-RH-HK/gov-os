A follow-up for your tests, in the same worktree (`/home/usain/gov-os-worktrees/W2-104-tests`, branch `w2/W2-104-tests`), under the same brief and rules as before (Step 0's sandbox check again first; Policy 2 (c): never read this ticket's implementation; refused twice for the same call, stop and say so).

The behaviour seen: once your tests were merged into the ticket's worktree, `gov accept DAEO-drhj` (the opaque acceptance runner, W2-96, DEC-959 item 6) refused before running anything: `ACCEPT_NO_MAP: ticket DAEO-drhj: the README of tests/acceptance/W2-104/ maps no KPI line`. The runner reads the README's map from a table whose header row has a column whose title starts with `KPI` and a column whose title starts with `Test` or `File` (case-insensitive); its rows name a KPI line (`Success 1`, `F1`, ...) in the KPI column and test files or case names in code spans in the test column. Your table's second column is titled `Cases`, so the table is not read. The runner's own reader is `src/gov/accept/runner.py` on `w2/integrate` (`parse_map`, `line_names`), which you may read.

What to do:
- Fix only `tests/acceptance/W2-104/README.md` so the runner reads a map naming every KPI line (success 1 to 4, failure 1 to 3) with its cases. Change no test and lower no expectation.
- Check it in your worktree with the runner itself: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-104-tests/src python3 -m gov.cli.main accept DAEO-drhj --json` (on your base every case still fails, which is expected; what counts is that every KPI line appears with its cases and none is unmapped). Quote the per-line counts.
- Commit only the README, with the trailers in the final block:
  `git commit -m "W2-104 tests: the README's KPI map in gov accept's form (a Tests column)" --trailer "Task: DAEO-drhj" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-959,DEC-820" --trailer "Rewrite-Reason: DEC-959 item 6: gov accept reads the map from a Tests column; the README's map was unreadable (ACCEPT_NO_MAP)" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`

Return: your last message, complete in itself, with the twelve fields first, each as a labelled line, any payload after them; include the commit's 12-digit hash, the runner's per-line result, the read refusals and other refusals you met, and your scratch figures. Refused twice for the same call: stop and say so.

```
task: <what you were asked to do, in one line>
status: <DONE | PACKAGES | ESCALATION | ESCALATION_BLOCKED | LAUNCH_BLOCKED | AUTH_REQUIRED, and one line of why>
work_completed: <what was done>
files_changed: <each path, or "none">
evidence: <commits with their trailers, logs, command outputs that show it>
tests: <each suite run, with its counts, or "none run">
discoveries: <what you found that was not known, or "none">
risks: <what could go wrong with what was done, or "none">
lessons: <what the next worker should know, or "none">
proposed_decisions: <each package, with your recommendation and confidence, or "none">
unresolved: <what is still open, or "none">
recommended_next_action: <one line>
```
