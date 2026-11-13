# E3's result: five bundles, one reader call each, on the 138 (E3-E5-DESIGN, approved by DEC-1092; as run `24e0e8b0`)

Run on 2026-11-07, 18:25 to 19:27 (62 minutes), by the CTO (session `ad44f5fe`).
- **Run folder:** `~/gov-os-runs/D4B/e3/`. The questions, answers and grades stay there; this record gives counts only.
- **The run:** 700 condition runs of 700, 0 errors. Spent $77.80 against a $150 projection; the $300 brake was not reached. The graders agreed on 690 of 700.

## Right end to end (the answer correct and its citation right), one reader call, no search-again
| condition | visible 40 | hidden 39 | spent 59 | **the 138** | correct | citation right | gold in the bundle | wrong claims | not found | median size | cost |
|---|---|---|---|---|---|---|---|---|---|---|---|
| top 5 | 25 | 25 | 34 | **84 (60.9 %)** | 101 | 99 | 100 | 10 | 27 | 4.6k chars | $9.62 |
| top 10 | 26 | 27 | 36 | **89 (64.5 %)** | 99 | 108 | 111 | 13 | 26 | 9.0k | $12.24 |
| top 20 | 33 | 29 | 39 | **101 (73.2 %)** | 112 | 115 | 117 | 3 | 23 | 16.3k | $16.30 |
| **today's bundle** | 37 | 32 | 45 | **114 (82.6 %)** | 121 | 123 | 123 | 3 | 14 | 21.8k | $15.54 |
| 40 unranked | 31 | 31 | 39 | **101 (73.2 %)** | 111 | 117 | 118 | 5 | 22 | 29.6k | $23.77 |

The nonexistent-id questions (h24, m60, apart) were right in every condition.

**Against today's bundle** (exact McNemar on right end to end, Holm within E3):
- top 5: 1 gain, 31 losses, p < 0.0001;
- top 10: 1 and 26, p < 0.0001;
- top 20: 1 and 14, p 0.0010 (Holm 0.0020);
- 40 unranked: 2 and 15, p 0.0023 (Holm 0.0023).

## What it means
- **Today's bundle is the best of the five, clearly.** It holds the same top 20 chunks as "top 20", plus the product's expansions (an item widened to its parent) within 6,000 tokens. Those expansions alone give 13 more right answers than the plain top 20 (114 against 101). E2's one-search figure on the same bundle was 115; the difference of 1 is the reader's run-to-run spread.
- **Fewer items are worse, and more wrong.** The top 5 and top 10 lose 25 to 30 right answers and make 10 to 13 wrong claims, against 3. With too little in front of it, the reader answers from partial evidence.
- **More items, unranked, are not better.** 40 candidates in no order give 101, against 114 for today's ranked and expanded 20, at about 1.5 times the cost.
- **E0's hit@5 (76.8 %) understates the agent;** today's bundle gives 82.6 % in one reader call, and E2 gives 92.8 % with search-again.

## Next: search-again on the best two (E3-E5-DESIGN §1)
- **The best:** today's bundle. Its search-again run is **E2 itself**: the same reader, instruction and bundle, up to three searches. A1 115, A2 and A3 128, so it is not run again.
- **The second place is a tie:** top 20 and 40 unranked, both at 101. The design named no tie-break, so **both are run with search-again**, which runs a superset of "the best two" rather than choosing between them after the fact.
  - The later searches are built in the condition's own form: the plain top 20 of the new search; the 40 unique chunks of its calls 1 and 2, shuffled.
  - Projection $45, brake $90.

**Basis:** question 1 (memory judged by what agents answer, end to end).
