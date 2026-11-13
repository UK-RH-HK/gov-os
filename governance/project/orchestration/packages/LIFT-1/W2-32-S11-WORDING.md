# W2-32 S11: the two measured lines, re-worded (for the owner; DEC-1074 (5), DEC-105)

**Status:** for the owner's decision. Nothing is merged or switched on before it.

## What S11 says today
S11 (`.tickets/DAEO-0pyc.md`) builds v456, the candidate pool, as five query-time settings in `retrieval.yaml`. It ends
with two measured lines:
1. **Equality:** with 60, 40, 2 and both true, the product's own path gives the research harness's v456 result
   *question for question* on the D-4b measure clone (e884675b).
2. **Speed:** a plain search's median stays at or under the pin's, measured by the CTO on the shared servers.

## What was measured (`w2/W2-32` `1aeae788`; acceptance 257 passed, 0 failed; review READY in round 2)
| on the 138 (tuning) | hit@5 | gap between the halves | median call |
|---|---|---|---|
| the product, pool on | 107 | 2.9 | 1.20 s |
| the product, pool off (same commit) | 108 | 13.1 | 1.48 s |
| the harness's v456, the question given to the depth rerank (score-once window, B0's base) | 107 (108 with h23's label corrected) | | |

- **Equality cannot hold by design.** 63 questions differ from the harness, the same 63 in both rounds. With v456's
  keys set, the harness leaves the product's fusion and runs its own (its `CUSTOM` path), so the two order candidates
  differently. The totals agree within 1.
- **Speed is met against the pool off** on the same commit (1.20 s against 1.48 s). **It is not yet measured against
  the pin side by side.** The pin's last figure (m6, 0.75 s) was taken on 11-04, under other load. It cannot be compared.

## Classification of findings (DEC-809)
None blocks. The review was READY in round 2. The equality line is a wording fault in the KPI, not a code fault.

## Options (DEC-105)
- **(a) Re-word now (recommended).**
  - Line 1 becomes: "with 60, 40, 2 and both true, the product's own path gives, on the D-4b measure clone, a hit@5 on
    the 138 within 2 of the harness's v456 with the question, and a gap between the halves no wider than with the pool
    off (the CTO's measure, the hidden half in counts only)."
  - Line 2 is kept. It is judged in re-pin window 4, the pin and the candidate measured one after the other on the
    same servers.
  - Cost: one ticket edit and the speed check inside window 4 (about 20 minutes). S11 merges for window 4.
  - Why: the score-once grid and every reranker cell were measured on v456. Shipping the pool keeps the product equal
    to what was measured.
- **(b) Keep line 1: make the product's fusion match the harness's.**
  - Cost: one engineer round on `retrieve.py` with tests first, and its review: about 0.5 to 1 day (est.). It touches
    the fusion every search uses.
  - Gain: none measured. The totals already agree within 1.
- **(c) Defer S11: window 4 ships without the pool.**
  - Window 4 then gives 108 with a gap of 13.1. The grid's cells (B0, M3) are no longer what ships, so they would need
    measuring again on the pool off.

**Recommendation: (a).**
