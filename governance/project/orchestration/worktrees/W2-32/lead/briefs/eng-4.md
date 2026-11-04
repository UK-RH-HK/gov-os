# W2-32 engineer, round G1 (S7; DEC-1066) (the CTO)

The owner chose W2-32's three gaps (DEC-1066): **G1 first** (S7), then G3 (S8, the fusion), then G2 (S6). The CTO merged
`w2/integrate` into `w2/W2-32` (`5e2251de`: the re-worded S6-S8). Do not merge yourself. Same rules as before (no
`gov retrieve`, no real model, the real-model exclusion on whole-folder runs, the `ps` check).

**S7 (G1): the models read the whole chunk.** The research (W2-15a's record, `docs/research/EXP-003/w2-15a-baseline.md`,
finding 2 and gap G1) found the embedder reads the first 512 characters (`EMBED_CHARS`) and the reranker the first 500
(`RERANK_CHARS`), while chunks run to 1,200: for Q10, Q16, q24 (and in part Q07, Q11) the gold sits past that point. And
(finding 3) parent expansion forgets its expanded parents between continuations, so a span comes back in a later batch.
Build: the embedder and the reranker read each chunk in full (the cut at or above the chunk's maximum size; the manifest's
cut changes, so S1's full re-embed follows on the next rebuild; your S2 code records the cut); parent expansion keeps the
set of expanded parents across continuations (in the continuation token or its state), so no span is sent twice. Keep S10
(GPU only) and everything else as it is. Unit tests with stand-ins; the evidence file's S7 row. The effect is measured by
the CTO (a rebuild and the measure) after measure 2; your branch merges only after measure 2 (DEC-1064). Return the twelve
fields with the `ps` check.
