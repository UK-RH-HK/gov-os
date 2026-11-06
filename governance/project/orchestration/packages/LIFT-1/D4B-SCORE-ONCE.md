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

## L2's result and L3, written before any cell is replayed (2026-11-06 ~13:30)
**L2:** q06 alone, on the labels re-anchored at `e884675b` (12:42), with the routing move switched off by the
sentinel. Counts and ids only (`drafts/score-once/l2_table.py`).
- **hit@5 on the 138 by stage:** the reranker's own order 100; plus the authority lift 106; plus routing's moves 108;
  the full pipeline 108.
- **Of the 30 misses, 27 never reach the top 5 in the reranker's own order.** Only 3 are pushed out by the lift (h26,
  m02, m30, each from 4 or 5 to 6 or 7), against about 9 it brings in (net +6). The routing moves push none out
  (net +2).
- **So for the 0.6B the misses are the reranker's, not the lift's or the moves'.**

**What L2 does not show, and L3 is for:** the lift adds 1.0 per tier step to the model's raw score, and the raw scales
differ.
- The 0.6B and the 4B give logits of about −14 to +11 (the 0.6B's median per-pass range is 13.06), so a step is
  about 1/13 of a pass's spread.
- gte and zerank give 0 to 1, so the same step outweighs everything they say. Merged or cascaded scores (0 to 1) are
  swamped the same way.
- Judged as measured, those cells would be judged mostly by the authority tiers, not by their reranker.

**L3 (the change; `rx.py` `_final`, `"lift_norm"`; tested 23 of 23):**
- **The lift:** each pass's rerank scores are min-max normalised to [0, 1], and the lift is added there.
- **The step:** **0.0766** per tier step, the inverse of the 0.6B's median per-pass range (686 passes,
  `l3-range`'s log). It is set from the baseline, so the 0.6B ranks about as today, and it is never tuned on a cell.
- **The routing moves unchanged:** L2 shows they push no answer out, so no bound is needed.
- **The same for every cell, B0 included:** every cell is replayed on v456 with `"rq":"question"` and
  `"lift_norm": 0.0766`.

## The grid's results (2026-11-06 ~13:50; L3, v456 with the question; counts only)
`drafts/score-once/grid_report.py`; the replays are in `~/gov-os-runs/D4B/score-once-replay/g-*`. All 17 exited 0,
and no text was unscored.
- **B0** (q06 alone, L3): 107/138, MRR 0.5589, spread 18.0 (visible 35, hidden 31, spent 41). As measured, before
  L3: 108, 16.3.

| cell | hit@5 | MRR | vis / hid / spent | spread | gains / losses | McNemar p | Holm p |
|---|---|---|---|---|---|---|---|
| **M2** q4b + gte, merged | **118** | **0.6376** | 36 / 35 / 47 | 10.3 | 14 / 3 | 0.013 | 0.191 |
| M3 zer + gte, merged | 118 | 0.6120 | 35 / 35 / 48 | 8.4 | 13 / 2 | 0.007 | 0.118 |
| C2 gte, then q4b on its top 12 | 117 | 0.6359 | 37 / 33 / 47 | 12.8 | 13 / 3 | 0.021 | 0.234 |
| C4 gte, then zer on its top 12 | 117 | 0.6199 | 37 / 34 / 46 | 14.5 | 12 / 2 | 0.013 | 0.191 |
| M6 q06 + q4b, merged | 117 | 0.6175 | 36 / 34 / 47 | 10.3 | 12 / 2 | 0.013 | 0.191 |
| M5 q4b + zer, merged | 115 | 0.6302 | 37 / 33 / 45 | 16.2 | 13 / 5 | 0.096 | 0.831 |
| A2 gte alone | 114 | 0.6233 | 34 / 34 / 46 | 9.2 | 11 / 4 | 0.118 | 0.831 |
| T2 gte for code, q4b for the rest | 114 | 0.6186 | 37 / 33 / 44 | 17.9 | 12 / 5 | 0.143 | 0.861 |
| A1 q4b alone | 114 | 0.6164 | 37 / 33 / 44 | 17.9 | 12 / 5 | 0.143 | 0.861 |
| C3 q06, then zer on its top 12 | 114 | 0.6086 | 35 / 34 / 45 | 11.2 | 10 / 3 | 0.092 | 0.831 |
| M1 q06 + gte, merged | 114 | 0.6048 | 35 / 34 / 45 | 11.2 | 8 / 1 | 0.039 | 0.391 |
| M4 q06 + zer, merged | 114 | 0.6004 | 36 / 32 / 46 | 12.0 | 7 / 0 | 0.016 | 0.191 |
| C1 q06, then q4b on its top 12 | 113 | 0.6251 | 35 / 33 / 45 | 11.2 | 11 / 5 | 0.210 | 0.861 |
| A3 zer alone | 113 | 0.5953 | 35 / 33 / 45 | 11.2 | 13 / 7 | 0.263 | 0.861 |
| T3 gte for code, zer for the rest | 113 | 0.5947 | 35 / 33 / 45 | 11.2 | 13 / 7 | 0.263 | 0.861 |
| T1 gte for code, q06 for the rest | 107 | 0.5613 | 35 / 32 / 40 | 19.7 | 1 / 1 | 1.000 | 1.000 (spread wider than B0) |

- **By the rule:**
  - **M2 leads:** 118, then MRR 0.6376, with a spread of 10.3 against B0's 18.0.
  - **M3 ties on hit@5** (118) and comes second on MRR. It needs no package: the 4B needs bitsandbytes in the
    product's reranker environment (an install).
  - No cell is significant after Holm's correction on 138 questions. M2's own exact p is 0.013. That is what the
    fresh 80 is for.
- **What L3 showed:** under the raw-scale lift, gte gave 78 and zerank 82. Under L3 they give 114 and 113, so their
  low scores were the lift's artefact, not the models'.
- **Next, before anything goes to the owner (§4):** the speed and GPU memory of M2, and of M3 as the runner-up, in a
  real window: both models loaded, each search scored by both, alone and 10 at once, under the GPU rules. Only an
  eligible cell goes onto the fresh 80.

## Version 6 (2026-11-06 ~14:45, before the extend window runs): DEC-1084's two measures
**What runs** (`drafts/score-once/extend_window.sh`, reviewed READY). One short window with the 0.6B alone, L3, the
question. Each variant runs into its own copy of the kept q06 cache, so only texts not scored before go to the GPU.
- **b0, a control and not a cell:** v456 as B0. It must score 0 new texts and equal g-B0 question for question, or
  the window stops.
- **E1:** `depth` 80, the 0.6B reranking 80 candidates instead of 40. L3's step stays 0.0766, set from the
  40-candidate passes, as declared.
- **E2:** `split`, a two-part question split, its parts searched as extra phrasings (L5).
- **E3:** `termmap`, the question in the records' own words as one extra phrasing (L5).
- **E4:** `split` and `termmap`.

**How they are judged:**
- **The comparison:** each cell is replayed from its extended cache (route answers and the 0.6B's scores from that
  cache only) and compared with B0, by §4's rule: hit@5 on the 138, then MRR, the spread not wider than B0's. Gains,
  losses and an exact McNemar test are given for each.
- **Holm over these 4 comparisons,** a family of their own. It is shown, not part of the rule.
- **Each replay must equal its window run,** as R0 did, or it does not count.
- **They are add-ons to the 0.6B, not rerankers.** They do not compete with M3.
  - A cell that beats B0 by the rule is reported as a lever to apply on top of the chosen reranker.
  - Measuring it with M3 needs zerank and gte to score its new texts, in a window of its own, at the owner's word.
- **E1 answers the owner's question** directly: does a wider pool help or hurt?

## Version 6's result (2026-11-06 14:50-15:06 window, replays 15:07-15:20; `~/gov-os-runs/D4B/score-once-extend/`)
The control b0 scored 0 new texts and equalled g-B0 in all 138 questions. Each cell's replay equals its window run in
all 138 (0 differing in hit@5 or first gold rank). The GPU peak was 9,668 MiB (E1), never at the budget. Counts only.

| cell | new texts scored | hit@5 /138 | MRR | visible /40 | hidden /39 | spent /59 | spread | gains / losses vs B0 | McNemar p | Holm (4) |
|---|---|---|---|---|---|---|---|---|---|---|
| B0 | 0 | 107 | 0.5589 | 35 | 31 | 41 | 18.0 | | | |
| E1 depth 80 | 5,320 | 107 | 0.5497 | 32 | 31 | 44 | 5.4 | 4 / 4 | 1.000 | 1.000 |
| E2 split | 205 | 108 | 0.5608 | 35 | 32 | 41 | 18.0 | 1 / 0 | 1.000 | 1.000 |
| E3 termmap | 60 | 108 | 0.5606 | 35 | 31 | 42 | 16.3 | 1 / 0 | 1.000 | 1.000 |
| E4 both | 250 | 109 | 0.5619 | 35 | 32 | 42 | 16.3 | 2 / 0 | 0.500 | 1.000 |

- **E1, a wider pool: it neither helps nor hurts the count, and it lowers MRR.** It gains 4 questions and loses 4,
  and its MRR falls (0.5497 against 0.5589). It narrows the spread because the visible set loses 3 and the spent set
  gains 3. The wider pool needs about twice the scoring (5,320 new texts on top of 5,486). Not a lever.
- **E4 (split and the term map) is the best cell by §4's rule:** 109, the highest MRR, with a spread no wider than
  B0's. E2 and E3 also pass the rule, each with 108. **None is significant:** +2 with no loss, p 0.50.
  - By version 6, E4 is a lever to apply on top of the chosen reranker. It is not measured with M3. That needs zerank
    and gte to score its 250 new texts, in a window of its own, at the owner's word.
- **Cost, not measured live here.** The replays' search times come from cached scores. E4 adds up to three phrasings
  a question, each searched and reranked. Its live time would be measured in M3's window, if the owner asks for one.

## Version 7 (2026-11-06 ~16:20, before L6 runs): L6, records of work one tier lower (DEC-1079 L6, DEC-1085 (1))
**The cell:** B0 with `"work_tier"`, one switch in the harness copy (`rx.py`, tested in `test_rx_l6.py`, 4 of 4; L5's
48 and combine's 23 still pass). The records of work below go one tier step under the middle, where reports already
sit. Every other tier is as the path map reads it, and reports keep their step: one change, one test.
- **The paths** (close, checkpoint, review and session records, which restate decisions; D4B-LEVERS L6):
  `docs/close/**`, `docs/checkpoints/**`, `governance/project/orchestration/closes/**`, `…/reviews/**`,
  `…/sessions/**`, `…/nightly/**`, `governance/project/orchestration/main/orchestrator/CHECKPOINT.md` and
  `…/main/orchestrator/PR-*.md`.
- **The lift moves both lists,** as the product's would: the fused list (0.004 a step) before the cut to 40, and the
  reranked list (L3's 0.0766 on the normalised score).

**How it runs, with no GPU:**
- It is replayed from E1's extended cache (`score-once-extend/caches/d80`). That cache holds the 0.6B's scores for the
  first 80 fused candidates of every call, and the same route answers as B0.
- **A control first:** B0 replayed from that cache must equal g-B0 in all 138. Otherwise the cell does not count.
- If the cell asks for a text that cache does not hold, the replay stops. That is reported, and it would need a short
  0.6B window.

**How it is judged:** by §4's rule against B0, with gains, losses and an exact McNemar test. It is a single
comparison, so no Holm. It is an add-on, like E2 to E4. If it wins, it is a lever to state for the owner, as a tier
change (DEC-952).

## The live window's result (2026-11-06 14:14-14:20; `~/gov-os-runs/D4B/live-window/20261106-141359/`)
- The window ran to its end (exit 0). The live service was restored at 14:20:48 (class 3's check: `rerank.by`
  service).

| | M2: q4b 8-bit + gte | M3: zer + gte |
|---|---|---|
| median search alone (limit 3.0 s, GPU reads included) | **4.51 s: not met** (4.15 s less the reads; p90 10.16 s) | **2.84 s: met** (2.56 s less the reads; p90 8.40 s) |
| failed or unranked, alone | 0 | 0 |
| 10 at once | median 27.24 s, slowest 32.08 s; none past 30 s per request, the slowest request 5.95 s: met | median 12.67 s, slowest 20.27 s; slowest request 3.81 s: met |
| the probe at the budget | met (both services) | met (both services) |
| GPU, judged (budget 14,255 MiB) | peak 13,327, 0 of 174 samples at or above: met | peak 12,712, 0 of 132 samples: met |
| GPU, reported only | after the warm-up 11,536; derived bound 14,922 | after the warm-up 10,436 |
| **verdict** | **not eligible** (speed alone) | **ELIGIBLE** |

- **M2** fails on speed alone: the 4B's reranking takes a median 2.54 s of each search.
- **M3 is the grid's eligible leader:** 118 of 138, MRR 0.612, spread 8.4; against B0, 13 gains and 2 losses, exact
  p 0.007, Holm 0.118.
- **Beside today's 0.6B** (D4B-LEVERS: 1.80 s alone, 6.6 s median at 10 at once), M3 is about 1.6 times slower alone
  and about twice as slow at 10 at once.
- **By §4, M3 goes onto the fresh 80 once, at the decision point, beside the 0.6B.**
- **For the owner's adoption decision, all of which this window assumes:**
  - two reranker models resident in the product (against W2-112's KPI and DEC-1043 (2)'s reasoning);
  - the cache released after each request (W2-112's memory release, re-pin window 4);
  - a product loader for zerank's "Yes"-logit score (the trial loader, in `src/`, a ticket);
  - L3's normalised lift in the product's ranking;
  - no install: zerank and gte need no new package.

## Version 5 (2026-11-06 ~14:30, before the live window runs): how the live window is read and judged
**The live window** (`drafts/score-once/live_window.sh`) measures M2 (the 4B in 8-bit + gte, merged) and then M3
(zerank + gte, merged), as they would run: both models loaded, each search scored by both.
- **The two services:**
  - two trial services on their own sockets, at `GOV_RERANK_GPU_SLOTS=3` for the trial services only. The slot-hold
    watcher keeps slot 1, so the live service and private rerankers are unaffected;
  - the smaller (gte) starts first;
  - the live 0.6B is stopped for the window and restored on every exit path.
- **The warm-up:** after both loads, one small request to each service. It releases the load's cached memory, because
  the trial copy empties its cache after every request (`GOV_RERANK_TRIAL_RELEASE=1`, window 4's form).
  - **Correction (2026-11-06 ~14:50, before the run):** an earlier line here said a live service's first request does
    this. It does not. Today's live worker never empties its cache (`src/gov/retrieval/rerank_worker.py`'s `scores`
    has no `empty_cache`; the live service held up to 15.75 GB, `rerank.py:38-39`).
  - **So every GPU figure of this window is with the release after each request.** Adopting M2 or M3 needs that
    release in the product (W2-112's memory release, re-pin window 4) as well as two services, and the owner decides
    with this stated.
- **The readings:** the GPU before and after the warm-up; the probe's peak at each model's own request bound (the
  4B's 8 texts and 12,000 characters).
- **The searches:**
  - 20 visible first calls, one at a time, each with a cold cache;
  - then 10 at once;
  - each search asks the two services one after the other. That is conservative for time; in parallel would be
    faster.
- **The variant:** v456, the question, L3 (`lift_norm` 0.0766).

**The four eligibility lines (§4), as read:**
1. **Speed alone:** the median whole search of the 20 is at most 3.0 s, and none failed or went unranked.
   - The median includes the harness's GPU read before each request, as in every earlier window, so it overstates
     the product.
   - The median without those reads is reported beside it, not judged.
2. **10 at once:** no request times out (the product's 30 s), and none failed or went unranked.
3. **The probe:** no shape at the budget, on either service.
4. **The GPU:**
   - **Judged:** the 1 Hz samples from after the warm-up to the end of the 10-at-once run, none at or above 14,255
     MiB.
   - **Reported, not judged:** the load-time samples' peak, and a derived bound (the GPU after the warm-up plus each
     service's peak minus its reserved-after).

**The outcome:**
- A cell that fails a line is not eligible, and the other is taken.
- If both fail, the 4B alone or gte alone (A1, A2: 114) are the eligible fallbacks. Each is measured the same way, in
  a window of its own.
- **Adoption is the owner's.** Two reranker models resident in the product is a new pattern, against W2-112's KPI
  and DEC-1043 (2)'s budget reasoning. M2 also needs bitsandbytes installed.

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
- **Withdrawn on review the same hour; nothing was judged under it.** The reviewer found the real cause in the code:
  - **`code_first` acts twice in the product:** before the fusion (`retrieve.py:327`, the code route sorted by cosine
    when the setting is truthy) and after the rerank (`:445`, the move).
  - **So L2's `code_first: 0` changed the fused head itself,** not only the move. That gave "4 of 40", and it would
    have confounded L2's stages.
  - Within one variant, a follow-up call reranks the same head as the first, so no fill is needed.
- **The fix:**
  - `code_first: 0` in a variant now keeps the setting truthy (a sentinel, so the pre-fusion sort stays as measured)
    and makes `routing.firsts` return nothing for it, so only the move is off. `named_first` and `ahead_types` act
    only after the rerank.
  - An unscored text again stops a replay in any call.
  - Tested: 21 of 21.
