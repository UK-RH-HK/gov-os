---
name: launch-worker-tree-is-cwd
description: launch_worker.sh runs the worker in the cwd tree unless LAUNCH_TREE is set; a test designer must be launched with LAUNCH_TREE=<W2>-tests
metadata:
  node_type: memory
  type: feedback
  originSessionId: 51a22e9c-4b7e-4ef3-b8d4-caa9a8236112
  modified: 2026-11-14T23:08:28.550Z
---

launch_worker.sh picks the worker's tree from the shell's cwd (or LAUNCH_TREE). Launched from the lead's tree, a test designer briefed to write in `<W2>-tests` lands in the lead's tree with the sandbox walling the tests tree (W2-188 td-4, 2026-11-14: stopped by pid at once, relaunched).

**Why:** the brief's "your tree" line does not move the sandbox; the launcher's tree does.
**How to apply:** for every test-designer launch, prefix `LAUNCH_TREE=/home/usain/gov-os-worktrees/<W2>-tests` (and a fresh log name, the stopped one's log stays). See [[check-before-ready-line]].
