# 2026-11-04, the day (DEC-1068): the record

## The methods' measures: the plan and the choice rule, written before any runs (DEC-1067 (b), DEC-1068)
- **When:** after re-pin window 3 is done (the hold) and both reviews are READY.
- **One at a time on the GPU**, under the GPU safety rules. No experiment runs beside them, and the GPU returns
  inside its budget between them (class 3 if the reranker keeps memory).
- **Base (m6):** integrate's head with W2-32's two branches merged, every DEC-1068 method off, and the adopted methods
  on: G1, x5, headers.
  - The product's own path (`measure.sh`), all 80 (the larger set, DEC-1069 (4), (9)), three runs, with the live 0.6B reranker.
  - It is the new base, because the labels changed since m5: hidden h02 and h24 corrected by the owner's operator
    (ACT-HLABEL-1).
  - Every search's ranked output is kept (`~/gov-os-eval/runs/<point>/`), so later label changes can be re-scored.
- **Each method alone (m6-M1 ... m6-M5):** the same commit, with one setting switched on in the measure clone only,
  then a rebuild (a full re-embed where the method changes the chunks), then all 80.
  - **One run each**: the noise band was 0 in every measure of the night, 13 points of three runs each. The base and
    the final combination keep three runs.
- **The rule:** a method is **kept** if its visible hit@5 is higher than the base's. A tie is decided by the higher
  visible full evidence; then it is not kept, because fewer methods wins. The hidden half is reported, never used.
- **The final combination (m7):** every kept method on together, three runs, all 80 (DEC-1069 (9), (10): re-based on m6).
  - If its visible hit@5 is lower than the best single kept method's, the pair that interferes is found by dropping
    one at a time on the visible half.
  - m7 is the verdict against the floor before re-pin window 4.

## Rows
- **After m6 (the owner, 2026-11-04 ~14:20):** the generated master-rule records `docs/contract/master-rules/MR-1.md`
  to `MR-6.md` say `status: PROPOSED` although they come from the accepted Contract; an agent reading one may think
  the rule is not in force. The generator gives each generated record the Contract's own status (a small fix).
- The sentinel raised a false ALERT at 11:43 while the CTO waited on the re-pin ACT; from now on the CTO writes
  `log/cto-standby.txt` for every wait on the owner or the operator (the owner, 2026-11-04).

## m6, the new baseline (DEC-1069 (9))
- 17:06-17:51, `24f06026`, the live product (G1, x5, headers) with the 0.6B reranker, the 80 questions (40 visible, 40
  hidden; labels after ACT-HLABEL-1/2/3 and the visible fixes), three runs, band 0: **hit@5 65 of 80 (81.2 %): visible
  36 of 40, hidden 29 of 40; full evidence 66 of 80: visible 34, hidden 32**. The old 48 within it: 38 (as m5).
  Visible misses: Q14, Q19, q23, q31; hidden misses 11. Every search's ranked output kept (`~/gov-os-eval/runs/m6/`,
  281 per run). The hidden re-pin moved 3 anchors with a reason line each. 887 s a run.

## The reranker trial (ACT-RERANK-TRIAL-1, DEC-1069 (11)-(13)): the rule, written before any candidate runs
- **All three run in turn, whatever the scores** (DEC-1069 (12)): the 0.6B on the trial copy (T2), mxbai-rerank-large-v2
  (T3), Qwen3-Reranker-4B in 8-bit (T4). Running a model is not adopting it.
- **Per model:** the product's own configuration on m6's clone (`~/gov-os-runs/D4B/m6/repo`, `24f06026`: G1, x5,
  headers), all 80 questions, one run (the band was 0 in every measure since 2026-11-03), every search's ranked output
  kept; hit@5 and full evidence, the visible half (it chooses) and the hidden half (reported, never used); the GPU peak
  (the probe's worst shapes at the padded bound, and the run's); the load time; the median search alone; 10 and 20
  searches at once (the probe's load, and the harness's own searches): the median, the slowest, timeouts, unranked
  answers; any failure.
- **T2's faithfulness check:** the 0.6B on the trial copy must give m6's per-question visible results exactly (36 of 40,
  34 full evidence, the same first gold ranks), or the trial path is not faithful: stop.
- **The choice rule:** a candidate is **eligible** only if T2 passed, no shape reached the budget (14,255 MiB), no
  request timed out at 10 at once, and its median search alone is at most **3.0 s**. It is **adopted** only if its
  visible hit@5 beats the 0.6B's **36 of 40**; on a tie, its visible full evidence beats **34**. Both eligible and
  winning: the higher visible hit@5, then full evidence, then mxbai (no install in the product, smaller, faster). The
  hidden half is reported beside each and never chooses.
- **The window:** the live reranker stopped from T1 to T6 (no agent's work depends on ranked search now); the GPU
  backstops armed for the harness and the trial; between models the GPU returns to the base.

## The trial, as it runs
- 17:54 T0, T1: the hold file written (the CTO's own, for the window); the live reranker (`pin-9894b0cf`'s service) stopped
  on SIGTERM in 1 s; both embedders warmed; **the GPU base 5,988 MiB**; two backstops armed. T2 started (the 0.6B on
  the trial copy: loaded in 11.0 s, READY on cuda:0, GPU 7,369 MiB after the load).
- ~18:00 the handover records brought to today (the owner's order): START-NEXT-SESSION.md, RESUME HERE, P1-PLAN's
  status table, DECISIONS-IN-FORCE, the emergency plan's pointer; `record/w2` synced.
