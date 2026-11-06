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

## Version 2 (2026-11-06 ~11:50, before any run): the depth rerank is given the question
- **The finding (L5, `a5c0c34f`, its check script):** on the measure clone (`routing.phrasings: true`), the
  harness's global rerank of 40 (v456's `depth`) scores against `STATE["query"]`, which is set by every phrasing the
  lexical route is asked. So the reranker was given the last phrasing (the question's content words, or the question
  with its resolved ids appended), not the question: the question itself in 0 of 5 checks.
  - **Every v456 figure was measured this way:** the trials, the 107 of 138, and the 60's 40 of 59.
  - **The product does not do this:** its page rerank, and W2-32 S11's port of v456, give the question.
- **The change (structural, never aimed at a question):** a variant key `"rq": "question"` gives the depth rerank
  the question as `retrieve` was asked it. Unset, the text is as measured. A continuation call keeps the default.
  Tested: 19 of 19 in the harness's test.
- **The window, as amended:**
  1. **q06f**, the 0.6B on v456 as every past figure was measured. It runs first, as the trial path's faithfulness
     check: it must reproduce its kept 107 of 138, question for question.
  2. **q06, q4b, gte and zer** on v456 with `"rq": "question"` (the product's form). q06's route answers come from
     q06f; the others' come from q06, and are checked against it.
- **The grid (§3) is judged on the version-2 runs only.** B0 is q06 on the question, after L3. q06f is recorded
  beside it, so the size of the artefact is known. No cell is judged on the old text.
- **Cost:** one more 0.6B pass, about 20 minutes of GPU.

## Version 3 (2026-11-06 ~12:05): the faithfulness check reads the outputs, not the verdicts. Written after the stop, and said so
- **What happened:** the window stopped as written. q06f gave 106 of 138 against the kept run's 107, differing in
  one question, h23 (a hit at rank 2 in the kept run, missed now), so the window stopped before any other model.
- **What the outputs show** (`drafts/score-once/diff_one.py`, `diff_all.py`; chunk ids, paths, line spans and
  expansions only, no text):
  - **all 140 questions are identical, across all 689 calls:** the 80 (397 calls) and the 60 (292 calls), against
    the kept run (`trial-w4-t2-qwen06b`), h23 included;
  - **retrieval reproduced exactly; only the measure's verdict on h23 changed.** On the same clone, that means h23's
    gold label changed in the sets root after 11-05 13:21. The CTO cannot confirm it, since it may not open the
    hidden file (the new deny rules refused even its `stat`). The owner's checker can.
- **The change:** the trial path's check compares the ranked outputs. It is stricter for the path (every item, span
  and expansion of every call, not 138 verdicts), and blind to a label edit, which no path can cause. Passed: 140 of
  140.
- **No cell is affected:** every cell, B0 included, is scored against the same labels, as they stand at the replay.
  The past figures (107 of 138) were scored on the labels of 11-05; the replays' figures use today's.
- **The window resumes from q06** (q06f's kept scores stand; no GPU repeated): q06, q4b, gte and zer on the question.
- **h23, found from `REANCHOR-LOG-hidden.md` (DEC-1083):** the label had not been edited.
  - My measure script's automatic re-anchoring (`repin_gold.py`, in `w4_point.sh`) moved h23's lines on 11-05 at
    14:40 to another clone's commit (`5a9e36c0`, lines 545-559).
  - The score-once runner (`so_measure.sh`) does not re-anchor, so on the g1 clone (`e884675b`, where the block sits
    at 528-542) h23's gold was looked for in the wrong lines.
  - Re-anchored at 12:42 to `e884675b`, after fetching that commit's history into the clone (objects only; its tree
    unchanged). The other 69 line-cited sources, the spent 60 and the visible half were already right for the clone.
  - Every model's figure is re-scored on these labels by replaying it alone (exact, as R0 showed).

## Version 4 (2026-11-06 ~12:50, before any stage or cell replay is judged): a follow-up call's unscored texts
- **The finding:** L2's replays with routing's moves switched off stopped: "4 of 40 texts were not scored by q06 in
  the window".
  - A question's first call reranks the fused list's first 40, the same under every stage and every cell, and the
    window scored them all.
  - A follow-up call (`--continue`) reranks the next ones, and which they are depends on what the earlier calls sent.
  - So a replay that changes the order can ask for texts the window never scored.
- **The change** (`rx.py` `_kept`, tested 22 of 22): in a follow-up call only, an unscored text is placed below every
  scored text of that pass and counted (`LOWFILL`). A first call with an unscored text still stops the run.
- **What it costs:**
  - **hit@5 stays exact.** It is decided in the first call, which returns 13 to 23 items.
  - **MRR is approximate only** where the first gold lies beyond the first call, by at most 1/13 a question.
  - The count of filled texts is reported beside every replay. A cell with filled texts is judged on hit@5 first, as
    the rule already says.
- **Not affected:** a model alone, B0 included, reproduces its window run exactly, with no text filled.
