# D4B-SCORE-ONCE: four rerankers score the 138 once; the grid, declared before any run (DEC-1081 (3))

- **For:** the owner. **By:** the CTO (session `812bc5ce`), 2026-11-06, **before the window and before any replay.**
  This page is committed before the first GPU job, and nothing in it changes after a result is seen. A change would be
  a new version with its reason, made before the run it affects.
- **Nothing is adopted or installed in the product** before the owner decides (DEC-1081 (3)). The verdict set of 80
  stays unused until the decision point (DEC-1078 (3)).

## 1. The four models and the window
| name | model @ revision | how it loads (the trial copy) | request bound |
|---|---|---|---|
| q06 | Qwen/Qwen3-Reranker-0.6B @ `e61197ed` (today's) | the cross-encoder, as live | 16 texts, 24,000 padded characters |
| q4b | Qwen/Qwen3-Reranker-4B @ `22e68366` | the cross-encoder in 8-bit (ACT-RERANK-TRIAL-1) | **8 texts, 12,000** (DEC-1079 (a); at 40 and the full bound it passed the budget) |
| gte | Alibaba-NLP/gte-reranker-modernbert-base @ `f7481e60` | the cross-encoder, as is | 16, 24,000 |
| zer | zeroentropy/zerank-1-small-reranker @ `a65fd51c` | the trial loader `yes-logit` (ACT-RERANK-TRIAL-2 §1; its code file never downloaded) | 16, 24,000 |

**The window** (`.gov-runtime/scratch/orchestrator/drafts/score-once/score_once_window.sh`, one quiet window under
the GPU rules):
- the live service is stopped for the window and restored after it with class 3's start line;
- one reranker at a time on the trial socket, with the backstop on the script's and the service's process groups;
- the harness stops at 14,255 MiB, and between models the GPU returns to the base;
- every stop is by pid.

Each model runs v456 (40 reranked once per question) on the 138 (the 80 and the 60, as every trial window), into a
kept score cache of its own.
- **The same candidate lists:** the 0.6B runs first, and its route answers are copied into the others' caches (its
  scores are not), so the four score the same 40 texts per question.
- **The trial path's own check:** the 0.6B must reproduce its kept run (`trial-w4-t2-qwen06b`, 107 of 138) question
  for question, or the window stops.
- **Recorded per model:** load time, GPU peak and samples over the budget, median search, cut texts. These are
  records, not the speed rule (section 4).

## 2. Before the replays: L2, then L3 (DEC-1079)
- **R0:** the replay of q06 alone (no reranker called) must equal the window's q06 run question for question, or no
  replay counts.
- **L2, where each miss leaves the top 5** (counts and ids only, from the measure's own per-question lines; no
  question is read). On q06 alone, the stages after the rerank are switched on one at a time:
  - the reranker's own order (lift 0, routing's two halves 0, DEC-424's move off);
  - then the authority lift;
  - then routing (named, then code);
  - then DEC-424's move.
  
  For each of the 31 misses this gives the stage at which its first gold left the top 5.
- **L3, written and committed before any grid replay**, from L2's figures and never aimed at a named miss: the lift
  on a per-query normalised score, and the moves ahead bounded. If L2 shows no displacement, L3 is "no change", said
  so. **L3 is applied the same way to every cell below**, including the baseline.

## 3. The grid (16 cells against the baseline, all at no GPU cost)
**Baseline B0:** q06 alone, on the pipeline after L3.

| cell | rule | models |
|---|---|---|
| A1 / A2 / A3 | alone | q4b / gte / zer |
| T1 / T2 / T3 | by question type: gte where the code route answers (the question names a symbol the code graph holds: the product's own test), the other model elsewhere | gte + q06 / gte + q4b / gte + zer |
| C1 | cascade: q06 orders the 40, q4b reorders q06's top 12 (DEC-1079 (a)'s cascade) | q06 then q4b |
| C2 / C3 / C4 | cascade, top 12 | gte then q4b / q06 then zer / gte then zer |
| M1 to M6 | two in parallel: each one's scores min-max normalised over the 40, merged with equal weights | q06+gte, q4b+gte, zer+gte, q06+zer, q4b+zer, q06+q4b |

The rules are fixed in code (`combine` in the score-once harness, tested 14 of 14):
- a cascade's head is ordered by the second model, inside [0.5, 1];
- its rest keeps the first model's order, inside [0, 0.4995];
- a merge is w × min-max(a) + (1 − w) × min-max(b), with w = 0.5;
- no weight or N is tuned on these sets.

## 4. How a cell is judged (the rule written before the run: D4B-MISSES (b), DEC-1079 L1)
- **Reported for every cell:**
  - hit@5 and MRR on the 138, and per set (visible 40, hidden 39, spent 59);
  - the spread between the three sets;
  - gains and losses against B0, with an exact McNemar p;
  - beside it, a Holm-adjusted p for the 16 comparisons (shown, not part of the rule).
- **A cell wins** with the highest hit@5 on the 138, then MRR, with a spread no wider than B0's.
- **Ties:** fewer models, then the smaller.
- **Eligible only if,** in a real window measured after the replays, before the owner sees it:
  - its median search alone is at most 3.0 s;
  - no request times out at 10 searches at once;
  - no probe shape reaches the budget;
  - the GPU stays under 14,255 MiB.

  A two-model cell is measured as it would run: both models loaded, or loaded in turn, as stated then. A cell that
  fails is recorded as not eligible, and the next one is taken.
- **Every set here is a tuning set** (DEC-1074). The winner, beside the 0.6B, goes onto the fresh 80 **once**, at the
  decision point, and only that verdict decides.

## 5. Known limits, stated now
- q4b's scores come at the narrower bound (8, 12,000). Padding differs from its earlier runs, so its alone figure may
  differ by a question or two from window 3's.
- A text longer than a model's bound is read up to it. The harness counts each one (`cut texts` in the log).
- A cell's scores before L3 are on each model's own scale. That is why L3 comes first and no cell is judged before it.
- 138 questions give little power. A gain of 5 is not yet significant (D4B-LEVERS §2), which is what the fresh 80 is
  for.

**Basis:** question 1 (memory: the reranker chosen from every candidate that fits, with its cost) and question 4 (the
GPU used once; every combination replayed from kept scores).
