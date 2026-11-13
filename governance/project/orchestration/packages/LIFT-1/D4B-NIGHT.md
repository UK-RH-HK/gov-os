# D4B-NIGHT: the night of 2026-11-04 (DEC-1067), for the owner by 09:00

By the CTO (session 33b3628c). The detailed log is `.gov-runtime/scratch/orchestrator/drafts/d4b/NIGHT.md`. Every
measure below is W2-61's measure on all 48 questions, run three times with a noise band of 0. Hit@5 and full evidence
are given for the visible half (V, 24 questions) and the hidden half (H, 24) separately. The hidden half never chose a
method (DEC-1067 (b)): each choice rule was written down before its measure ran.

## 1. The figures after each measure
| measure | what it adds | hit@5 (of 48) | V | H | full ev. | V | H | speed per search |
|---|---|---:|---:|---:|---:|---:|---:|---|
| m1 (D-4b's start) | the baseline | 28 (58 %) | 12 | 16 | 34 | 17 | 17 | about 4x the pinned ~1 s |
| m2 | D-7 + G4 (the path map); W2-13 S6; Q09 re-label; Q11, q10 re-anchors | 29 | 13 | 16 | 34 | 18 | 16 | 1.34 s |
| m2g1 | **G1** (the models read the whole chunk; no span sent twice); Q03, Q16, Q19 re-labels | 35 (73 %) | 18 | 17 | 35 | 18 | 17 | 1.37 s |
| m3 | G1 + **x5** (routing by question type + three phrasings), harness | 37 (77 %) | 20 | 17 | 36 | 19 | 17 | 0.62-0.66 s (harness) |
| m4 | x5 + **contextual headers** (index-time), harness | 38 (79 %) | 21 | 17 | 36 | 19 | 17 | 0.60-0.65 s (harness) |
| **m5** | **the product's own path, everything adopted switched on** (`dc8a2829`) | **38 (79.2 %)** | **21** | **17** | **36** | **36**V | **36**H | **1.45 s** (1.39-1.91; product, cold) |

Notes on the table:
- "Harness" is the research agent's in-process variant switch over the product's own code. At no-op it equals the
  product on 24 of 24 digests.
- The harness's speed is not the product's: the harness reuses routes within a question. The product's figure is
  m5's.
- Q16 was re-worded tonight, so Q16 figures from before tonight are not comparable with later ones.

**Against the floor (85 % on the 48, at least 21 of 24 on the hidden half): **not met.** m5, the last measure before re-pin window 3, gives 38 of 48 (79.2 %) against 41 (85 %), and the hidden half 17 of 24 against 21. The visible misses left are Q14, Q19 and q23; the hidden half has 7. The product matches the harness exactly (m4's 38: 21 / 17), so S8-F2's form difference costs nothing.**

## 2. Which methods worked, and by how much
Each was measured alone against G1's 18 of 24 on the visible half (the research agent's harness, visible half only):

| method | V hit@5 | verdict |
|---|---:|---|
| routing by question type (G3: a named symbol's code hits ahead; a named record's best chunks ahead) | 20 (+2) | **adopted** (x5) |
| three deterministic phrasings (the question; its content words; with the record ids appended) | 19 (+1) | **adopted** (x5) |
| the reranker shown each chunk's path, title and section | 20 | not adopted: it gains Q19 but loses Q04, and adds nothing on top of x5 |
| question expansion with the graphs' ids and symbols, in both indexes | 19 | not adopted: it adds nothing on top of x5 |
| contextual headers when embedded (index-time) | +1 on top of x5 (q24) | **adopted** (m4) |
| each route's top hits guaranteed a place in the pool | 17 (-1) | lost |
| a global rerank pool of 40 | 15 (-3) | lost |
| a repository instruction for the embedder | 16 (-2) | lost |
| a repository instruction for the reranker | 14 (-4) | lost |
| authority lift doubled | 15 (-3) | lost |
| route agreement, a per-file cap, blending fusion and rerank | 18 (0) | no effect |

What drove the gains: **G1** (+6 overall, two of them from re-labels), then **routing** (+2), then **headers** (+1).
Fusion weights do nothing, because the reranker decides the top 5.

Index-time methods not yet built, with the research agent's estimates: a file-level index beside the chunk index
(+1); code chunks cut on definitions (+1: q23, q24); a reverse `depends_on` edge in the closure (+1: Q14);
identifier tokenisation (0 to +1); one span per register entry (0 to +1).

## 3. My recommendation on the stronger reranker and embedder
**The reranker: yes, a trial, and it is the lever with the most room.**
- **Evidence that the reranker is the bottleneck:**
  - Every pure fusion change scored between -2 and 0.
  - Reading the whole chunk was the biggest single gain.
  - Instructions to the reranker cost 4 questions.
  - Today's model, Qwen3-Reranker-0.6B, scores below its own first stage on code in its published table (MTEB-Code
    73.4 against 75.4).
  - Of the misses left after m4, several never reach the top 5 under any variant tried tonight (Q14, q23, q24 and the hidden
    ones). So the ranking, not the recall, is what limits.
