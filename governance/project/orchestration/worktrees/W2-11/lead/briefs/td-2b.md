Your lead's answer to P-W2-11-TD-3. It is decided ground, not a new decision: your brief allowed you to "fix the README's map to the form it reads only if that changes no test", and DEC-983 already puts the ticket's last success lines (the anti-drift kit, scope control, timing tests) in round 2, so no new case is needed in round 1.

Do this, in `/home/usain/gov-os-worktrees/W2-11-tests`, under the same rules as your first brief (Policy 2 (c): never read this ticket's implementation; the code under test per command; budget; command forms; refused twice, stop):

1. Rewrite the map in `tests/acceptance/W2-11/README.md` as the Markdown table `gov accept`'s runner reads (`src/gov/accept/runner.py`, `parse_map`): a `KPI` column and a `Test` (or `File`) column whose items are code spans, outside any fence. Name the lines by the ticket file's current numbering (`.tickets/DAEO-k7hz.md`: success-1 to success-16, failure-1 and failure-2, in the order they stand there). Each case goes under the ticket line it shows.
2. The README's own lines that are not ticket KPI lines (the card's lines: G13 versions, G15 judgement rules, DEC-791 (ii), nothing repository-scoped, and any other): put each under the ticket line it serves, if one plainly does; otherwise leave it out of the table and say so in the README's prose (`gov accept` counts unmapped cases without naming them; that is acceptable).
3. The lines with no case in round 1 (by DEC-983, round 2's: success-14, success-15, success-16, and any other with none): keep them out of the table and list them in the prose as round 2's, so `gov accept` reports no line no test proves.
4. Keep the expected red reasons in the prose or in a third column; change no test file.
5. Check it: `cd /home/usain/gov-os-worktrees/W2-11-tests && PYTHONPATH=/home/usain/gov-os-worktrees/W2-11-tests/src python3 -m gov.cli.main accept DAEO-k7hz --json` once. Report its per-line outcome and counts as it gives them (some lines may fail at this head for reasons outside your batch: the copies under `.claude/` and the validator are not built). If it still refuses the map, report its message and stop.
6. Commit: `git commit -m "<subject>" --trailer "Task: DAEO-k7hz" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-992, DEC-959, DEC-983" --trailer "Rewrite-Reason: DEC-959 item 6 (the README map in the form gov accept reads)" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`, after checking the hooks folder holds no `pre-commit` file.

`/tmp/gov-os-lead-W2-11` is read-only to your sandbox: keep the sandbox's own TMPDIR. Do not retry the refused clean-up call; name what you leave in your scratchpad.

Return as before: one message, the twelve fields first, each as a labelled line, any payload after (the table's line-to-case summary, the lines left for round 2, the `gov accept` result).

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

The twelve fields first, any payload after. Refused twice for the same call: stop and say so.
