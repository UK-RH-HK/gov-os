# E2's result: search-again on the 138 (declared in E1-DECLARATION.md and its amendment, `393305c3`)

Run on 2026-11-07, 17:24 to 17:39 (15 minutes), by the CTO (session `ad44f5fe`).
- **Run folder:** `~/gov-os-runs/D4B/search-again/e2/`. The questions, answers and grades stay there; this record gives counts and ids only.
- **Retrieval:** the product's (E0's first bundles; later searches with `pin-bcea09060ebc`). The reader has the "may be incomplete" line (DEC-1091 (3)).
- **Brake:** not reached ($21.95 spent, against a $25 projection and a $50 brake). 0 errors.

## Right end to end (the answer correct and its citation right), by condition
| set | A1, one search | A2, up to two | A3, up to three |
|---|---|---|---|
| visible 40 | 37 | **40** | 40 |
| hidden 39 (counts only) | 32 | **35** | 35 |
| spent 59 | 46 | **53** | 53 |
| **the 138** | **115 (83.3 %)** | **128 (92.8 %)** | 128 (92.8 %) |
| nonexistent-id, apart (2) | 2 | 2 | 2 |

- **A1 against A2:** 13 gains, 0 losses, exact McNemar **p = 0.0002**.
- **A2 against A3:** 0 and 0, p = 1.0. **A third attempt adds nothing on the 138.**

**More figures:**
- **Answer correct (the citation aside):** 121 at A1, and **135 (97.8 %)** at A2 and A3.
- **Wrong claims** (answered, not correct): 2 at A1 (both hidden), 3 at A2 and A3 (all hidden). **The visible and spent sets have none.**
- **Not found:** 15 at A1. These are mostly requests to search again cut at the first attempt; it is 0 at A2.
- **Misses recovered:**
  - E0 has 15 questions whose first bundle lacks the gold. For 8 of them, a later search's bundle holds it (the retrieval level).
  - **13 questions not right at A1 are right at A3** (the answer level): Q14, q23, q31, h01, h16, h27, m01, m03, m09, m30, m33, m36, m43.
  - Q14, the pilot's wrong claim, is now right, with the "may be incomplete" line.
- **The graders agreed on 138 of 140.**

## Cost and time (measured)
- **The run:** $21.95 in all for 140 questions, $0.157 a question.
  - 159 reader calls and 19 live searches, with a median reader call of 10.4 s (p90 16.4 s);
  - 280 grader calls (two per graded answer).
- **Tokens:** 2,493,057 in (2,179,250 cache creation, 312,919 cache read, 888 plain) and 276,095 out.

## What it means
- **Searching again once is worth it.** On the 138, what agents answer right end to end goes from 83.3 % to 92.8 % with up to two searches. It never made a right answer wrong, and the cost of the second search is small (19 searches for 140 questions).
- **Two searches are enough.** The third never changed an outcome here.
- **The remaining 10 at A2:**
  - 3 are wrong claims, all hidden, counted only, never inspected;
  - 7 are correct answers whose citation missed the gold's lines.
- **Against E0's retrieval figures:** hit@5 76.8 %, in the first call's bundle 89.1 %. An agent answers better than hit@5 suggests, because it reads the whole bundle, and better again when it searches once more.
- **This is the evidence for the practice package (DEC-1085 (5)):** search again once, in your own words, when the bundle does not answer or your answer may be incomplete. It is on the tuning sets (visible, hidden and spent). The fresh 80 gives the verdict, once, after the decisions.

**Basis:** question 1 (memory judged by what agents answer, end to end).
