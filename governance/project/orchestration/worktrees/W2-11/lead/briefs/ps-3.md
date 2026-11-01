Batch 2 accepted (adeda5b8, 99dd5ca5). **Now do batch 3 of your brief (the test-design skill's additions and orchestration's three reference files), commit it, and return** with the twelve fields first, as before, plus lines added and removed per file, the validator's result per skill touched, and your scratch figures. Every rule of your original brief still holds. Step 0 again only if this is a new launch (it is: report it as before).

Notes from your lead for this batch:
1. **P-5:** keep `scenarios.md` (situation, expected behaviour, pass line) as the form; your lead names it for the skill harness's ticket. Nothing to do for it now.
2. **test-design:** its "written before implementation" wording goes (DEC-959's Swept line): the designer works from the spec in parallel with the implementer, never reading its work, and shows its tests red against the ticket's base. Add the items of batch 3 lean, with detail in a reference file one level deep if the body would pass the validator's limit; link it from SKILL.md. The README map in the form `gov accept` reads: take it from its KPI lines (`.tickets/DAEO-ouet.md`) and, if useful, from its in-progress code on branch `w2/W2-96` (`git show w2/W2-96:<path>`); if its form is not settled there, state the map's content (each KPI line, the tests under it, the expected red reason) and say the exact syntax follows that runner.
3. **orchestration:** the three reference files (integration-queue, nightly-sheriff, incident-response), each short and for any repository (placeholders for the project's tools, branches and record paths), linked from SKILL.md in a line each; SKILL.md's body must stay under the validator's limit (it is at 2,319 of 2,500 tokens): shorten elsewhere if needed rather than drop a rule.
4. Proportion: lean, as for batch 2.

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
