# E3's search-again on the tied second place: top 20 and 40 unranked (E3-RESULT; E3-E5-DESIGN, DEC-1092)

Run on 2026-11-07, 19:11 to 19:43 (32 minutes), by the CTO (session `ad44f5fe`).
- **Run folder:** `~/gov-os-runs/D4B/e3-sa/` (counts only here).
- **Script:** `drafts/d4b/e3sa_run.py`. E2's reader and graders; up to three attempts; each later search built in its condition's own form.
- **The run:** 280 runs, 0 errors. Spent $31.70 against a $45 projection; the $90 brake was not reached. 50 live searches in all.
- **A slip:** the CTO's two record commits at about 19:30 (W2-136's merge and its records) each started the integration store's hook rebuild, about 30 s, while this run made live searches. DEC-1067 says no rebuild beside a measure. It was a different store (E0's clone is not the integration store), and the backstop read the GPU flat at about 7.5 GB, so no figure is expected to move. It is named here all the same.

## Right end to end, of the 138
| condition | A1 (one search) | A2 (up to two) | A3 (up to three) | wrong claims A1 / A2 / A3 |
|---|---|---|---|---|
| top 20 | 101 | **116** | 117 | 5 / 7 / 7 |
| 40 unranked | 104 | **118** | 123 | 4 / 5 / 5 |
| **today's bundle (E2)** | 115 | **128** | 128 | 2 / 3 / 3 |

By set at A2:

| condition | visible 40 | hidden 39 | spent 59 |
|---|---|---|---|
| top 20 | 36 | 32 | 48 |
| 40 unranked | 35 | 33 | 50 |
| today's bundle | 40 | 35 | 53 |

**The tests:**
- **A1 against A2:** top 20 gains 15 and loses 0 (p 0.00006); 40 unranked gains 14 and loses 0 (p 0.0001).
- **Against today's bundle at A2 (E2's 128):** top 20 has 0 gains and 12 losses (p 0.0005); 40 unranked has 1 gain and 11 losses (p 0.006).
- **The A1 figures differ from E3's one-call run** (101 and 101) by 0 and 3. That is the reader's run-to-run spread on the same bundles.

## What it means
- **Searching again helps every bundle.** It never lost a right answer: 15 and 14 gains, no losses.
- **Today's bundle with search-again stays the best:** 128, against 116 and 118 at the same two searches.
- **The ranked, expanded bundle is the right thing to hand an agent,** and "search again once" the right practice beside it.
- **A third search adds 5 for 40 unranked** (118 to 123), but nothing for today's bundle (E2) and 1 for top 20. Two searches stay the default (DEC-1094 (2)).
- **For the fresh 80, the candidate configuration from the 138** is today's bundle (the pin's retrieval with the pool on), with search again once. It is chosen before the 80 runs (DEC-1092 (4)), and E4 and E5 still to come.

**Basis:** question 1 (memory judged by what agents answer, end to end).
