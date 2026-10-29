# Lead checkpoint — DAEO-cy5o (W2-57), run 4 (judgement-only re-probe after W2-68's merge, DEC-895)

- **State:** merged `w2/integrate` at `848f5ab366b9` into `w2/W2-57`: merge `27f290a2beef` (no conflict; trailers Task: DAEO-cy5o, Implements: DEC-895, Role: orchestrator, Co-Authored-By).
- **Start head:** `d0cb962998b5` (end of run 3, clean).
- **Judged x changed since `8d9d78d93529`:** `src/gov/close/command.py` (W2-68: `_batch.check_red_run`, `_scope` moved before the pre-close gate, `reused_check` standing for gov check, `reused_form`, fingerprints and `reused` in the evidence block) and `docs/plan/WAVE_2_WBS.md` (new W2-75 card only). Lists in `log/run4/judged.txt`, `log/run4/changed.txt`.
- **Containment note on the merge:** flagged, left in place, two Role: owner decision-record commits already on integrate (`6367e96597e4` DEC-931, `bc37c419359c` DEC-933); brought in by the merge, not made here.
- **Next:** rebuild, keyword warn, gov check, W2-57 + tests/unit/close close-form, collect-only; gov checkpoint + commit; reviewer rev-4 (gov launch, effort max) at that head; probe record if pass; trailer_gate; return.
- **Loop count:** run 4 adds no code; no implementer.
