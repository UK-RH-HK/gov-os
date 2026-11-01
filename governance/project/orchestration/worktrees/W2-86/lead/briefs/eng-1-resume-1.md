Your lead's review of commit 3bc60ad31987 against the specification: one correction, nothing else.

The specification says `kernel-template` changes **only its `paths` and its `embedding_policy`**. Your commit also changed its `provenance` from `written under a ticket; vendored parts are pinned in the tool registry` to `written under a ticket; git history`. Restore the original value exactly (`provenance: written under a ticket; vendored parts are pinned in the tool registry`), changing nothing else in the file. Keep the new namespaces as they are.

Then: re-run `PYTHONPATH=/home/usain/gov-os-worktrees/W2-86/src python3 -m gov.check.pathmap`, your unit test, and the acceptance tests once (results only), and `git diff 9dc5288161c4 -- governance/project/path-map.yaml` (quote that the provenance line no longer appears in it). All the rules of your first brief still hold (sandbox, DEC-732, DEC-820 (c) and (d), command forms, no hooks check skipped, refused twice: stop). Commit as a new commit (no amend):

    git commit -m "W2-86 (DAEO-jsg1): kernel-template keeps its provenance unchanged; only its paths and its embedding policy move" --trailer "Task: DAEO-jsg1" --trailer "Implements: DEC-952, DEC-388" --trailer "Role: engineer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

Then `git log --oneline -2` and `git status --short`, quoted.

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

Your return gives the twelve fields first, each as a labelled line, with any payload after them. Refused twice for the same call: stop and say so.
