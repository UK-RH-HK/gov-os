---
name: auditor-brief-step0-path-no-find-root
description: "worker briefs name the step-0 file's literal path and forbid `find /`; au-1 on W2-191 walked the eval root with `find / -not -path` hunting EMG-d4b-launched.md (11-16)"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 89b1ca32-6712-49cd-a23c-727748f78929
  modified: 2026-11-16T16:52:22.508Z
---

W2-191 au-1 (2026-11-16) looked for `EMG-d4b-launched.md` with `find / -name ... -not -path '*/gov-os-eval/*'`.
`-not -path` does not prune, so find walked into the evaluation sets' root (no path printed, no content read; the
hidden folders are sandbox-denied, the root itself is not). This was a wall breach, reported to the owner in the return.

**Why:** the brief said "do step 0 of EMG-d4b-launched.md" without its path, and the worker searched the whole disk.

**How to apply:** every worker brief gives the literal path `<tree>/.gov-runtime/scratch/brief/EMG-d4b-launched.md`
and the line "never search from / or from /home/usain; search only the named trees". Related: [[check-before-ready-line]].
