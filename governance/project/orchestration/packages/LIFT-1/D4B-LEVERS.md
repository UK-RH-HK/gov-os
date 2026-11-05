# D4B-LEVERS: the reranker's second window and the research survey: what to adopt, what not (DEC-1077)

- **For:** the owner. **By:** the CTO (session `812bc5ce`), 2026-11-05 evening.
- **Evidence:**
  - the second and third trial windows: `~/gov-os-runs/D4B/trial-w4b/`, `trial-w4-t4b-qwen4b-8bit-d24/`,
    `trial-w4b-norerank/`;
  - the research survey `docs/research/D4B-memory-survey.md` and its draft `docs/research/D4B-memory-survey-package-draft.md`, written to
    disk from the session's return.
- **Nothing is adopted until you decide.** The verdict set of 80 stays unused until the decision point (DEC-1078 (3)).

## 1. The results side by side (the 138 = the 79 + the spent 59; counts only)
| | 0.6B (today) | Qwen3-4B 8-bit, 40 reranked | **Qwen3-4B 8-bit, 24 reranked** | **No reranker** (the fused order) | mxbai-large-v2 |
|---|---|---|---|---|---|
| hit@5, the 138 | 107 | 112 | **112** | **95** | 76 |
| MRR, the 138 | 0.5567 | 0.5927 | 0.5935 | 0.4867 | 0.3927 |
| the 79: hit@5 (visible / hidden) | 67 (34 / 33) | 69 (35 / 34) | 68 (36 / 32) | 63 (35 / 28) | 50 (27 / 23) |
| the 79: MRR; the halves' gap | 0.6313; 0.4 | 0.6406; 0.3 | 0.6503; 7.9 | 0.5332; 15.7 | 0.4530; 8.5 |
| the spent 59: hit@5; MRR | 40 (67.8 %); 0.4567 | 43 (72.9 %); 0.5286 | 44 (74.6 %); 0.5175 | 32 (54.2 %); 0.4245 | 26 (44.1 %); 0.3119 |
| spread between the three sets | 17.2 | 14.6 | 15.4 | **33.3** | 23.4 |
| against the 0.6B: gains / losses; exact McNemar p | – | 11 / 6; p 0.33 | 9 / 4; p 0.27 | 9 / 21; **p 0.04** | 9 / 40; p < 0.001 |
| one search alone (median of first calls; p90) | 1.80 s (8.7) | 3.89 s (12.1) | **2.84 s** (9.6) | 1.13 s (9.2) | 2.09 s (10.0) |
| 10 searches at once (median) | 6.6 s | 29.6 s | 18.6 s | – | 9.6 s |
| 20 searches at once (median) | 13.0 s | 54.1 s | 33.2 s | – | 17.5 s |
| GPU peak during the runs (budget 14,255) | 9,847 MiB | 15,052 MiB (10 samples over) | 14,722 MiB (2 samples over)* | the embedders only | 11,162 MiB |
| load time | 11.0 s | 21.7 s | 27.0 s | – | 11.5 s |

\* The 4B-at-24 GPU samples cover its 60 run and its 10- and 20-at-once runs (window 2). Its 80 run was repeated in
window 3 without the sampler, after the slip below.

**The reranker's net contribution** (DEC-1077 (c)), the 0.6B against the fused order alone: it lifts 21 answers into
the top 5 and pushes 9 out, net +12. It improves the first gold rank in 58 questions and worsens it in 24. Without it
the three sets drift apart: the spread is 33.3 against 17.2. **The reranker is what makes the structure agree across
sets.**

**mxbai, checked on a stand-in** (DEC-1077 (a)): its own configuration, tokenizer and template with tiny random
weights. sentence-transformers 6.1 renders every pair through mxbai's own template, and the instruction survives at
every length we send (up to about 4,500 tokens of its 32,768). The research session found the same by reading the
code and rendering the template. **Its 76 is its real result here.** No re-run was made, since it would repeat itself.

**A slip, recorded:** my measure script had copied W2-32's re-labelled q12 into the sets root, so the second window's
two 80-question runs refused at the start. The sets root was restored from integrate and checked before window 3, and
both runs were repeated there. No other figure is affected (`drafts/d4b/ROWS.md`).

## 2. By the rule written before the run (DEC-1076 (4))
- **The 4B at 24 candidates passes the rule as written:**
  - it is eligible: 2.84 s alone, at most 3.0; no timeout at 10 at once; no probe shape at the budget;
  - it wins: 112 against 107 on the 138, and the spread is not wider (15.4 against 17.2).
- **But three facts weigh against adopting it now:**
  1. **The gain is not yet significant.** 9 gains against 4 losses gives p = 0.27, and the 40-candidate run's 11
     against 6 gives p = 0.33. One question is 0.7 points of the 138. The halves' gap on the 79 widens from 0.4 to 7.9
     (36 against 32).
  2. **The machine.** 20 searches at once take 33 s against 13 s today. The runs touched the GPU budget twice
     (14,722 MiB, 1,150 under the backstop), with nothing else on the GPU but the two embedders.
  3. **The cost to adopt.** bitsandbytes must be installed in the product's reranker environment (your operator's
     ACT), W2-112's loader must change for the 8-bit load, and the GPU must be watched.
- **The 4B at 40:** not eligible (3.89 s alone; 10 GPU samples over the budget).

