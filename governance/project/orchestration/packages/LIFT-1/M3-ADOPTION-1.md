# M3-ADOPTION-1: whether the product adopts M3 (zerank + gte) as its reranker (DEC-1087 (12), DEC-1043, DEC-1085 (3))

For the owner. Drafted 2026-11-07 by a product-spec agent for the CTO (session `ad44f5fe`). It was written **before
E4's end-to-end figures were read**, so its thresholds in §5 are declared ahead of them.
- **Nothing is adopted or installed** until the owner decides (DEC-1081 (3)).
- Adopting any two-model cell changes DEC-1043's one shared reranker, so the decision is the owner's (DEC-1085 (3)).
- It comes after all the experiments, from what they show about agents and their bundles (DEC-1087 (12)).

## 0. In short
- **M3 retrieves better on the 138.** On window 4's code it gives hit@5 117 against the 0.6B's 106 (14 gains, 3
  losses, exact p 0.013). M1 (the 0.6B + gte) gives 114 (9 gains, 1 loss, p 0.022).
- **M3 and M1 are not told apart.** M3 against M1: 5 gains, 2 losses, p 0.45.
- **The agent's bundle holds the gold equally often.** In the first bundle: 123 of 138 for M3, for M1 and for the
  0.6B. Agents read the whole bundle (E3), and they search again once (E2: 128 of 138 right with the 0.6B).
- **M3 costs every search a second model.** At 10 searches at once it took 12.7 s against 6.6 s. Its GPU peak was
  12.7 GB against about 9.5 GB. It needs a new loader and two pins.
- **E4 decides.** If M3's bundles do not make agents answer better, a hit@5 gain alone may not pay for doubling the
  scoring load. The recommendation in §5 is written on that condition.

## 1. What M3 is, and what runs today
- **M3:** zerank-1-small (its "Yes"-logit score) and gte-reranker-modernbert-base.
  - Each scores the pool's 40 candidates.
  - Each set of scores is min-max normalised over the 40.
  - The two are merged with equal weights (w = 0.5).
  - L3's normalised lift is added: 0.0766 per authority tier step, on the normalised score (D4B-SCORE-ONCE, "L3").
- **M1:** the same rule with the 0.6B in zerank's place.
- **Today's product:** Qwen3-Reranker-0.6B alone, in the one shared reranker service (W2-112). The authority lift is
  added to its raw score (`authority.py` `reranked`, lift 1.0 per step). There is no L3 in the product.

## 2. What adopting M3 would change in the product

### 2.1 The models and their memory
| | the 0.6B (today) | gte | zerank |
|---|---|---|---|
| model @ revision | Qwen/Qwen3-Reranker-0.6B @ `e61197ed` | Alibaba-NLP/gte-reranker-modernbert-base @ `f7481e60` | zeroentropy/zerank-1-small-reranker @ `a65fd51c` |
| size | 0.6 B | 149 M, weights in F32 | 1.7 B (Qwen3-1.7B shape), weights in bf16 |
| download | in the live cache | 575 MB, in `~/.cache/gov-os-trial/hf` | 3.3 GB, in `~/.cache/gov-os-trial/hf` |
| licence | as pinned (ADR-0002) | Apache-2.0 | Apache-2.0 (its 4B sibling `zerank-1` is not, and is not used) |
| how it loads | the cross-encoder, as today | the cross-encoder, as it is | **a loader of our own**: the "Yes" logit at the last real position, divided by 5, through a sigmoid |
| GPU peak while scoring alone (window 4, live service stopped, base 5,969 MiB) | 9,427 to 9,670 MiB live, at 20 at once | 7,856 MiB | 10,696 MiB |

### 2.2 The service design
Today there is one service, one model, one GPU slot and one lock (W2-112; DEC-1043 (2)). A slot-hold watcher keeps
every other slot, so no private reranker runs beside it (DEC-1046). M3 needs two models scoring every search.

- **S1, one service with both models (recommended).**
  - One process, one socket, one slot, one lock, as today.
  - Each request is scored by both models in turn, and the cache is released after it.
  - Requests stay one at a time, so the GPU holds both models plus one request's working memory, never two requests.
  - The service's GPU share threshold rises from 5.5 GiB free to its measured peak plus the headroom (DEC-1046 (1)).
