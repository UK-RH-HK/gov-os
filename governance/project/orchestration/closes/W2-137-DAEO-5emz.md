# W2-137 (DAEO-5emz) closed: merged, review READY, after W2-32's close (its waits_on), closed by DEC-953's practices (DEC-1132 (1))

- Merged into w2/integrate (w2/W2-137, -tests, -d10); review READY (`.gov-runtime/scratch/orchestrator/reviews/w2-137.md`, verdict.py; F1-F4 Wave 3 rows); live since the re-pin; S5 measured by the CTO 11-07 (GPU peak 9,670 MiB, under 14,255; hit@5 and MRR within 1)
- Waited on W2-32 (its waits_on), closed 2026-11-13 by DEC-1169 (1); W2-112, its other wait, closed earlier
- Check on w2/integrate at 8ba025e8f (a clean worktree, through heavy_slot.sh): `gov accept W2-137` pass, 37 passed, 0 failed, 0 skipped
- Waited on by: W2-88 (waits_on), W2-145 (waits_on)
- Closed: 2026-11-13, by the orchestrator under DEC-953 items 1 and 5, DEC-1132 (1)
