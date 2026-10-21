
## Parallel run: containment records that are not defects (DEC-254, 2026-10-04)

Until W1-50 (`DAEO-xnbx`) judges a HEAD move commit by commit, by each commit's own `Role` and `Task` trailers, the
post-command containment check (W1-03) writes two kinds of finding for permitted actions of the parallel run
(DEC-235). The owner accepted both as records, not defects (DEC-254). Each is also noted in its ticket's close row in
the orchestrator's checkpoint.

- **An integration merge.** The check flags any HEAD move that contains a merge commit ("HEAD moved (not a forward
  move on the same branch)"). Every merge of a ticket branch into `w1/integrate` by the main orchestrator, as the
  orchestrator prompt's section 3 prescribes, writes one such line to `.gov-runtime/findings.jsonl` in the main tree.
  First seen: the merge of `w1/W1-37`, commit `00e3d539`.
- **A worker's commit attributed to its lead.** In a ticket's worktree the lead (role orchestrator) waits for its
  worker with its own Bash calls. When the test designer commits under `tests/acceptance/<W1-id>/` during such a
  call, the check attributes the commit to the lead's call and flags "committed path(s) outside allowed paths" in
  that worktree's `.gov-runtime/findings.jsonl`. The commit is the designer's, in the designer's scope. Seen in the
  worktrees of W1-37, W1-18 and W1-08. A worktree's findings file is copied to
  `.gov-runtime/scratch/orchestrator/log/<W1-id>-findings.jsonl` in the main tree before the worktree is removed.
- **The W1-01 history test** failed on the first integration merge for the same reason, and is revised under
  DEC-253 in W1-50's test design batch.
