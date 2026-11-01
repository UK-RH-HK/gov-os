Batch 1 accepted (45e57f00, 4f5dffc1). Your lead has since merged the independent test designer's tests into this branch (632e708b, `TESTS-READY` exists): you still never read `tests/acceptance/W2-11/`; you run them once in batch 4, reading results only.

**Now do batch 2 of your brief (the skill template and `qa-review`), commit it, and return** with the twelve fields first, as before, plus lines added and removed per file, the validator's result per skill, and your scratch figures. Every rule of your original brief still holds (sandbox, Policy 2, DEC-732, paths, budget, commands the guard can read, commits and trailers, two-refusal stop, AUTH_REQUIRED). Do not repeat step 0 unless the session restarted.

Notes from your lead for this batch:
1. **Proportion.** Batch 1 came to +963 −252 lines, already past the whole round's estimate (600 to 900). Keep batches 2 to 4 lean: the skill template under about 150 lines of body; `qa-review`'s SKILL.md under about 150 lines with detail one level deep only where it earns its place; the three scenarios short (a situation, the expected behaviour, how a fresh session is judged to have passed). No restating of rules the briefs already carry: refer to them.
2. **Write the scenarios first** in each case (the template's own three, then `qa-review`'s three), and commit so the order shows (scenarios in an earlier commit than the text, or say in the commit message how the order is shown).
3. **DEC-791 (ii):** your reading stands: each listed decision's part that holds in any repository goes in the kernel with its id (your lead's decision).
4. **The role file's "tests first" sentence and its `gov launch` code spans** stay as they are (another ticket holds the rest of that file): name them in your return's `unresolved`, as you did.
5. Scratch: your session scratchpad is fine (the Write tool is refused under `.gov-runtime/scratch/ps/`).
6. `gov retrieve` may still answer STORE_MISSING (the store's rebuild is queued behind others); try it once at the start of the batch and report.

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
