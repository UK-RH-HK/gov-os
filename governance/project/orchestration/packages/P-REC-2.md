# P-REC-2 — Only the main orchestrator of W2-00 may write the record worktree: a guard rule (P2; gates nothing)

**From:** the W2 orchestrator, 2026-10-21 17:42 (the time of the commit that filed it) BST, on DEC-887 item 3 (the owner: "Confirm the guard allows the orchestrator, and only the orchestrator, to write that worktree").

## 1. Context
- DEC-887 moved the raw orchestration record to the branch `record/w2`, in the worktree `~/gov-os-worktrees/W2-00-record/`. The orchestrator's sync writes and commits there.
- Ticket leads run with role `orchestrator` too (each with its own ticket), so "the orchestrator" in the guard's sense includes every lead.

## 2. What happened (read in the code, `src/gov/guard/decide.py` `_path_allowed`, `src/gov/guard/runs.py` `own_folder`)
- The guard refuses every session's tool writes (Write, Edit, the write targets of a Bash command) outside that session's project root, except its scratch and its own run folder `~/gov-os-runs/<its ticket>/`.
- No role's tool write lands in the record worktree. That includes the main orchestrator, whose project root is the main tree.
- The own-folder route needs the session's ticket `in_progress`; W2-00 (`DAEO-sdxk`) is `open`.
- The record is written by git and by `sync_context.py`, which the guard does not judge: they are opaque programs, the accepted residual of the prompt §2.
  - A lead's own opaque program could write there, stopped only by its brief.
  - A sandboxed worker cannot write there at all.
- So the guard confirms "nobody by tool", not "the orchestrator only". This is the same protection the record had inside the main tree, where a lead's tool writes are refused too.

## 3. Why it matters
- The record is Policy 1's committed context.
- The ordinary-work risk is small: a lead has no reason to write another tree, and its brief forbids it.
- Classification: ordinary work: no, because only a deliberately opaque write by a lead reaches it; consequence: other.

## 4. Options
- **(a) A guard rule, stricter only.** Writes into the record worktree are allowed only to a session with role `orchestrator` and ticket W2-00, by tool and by known commands (`git -C <record>`, the sync script named by path). Every other session is refused, including leads, whose ticket differs.
  - It rides in the next guard ticket (W2-10 or W2-56; DEC-802), about 20 lines plus one acceptance case per role.
  - Stricter only, but a guard change, so it is the owner's (CAP-33 via that ticket's review).
- **(b) A Wave 3 hardening row** (ordinary work: no, DEC-801), with today's protection: tool writes refused to all, and the briefs.
- **(c) Accept as is**, with no row.

## 5. Recommendation
**(b), confidence medium.** By the judgement rules, a finding that needs a deliberate construction is a row, not a round. Take (a) if you want the property guard-enforced in Wave 2.

## 6. What it blocks, and what waiting costs
Nothing. The record is written today by the orchestrator's sync and git only.
