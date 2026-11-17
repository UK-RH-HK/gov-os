---
name: worktree-add-then-mkdir-with-and
description: "chain mkdir of <tree>/.gov-runtime/scratch/empty-home after git worktree add with &&, never ;  — a failed add plus mkdir makes the folder and blocks every retry"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 40d041e4-ce6d-4cea-ac41-af1b96280996
  modified: 2026-11-16T09:50:25.001Z
---

Make a worker tree's empty-home only after `git worktree add` succeeded: `git worktree add ... && mkdir -p <tree>/.gov-runtime/scratch/empty-home`. With `;` a failed add (stale `w2/<W2>-tests` branch, 11-16 W2-56) still runs mkdir, so the path exists and the next add fails with "already exists"; a failed `-b` add also leaves the new branch behind (attach it without `-b`). Also: launch_worker.sh needs `--class Cn --model <id>` before the role.

**Why:** W2-56 tests run 11-16 lost three retries to this; each time I had to rmdir the stray folders first.
**How to apply:** check `git branch --list w2/<W2>-tests` first (delete it only if merged into the ticket head); chain the add and the mkdir with &&. See [[copy-td-logs-before-worktree-remove]], [[launch-worker-tree-is-cwd]].