- **S2, two services.**
  - This is how the 11-06 live window ran: two trial services on their own sockets, at three slots.
  - The second service takes the slot a private fallback would use. Two requests can then be on the GPU at once, so
    their working memory stacks.
  - It changes the slot rules (DEC-1043, DEC-1046) and the slot-hold watcher.
- **The fallback:** if one model fails, the search uses the other alone, normalised, and says so in `rerank.reason`.
  If both fail, a private reranker with the pair runs under the slot rule, or the order stays unranked and named
  (DEC-374, DEC-1033). Never the CPU.

### 2.3 Installs, downloads and pins
- **No package is installed.** The live reranker venv already has transformers 5.18 and sentence-transformers 6.1
  (ACT-RERANK-TRIAL-1: the trial venv is a clone of it, plus bitsandbytes, accelerate and psutil, which only the 4B
  needs). gte loads as it is. zerank loads through `Qwen3ForCausalLM` with `trust_remote_code=False`. Its own code
  file was never downloaded (ACT-RERANK-TRIAL-2).
- **The downloads move:** the two snapshots go from `~/.cache/gov-os-trial/hf` into the live HF cache, with their
  hashes checked and the live venv unchanged. That is an operator ACT, rehearsed (P-ACT-SPLIT).
- **The pins:** `rerank.py` pins one `MODEL` and `REVISION` today. It would pin two. ADR-0002 §2 and DEC-397 pin the
  model and environment, so they change. ADR-0002's refresh is already due after the experiments (DEC-1093 (3)).

### 2.4 L3 in the product
Without L3, gte and zerank are judged mostly by the authority tiers, not by their scores. Under the raw lift they gave
78 and 82 on the 138; under L3, 114 and 113 (D4B-SCORE-ONCE). A merged score (0 to 1) is swamped the same way. So M3
and M1 both need L3 in the product. For the 0.6B alone, L3 changes nothing that counts (E0b: 106 with it, 106 in the
product).

### 2.5 The code tickets it needs (proposed; each tests first, one review)
| ticket (proposed) | what | needed for | est. |
|---|---|---|---|
| R-1, L3 in the product | each pass's rerank scores min-max normalised before the authority lift; the step 0.0766 in `retrieval_authority`'s `lift.rerank`; the 0.6B alone within 2 of today on the 138 | M3 and M1 | 0.5 day |
| R-2, two rerankers merged | the client gets both models' scores over the pass's 40, normalises each over the pass, merges at w 0.5; one model failing gives the other alone, named; the bundle's `rerank` names both | M3 and M1 | 1 day |
| R-3, the service with two models (S1) | both pinned models loaded in the one service, each request scored by both, the release after each; the share threshold from the measured peak; the fallback of §2.2 | M3 and M1 | 0.5 to 1 day |
| R-4, zerank's loader | the trial loader ported to `rerank_worker.py`: the local snapshot, no remote code, the published template (the query as the system message, the passage as the user message, the generation prompt; cuts at 2,000 and 10,000 characters), the score; tested against a planted tokenizer | M3 only | 0.5 day |
| ACT-R, the downloads | the snapshots into the live HF cache, hashes checked, rehearsed | gte for M1; both for M3 | about 1 h of the operator's time |
| R-5, the product's measure | S11's rule (the product within 2 of the harness on the 138), then a live window on the product build: alone, 10 and 20 at once, the GPU, at W2-137's cap of 64 | M3 and M1 | 0.5 day, one GPU window |

- **In all:** M3 about 3 to 3.5 days of agent work, about 2 calendar days with R-1 and R-4 in parallel. M1 about 2.5
  days of work, about 2 calendar days with its own live window first (§3.5).
- SEVEN-ANSWERS §1 said 1 to 1.5 days. This is more because it counts the service design, the fallback and the
  product's own measure.
- W2-112 is closed and never edited (DEC-1088 (6)). Its tests that assume one model may need an independent test
  designer's revision, in a ticket of its own.

## 3. The evidence, for and against

