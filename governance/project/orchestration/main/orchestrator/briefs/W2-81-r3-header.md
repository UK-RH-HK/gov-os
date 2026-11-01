# W2-81 (DAEO-l78m) — round 3, declared by the CTO before it starts (DEC-1005, delegated)

**Read this first; it overrides the steps below where they differ.** P-W2-81-R2-2 decided (a), as a declared round
3 with one review (DEC-916; the reviews are converging, so no owner exception is needed):
1. One designer batch (resume session 9c2f47ad... as before, effort xhigh): F1 first — the runner helper
   (`test_w2_81_runner.py`, around line 37) must make its folders under `tmp_path`, never beside a run folder inside
   this repository (the review module's helper already does); F2 rides along — a typo in a hidden forbidden citation
   is refused or named, never dropped silently (it would turn NOT_READY into READY once W2-93's hidden half exists).
   As described behaviours, never the reviewer's text. F3 (a control named only in a finding's subject) is an entry
   criterion of the ticket that builds the findings capability: return it as such, no work here. The floors reading
   (pooled figure or the measurement half alone): return it as a residual with your recommendation.
2. Remove the stray empty folder the old helper made (`no-hidden-questions` inside W2-81's acceptance folder) by the
   designer's commit (it is in its paths); any other stray folder you list: name it for the CTO.
3. A gov checkpoint record; round 3's one review (a fresh independent-auditor, effort max) on the new head; commit
   its probe record only on a pass, and in the same commit mark the earlier records superseded (DEC-997).
4. The scoped run once; return DONE with the exact head. A fail: PACKAGES with the findings; no further round.
Rebuilds: `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/rebuild_slot.sh <tree>`
(a heavy-job slot and the tree's own lock, DEC-1001), never `flock /tmp/gov-os-rebuild.lock`.

---

