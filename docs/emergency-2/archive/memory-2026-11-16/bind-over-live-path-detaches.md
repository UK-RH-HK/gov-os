---
name: bind-over-live-path-detaches
description: "a bwrap bind over a live host path is unmounted when the host renames over it; freeze on sandbox-private tmpfs (job runner round 7, 11-16)"
metadata:
  node_type: memory
  type: feedback
  originSessionId: acd80751-ac8f-4230-9bae-15c678a54895
  modified: 2026-11-16T03:53:08.879Z
---

A bind mount placed on a dentry the host can change (for example `--ro-bind-fd frozen live/tool.sh`) gets detached by the kernel when the host renames another file over that path or unlinks it. A mount point in another mount namespace is unmounted on rename. So the sandbox sees the new bytes. Tested 2026-11-16 with bwrap 0.9: `FROZEN`, then `SWAPPED-BY-RENAME`. bwrap 0.9 also has no `--overlay-src`, and it cannot mkdir on a read-only `/` (so `/sets` is not possible; the job runner uses `/mnt/sets`).

**Why:** review 7 asked for exactly that per-file bind. Building it as asked would have shipped a hole that a rename reopens.

**How to apply:** anything a sandboxed job must see frozen has to stand on a mount point inside the sandbox's own tmpfs (HOME or /tmp), with its parents made by bwrap (`--tmpfs root`, `--dir`, binds, then `--remount-ro`). Test a reviewer's mechanism against a rename during the run before building it. See [[pytest-through-heavy-slot]].
