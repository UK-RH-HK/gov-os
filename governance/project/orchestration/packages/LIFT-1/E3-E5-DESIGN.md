# E3 to E5: the end-to-end design package, for the owner's approval before any run (DEC-1085 (6), DEC-1087 (11), DEC-1091)

For the owner. The CTO, 2026-11-07, session `ad44f5fe`. It follows SEVEN-ANSWERS §7 as approved and is amended to the product's bundles (E1-DECLARATION). **Nothing here runs before the owner approves it.**

## 1. What is measured
**The question:** what an agent actually answers, right end to end, from what memory hands it. "Right" means the answer is correct and its citation is right. "Not found" is right only for the nonexistent-id questions (h24, m60), which are counted apart.

**The conditions, each a bundle given to the same reader** (one reader call per question per condition, no search-again unless named):

| exp | condition | built from | GPU |
|---|---|---|---|
| E3 | **top 5** | the first call's ranked items 1-5 (E0's kept outputs) | no |
| E3 | **top 10** | items 1-10 | no |
| E3 | **top 20** | items 1-20, as ranked | no |
| E3 | **today's bundle** (the baseline) | the first call's bundle exactly as an agent receives it (its items, cuts and expansions, 6,000 tokens) | no |
| E3 | **40 unranked** | the pool's 40 candidates (calls 1 and 2's items) in a fixed shuffled order, seed per question | no |
| E3 | **search-again on the best two** | E2's practice (up to three searches) on the two best of the five above | live searches |
| E4 | **today's bundle by M3** (zerank + gte) and **by M1** | the score-once harness at window 4's commit, once E0b is fixed (E0-DECLARATION) | the harness scores, one window |
| E5 | **a page of 40 within 12,000 tokens** | a live run with `--batch-size 40 --bundle-budget 12000` on E0's clone | one GPU job, ~25 min |

- **Shared baseline:** E4's 0.6B condition and E5's 6,000 condition are E3's "today's bundle". They are run once and shared.

## 2. The reader, the grader and the rubric
- **The reader:** the same as E2 (`claude-opus-5-5`, effort high, no tools, no transcript, the run's own system prompt with the "may be incomplete" line, `--json-schema`). It is given the question and one bundle. In the search-again condition, the bundles accumulate.
- **The citation:** checked by code, with the measure's own matcher (`gov.retrieval.measure._match`: gold re-anchored at the clone's commit, source families).
- **The answer:** graded by `claude-opus-5-5` (counts) and checked by `claude-sonnet-5-5` (agreement, reported) on every graded answer. The pilot and E2 show the second grader costs little.
- **The rubric, fixed now:**
  - **correct:** it states the gold answer's facts and contradicts none;
  - **wrong:** it contradicts them or misses their substance;
  - **not found:** it says so.

  A wrong claim is an answer that is not correct. The questions, answers and grades stay in the run folders, and the CTO sees counts and ids only (the hidden-half rule).
- **Statistics:** each condition against today's bundle, exact McNemar on "right end to end", with Holm within each experiment. Gains, losses and p are always given (DEC-1079).
- **Reported per condition, per set (visible 40, hidden 39, spent 59) and on the 138:**
  - right end to end, correct, citation right, wrong claims and not found;
  - the reader's input tokens (the bundle's size);
  - cost and wall time.

## 3. The point for the owner: who reads the hidden and spent sets
As in E2, approved by DEC-1086 C for search-again: the readers and graders read the hidden and spent questions and their gold, in sessions with no tools and no transcript, from run folders under `~/gov-os-runs/D4B/`. No measured role reads them, and the CTO sees counts only. **Recommended: the same for E3 to E5** (the misses are mostly in those sets).

## 4. Cost (projected from the pilot's and E2's measured calls) and the runaway brake (DEC-1091 (2))
| exp | calls | projection | brake (twice) |
|---|---|---|---|
| E3, five conditions | 690 reader calls plus graders; top 20 and 40 unranked carry about 2-3 times the input | **about $150** | $300 |
| E3, search-again on the best two | about 300 reader calls plus graders | **about $55** | $110 |
| E4, two new conditions | 276 reader calls plus graders, plus E0b's harness window | **about $50** | $100 |
| E5, one new condition | 138 reader calls plus graders (the larger bundles) | **about $35** | $70 |
| **in all** | | **about $290** | |

- **A correction to E1-PILOT-RESULT:** it projected E2 to E5 at "$100 to $150 in all". With E2's measured cost per call, and the larger bundles of top 20, 40 unranked and 12,000, E3 to E5 come to about $290.
- **Time:** about 2 to 3 hours of runs at four calls at once. E4 waits for E0b's fix.

## 5. The K9 bar on end-to-end accuracy, proposed before any run (DEC-1085 (6))
- **The proposal:** on the fresh 80, measured once on the chosen configuration and practice, **right end to end at least 85 %**, the target **95 %**, and **wrong claims at most 5 %**.
- **Beside DEC-1083's hit@5 bar** (85 % on the fresh 80), not replacing it. Both are reported.
- **Why these figures:** the same floor and target as CAP-10 and DEC-957, applied to what agents answer. The wrong-claim ceiling exists because an agent that answers confidently and wrongly does more harm than one that says "not found".

## 6. The order, and what follows
1. E2 (running).
2. E3's five conditions.
3. E3's search-again on the best two.
4. E5.
5. E4, once E0b is fixed.
6. Then the owner's decisions: the configuration, the skill rule (search-again as practice, DEC-1085 (5)), the K9 bar. Then the fresh 80, once.

**For the owner:**
1. Approve E3 to E5 as designed.
2. The hidden-set reading as in E2 (§3).
3. The K9 end-to-end bar (§5).

**Basis:** question 1 (memory judged by what agents actually answer, against a bar declared before the figures).

## As run (approved by DEC-1092; written before E3's run)
- **How the conditions are built** (`drafts/d4b/e3_run.py`, run with the pin's python):
  - **top 5, 10, 20:** the first call's ranked chunks with **their own spans**. Each chunk's span comes from the clone store's `lexical_chunk`, so an item the product expanded goes back to its chunk.
  - **today's bundle:** the first call's evidence **exactly as sent**, its expansions included.
  - **40 unranked:** the unique chunks of calls 1 and 2 (the pool's 40), with their own spans, shuffled with the question's id as the seed. The reader is told the items are in no particular order.
- **Dry run, gold in the bundle before any reader** (of the 138):
  - top 5: 100;
  - top 10: 111;
  - top 20: 117;
  - today's bundle: 123 (E0's figure);
  - 40 unranked: 118.

  Median sizes: 4.6k, 9.0k, 16.3k, 21.8k and 29.6k characters. Today's bundle holds more gold than the plain top 20 because the product's expansions widen some items to their parent.
- **The reader and grader** are E2's, with the "may be incomplete" line. A `search_again` verdict counts as not found here.
- **E3's five conditions:** projection $150, brake $300. Search-again on the best two follows as its own run.
