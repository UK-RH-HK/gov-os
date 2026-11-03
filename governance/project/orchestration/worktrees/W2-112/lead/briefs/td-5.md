The lead: the FULL review's round 1 found one blocking behaviour the tests miss. Write a test for it in `/home/usain/gov-os-worktrees/W2-112-tests`, under the same rules as before. Your first brief still holds in full: Policy 2 (c) and (d); `gov retrieve` from the W2-00-store only, with P-R1; the read refusals (DEC-849); DEC-732's `PYTHONPATH` rule; the guard's command forms; row W2-L423's rule; the scratch budget. Refused twice for the same call: stop and say so.

## The behaviour (a described behaviour, DEC-136; KPI success-7)

KPI 7 makes the owner's ACT that retires the GPU-slot stopgap a deliverable of this ticket. It is written as the last section of the research record `docs/research/W2-112-shared-reranker.md`, the same file your `test_w2_112_record.py` already reads. The reviewer found that the ACT as written is unsafe:

- **What was done:** the ACT tells the operator to remove the interim module and its `.pth` from the reranker environment as soon as W2-112 has merged, and lets the operator remove the slot lock files `/tmp/gov-os-rerank-gpu-0.lock` and `-1.lock` once no process holds them.
- **What happened:** only W2-112's own private worker carries the slot rule itself. The installed, pinned `gov` (`~/.local/bin/gov`, re-pinned only at ACT 2) and every other checkout and worktree still start private rerankers with the old worker, which relies on the module alone. With the module removed, those rerankers load on the GPU beside two held slots: a third copy, the crash state of DEC-1031. With the lock files removed while two rerankers hold them, a new reranker takes a fresh lock file and loads: three on two slots.
- **What should happen:** the ACT's precondition is that the installed `gov` and every tree that can start a reranker carry the worker's own slot rule (for example, after ACT 2's re-pin and once no worktree runs an older worker), not merely that W2-112 has merged; until then the module stays. The ACT never removes, and never tells the operator to remove, the slot lock files.

## What you do

- Add to `tests/acceptance/W2-112/` (README map included, its row under success-7, in the form `gov accept` reads) one test, or a few, that read the research record's last section, the ACT, and hold the behaviour above:
  - the ACT's precondition names the installed (pinned) `gov` or its re-pin, not W2-112's merge alone;
  - no command or step in the ACT removes the `/tmp/gov-os-rerank-gpu-*.lock` files.
  Keep the expectations to what the behaviour states; loose wording is fine (a document test).
- Run your new test against the current ticket head's document, read with `git show w2/W2-112:docs/research/W2-112-shared-reranker.md`. That is the research record, not code. If you prefer not to read it, run the test against a copy: `git show w2/W2-112:docs/research/W2-112-shared-reranker.md > /tmp/gov-os-lead-W2-112/td/doc.md`. It must fail for the stated reason. Also give the collection line.
- One commit, only `tests/acceptance/W2-112/`, trailers in the final block:

      git commit -m "W2-112 (DAEO-clon): the stopgap's retirement ACT keeps the slot rule for every tree (review round 1, F1)" --trailer "Task: DAEO-clon" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-1033,DEC-1032" --trailer "Rewrite-Reason: review round 1 finding F1, given as a described behaviour (DEC-136)" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

  First check the hooks folder.

## Return

One message, your last, complete in itself: the twelve fields first, each as a labelled line, any payload after. Give: the commit hash (12 digits), the tests added, the red reason as seen, the collection line, the read refusals, your scratch figures.

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
