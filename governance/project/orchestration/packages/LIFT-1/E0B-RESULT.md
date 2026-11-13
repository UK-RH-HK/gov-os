# E0b's result: the score-once harness against the product on window 4's commit (E0-DECLARATION §E0b)

Run on 2026-11-07, 21:13 to 21:29, by the CTO (session `ad44f5fe`).
- **Script:** `drafts/d4b/e0b_run.sh`. The harness fix was reviewed READY (`.gov-runtime/scratch/orchestrator/reviews/e0b-harness.md`) and pinned in `drafts/score-once/E0B-REVIEWED.sha256`.
- **Where:** E0's clone at `c00d525fd420`, the product's pool off inside the harness only. Log `~/gov-os-runs/D4B/e0b/e0b.log`; kept outputs in `~/gov-os-eval/runs/e0b/`. Counts only.

## The runs
- **The seed:** the kept 0.6B scores, 16,025 rows, with 246 conflicts (1.5 %). Earlier windows scored the same question and text slightly differently (batch padding); the first source's score is kept. The readiness record expected 0; this is the named risk 1.
- **Run A** (v456, no `lift_norm`; the new texts scored on the live 0.6B, one light GPU job, the backstop armed): 314 texts scored live, 0 unscored, 0 cut. Median search 334 ms.
- **Run B** (v456 with L3's `lift_norm` 0.0766, B0's form; strict, no GPU): 0 texts scored live, 0 unscored.

## The figures
| | visible 40 | hidden 39 | spent 59 | **the 138 hit@5** | hit@10 | hit@20 | MRR | in the bundle |
|---|---|---|---|---|---|---|---|---|
| E0, the product (pin, pool on) | 34 | 32 | 40 | **106** | 118 | 124 | 0.5665 | 123 |
| **E0b A, the harness, no lift** | 34 | 32 | 42 | **108** | 119 | 124 | 0.5616 | 123 |
| E0b B, the harness, `lift_norm` (B0's form) | 33 | 32 | 41 | **106** | 119 | 124 | 0.5602 | 123 |

- **A against E0, question for question:** 7 of 138 differ in hit@5 or first gold rank (Q03, Q13, h28, h33, m20, m35, m36). Net hit@5 is +2 for the harness.
- **Within W2-32 S11's "within 2 of the product on the 138"** (DEC-1086 A).

## What it means
- **The harness stands for the product** on window 4's commit, within 2. Bundles the harness builds (E4's M3 and M1 conditions) can stand for what the product would build with those rerankers.
- **L3's normalised lift** (run B) gives 106, the product's figure, at a slightly lower MRR. It is B0's form, kept for E4's conditions as D4B-SCORE-ONCE scored them.
- **Next: E4.** M1 (the 0.6B with gte) and M3 (zerank with gte) need gte's and zerank's scores on the texts window 4 changed. That takes one scoring window of their own: the live service stopped and restored on every exit path, as the score-once window was. It is prepared, reviewed, then run. The reader runs follow on the bundles.

**Basis:** question 1 (the harness measures what ships, within 2, before it builds any condition the product does not have).
