---
name: launched-path-is-short
description: "launched/headless sessions have a 5-entry PATH; interactive CTO sessions 46 (27 on /mnt/c) — a PATH-dependent cost only shows with the real session's PATH"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 4bcdcab9-03c1-4587-8f57-8f34b1057b48
  modified: 2026-11-15T00:00:56.955Z
---

A worker started by launch_worker.sh (and a headless lead) has PATH with 5 entries; the interactive CTO/VS Code sessions carry the WSL-appended Windows PATH (46 entries, 27 under /mnt/c, slow 9p lstat). The guard's install check (`has_install`, realpath of every PATH entry) costs ~0.2 ms in a launched session and ~52 ms in the CTO's.

**Why:** W2-111 td-1 (2026-11-15) could not make the Bash timing cases red before the change: the brief said "use the inherited PATH" and assumed the CTO's 52 ms figure would reproduce. It didn't.

**How to apply:** when a brief asks for red-before on a cost that depends on the environment (PATH, mounts, tree count), say whose environment; take the before/after figures with the real session's PATH (count PATH entries from /proc/<claude pid>/environ, PATH only — never print the rest, it holds keys) and record the entry count. Related: [[check-before-ready-line]].
