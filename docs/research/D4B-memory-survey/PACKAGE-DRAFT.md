# D4B-PACKAGE-DRAFT: the next memory levers (a draft for the owner, for the CTO's review)

- **By:** the research role, 2026-11-05, from `REPORT.md` in this folder. Nothing here is adopted. It is a draft for
  the CTO to review and put to the owner. Written to disk by the CTO from the session's return.
- **The base:** v456 + the stated links + Qwen3-Reranker-0.6B.
  - hit@5 **107 of 138**: visible 34/40, hidden 33/39, spent 40/59;
  - MRR 0.5567;
  - spread between the sets 17.2;
  - alone 1.80 s; 10 at once 6.6 s; 20 at once 13.0 s (D4B-TRIAL-W4).
- **The rules every item is measured under:**
  - structural fixes only, never a fix aimed at a named question;
  - judged on all the used sets together, the 138: hit@5, then MRR;
  - the spread between the sets must not widen;
  - eligible only within the speed limit (median alone ≤ 3.0 s), the concurrency limit (10 and 20 at once without
    timeouts) and the GPU budget (no sample at 14,255 MiB);
  - the choice rule written before each run;
  - **the verdict on a fresh set of 80, used once**, at the decision point.
- **How the ranges are reasoned:**
  - from the trial's measured figures and D4B-MISSES' kinds;
  - scaled from the spent 59 to the 138 by the ratio of misses (19 of the 59's against 31 on the 138);
  - discounted for overlap between levers.
  - Expect a used-set gain to shrink on the fresh set. Visible gains held at about a fifth on the hidden half before
    (12 → 21 visible against 16 → 17 hidden), and the blind set scored 17 points under the tuned halves.

## The order I would try them in

| # | What | Expected hit@5 on the 138 [E] | GPU | Time | Install | Code |
|---|---|---|---|---|---|---|
| P0 | **Measurement first.** (a) every comparison reports its discordant pairs and an exact McNemar test; (b) the label-alternatives audit as D4B-MISSES (c) recommends | none on retrieval; the spent 59 may be understated by up to 7 (labels) | 0 | 1 h (script) + the audit | none | a measure-report addition |
| P1 | **Where each miss left the top 5:** for each of the 31 misses (ids and ranks only), the gold's place in the reranker's raw order, after the authority lift, and after the named/code/lesson moves | none itself; it decides P3 | 0 | 2-3 h | none | a research script over the kept outputs |
| P2 | **Rerank replays from kept scores** (every reranker here is pointwise, so these are exact). A small grid, declared before: (a) cascade, 0.6B over 40 then the 4B over its top N, N ∈ {8, 12, 16}; (b) the 4B alone over the fused top N, N ∈ {16, 24}; (c) the lift on a per-query rank- or z-normalised score, for the 0.6B, the 4B and mxbai | (a) **+2 to +5**: the 4B's measured +5 over 40, most misses at places 6-12; (b) +1 to +5; (c) −2 to +3 for the 0.6B, and it shows whether mxbai's −31 is the lift | 0 for the replays; then one window of 30-45 min to confirm the winner's speed and memory | half a day | none for the replay; the product needs bitsandbytes (an install, an owner ACT) and W2-112's loader change | a replay reranker in the harness; for (a) in the product, a second model in the service with its own request bound (8 texts or 12,000 characters) |
| P3 | **If P1 shows the gold displaced after the rerank:** bound the post-rerank moves. Move ahead only chunks within δ of the reranker's 5th score, or cap the places pre-empted at 2, with the lift on normalised scores (P2c) | **0 to +3** | 0 (replay) | 2-4 h | none | `routing.py`, `authority.py` (query time) |
| P4 | **Records of work in their own tier, below the middle:** `docs/close/**`, `docs/checkpoints/**` and the orchestration `closes/nightly/sessions/reviews/**` (keyword-only, restating decisions; crowding in 4 of 19 misses) | **−2 to +3** (questions about what a ticket did may lose) | one 0.6B run, about 15 min (the head of 40 changes, so the replay cannot cover it) | 1 h | none | `path-map.yaml` `retrieval_authority` (the owner approves the tier, DEC-952) |
| P5 | **Query phrasing, no model** (the approved second lever): split two-part questions; map the user's words to the record's from the register's labels and headings | **+1 to +5** (in reach of 10 of the 19; the vocabulary misses only this reaches) | one run of about 15 min per variant | a day | none | `routing.phrasings` |
| P6 | **The embedder:** first the end-of-text check (minutes: compare the vectors of `text` and `text<|endoftext|>` on the shared service); then Qwen3-Embedding-4B | **+1 to +4** (strong in 2 of 19, weak in 2), more if the end-of-text check fails | Q4 about 2.5 GB per server, so one server serving both; a re-embed of 2.5-3 h in a measure clone | 1 day | `ollama pull` (an owner ACT) | `models.yaml`, a rebuild |
| P7 | **If P2(a) is adopted:** a faster 8-bit format for the 4B on Blackwell (FP8 via torchao, or AWQ/GPTQ kernels) instead of bitsandbytes | 0 (speed only): est. −30 to −40 % of the 4B's time | a short probe | half a day | an install (an owner ACT) | the worker's loader |

**If P2 to P6 all land, the total [E]:**
- P2 and P3 together: +3 to +7 on the 138, or 110-114.
- P5: +1 to +5. P6: +1 to +4. They overlap with P2 and P3 (the same near misses).
- So about **112-118 of 138 (81-86 %)** on the used sets.
- **On the fresh 80, expect about half of the used-set gain** [E].

## What not to do, and why
- **mxbai re-run "with its template":**
  - The trial already applied it. The snapshot's `chat_template.jinja` matches the vendor library's prompt, and
    `sentence-transformers` 6.1 renders every pair through it (REPORT 1.3).
  - P2(c) tests the one design confound found, the lift scale, for free.
- **Deeper pools** (routes past 60, more than 40 reranked): weak pointwise rerankers degrade with depth ("Drowning in
  Documents"), and only 2 of the 19 misses were below the 40.
- **Qwen3-Reranker-8B, listwise 7B LLMs:** over the time limit even alone (est. 5-15 s). The 8B gains nothing over the
  4B in Qwen's table.
- **The 4B over all 40 in the product:** 54 s at 20 at once, and over the GPU budget at peak (measured).
- **jina-reranker-v3, jina-reranker-v2, Contextual AI v2:** non-commercial licences.
- **Small encoders as a replacement** (Ettin 150M to 1B, MiniLM, bge-v2-m3):
  - The Ettins are distilled from mxbai-large-v2, which lost here.
  - bge-v2-m3 is weak on code (CoIR 36).
  - gte-reranker-modernbert-base (CoIR 79.99, 149M, Apache) is the one worth a later, optional *code-only* trial.
- **ColBERT models:** below cross-encoders on BEIR; a new token index.
- **LLM-extracted graphs** (GraphRAG, LightRAG): our questions are mostly single-hop, where vanilla RAG beats them
  (NQ 64.78 against 63.01). Our stated graph (37,815 pairs) is the exact form of what they approximate.
- **A task instruction for the reranker, now:** it needs a GPU run per model, lost on night one, and gains 1-5 % at
  most by Qwen's own claim. Later, if the 4B is adopted.

## How each would be measured
- **P2 and P3** run on the kept outputs and scores with a replay reranker: no GPU, no change to the routes. The grid is
  declared before. The winner is chosen by the rule (the 138, hit@5 then MRR, the spread not widening, the discordant
  pairs reported). Then one GPU window measures its speed alone, at 10 and at 20 at once, and its memory, with the
  backstop armed.
- **P4 and P5** are each one product run on the 138 under the harness (about 15 min each), against the base.
- **P6** is a measure clone with the new embedder, rebuilt; all 138 measured; speed and GPU beside it.
- **At the decision point:** the fresh 80, once.

## For the owner
- **(a)** P0 to P2 now: no GPU beyond one confirmation window, no install (recommended).
- **(b)** P3 and P4 after P1's figures. P4 changes the authority tiers (DEC-952), so it is yours.
- **(c)** Whether the 3.0 s limit stands. A cascade is est. 2.6 s alone and about 29 s at 20 at once, against 13 s
  today.
- **(d)** Non-commercial rerankers: not considered (recommended), or allowed for research only.
- **Basis:**
  - Question 1 (memory): levers chosen from the misses' kinds, with their cost beside them.
  - Question 2: a trial confounded by its own pipeline misjudges the model, and a gain of 5 in 138 is not yet
    evidence on its own.