### 3.1 Retrieval
**On window 4's code** (the clone at `c00d525fd420`; today's E4 window and replays, `~/gov-os-runs/D4B/e4/`). Counts
only. The 0.6B is E0b's run B (the harness in B0's form, with L3). E0 is the product.

| | visible 40 | hidden 39 | spent 59 | **hit@5 /138** | hit@10 | hit@20 | MRR | in the bundle | spread |
|---|---|---|---|---|---|---|---|---|---|
| the 0.6B, product (E0) | 34 | 32 | 40 | 106 | 118 | 124 | 0.5665 | 123 | 17.2 |
| the 0.6B, harness with L3 (E0b B) | 33 | 32 | 41 | 106 | 119 | 124 | 0.5602 | 123 | 13.0 |
| gte alone | 33 | 35 | 45 | 113 | 121 | 123 | 0.6231 | 123 | 13.5 |
| zerank alone | 34 | 34 | 45 | 113 | 121 | 123 | 0.5937 | 123 | 10.9 |
| **M1**, the 0.6B + gte | 34 | 35 | 45 | **114** | 122 | 123 | 0.6010 | 123 | 13.5 |
| **M3**, zerank + gte | 34 | 36 | 47 | **117** | 122 | 124 | 0.6070 | 123 | 12.6 |

**Gains and losses on hit@5, exact McNemar** (from the kept per-question lines, ids and verdicts only):

| comparison | gains / losses | p | by set (visible / hidden / spent) |
|---|---|---|---|
| M3 against the 0.6B (E0b B) | 14 / 3 | 0.013 | 2-1 / 4-0 / 8-2 |
| M1 against the 0.6B (E0b B) | 9 / 1 | 0.022 | 2-1 / 3-0 / 4-0 |
| M3 against M1 | 5 / 2 | 0.45 | 0-0 / 1-0 / 4-2 |
| M3 against the product (E0) | 14 / 3 | 0.013 | 1-1 / 4-0 / 9-2 |

Holm over the two comparisons with the 0.6B gives 0.025 for each.

**On the 11-06 grid** (the g1 clone, 16 cells against B0 107; D4B-SCORE-ONCE):
- M3: 118, MRR 0.6120, spread 8.4; 13 gains, 2 losses, p 0.007, Holm (16) 0.118.
- M1: 114, MRR 0.6048, spread 11.2; 8 gains, 1 loss, p 0.039, Holm 0.391.

**What it means:**
- **For:** M3 leads on both commits, and its gain holds within one question across a change of code and store.
- **Against:**
  - **It is the same 138 questions.** M3 was chosen from 16 cells on them. Window 4 reproduces the gain on new code;
    it is not a fresh test. SEVEN-ANSWERS expects about half the gain on fresh questions. Only the fresh 80 can tell.
  - **No comparison survives Holm on the grid,** and M3 is not told apart from M1.
  - **The bundle does not change.** Gold is in the first bundle for 123 of 138 under every reranker. M3 moves gold up
    inside the bundle (hit@5, MRR); it does not bring new gold into it.
  - **M1's spread on window 4** (13.5) is 0.5 points wider than the 0.6B's in B0's form (13.0). Under §4's rule it
    would not win on this commit. It passed on the grid (11.2 against 18.0).

### 3.2 End to end: what is known before E4
- **E3:** agents answer best from today's bundle, 114 of 138 in one reader call. The top 5 alone gives 84. What helps
  agents is the whole ranked, expanded bundle, not the top 5 alone.
- **E2:** with search-again once, today's bundle gives 128 of 138 (92.8 %), and wrong claims stay at 3.
- **E5:** a bundle twice the size gives 115 against 114 (p 1.0). More in the bundle buys nothing.
- **The reader's own spread** is 1 to 3 answers between runs on the same bundles (E3 against E2 at one search; E3-SA's
  repeat).

