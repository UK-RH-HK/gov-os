# D4B-RESEARCH: what the retrieval survey changes before measure 3 (for the owner; DEC-1066 (5))

By the CTO (session 33b3628c), 2026-11-04 ~00:55. Source: the research agent's survey and 63 no-install runs on measure
1's clone. The report is `docs/research/EXP-003/retrieval-survey/REPORT.md`, on branch `w2/research-retrieval`
(`d49aae04`; harness and raw records `3c14830e`), not merged. Measured figures are hit@5 of 48, with the shipped search
at 28. Estimates are marked (est.).

## What it found
| lever | measured | note |
|---|---:|---|
| the reranker reads the whole chunk (G1's reranker half) | **+4 → 32** | biggest single lever; no install |
| the code route's first 2 hits ahead for a question that names a symbol | **+3 → 35** | routing by question type |
| the named record's 2 best chunks ahead for a question that names a record | **net +1 → 36** | gains Q06, Q07; loses h22: fragile |
| every pure fusion change (RRF k, closure weight, per-route quotas, min-max, blends) | −2 to 0 | the reranker decides the top 5 |
| G4 (lens B's report and the fixtures out) | 0 | still right, for an honest measure |
| the best result per question over all 63 runs | 39 | 9 questions are never hit by any variant |

**s01 = 36/48 (75 %)**, 18 of 24 on each half, confirmed by a cold rerun. The levers were chosen over all 48 questions, so
**the hidden half's 18/24 is optimistic** (s01 is also the best on the visible half alone). The survey's tables show
the published case for a stronger reranker: Qwen3-Reranker-0.6B, today's model, scores *below* its own first stage on
code (MTEB-Code 73.4 against 75.4).

## My view: what changes before measure 3
1. **G1 (W2-32 round 1, built as S7): as built.** Both models read the whole chunk. Add one rule from the GPU evidence:
   **at most 16 texts per reranker request**. Sending 100 whole chunks at once is what pushed the GPU to 15.75 GB
   tonight. This is a ticket note within S7, not a new KPI; I will apply it unless you object.
2. **G3 (round 2) as routing by question type, not fusion weights.** DEC-1066 (2) worded S8 as "the fusion keeps each
   route's top hits". Quotas and weights measured 0 or worse; routing measured +3 and +1. **Proposed S8:**
   - a question that names a symbol puts the code route's first 2 hits ahead after the rerank;
   - a question that names a record puts that record's 2 best chunks ahead.
   Each half is kept only if it holds at the round's measure (F1's revert rule), so the fragile second half is dropped
   if it does not. **Yours to decide** (it changes your DEC-1066 (2) wording).
3. **G2 (round 3): unchanged** (est. +0 to +2; needs a lexical code change, so not measurable here).
4. **Keeping the hidden half honest.**
   - W2-32 adopts only levers that also win on the visible half alone (v14, r01 and s01 do).
   - Measure 3 reports the hidden figure with this caveat.
   - The research branch's `raw/` (the hidden half's ranks for 63 variants) stays out of integrate, so no measured
     role can tune on it. Only `REPORT.md` and `harness/` merge.
   **Yours to decide.**
5. **The never-hit questions.**
   - Q16 and Q19 (visible) get a blind label check by an independent session, as q03 and Q09 did.
   - The four hidden ones (h02, h07, h11, h24) are checked by the hidden half's own role (W2-61h), under the
     hidden-half rule.
   **Yours to decide.** Est. 0 to +2, as for Q09.

## What needs you (an install: never the CTO's)
6. **A stronger reranker.**
   - **Recommended: mxbai-rerank-large-v2.** 1.5 B, Apache-2.0, about 3 GB in bf16, so it fits the reranker's
     existing 3.5 GB share. CoIR 70.9 against today's 65.2.
   - The alternative is Qwen3-Reranker-4B quantised (CoIR 73.9). It needs a quantised load (an install) or
     llama.cpp's reranking mode (community GGUFs reported broken).
   - Est. +3 to +5. It needs a download plus an install by your operator. Then the research harness tries it with no
     change to `src/`, and it is adopted only if it beats the current reranker on the visible half.
   - **Recommended timing:** approve now, so the trial runs during W2-32's rounds. It lands in measure 4, which keeps
     measure 3 a clean reading of W2-32.
7. **A stronger embedder (Qwen3-Embedding-4B):** later. It means one server for both roles and a 2.5–3 h full
   re-embed. Est. +2 to +4. Recommended after measure 4.
8. **No-install extras for measure 4, decided after measure 3:**
   - a query instruction specific to this repository (est. 0 to +2);
   - a reverse-dependency route for "which tickets depend on X" (Q14, est. +1).

## Estimate against your target
| reached with | hit@5 (est.) |
|---|---|
| W2-32's three rounds, G1's embedder half, Q09's re-label | 38–41 of 48 (79–85 %) |
| plus the stronger reranker and embedder | 42–45 (88–94 %) |

**95 % (46) is not shown reachable on this evidence:** six questions are never retrieved by any variant. 21 of 24 on
the hidden half at measure 3 is reachable only near the top of the first row. Item 5's label checks and item 6's
reranker are the levers that could close the gap.

**For you:**
- (a) S8 reworded as in item 2;
- (b) the hidden half's raw records kept off integrate (item 4);
- (c) the label checks of the six never-hit questions (item 5);
- (d) the stronger reranker: which model, and the install now or after measure 3 (item 6);
- (e) the embedder after measure 4 (item 7).
