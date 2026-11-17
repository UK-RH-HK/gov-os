---
name: copy-td-logs-before-worktree-remove
description: "a test designer's launch logs live in the -tests worktree's ignored .gov-runtime; `git worktree remove` deletes them; copy them to the lead records first"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 0227d6e2-43be-40b5-8934-43a15e9e0a68
  modified: 2026-11-15T05:50:04.062Z
---

With LAUNCH_TREE=<W2>-tests, launch_worker.sh writes the test designer's log, summary, tripwire and exit files under `<W2>-tests/.gov-runtime/scratch/lead/log/`. That folder is git-ignored, so `git worktree remove` deletes it without warning. W2-178 lost td-1's logs this way on 2026-11-15; its return survived only in the lead's transcript.

**Why:** the hand-over and the return have to point at worker logs that still exist.

**How to apply:** before tests_worktree_remove, `cp -a <W2>-tests/.gov-runtime/scratch/lead/log/td-*` into the lead tree's `.gov-runtime/scratch/lead/log/`. Related: [[launch-worker-tree-is-cwd]].