### § E4's end-to-end result (to be filled by the CTO)
E4's reader runs are going now. This section is left for the CTO to fill when they end. It should say, in plain words:
- how many questions agents answered right end to end from M3's bundles and from M1's, against today's bundle from the
  0.6B (E3's run, shared), on the 138 and per set;
- the wrong claims and the "not found" answers beside each;
- the gains and losses against today's bundle, with the exact McNemar p and Holm over the two;
- whether each difference is wider than the reader's own spread;
- the cost of the runs;
- and which branch of §5 applies.

### 3.3 Speed, alone and with many agents at once
| what ran | alone, median (p90) | 10 at once, median (slowest) | 20 at once, median | source |
|---|---|---|---|---|
| the 0.6B, today (cap 16, pool on) | 1.68 s (PAT-1, 10 questions); 1.80 s (8.7) in D4B-TRIAL-W4 | 6.6 to 6.8 s (8.9) | 13.4 to 13.9 s; 14.5 to 17.4 s in G1's bursts | PAT-1 §3-4, G1-PROFILE |
| the 0.6B at W2-137's cap of 64 | | 7.35 to 7.66 s (10.4) | 14.8 to 15.1 s | W2-137 S5 |
| **M3**, two trial services asked in turn (cap 16) | **2.84 s (8.40)**; 2.56 s without the harness's GPU reads | **12.67 s (20.27)**; the slowest request 3.81 s | **not measured** | the 11-06 live window |
| M1 | not measured | not measured | not measured | |

- **Alone:** M3 is about 1.6 times today's. It meets the 3.0 s line by 0.16 s.
- **10 at once:** M3 is about 1.9 times today's. Nothing timed out.
- **20 at once:** not measured. G1-PROFILE shows the GPU busy most of a burst (a median of 84 to 86 %), so the time
  is set by the scoring work. A second model roughly doubles that work per search, so **20 at once would take about
  26 to 30 s per search** (twice today's 13.4 to 15.1 s). That is an estimate, not a figure. Each request stays far
  under the 30 s request limit (the slowest at 10 was 3.81 s), but every agent then waits about half a minute per
  search.
- **What that means for the three layers:** W2-112's ticket expects about 10 agents searching at once, and CAPACITY-1
  about 29 sessions. With M3, 10 at once is about 13 s a search and 20 at once about half a minute.
  - Batching would recover at most the 10 to 35 % idle gaps (G1-PROFILE), the same for either reranker.
  - G1's lever, fewer pairs or tokens per search, pulls the other way from adding a model.
- **M1 is not measured live.** "gte is small" suggests M1 sits between the 0.6B and M3. M2's window hints otherwise:
  with the 4B's 2.54 s taken out, the rest of an M2 search (gte, the routes, the reads) took about 2.0 s, against
  1.8 s for a whole 0.6B search. gte loads in F32 and reads long inputs, so its share is not negligible. M1 may be
  nearer M3 than expected. It needs its own window.

### 3.4 GPU memory (the budget 14,255 MiB: 16,303 less the 2 GB headroom)
- **The base:** both embedders warm and no reranker, 5,969 MiB (today's window).
- **Today:** 7,441 to 7,483 MiB with the service idle; a peak of 9,427 to 9,670 MiB at 20 at once (PAT-1, G1, W2-137).
- **M3, the 11-06 window:** 10,436 MiB after the warm-up and a peak of 12,712 MiB at 10 at once (0 of 132 samples at
  or over the budget). That leaves 1,543 MiB of margin. It was measured with the release after each request, which the
  product now has (W2-112's release, live since window 4).
- **M1:** not measured. The 0.6B's peak plus gte's working share (about 1.9 GB in today's window) gives about 11.3 to
  11.6 GB, an estimate.
- **Not measured for M3:** the peak at 20 at once, and at W2-137's cap of 64. The padded bound (24,000 characters)
  keeps each request's size as before, and under S1 requests never overlap, so no rise is expected. R-5 measures it.

### 3.5 DEC-1076 (4)'s eligibility rule, line by line (with D4B-SCORE-ONCE §4's GPU line)
| line | M3 (11-06 live window) | M1 |
|---|---|---|
| median search alone at most 3.0 s | **pass**: 2.84 s (margin 0.16 s) | not measured |
| no request times out at 10 at once | **pass**: the slowest request 3.81 s, against 30 s; none failed or went unranked | not measured |
| no probe shape reaches the budget | **pass**, on both services | not measured |
| the GPU under 14,255 MiB | **pass**: peak 12,712, 0 of 132 samples | not measured; about 11.5 GB estimated |
| recorded beside it: the median at 20 at once | **not measured** (DEC-1076 (4) asks it recorded; it is not a pass line) | not measured |
| wins over the 0.6B: hit@5 higher on the 138 | **pass**: 118 against 107 (grid); 117 against 106 (window 4) | pass: 114 against 107 and against 106 |
| ... with a spread no wider than the 0.6B's | **pass**: 8.4 against 18.0 (grid); 12.6 against 13.0 (window 4) | pass on the grid (11.2); **fails on window 4** (13.5 against 13.0) |
| verdict | **eligible**; the verdict comes from the fresh 80 | **not yet eligible**: no live window |

### 3.6 Cost and risk
- **Build:** about 3 to 3.5 days of agent work for M3 (§2.5), and one ACT.
- **GPU:** every search scores 40 pairs twice. Today's GPU is already saturated with 20 agents searching (G1).
- **Two pins to keep:** two snapshots, two revisions, two licences (both Apache-2.0), and two upgrade paths.
- **The loader is ours.** It reproduces zerank's template and score without its code. If a later transformers changes
  how the chat template renders, scores can drift without an error. R-4's test pins the template and a known score.
- **zerank is young:** revision of 2026-07-24, with a slip on its own card (it names a 4B base; the config is 1.7B's).
- **The speed margin is thin:** 0.16 s alone, measured once, with the two services asked in turn.
- **Fallback is wider:** a failed model leaves the other alone, a different ranking from the one judged.
- **Not reversible for free:** going back after the lift is a re-pin with the 0.6B and the 0.6B's lift. Cheap in code,
  but it is a new pin and a new measure.

## 4. The options
| option | what | build | the fresh 80 (chosen before it runs, DEC-1092 (4)) | dates (the lift about 11-15) | G1, agents at once |
|---|---|---|---|---|---|
| **(a) adopt M3** | zerank + gte, merged, L3 | R-1 to R-5 and the ACT: about 2 calendar days | judged on M3. K9's bar is on the pin that carries the chosen reranker (DEC-1083 (2)), so the 80 waits for the build and its re-pin | the lift about 11-17; EXAMIN's copy about 2 days later | 10 at once about 13 s; 20 at once about 26 to 30 s (estimate) |
| **(b) adopt M1** | the 0.6B + gte, merged, L3 | R-1, R-2, R-3, R-5 and the ACT for gte; first a live window for eligibility (about 1 h with its preparation) | judged on M1, after the build, as (a) | the lift about 11-17 | not measured; likely between today and M3, and maybe near M3 (§3.3) |
| **(c) keep the 0.6B; revisit after the three layers' load is known** | today's product | none | judged on today's configuration (today's bundle, search again once). M3 and M1 may be measured on the 80 for data beside it (DEC-1092 (4)) | no change: the lift about 11-15 | today's: 6.6 to 7.7 s at 10, 13.4 to 15.1 s at 20 |
| **(d) adopt only where answers improve** | (a) or (b), but only if E4 shows agents answer better from its bundles | as (a) or (b), or none | as (a) or (b), or as (c) | as (a) or (b), or as (c) | as (a) or (b), or as (c) |

- **(c) in detail:** M3 stays the leading candidate. After the lift, when the three layers run, their real search
  load is known, and so is G1's fix. M3 or M1 is then weighed against that load, with its own fresh check.
  - **One caution if M3 is measured on the 80 for data:** a later adoption chosen on those figures would have no
    fresh set left to confirm it.
- **(d)** is not a different reranker. It is the rule that decides between (a), (b) and (c). **If E4 shows no
  end-to-end gain, a hit@5 gain alone may not justify doubling the scoring load** on every search.
- **Also seen, beyond the brief:** gte alone gives 113 on window 4, with the highest MRR (0.6231), and it is one small
  model in place of the 0.6B. Its speed is not measured live. If G1's saturation calls for a smaller reranker, it is
  the first one to measure.

## 5. The recommendation, conditional on E4
**Recommended: (d) as the rule, with (c) the expected outcome.** Confidence: medium (about 0.6) that E4 lands in the
first branch below; high (about 0.8) that the branches are the right ones.

**"Above end to end" is declared here, before E4's figures are read:** M3's bundles give at least 4 more right
answers of the 138 than today's bundle from the 0.6B (more than the reader's own spread of 1 to 3), with no more wrong
claims. The exact McNemar p is reported beside it. With 138 questions it will rarely be under 0.05, so it is not the
line.

| E4 shows | then | why |
|---|---|---|
| M3 not above the 0.6B end to end | **(c)**: keep the 0.6B, revisit after the three layers' load is known | a hit@5 gain that agents do not turn into right answers does not pay for twice the scoring on every search |
| M3 above, and M1 above too | **(b)** if M1's live window passes the eligibility rule; else (a) | M1 keeps the pinned 0.6B, needs no new loader, and is not told apart from M3 on retrieval (5 and 2, p 0.45) |
| M3 above, M1 not | **(a)**, on the speed condition below | the gain is M3's own |

**The speed condition for (a) or (b):** on the product build (R-5), at W2-137's cap:
- alone at most 3.0 s;
- at 10 at once, no timeout and the GPU under budget;
- **at 20 at once measured,** with the owner told the figure before the lift's re-pin.

If 20 at once passes 30 s per search, the choice comes back to the owner with G1's options.

**What must hold for this to stand:**
- E4's bundles from the harness stand for the product's (E0b: within 2 on window 4's commit).
- The reader's spread on E4 is like E2's and E3's (1 to 3).
- The K9 bar is chosen as the fresh-80 package proposes (DEC-1095 (3)). If K9 keeps hit@5 at 85 % as its one bar,
  the case for M3 is stronger: the 0.6B is at 76.8 % on the 138, and M3 at 84.8 %. If the end-to-end bar is used
  (E3-E5-DESIGN §5: right at least 85 %), the 0.6B with search-again already gives 92.8 % on the 138.

## 6. For the owner
1. **The line for "above end to end" in E4.** (i) at least 4 more right answers and no more wrong claims; (ii) exact
   McNemar p under 0.05; (iii) any gain. **Recommended: (i),** declared now, with p reported.
2. **The reranker, once E4 is read.** (a) M3; (b) M1; (c) keep the 0.6B and revisit after the three layers' load is
   known; (d) the rule in §5. **Recommended: (d),** which gives (c) unless E4 shows a gain.
3. **If (a) or (b): the service design.** S1, one service with both models; S2, two services. **Recommended: S1** (one
   slot, one lock, requests never overlap on the GPU).
4. **If (a) or (b): when.** Before the lift (the lift about 11-17, the 80 judged on the new pin); or after the lift as
   an upgrade (the 80 judged on the 0.6B, the reranker changed later with a fresh check of its own). **Recommended:
   before the lift only if E4 shows a gain;** otherwise there is nothing to build.
5. **Under (c): measure M3 and M1 on the fresh 80 for data, beside the judged configuration?** Yes or no.
   **Recommended: yes.** It costs one short GPU window and a reader run. Know that the 80 is then spent for choosing
   between them.
6. **The K9 bar's form** (in the fresh-80 package, DEC-1095 (3)) weighs on this choice (§5). **Recommended:** decide
   the bar first, in that package, then this.

**Basis (DEC-1052's five tests):**
1. **Memory:** yes. It is the reranker, the core of what agents are handed.
2. **Would ordinary work fail open or lose work without it?** No. The 0.6B works, and agents answer 92.8 % right with
   search-again. M3 is an improvement, not a guard, so it must show its gain end to end.
3. **Does it run only where the risk is?** No. It runs on every search, and doubles the scoring each time. That is
   why speed at 10 and 20 at once is part of the decision.
4. **More delivery with less drift, or only more machinery?** Only if E4 shows agents answer better. Otherwise it adds
   two pins, a loader and slower searches.
5. **Proven in use before it enters the product?** Not yet. M3 has run only in the harness and one trial window, on
   tuning sets. The fresh 80 and the product's own window would be its proof, never on the same day as adoption.
