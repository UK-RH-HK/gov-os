# E1's pilot result: search-again on 5 visible questions (declared in E1-DECLARATION.md, `a29d4157`)

Run on 2026-11-07, about 17:20 to 17:28, by the CTO (session `ad44f5fe`).
- **Outputs:** `~/gov-os-runs/D4B/search-again/pilot/` (one file per question, plus `summary.json`).
- **Script:** `drafts/d4b/e1_pilot.py`.
- **Retrieval:** the product's (E0's first bundles; later searches with `pin-bcea09060ebc`).

## Per question
| question | first bundle holds gold | attempts | gold in bundle by attempt | final | citation | grader (opus) | check (sonnet) | cost |
|---|---|---|---|---|---|---|---|---|
| Q14 | no | 1 | no | answer | wrong | wrong | wrong | $0.16 |
| q23 | no | 2 | no, **yes** | answer | right | correct | correct | $0.30 |
| q31 | no | 2 | no, **yes** | answer | right | correct | correct | $0.29 |
| Q01 | yes (rank 1) | 1 | yes | answer | right | correct | correct | $0.16 |
| Q03 | yes (rank 6) | 1 | yes | answer | right | correct | wrong | $0.20 |

- **Misses recovered:** 2 of 3. In q23 and q31, the reader searched again in its own words, the second bundle held the gold, and both answers were right end to end. Under A1 (one search) both would have been answered or settled without the gold.
- **One wrong claim (Q14):**
  - The question is about which tickets depend on W2-03. Its gold is spread over many places (13 pieces), and the label is marked volatile (DEC-1069).
  - The reader answered from the first bundle, while saying itself "this list may not be complete, because the bundles don't include a search of every ticket's deps". It did not search again.
  - **The practice's instruction does not tell the reader to search again when it knows its answer is partial.** This is the main design point for the owner before E2 (below).
- **The graders agreed on 4 of 5.** On Q03 the first grader said correct and the check said wrong. The first grader's verdict counts (D4B-SEARCH-AGAIN §4), and the disagreement is counted.
- **The schema held** on every call (structured output, no error), and no call reached its budget cap.

## Cost and time (measured, each call's own `total_cost_usd` and usage)
- **Total:** $1.11. The reader cost $0.92 (7 calls, `claude-opus-5-5` at effort high); the graders cost $0.19 (10 calls).
- **Tokens:** 119,255 in (109,941 cache creation, 9,280 cache read, 34 plain) and 13,915 out.
- **Per question:** $0.22 in the pilot, which over-represents misses (3 of 5). By kind: about $0.16 when the first bundle answers, and about $0.30 when it takes a second search.
- **Projected to the 138:** E0 has 123 questions with gold in the first bundle and 15 without, which gives **about $25** (up to $31 at the pilot's mix).
- **Wall time:** the reader's median call took 13.3 s (the estimate was 45 s). At 4 calls at once, the 138 take about 15 to 20 minutes.
- **E2 to E5, projected from the pilot's cost per token:** about $8 per million tokens across reader and graders, against SEVEN-ANSWERS §7's about 15M tokens, gives **about $100 to $150 in all**. E3 is the largest part. The figure is uncertain until E2 measures it on the 138.

## For the owner, before E2 (DEC-1086 C)
1. **The cap.** Recommended: **$40 for E2** (the 138 with up to three searches and two graders; projected $25 to $31, plus margin). Every call keeps its own cap (`--max-budget-usd`), and the run stops if its spend passes the cap.
2. **The instruction (Q14).** Recommended: add one sentence to the practice before E2: "If you can tell your answer may be incomplete, search again for what is missing." This changes the practice under test.
   - It was found on the visible half, by the pilot, whose job is to check the instructions. E2 then measures it once on the 138.
   - The alternative is to run E2 as declared and treat Q14's kind as a finding.

**Basis:** question 1 (an agent's search practice measured end to end) and question 4 (the cost known before the run).
