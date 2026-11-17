---
name: merge-never-staged
description: never leave a git merge staged (--no-commit) in the shared main tree; helpers commit there and take it
metadata:
  node_type: memory
  type: feedback
  originSessionId: ad44f5fe-276d-46b7-85cd-df9f8d97a3ec
  modified: 2026-11-16T16:30:32.179Z
---

Never leave `git merge --no-commit` staged in the main tree of Dynamic-Agentic-Engineering-OS. Helpers commit on
w2/integrate in the same tree, and their `git commit` turns the staged merge into their commit (2026-11-09: W2-56
landed inside cf23e9f8d under W2-153's subject, the landing check raised a P1, correction f3477a239).

**Why:** a merge under the wrong task trailer reads as a control-path change outside a ticket, and it lands before
the CTO's check finishes.

**How to apply:** verify on the ticket branch (or in a scratch worktree), then merge in one command with the
ticket's `Task:` trailer: `git merge --no-ff w2/W2-NNN -m ...`. Related: [[waits-by-pid-only]].

**11-16 (W2-111 follow-up 03 fork):** `git merge -F -` does not read the message from stdin. Write the message to a file and pass `-F <file>`, or use `-m`.
