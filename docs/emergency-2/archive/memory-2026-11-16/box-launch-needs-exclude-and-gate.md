---
name: box-launch-needs-exclude-and-gate
description: a boxed gov launch writes <gitdir>/info/exclude (DEC-402 placeholders) and needs gate.json; planted worlds on /dev/shm fail the disk floor
metadata:
  node_type: memory
  type: project
  originSessionId: acd80751-ac8f-4230-9bae-15c678a54895
  modified: 2026-11-16T17:20:07.163Z
---

gov launch's `exclude_placeholders` (src/gov/launch/sandbox.py) always opens the common gitdir's info/exclude read-write, so a box that mounts `info/` read-only refuses every worker launch ("placeholder names cannot be kept out", DEC-402). Fix 6 (11-16) binds info/exclude alone writable. A planted world also needs `$HOME/.gov-os/machine/gate.json`, and on /dev/shm its disk/inode floors (100 GiB / 10M) shut the gate: lower them in the planted copy only.

**Why:** fix 6 probe failed twice on world artifacts before the box itself was proven.
**How to apply:** rehearsing launches in a box: copy gate.json into the planted HOME, lower floors there, and check info/exclude is bound. See [[bwrap-mount-order-and-wsl-dns]].
