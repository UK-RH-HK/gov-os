# Memory recall diagnosis: the hidden half, in kinds only (DEC-1070 (6))

- **By:** an independent session acting in W2-61h's role (the hidden half's checker, `.tickets/DAEO-h2k3.md`), on the CTO's brief. It is read-only apart from this file.
- **Date:** 2026-11-04.
- **What was read:** the 7 hidden question files below; the m6 clone (`~/gov-os-runs/D4B/m6/repo`) at its head, with the gold spans resolved by the measure's own `_span` and the chunk table of its store (read-only); the kept first-call outputs in `~/gov-os-eval/runs/m6/run1/` (the 20 gathered and the NOT_GATHERED gaps); the CTO's `stage1`, `stage2-depth1000` and `stage3-routes` rows for these ids; the route code (`retrieve.py`, `routing.py`, `lexical.py`, `semantic.py`, `chunking.py`). Nothing was run: no retrieval, no `gov`, no measure, no model.
- **The hidden-half rule was kept:** this report holds ids, kinds, counts and general phrases only. It has no question text, gold answer, gold path, heading, line or fact, and no path of a competing chunk.
- **No label was judged:** no id is marked "outside scope".
- **The closure route:** none of the 7 first calls has a closure item in its 20 (the CTO's `closure_any_in_20` is 0 for each), so the closure's unranked set neither crowds these fusions nor cuts their gold.

## Per id

| Id | Piece | Kinds | What outranked the gold in the first call (kind and tier) | Levers that plausibly reach it |
|---|---|---|---|---|
| h02 | 1 | K2, K7, K4, K1 (partial) | Governing: other chunks of the gold's own decision section (the "how applied" part, which was gathered) and earlier and later decision records on the same topic. Middle: a proposal package on the same topic, and plans. Reports and assessments sit just past the 20. | Widening a gathered chunk to its section: strong, since a sibling is already in the 20. Deeper route lists (100) together with more chunks reranked (40) would reach keyword 90. |
| h02 | 2 | K6, K4, K5 | The same as piece 1. The answer sits in a later record under the name of the mechanism that replaced the one the question names. | None of the listed levers. A supersession hop from a gathered record would be needed (not on the list). |
| h05 | 1 | K5, K7, K4, K3 | Governing: architecture-record table rows and decision records on the same subject, and a capability page whose title matches the question's generic words. Middle: packages, a ticket and a research report on the same subject. Code: other modules with similar settings. | Deeper route lists (60), since keyword 33 and meaning 42 sit just past 30, with more chunks reranked (40). A file-level index is weaker. |
| h11 | 1 (code alternative) | K3, K6, K1, K5 | Governing: capability pages, contract items and decision records on the same topic. Middle: a change record on the same decision, and plan cards and tickets on the same topic. | None of the listed levers: the best rank is meaning 123 and keyword is over 500. It needs phrasing (the user's terms mapped onto the record's labels), or a hop from a gathered record to the code that cites it. |
| h11 | 1 (record alternative) | K4, K6, K7, K5 | As above. | As above. |
| h16 | 1 | K8, K7, K4, K5 | Middle: proposal and investigation packages and tickets on the same topic. Reports: research and audit reports. Governing: one decision record. | A file-level index, for the whole configuration file. Depth does not reach it (ranks 140 to 152). Splitting a two-part question into its parts (phrasing, not on the list) would also help. |
| h16 | 2 | K8, K1, K5 | As above. | Identifier tokenisation: the question's words appear in the code only inside snake_case identifiers and environment names, which the tokenizer keeps whole, and M4 is off in m6. Depth does not reach it (ranks over 400). |
| h17 | 1 | K2, K7, K4 (mild), K5 | Governing: other chunks of the gold's own decision section (its heading chunk at place 6, and the items before and after it), and later records on the same subject. Middle: the plan card and the ticket for the same subject, and an archive note. Code: a sibling function in the gold file. | Widening a gathered chunk to its section: strong, since the heading chunk is in the 20. More chunks reranked (40) would take fused 27. The meaning route not cut after fusing the phrasings, together with deeper lists (60), would keep meaning 25 from being dropped. |
| h17 | 2 | K4, K5 | As above. | Deeper route lists (100) with more chunks reranked (40), for keyword 83. |
| h27 | 1 | K2, K7, K1, K5 | Middle: one large plan table whose many row chunks each match the question's generic words (most of the 20), a section of a prompt and a list summary. Governing: a decision record on a neighbouring subject. | Deeper route lists (100), for meaning 58 to 75, with more chunks reranked. Widening a gathered chunk to its section works only if the sibling at fused 49 gets reranked. A per-file cap in the fusion (not on the list) would also help. |
| h33 | 1 (configuration alternative) | K7, K4, K5 | Generated copies of one text (four places in the 20), derived pages, governing decision and architecture records, kernel files, plans, tickets and assessments, all restating the same content. | The meaning route not cut after fusing the phrasings (24 becomes 32 uncut), with deeper lists (60) and more chunks reranked (40). Keyword 61 to 75 needs depth 100. Collapsing duplicate generated copies (not on the list) would free places. |
| h33 | 1 (table alternative) | K7, K5 | As above. | As above. |

Kind notes, in general terms:
- **K4** here is mostly an answering item that shares its chunk with a long title or status line or with unrelated items, or a field block chunked by size together with neighbouring blocks.
- **K7** here is a numbered list item (h02, h17, h27, h11's record), a YAML field (h16, h33), a table row (h33) or a single code line (h05).
- **K8 (h16)** is a two-part question: each gold piece matches only half of the question's words, so each loses to sources that match the other half too.

## Counts over the 7 ids

An id is counted once if any of its pieces or alternatives has the kind or the lever.

| Kind | Ids |
|---|---|
| K1 vocabulary | 4 (h02, h11, h16, h27) |
| K2 split section | 3 (h02, h17, h27) |
| K3 code fragment | 2 (h05, h11) |
| K4 diluted chunk | 6 (h02, h05, h11, h16, h17, h33) |
| K5 crowded topic | 7 (all) |
| K6 indirect | 2 (h02, h11) |
| K7 form | 7 (all) |
| K8 other (two-part question) | 1 (h16) |

| Lever (plausible) | Ids |
|---|---|
| Deeper route lists (60 or 100) | 5 (h02, h05, h17, h27, h33) |
| More chunks reranked (40) | 4 (h02, h05, h17, h33) |
| The meaning route not cut after fusing phrasings | 2 (h17, h33) |
| Code chunks cut on definitions | 0 (h05 marginal) |
| Widening a gathered chunk to its section | 3 (h02, h17 strong; h27 conditional) |
| A file-level index | 2 (h05 weak, h16) |
| Identifier tokenisation | 1 (h16) |
| None of the listed levers | 1 id entirely (h11), plus h02's second piece |

Levers outside the list that the kinds point to:
- Phrasing: splitting multi-part questions and mapping the user's terms to the record's (h11, h16, h27).
- A supersession or citation hop from a gathered record (h02, h11).
- Collapsing duplicate generated copies, or a per-file cap in the fusion (h27, h33).

Hit@5 also needs the reranker to lift the gold into the first five once it is in the 20. These levers only bring the gold to the reranker.
