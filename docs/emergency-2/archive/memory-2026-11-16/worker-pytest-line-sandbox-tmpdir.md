---
name: worker-pytest-line-sandbox-tmpdir
description: "A launched worker's pytest line must use TMPDIR=\"$TMPDIR\" (the sandbox's) and PYTHONUSERBASE=/home/usain/.local; mkdir /tmp/<x> and Write under .gov-runtime/scratch are denied (W2-174 en-1, 11-15)"
metadata:
  node_type: memory
  type: feedback
  originSessionId: f5ed7cab-d43c-443a-96da-706f0d5f230f
  modified: 2026-11-15T21:17:24.530Z
---

On 2026-11-15 21:16 W2-174's engineer en-1 stopped with nothing built: my brief's line `mkdir -p /tmp/w2-174-en ... && env TMPDIR=/tmp/w2-174-en HOME=<empty> ... heavy_slot.sh python3 -m pytest ...` was denied twice by the launched session's permissions, and a Write of `<tree>/.gov-runtime/scratch/run_fields.sh` was denied ("directory denied by your permission settings"). The test designer td-1 hit the same and got through with `TMPDIR="$TMPDIR"`, scratch files via Bash heredoc into `$TMPDIR`, and `PYTHONUSERBASE=/home/usain/.local` (an empty HOME hides the user site packages, so pytest does not import).

**Why:** the gov launch sandbox writes only the worktree and its own `$TMPDIR`; the harness denies Write/Edit under `.gov-runtime/scratch` for launched sessions.

**How to apply:** in every worker brief give the pytest line as `env TMPDIR="$TMPDIR" HOME=<tree>/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=<tree>/src bash .../heavy_slot.sh python3 -m pytest ...`, the empty-home folder made by the lead before the launch, scratch scripts via Bash heredoc into `$TMPDIR`, never `/tmp/<name>`. Related: [[pytest-through-heavy-slot]], [[auditor-scratch-via-bash]].
