# D4B-MISSES: the spent 60's 19 misses by kind, and the next lever (DEC-1074 (2))

- **For:** the owner. **By:** the CTO, session `812bc5ce`, 2026-11-05.
- **Evidence:** the auditor's record `docs/audit/memory-verdict-misses-kinds.md` (`3f975a3e`; W2-61h's role, kinds and
  counts only, leak check 0 and 0); the CTO's stage rows `~/gov-os-runs/D4B/diag/stage1-verdict.*` and
  `stage2-verdict-depth1000.json` (ids and ranks only).
- **The run classified** is the measurement set's single use: v456 plus the stated links, 40 of 59. The auditor asked
  whether it was v456, since the clone's own code pages 20. It was: the harness wrapped the clone with v456's settings
  (`sem_uncut`, routes 60 deep, `depth` 40, `perfile` 2, `dedup`), and every first-call rerank sent 40 texts
  (`verdict/v/run1/rx.log`). The page of 20 an agent sees is the first page of that 40-reranked order.

## 1. The result
**Your four kinds:**

| Kind | Count |
|---|---:|
| Ranked below 5 (the gold reached the ranking, then lost the top 5) | **10** |
| Vocabulary (the question asks in other words than the gold states) | 4 |
| Never retrieved (in neither route's top 60, for a reason other than vocabulary) | 3 |
| Other (the answer's section was found, the answer item was not) | 2 |

**Where the misses were lost:** 10 were reranked below 5, at places 6 to 12 (near misses), 2 were cut below the 40
reranked, 3 had only a neighbouring chunk of their section, and 4 were in neither route's top 60.

**The main causes:** the reranker 6, vocabulary 4, crowding (the same topic restated across files and tiers) 4, the
answer's form (one item diluted in its chunk) 3, a two-part question 2. In 4 of the ranked-low misses, a route had the
answer in its own top 5, and the reranker pushed it down.

**What reaches them** (the auditor's judgement, strong / weak):

| Lever | Strong | Weak | In reach |
|---|---:|---:|---:|
| A stronger reranker | 6 | 7 | 13 |
| Query phrasing or term mapping (splitting two-part questions, the user's words mapped to the record's) | 7 | 3 | 10 |
| A hop (from the record found to the one it links) | 4 | 3 | 7 |
| A stronger embedder | 2 | 2 | 4 |
| Answer-unit chunks | 1 | 11 | 12 |

**Two cautions:**
1. **In 7 of the 19, a chunk in the first five already answers the question, wholly or in part, but is not a labelled
   source.** These may be missing alternatives in the labels rather than retrieval misses. Labels are audited on a
   schedule, never because a question missed (DEC-1070 (14)), so nothing is re-labelled now. But 67.8 % may understate
   memory by up to 7 questions, and only an independent label audit can say how many.
2. **Two label doubts** (m12 incomplete, m37 ambiguous), by id only, for whoever owns the labels at the next audit.

## 2. The recommendation: the reranker trial next
- **Why:** by your rule, mostly ranked low means the reranker trial next. The evidence agrees: the reranker is the main
  cause in 6 and in reach of 13 of the 19, and most ranked-low misses sit at places 6 to 12. The embedder is the
  strong lever in only 2.
- **What runs:** ACT-RERANK-TRIAL-1's T3 and T4 as installed (mxbai-rerank-large-v2, then Qwen3-Reranker-4B in 8-bit),
  each beside the 0.6B, on the adopted structure (v456 and the links), with speed and GPU figures. No install is
  needed: the downloads and the trial venv are kept. The trial copy releases its cache after each request; the live
  service gets that release in re-pin window 4.
- **The choice rule, to be written before it runs** (it replaces the trial's old rule, which chose on the visible half
  of m6): on all the used sets together, the 79 and the spent 59 (138 questions), hit@5 then MRR, the gap between the
  sets not widening; eligible only under the trial's speed, concurrency and GPU limits. The verdict is the new set of
  80 at the next decision point, as DEC-1074 (3) says.
- **Then, second:** query phrasing as a research prototype (no install, no model): splitting two-part questions and
  mapping the user's words to the record's. It reaches 10, and it covers the vocabulary misses the reranker cannot
  reach. **The embedder trial third.**

## 3. For you
- **(a)** The next lever: the reranker trial, as in section 2 (recommended), or the embedder and phrasing first.
- **(b)** The trial's choice rule as written in section 2.
- **(c)** The missing alternatives (caution 1): **recommended**, the new set's cross-check (ACT-MSET-4) also lists, per
  question, any other place in the governing or restating tiers that states the same answer, as a recommended
  alternative (an R7 check, recorded in the rubric's next version); the tuning sets get the same at their next
  scheduled audit. Or leave the labels as they are.
- **Basis:** question 1 (memory: the lever chosen from the misses' kinds, not from guesses) and question 2 (a label
  that misses a true answer misjudges memory).
