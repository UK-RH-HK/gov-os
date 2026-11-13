# E5's result: today's bundle at 6,000 tokens against a page of 40 within 12,000 (E3-E5-DESIGN, DEC-1092)

Run on 2026-11-07 by the CTO (session `ad44f5fe`). Counts only.
- **The live part:** 19:44 to 20:05. The 138 went through the pinned gov on E0's clone (`c00d525f`) with `--batch-size 20 --bundle-budget 12000`, a page of 40.
  - Log: `~/gov-os-runs/D4B/w4-e5/e5.log`; kept outputs in `~/gov-os-eval/runs/w4-e5/`.
  - No model tokens; the backstop did not trip.
- **The reader run:** 140 reader calls with E3's reader and graders, compared with E3's run on today's 6,000-token bundle. Run folder `~/gov-os-runs/D4B/e5/`.
  - Spent $29.50 against a $35 projection; the $70 brake was not reached. 0 errors, 13 minutes.

## The retrieval (the live part)
| | gold in the first bundle | hit@5 | hit@10 | hit@20 | MRR |
|---|---|---|---|---|---|
| 6,000 tokens, page 20 (E0) | 123 | 106 | 118 | 124 | 0.5665 |
| **12,000 tokens, page 40** | **124** | 108 | 118 | 123 | 0.5691 |

## What agents answer: right end to end, one reader call
| | visible 40 | hidden 39 | spent 59 | **the 138** | correct | wrong claims | median size |
|---|---|---|---|---|---|---|---|
| 6,000 (E3's "today's bundle") | 37 | 32 | 45 | **114** | 121 | 3 | 21.8k chars (19 items) |
| **12,000, page 40** | 36 | 33 | 46 | **115** | 123 | 4 | 43.6k chars (36 items) |

- **12,000 against 6,000:** 3 gains, 2 losses, exact McNemar **p = 1.0**.
- **The nonexistent-id questions** (h24, m60) were right at both sizes.

## What it means
- **Doubling the bundle buys nothing.** It costs twice the reader's input (about $0.21 a question against $0.11) and one more gold source in the bundle, for one more right answer, which is noise.
- **The 6,000-token bundle stays** (BUNDLE-BUDGET-1; W2-135's 4,000-character cap per item stands).
- **The candidate configuration for the fresh 80 is unchanged by E5:** today's bundle at 6,000 tokens, with search again once (E2, E3-SA-RESULT). E4 (the other rerankers) is still to come, after the harness fix.

**Basis:** question 1 (memory judged by what agents answer) and question 4 (no larger bundle without a measured gain).
