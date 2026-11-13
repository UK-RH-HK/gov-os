# E4's result: today's bundle built by M3 and by M1, against the 0.6B (E3-E5-DESIGN, DEC-1092)

Run on 2026-11-07 by the CTO (session `ad44f5fe`). Counts only.
- **The scoring window, 22:17 to 22:28** (`drafts/score-once/e4_window.sh`; review READY in round 2, `reviews/e4-window.md`; pinned `E4-REVIEWED.sha256`): the live service stopped for the planned window, gte and zerank loaded one at a time, 360 missing texts scored by each (0 lacking after), the GPU peak 10,696 MiB (never at the 14,255 budget), the live service restored (class 3's check: `rerank.by` = service).
- **The replays, 22:28 to 22:38** (`e4_replays.sh`, strict, no GPU): M3 (zerank + gte, merged, L3's lift) and M1 (the 0.6B + gte, merged).
- **The reader runs** (`drafts/d4b/e4_run.py`; E3's reader and graders, one call per question on each cell's first bundle): 280 runs, 0 errors, spent **$37.33 against a $35 projection** (over by $2.33, within the $70 brake; the M3 and M1 bundles carry slightly more text), 24 minutes.

## Retrieval on window 4's code (the replays)
| reranker | hit@5 (of 138) | MRR | gold in the first bundle |
|---|---|---|---|
| the 0.6B (E0b B, B0's form) | 106 | 0.560 | 123 |
| **M1** (the 0.6B + gte) | 114 | 0.601 | 123 |
| **M3** (zerank + gte) | **117** | 0.607 | 123 |
| (gte alone, zerank alone: the window's by-products) | 113, 113 | 0.623, 0.594 | 123, 123 |

## What agents answer: right end to end, one reader call
| bundle built by | visible 40 | hidden 39 | spent 59 | **the 138** | correct | wrong claims |
|---|---|---|---|---|---|---|
| **the 0.6B (E3's "today's bundle")** | 37 | 32 | 45 | **114** | 121 | 3 |
| M3 | 34 | 32 | 45 | **111** | 119 | 2 |
| M1 | 34 | 33 | 46 | **113** | 120 | 4 |

- **M3 against the 0.6B:** 3 gains, 6 losses, exact McNemar p 0.51.
- **M1 against the 0.6B:** 3 gains, 4 losses, p 1.0.
- **The nonexistent-id questions** were right in every cell.

## What it means
- **The better rerankers rank the gold higher, but agents do not answer better.** M3 lifts hit@5 by 11 (106 to 117). Every cell holds the gold in the first bundle for the same 123 questions, and the reader reads the whole bundle. So moving the gold from rank 6 to rank 3 inside a bundle of 19 changes nothing that the agent then does.
- **Under the reading rule fixed before these figures** (M3-ADOPTION-1, committed at `e0c63aa4`: at least 4 more right answers than today's bundle, with no more wrong claims), **M3 is not better end to end.** Neither is M1.
- **For the configuration of the fresh 80:** the 0.6B stays. That means the pin, the pool on, today's bundle, and search again once.

**Basis:** question 1 (a reranker is judged by what agents answer, not by hit@5 alone) and question 4 (no second model, doubling the scoring on a busy GPU, without an end-to-end gain).
