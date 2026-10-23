## Commit

Commit only your test paths, a group at a time (the doctor revisions with one reason, the old-path case, the new KPI tests and their README, …), with the trailers in the final block (DEC-182, DEC-476):

    git commit -m "<subject>" -- <your paths> --trailer "Task: DAEO-9nys" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-889, DEC-898" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

A revision commit also carries `--trailer "Rewrite-Reason: <reason>"`. Before each commit check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (only `*.sample` files); if one is there, stop and return. Never `--no-verify`, never `core.hooksPath`. After each commit, check `git log --oneline -2` and `git status --short`.

## Return

Your last message, complete in itself. **The twelve fields come first, each as a labelled line** (label at the start of a line, a colon, at least one word; "none" where there is nothing), and any machine-readable payload after them. Put in it: the sandbox check (step 0) first in `work_completed`; every commit's hash with its trailers; the test count; each KPI line with its tests; the red reason as you saw it for each new test; for each revised case, its plant, red and green; every case you could not revise and why; the `gov.__file__` line; the collection line; your scratch figures; the read refusals met; whether you used `gov retrieve`; any package.

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

Refused twice for the same call: stop and say so; no third try.
