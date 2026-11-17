---
name: reopen-old-ticket-needs-verify
description: "a reopened pre-11-06 ticket's plain KPI strings make gov brief refuse KPI_NO_VERIFY; append Verify clauses before the brief; and make worktrees with tools/new_worktree.sh (seeded), not bare git worktree add"
metadata:
  node_type: memory
  type: feedback
  originSessionId: acd80751-ac8f-4230-9bae-15c678a54895
  modified: 2026-11-16T05:48:18.944Z
---

On 2026-11-16 the W2-81 reopen (DEC-1197 (2)) hit `BRIEF_NOT_READY: KPI_NO_VERIFY S1..F5`: its 2026-10-29 KPI lines are plain strings with no `Verify:`. I appended ` Verify: <README section / self-tests / run that checks it>` to each line (no line text changed), noted it in the reopen paragraph for the owner's reading, and the brief built. I also made three worktrees with a bare `git worktree add`, then had to run `seed_store.py warm` by hand.

**Why:** gov brief's ready check applies to every ticket a lead or worker brief is built for, closed-and-reopened ones included; the seeded worktree is DEC-1032 (iv)'s form.

**How to apply:** before a reopen's brief, run `gov brief <role> <id> >/dev/null` and fix KPI_NO_VERIFY in the same commit as the reopen; quote failure lines when adding ": " to a plain YAML scalar. Create every lead worktree with `bash .gov-runtime/scratch/orchestrator/tools/new_worktree.sh <W2>` (an existing merged `w2/<W2>` branch: `git branch -f` it to w2/integrate first, after checking it is an ancestor). Related: [[check-before-ready-line]], [[brief-worker-model-launcher-picks]].
