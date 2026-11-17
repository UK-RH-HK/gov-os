---
name: auditor-scratch-via-bash
description: "a launched independent auditor has no Write/Edit tool; a Write call falls to \"ask\" and in quiet hours (02:00-07:30) the guard refuses and queues it; brief it to make scratch files with Bash in $TMPDIR"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 0227d6e2-43be-40b5-8934-43a15e9e0a68
  modified: 2026-11-15T05:44:19.377Z
---

A launched independent-auditor gets only Bash, Read, Grep, Glob (launch_worker.sh's cli()). If it calls the Write tool for a scratch file, the call needs approval; in quiet hours the guard refuses it and queues it for 09:00 (DEC-991). W2-178 au-1 (2026-11-15 05:40) lost its planted red runs this way, so the narrow check came back partial.

**Why:** a narrow check that has to plant a red needs scratch files. If the brief does not say how to make them, the auditor reaches for Write.

**How to apply:** every auditor or probe brief that asks for a planted or red-on-copy run says: "You have no Write or Edit tool. Make scratch files under your sandbox's $TMPDIR with Bash only (a heredoc or python3 -c), never with the Write tool." Related: [[pytest-through-heavy-slot]].
