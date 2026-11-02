# W2-104 (DAEO-drhj) — run 2 after P-W2-104-CMDLIST (DEC-1020, delegated)

**Read this first; it overrides the steps below where they differ.** Your run 1 returned DONE at `ac2d92af8c0e`
with one P2 open; `git rev-parse --short=12 HEAD` must show it and `git status --short` nothing, or stop and return
PACKAGES naming it. The CTO decided:
- **P-W2-104-CMDLIST (a) (DEC-1020):** your allowed paths now take `src/gov/check/commands.py` for one line:
  `skilleval` in `RECORDED_GOV_COMMANDS`, and nothing else in that file.
- **P-W2-104-CLAUDEPATH (c):** PATH lookup stays; a residual.
- **Steps:** (1) merge `w2/integrate` into your branch first (the ticket file changed there, `d942524f`; `gov launch`
  reads it from your worktree), `--no-ff`, with `Task: DAEO-drhj` and `Role: orchestrator`. (2) One fresh engineer
  (through `gov launch`, sandboxed, effort high) adds the line and commits it. (3) Run W1-26's folder and the scoped
  selection once (through `verify_lock.sh`, in a heavy-job slot; output outside the worktree). (4) DONE with the exact
  head. No new rebuild unless the selection or `gov check` needs one (`rebuild_slot.sh`, never the old lock).
- Name each red as yours or inherited, as in run 1; inherited reds are not this ticket's to fix.

---