- **Recommended model: mxbai-rerank-large-v2** (1.5 B, Apache-2.0, about 3 GB in bf16, CoIR 70.9 against 65.2). It
  fits the reranker's existing 3.5 GB share.
- **Two conditions before it loads:**
  1. Tonight's padded request bound (in the product since `b7085897`), which is already there.
  2. The shared service releasing its cache after each request. Tonight it kept its PyTorch peak, climbing to 15.9 GB.
     This is a change to W2-112's code, so a re-pin; see section 4.
- **Steps:** a download and an install (yours: an operator ACT); a trial in the harness on the visible half; adopted
  only if it wins there.
- **Est.:** +3 to +5 (the research agent's estimate, from the published code gain).

**The embedder: not yet.**
- Qwen3-Embedding-4B means one server for both roles, about 2.5 GB at Q4 per server, and a 2.5-3 h full re-embed.
- G1 has just changed what the embedder sees, and headers changed it again. The whole-chunk embeddings' own gain is
  in m2g1, but it is not separated from the reranker's half.
- My recommendation: after the reranker trial, measured the same way. Est. +2 to +4.

## 4. What else needs you
1. **Hidden labels h02 and h24 are wrong, by an independent auditor's blind check; they are not yet corrected.**
   - The guard refuses an auditor's writes outside its own record (DEC-953 item 2), so the write to the sets root was
     refused. I did not route round it.
   - h07 and h11 are right.
   - **Decide who writes the two corrections:** (a) an operator ACT lets that role write the sets root for this task;
     or (b) your operator applies the corrected files the auditor holds.
   - Until then, h02 and h24 are scored on their wrong labels.
2. **Q16 was re-worded**, a step past "the label", by its blind checker: its old gold rested on a superseded decision
   and the question had become ambiguous. **Keep or revert?** Recommend keep.
3. **Re-pin window 3 and the integration store:** the adopted methods are on `w2/integrate` (`dc8a2829`) but not live
   until the re-pin, an (a) ACT for your operator. I will rehearse it in a scratch clone first, when you say.
4. **Two GPU backstop trips** (03:53 and 05:37), both during experiments, both handled without harm. The embedders
   stayed whole, with no failed request.
   - The cause was a request-size bound on the count of texts, not their size. The fix is in the product and the
     harness.
   - Once, the reranker would not stop on SIGTERM and I used SIGKILL, which is a harder stop than class 3's command
     (the service holds no state). Tell me if that should be in the class.
   - The reranker keeps its peak memory: a D-9 row and a re-pin item.
5. **Deferred to D-9 (my calls):**
   - R2-F1: nested Python parents can send lines twice. That costs tokens, not hits. Two fixes tonight each broke the
     bundle's contract, so the work is parked at `park/W2-32-R2-F1` and its case is a strict xfail.
   - q12's gold answer names 3 of 5 refusal cases. The anchor is right; hit@5 scores the sources.
   - DEC-1033 (2)(b) has no "changed by DEC-1065 (1)" mark in the register.
6. **My mistakes tonight:**
   - At 05:38 a text-match stop also killed W2-32's phrasings engineer mid-work. Its uncommitted work was kept and the
     session resumed. From now on I stop processes only by the pids the backstop paused.
   - Measure 3's first figure ran on a harness with the sum bound. The padded rerun (m3b) gave the same figures.
7. **A worker routed round a guard refusal:** the headers engineer took a refused `git show :3:<file>` as a false
   refusal and resolved the conflict another way. The refused read itself did not happen. Recorded against DEC-849.
8. **Rows:**
   - the empty-HOME rule makes 29 cases red that are green with the real HOME;
   - 17 suites share one vector cache per sandbox;
   - `hidden/` is mode 755 inside the sets root's 700;
   - the prompt's resource floor is stale (6.7 GB against DEC-947's 3 GiB);
   - O-A1 has no register entry;
   - the main repository's `core.bare` went true at 00:31 (cause not found; a watcher is armed);
   - the headers' F3 (worktrees branched before the switch re-embed) and F4 (code-block `#` lines read as headings).

**For you, in short:**
- (a) the reranker trial: install mxbai-rerank-large-v2, with the service's cache fix in the re-pin;
- (b) the embedder after it;
- (c) who corrects h02 and h24;
- (d) Q16 kept;
- (e) re-pin window 3, when;
- (f) SIGKILL in class 3.
