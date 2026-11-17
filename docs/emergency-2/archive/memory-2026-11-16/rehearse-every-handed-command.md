---
name: rehearse-every-handed-command
description: every command handed to the owner, the operator or a session is first run by tools/rehearse.sh on a scratch clone; its expected output is copied from rehearsals/<id>/RESULT.md (P-SESSIONS-1 item 3, 11-15)
metadata:
  type: feedback
---

The owner's rule (2026-11-15 ~23:40, P-SESSIONS-1 item 3): every command I hand to anyone is rehearsed first in a scratch copy, and its expected output comes from that rehearsal.

**Why:** on 11-15 I handed out unrehearsed commands that failed or misled: W2-81's `--mode run`, the start line without the replies-folder allow, and an `env -i PATH=$PATH` that split on spaces.

**How to apply:** run `bash .gov-runtime/scratch/orchestrator/tools/rehearse.sh <new id> <source repo> '<command with {REPO}>'`. Quote that `RESULT.md`'s exit code and output as the expected lines, and name the RESULT.md path in the package. A script that takes `--repo`/`--run` gets `{REPO}`. Headless `claude -p` runs use the short PATH from `adopter.sh`. Related: [[w2-81-run-needs-session-and-kit]], [[sessions-get-tools-at-start]].

**An install rehearsal hit live (11-16 01:09).** A reviewer agent rehearsing `install.sh` left out the target-root override, and the script installed the not-ready job runner into the live `~/gov-os-operator`. The guard cannot see writes made inside a script. Every install script must require its target root explicitly, with no silent default to the live folder, and every reviewer brief must say so. Undo: `drafts/operator-jobs/undo-accidental-install.sh` (rehearsed).
