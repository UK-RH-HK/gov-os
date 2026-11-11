# D4B-TRIAL-W4: the reranker trial on the adopted structure (DEC-1076 (3), (4)), for the owner

- **By:** the CTO, session `812bc5ce`, 2026-11-05, window 13:14 to 14:02.
- **Where:** the g1 clone (`e884675b`: m6 + the stated links) with the harness's v456, the trial copy on its own
  socket, the live 0.6B stopped by its own pid for the window and restored under class 3 after it (`rerank.by` =
  service). Scripts: `drafts/rerank-trial/trial_window.sh`, `trial_w4.sh`; records `~/gov-os-runs/D4B/trial-w4*`.
- **The sets:** the visible 40, the hidden 39 and the spent 59 (h24 and m60 apart): 138 questions, counts only.
- **Faithful:** the 0.6B on the trial copy reproduced the live 0.6B's records on all 138 (0 differing in hit@5 or
  first gold rank).
- **No GPU trip.** The backstop was armed per model on the job's process groups.

## 1. Side by side
| | 0.6B (today) | mxbai-rerank-large-v2 | Qwen3-Reranker-4B, 8-bit |
|---|---|---|---|
| hit@5 on the 138 | **107** | 76 | **112** |
| MRR on the 138 | 0.5567 | 0.3927 | **0.5927** |
| visible 40 | 34 (85.0 %) | 27 (67.5 %) | 35 (87.5 %) |
| hidden 39 | 33 (84.6 %) | 23 (59.0 %) | 34 (87.2 %) |
| spent 59 | 40 (67.8 %) | 26 (44.1 %) | 43 (72.9 %) |
| spread between the sets | 17.2 | 23.4 | **14.6** |
| a search alone: median of first calls (p90) | 1.80 s (8.7 s) | 2.09 s (10.0 s) | **3.89 s** (12.1 s) |
| 10 searches at once: median (slowest) | 6.6 s (12.2 s) | 9.6 s (10.8 s) | 29.6 s (32.3 s) |
| 20 searches at once: median (slowest) | 13.0 s (15.1 s) | 17.5 s (19.9 s) | 54.1 s (57.8 s) |
| timeouts or unranked answers | 0 | 0 | 0 |
| GPU after the load (base about 6,250 MiB) | 7,655 MiB | 9,590 MiB | 10,845 MiB |
| GPU peak during the runs | 9,847 MiB | 11,162 MiB | **15,052 MiB** (10 samples of 929 at or over 14,255) |
| GPU peak, the probe's worst shapes (one at a time; 20 at once) | 7,737 MiB | 9,686 MiB | 11,011; 13,306 MiB |
| load time | 11.0 s | 11.5 s | 21.7 s |

**How "a search alone" is read.** The harness keeps each run's rerank scores, so a question's later calls reuse them,
and the median of all calls is about 0.30 s for every model. The honest figure for one search is each question's
first call, which reranks its 40 candidates: that is the row above.

## 2. By the rule written before the run (DEC-1076 (4))
- **mxbai-rerank-large-v2:** not adopted. It loses 31 questions, and the spread widens.
- **Qwen3-Reranker-4B in 8-bit:** it wins on quality: +5 on the 138, MRR +0.036, the spread narrower (14.6 against
  17.2), and +3 on the spent 59 (72.9 %). **But it is not eligible as the rule is written:**
  - its median search alone is 3.89 s, over the 3.0 s limit;
  - its runs reached the GPU budget (14,255 MiB) 10 times, peaking at 15,052 MiB. That is 820 MiB under the backstop,
    with nothing else on the GPU but the two embedders. The probe's shapes alone stayed under the budget, so the rule's
    letter (no request shape at the budget) holds, but the run did not;
  - at 10 searches at once a search takes about 30 s, against 6.6 s today; there were no timeouts.
- **So nothing is adopted by the rule.** Adoption is yours either way.

## 3. A caution on mxbai's figure
Its result contradicts its published scores (CoIR 70.9 against the 0.6B's 65.2). Its snapshot carries its own input
template, saved by an older sentence-transformers: "query: … document: …" with its own relevance instruction. The
trial worker sends it plain (query, text) pairs, so it most likely never saw that template. This is likely a fault in
how the trial fed it, not the model's quality. Only a short re-run with its template applied can settle it (about 15
minutes on the GPU, no install; a change to the trial copy's worker only).

## 4. The recommendation
1. **mxbai: one re-run with its template applied** (the trial copy's worker only, rehearsed on a stand-in first),
   under the same rule, before it is judged. It is the cheap candidate: the smallest, no install in the product, and
   fast at 10 at once.
2. **The 4B: not now.** Its gain is real (+5, and the narrowest spread). Its cost is twice the time per search and
   about 4.5 times at 10 at once; the GPU close to the backstop; bitsandbytes in the product's venv (an install); and a
   loader change in W2-112. It returns only if mxbai, re-run fairly, does not reach it. A variant that reranks fewer
   candidates (24, not 40) would cut its time, but it is a structural change and would need measuring first.
3. **Then the approved order goes on:** query phrasing as a no-install prototype, then the embedder.

## 5. For you
- **(a)** The mxbai re-run with its template (recommended), or mxbai closed as measured.
- **(b)** The 4B: not adopted now (recommended), or a variant at a smaller rerank depth measured, or adopted beyond the
  speed limit (your call; the limit was proposed by the CTO).
- **Basis:** question 1 (memory: the reranker chosen on every used set, with its cost beside it) and question 2 (a
  model that crowds the GPU near the backstop risks every search; a candidate judged on a faulty load misjudges it).
