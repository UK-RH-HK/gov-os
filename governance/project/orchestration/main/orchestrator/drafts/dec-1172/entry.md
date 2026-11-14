### DEC-1172 — The evening of 2026-11-13 (2): W2-88 NC-1 (a); W2-23's commit reset as the CTO's P2
- **Status:** ACCEPTED (owner, 2026-11-13, in the chat ~17:45; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-11-13)`) · **Under:** DEC-1167 (1), DEC-1154, DEC-1164 (18), DEC-1088 (6), DEC-974
- **Decision:**
  - (1) **P1-W2-88-NC-1 (a):** A9 commits its own record through its own step in `fabric.py`, never through W2-23's `project.commit`. On a refused commit, A9 runs its narrow undo (the record added to what it wrote and staged) and refuses with the commit's code, with no reset. NC-2 (an interrupt between `git add` and its listing) rides along. W2-23's `project.commit` and `project.restore` stay unchanged in this run. One test batch (a planted refusing hook), one engineer batch, `gov accept`, then a narrow independent check (W2-88 run 6).
  - (2) **W2-23's `project.commit` reset for A1 to A8:** a commit refused there (a pre-commit hook, commit signing) calls `restore` (`git reset --hard`) and loses the work too. This is a defect inside closed W2-23's own scope, so the CTO fixes it under DEC-1164 (18) as a P2: listed for the owner's reading, landed on a narrow independent check. The order: after W2-27 starts, and before any adoption of EXAMIN's real repository.
- **Basis:** the owner's message of 2026-11-13 (~17:45): "W2-88 NC-1 (a)", and "The same reset sits in W2-23's project.commit for A1 to A8 … fix it under DEC-1164 (18) as your P2 after W2-27 starts, before any adoption of EXAMIN's real repository, and list it for my reading."

DND rows:
| 188 | DEC-1172 (1): W2-88 NC-1 (a), run 6 (fabric.py's own record commit, narrow undo, no reset) | IN PROGRESS: run 6 released 17:55 UTC |
| 189 | DEC-1172 (2): W2-23 `project.commit`'s reset for A1-A8, CTO's P2 under DEC-1164 (18), listed for the owner's reading | WAITS: W2-27's start; before any adoption of EXAMIN's real repository |
