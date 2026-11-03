# D4B-GAPS: the gaps for W2-32, from measure 1 and the five modes (P1, for the owner; W2-15a's KPI: at most three, chosen with the owner)

By the CTO (session 33b3628c), 2026-11-04 ~00:30. Sources: D-4b measure 1 (`~/gov-os-runs/D4B/m1/`); W2-15a's evidence
record (`docs/research/EXP-003/w2-15a-baseline.md` on `w2/W2-15a`, `fd637510`, by the research agent); DEC-1065 (3).
Estimates are the research agent's, marked (est.).

## The measure (48 questions; hit@5; three identical runs, noise band 0)
| mode | visible | hidden | all | full evidence |
|---|---:|---:|---:|---:|
| lexical only | 12 | 13 | 25 (52.1 %) | 27 |
| semantic only | 10 | 11 | 21 (43.8 %) | 20 |
| fused, no reranker | 13 | 12 | 25 (52.1 %) | 34 |
| **fused + reranker (shipped)** | 12 | 16 | **28 (58.3 %)** | 34 |
| the best mode per question | 16 | 18 | 34 (70.8 %) | — |

No single route beats the fused search in total, but **per question single routes win where the fusion loses** (34
against 28): by DEC-1065 (3), the fusion is a gap. The lighter reranker is not installed (not measured; nothing installed).

## What the misses come from (the research agent's classification of the 20)
1. **The fusion drops single routes' top hits.** The closure route enters the rank fusion (RRF, k=60) as an *unranked*
   set of every chunk it reaches, so any chunk two routes return outscores one route's first hit (h22: rank 1 in
   semantic, rank 72 fused; also Q11, Q18, h04).
2. **The models see under half of each chunk.** The embedder reads the first 512 characters, the reranker the first 500;
   chunks run to 1,200. The gold lies past that point for Q10, Q16, q24, and in part Q07, Q11.
3. **The evaluation set's own source document crowds the top 5.** `docs/assessment/2026-10/B-memory-retrieval.md` (lens B's
   report, which quotes the visible questions; never a gold source, W2-61 F4) is in the top 5 for 7 of the 12 visible misses.
4. **Parent expansion sends a span twice** across continuations (and identical close records duplicate each other).
5. **Q09 is a labelling miss:** the Contract's CAP-15 states the answer at rank 1, but its gold names only the ticket's KPI line.
6. No visible miss is an indexing gap: every visible gold chunk is indexed and embedded.

## The gaps (choose at most three for W2-32's rounds; two lie outside its menu)
| gap | what changes | targets | est. | W2-32 line |
|---|---|---|---|---|
| **G1 chunking and what the models see** | the embedder and the reranker read the whole chunk (1,200 characters: `EMBED_CHARS`, `RERANK_CHARS`; the manifest's cut changes, so a full re-embed by S1), or spans of ~500 characters; parent expansion keeps its expanded parents across continuations (cause 4) | Q10, Q16, q24, Q07, Q11, hidden misses past character 500 | +2 to +4 | S7 (chunking) |
| **G2 lexical tuning** | code ranked above tests and assessments for code questions; call sites preferred for `--id` questions | Q10, Q11, q23, h07, h08 (Q18, h04 with G3) | +2 to +3 | S6 (lexical) |
| **G3 the fusion** | the closure route ranked or down-weighted; each route's first hits kept a place in the first batch; the semantic route's hits kept through fusion and rerank | h22, h04, Q07, Q11, h16, Q18, Q06 | +3 to +5 | **outside the menu** (S8 is "the hit@5 85 row"): needs W2-32's KPIs changed (DEC-1065 (3): the owner decides) |
| **G4 the measure's own document out of the index** | lens B's report (and the evaluation fixtures) out of both indexes (D-7's scope: the path map; a keyword-index exclusion if the lexical index has none, then a small code change) | up to 7 visible misses (est. +2 to +5) | +2 to +5 | **outside W2-32**: D-7 (the index scope), now |

Not a gap but a decision: **Q09's label** (its gold names the KPI line, the Contract answers it): re-labelled by an
independent session, as q03 was (DEC-1060), or kept. Recommended: re-label, blind to the answers (+1).

## Honest estimate against the target
The research agent's estimate for G1 to G3 together is **33 to 36 of 48 (69-75 %)**, capped near the per-question best
(34) unless the models see more. With G4 and Q09, about **37 to 41 (77-85 %)** (est., the CTO's sum; overlapping targets
make it uncertain). **The 85 % floor is reachable only at the top of that range; 95 % (46 of 48) is not reachable with
these levers.** Beyond them the next levers are bigger: a stronger reranker or embedder (an install: the owner's), the
reranker reading more than one chunk per candidate, query rewriting. W2-32's S9 brings it back to the owner after two
rounds below 85 %.

## Recommendation
- **G4 now, inside D-7** (it is index scope, not retrieval tuning; measured by measure 2 with D-7's other changes).
- **G1, G3 and G2 as W2-32's three rounds**, in that order (G1 and G3 have the largest effects; G3 needs W2-32's KPI S8
  read as "the fusion keeps single routes' top hits", or a new line), each round with a rebuild and a measure and F1's
  revert rule.
- **Q09 re-labelled** blind, by an independent session, with the old label kept on record (DEC-1060's form).
- **The next levers** (a stronger model; the reranker's reach) as a package after W2-32's first two rounds, if S9 triggers.

**For the owner:** (1) the three gaps and their order; (2) whether W2-32's KPIs change for G3; (3) G4 in D-7; (4) Q09's
re-label.