## 3. What the research found (the short of `docs/research/D4B-memory-survey.md`)
1. **Our pipeline may hide the reranker's own order.** After the rerank:
   - the authority lift adds 1.0 per tier step to the raw score;
   - up to 2 named-record and 2 code chunks move ahead;
   - failure and lesson records move ahead.

   A question that names a record and a symbol can have 4 of its 5 first places fixed before the reranker's order
   counts. The misses' "ranked 6 to 12" are final ranks; no record yet says whether the reranker's own order had the
   answer in its top 5.
2. **The authority lift is on each model's raw score scale.** One step of 1.0 means different things to the 0.6B, the
   4B and mxbai, so the trial compared them under different effective weights. Others lift on a normalised score
   (Vespa, Azure).
3. **The field's pattern is two stages:** hybrid recall, then one reranker over one head of 50 to 150. Some chain a
   cheaper and a stronger stage (Qdrant, Vespa). The graph is used as **expansion from seeds** (Zep, HippoRAG,
   Continue), not as a ranked list fused beside the others; our closure enters the fusion in path order (measured
   neutral). Zep is the closest design to ours; it also carries currency into the ranking.
4. **Rerankers hurt as the pool deepens** ("Drowning in Documents"), and the 0.6B is published to *lower* code
   retrieval (MTEB-Code 73.4 against its embedder's 75.4); the 4B raises it to 81.2. So a deeper pool is not the
   lever; a stronger reranker on a narrower head is.
5. **The candidates that fit and are licensed for us** are the Qwen3 family, mxbai and the small Apache encoders
   (gte-reranker-modernbert-base, CoIR 80.0, a possible code-only reranker). jina-v3, jina-v2 and Contextual AI v2 are
   non-commercial.
6. **Others' reported hit rates** (Azure, Anthropic, Zep, Cursor) are on their own sets. None is on governance records,
   so the field gives directions, not targets. Azure's figures show keyword search alone beating hybrid on keyword-like
   questions (79.2 against 61.0), which supports our exact-id lift.
7. **The embedder's end-of-text check** (the research's P6 first step): I ran it on the query server. The cosine
   between `text` and `text<|endoftext|>` is 0.995 and 0.976, so Ollama most likely appends the token already. No sign
   of the reported fault.

## 4. What I recommend, in order (the research's draft reviewed)
| # | What | Expected hit@5 on the 138 (est.) | Cost | Yours to decide |
|---|---|---|---|---|
| L1 | **Significance in every comparison:** each figure with its gains, losses and an exact McNemar test (as in section 1 here) | none (it stops us adopting noise) | a script | adopt as practice |
| L2 | **Where each miss leaves the top 5:** for the 31 misses on the 138 (ids and ranks only), the answer's place in the reranker's own order, after the lift, and after the moves ahead | none itself; it decides L3 | 2-3 h, no GPU | go ahead |
| L3 | **The lift on a normalised score, and the moves ahead bounded** (only chunks near the reranker's 5th score move ahead), if L2 shows displacement | 0 to +3 | replay from kept outputs where they suffice; else one 15-minute run | the change, after L2 |
| L4 | **A cascade:** the 0.6B over 40, then the 4B over the 0.6B's top 12 | +2 to +5 (est.: 2.6 s alone, about 29 s at 20 at once) | one GPU window (about 30 min); adoption needs the bitsandbytes ACT and a loader change | the trial now; adoption after the fresh 80 |
| L5 | **Query phrasing, no model** (your approved second lever): two-part questions split; the user's words mapped to the record's labels | +1 to +5 (it reaches the vocabulary misses, which no reranker does) | a day; one 15-minute run per variant | go ahead |
| L6 | **Records of work in a tier of their own below the middle** (close, checkpoint and review records, which restate decisions; crowding in 4 of the 19 misses) | −2 to +3 | one 15-minute run | the tier (DEC-952) |
| L7 | **The embedder** (Qwen3-Embedding-4B) | +1 to +4 | an `ollama pull` (an ACT) and a 2.5-3 h re-embed in a measure clone | later |

**Not recommended:** deeper pools; the 8B or 7B listwise rerankers (too slow); the 4B over all 40; non-commercial
models; ColBERT; extracted-entity graphs (our questions are single-hop, and our graph is stated, not extracted); a
reranker task instruction now.

**If L3 to L6 land, about 110 to 116 of 138 on the used sets (est.); expect about half of that gain on the fresh 80.**

## 5. Decisions for you
- **(a) The reranker, for now:**
  - **(a1) Recommended:** keep the 0.6B in the product. Measure the cascade (L4) beside the 4B at 24 in one quiet
    window. At the decision point, take the best one onto the fresh 80 once, beside the 0.6B. The fresh 80 gives the
    figures significance that the 138 cannot.
  - **(a2)** Adopt the 4B at 24 now: it passes the written rule. This needs bitsandbytes installed in the product's
    reranker environment (your operator's ACT), W2-112's loader changed for the 8-bit load, and the GPU watched.
  - **(a3)** Keep the 0.6B, and close the 4B for this wave.
- **(b)** L1 and L2 now (no GPU, no install): recommended.
- **(c)** L3 after L2's figures; L5 now (approved); L6 is a tier change, yours.
- **(d)** Non-commercial rerankers stay excluded: recommended.
- **Basis:** question 1 (memory: each lever chosen from the misses' kinds and the measured contribution of each
  component, with its cost beside it) and question 2 (a gain of 5 in 138 is not yet evidence on its own; a model
  compared under different effective weights is misjudged).
