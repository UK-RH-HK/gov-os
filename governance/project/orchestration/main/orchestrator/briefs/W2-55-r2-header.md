# W2-55 (DAEO-arrl) — run 2: the backfill kept current by a mechanism (DEC-1027 B, DEC-1028 item 2)

**Read this first; it overrides the steps below where they differ.** Your branch was merged into `w2/integrate` and
its close (with W2-05 and W2-96, 2026-11-02 01:48) was refused on your own
`test_one_row_per_register_entry_at_the_base_in_its_order`: "31 missing (DEC-984 …)". The proposal stops where you
built it, and the register grows with every decision (DEC-984 to DEC-1028 since). `git rev-parse --short=12 HEAD` must
show `aca862331a43` and `git status --short` nothing; else return PACKAGES naming it. The owner decided (DEC-1028
item 2, option (i), and "a mechanism, not a promise"); your ticket file carries the new KPI line (`09a1ac54`):
1. **Merge `w2/integrate` first** (`--no-ff`, `Task: DAEO-arrl`, `Role: orchestrator`): the ticket file and the
   register changed there. The tests worktree `~/gov-os-worktrees/W2-55-tests` exists: merge `w2/integrate` into it too
   before the designer starts.
2. **In parallel (DEC-959 item 7, DEC-963):**
   - the test designer (in the tests worktree, from the integration store) changes the backfill case so it reads the
     register **as of the proposal file's own commit** (the last commit that changed `docs/research/W2-55-backfill.md`),
     not the moving base, and adds the append mode's cases (a new register entry gets its row appended in register
     order; no existing row is rewritten; running it twice adds nothing). `Rewrite-Reason: DEC-1028 item 2`. Nothing
     else lowered.
   - a fresh engineer gives the proposer (`src/gov/decisions/backfill.py`) an append mode (for example
     `python3 -m gov.decisions.backfill --append docs/research/W2-55-backfill.md`) that adds only the rows of entries the
     file lacks, in register order, never rewriting a row, idempotent; with its own unit tests under
     `tests/unit/decisions/`. Then it runs the append once, so the proposal covers the register at your merge head.
3. Merge the tests, `gov accept` (all lines), the scoped run once in a heavy-job slot (output outside the worktree;
   no rebuild unless the selection needs one; the shared embedder is overloaded today, so never take an embedder
   timeout for a code red), `gov context DAEO-arrl --json` once (the ceiling, common brief 6a).
4. Return DONE with the exact head, and the append command's exact form: the CTO wires it into its decision-recording
   tool so every new decision adds its row in the same commit.

---

