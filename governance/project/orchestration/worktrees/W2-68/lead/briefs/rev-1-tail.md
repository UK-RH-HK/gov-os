
## Return

One message, your last, complete in itself. **The twelve fields come first, each as a labelled line** (label at the start of a line, a colon, at least one word; "none" where there is nothing), and any machine-readable payload after them:

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

After the twelve fields, the payload: **the probe record's full content**, ready for the lead to write to `docs/probes/DAEO-2gc7/PR-DAEO-2gc7.md`: a YAML frontmatter (`type: probe`, `task: DAEO-2gc7`, `reviewer_session: <your session id if you know it, else "see the lead's note">`, `reviewer_wrote_nothing: true`, `commissioned_by: orchestrator`, `judged_by: orchestrator`, `judgement: pass` or `fail`, `probed_commit: <the full id of the head>`), then the head probed, the method (what you ran), what you found sound, and each finding as a described behaviour, never as code (DEC-136): what was done, what happened, what should have happened, its severity, and its two lines `Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other`. Only a finding with "yes" and "fails open" or "loses work" fails the probe. Your `evidence` line also gives the `gov.__file__` line, whether you used `gov retrieve`, and the read refusals you met.
