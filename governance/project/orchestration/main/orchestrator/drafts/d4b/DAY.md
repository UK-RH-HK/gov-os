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
- 18:01 T2's run: the 0.6B on the trial copy, all 80, **identical to each of m6's three runs on every question** (hit@5,
  first gold rank, full evidence): visible 36/40 (34), hidden 29/40 (32). Median search 666 ms; run GPU peak 9,646 MiB;
  the probe's peak 7,459 MiB, no shape near the budget; the probe at 10 at once p50 2.08 s, at 20 p50 4.15 s, no
  timeouts; the harness's 10 searches at once: median 4.60 s, slowest 8.76 s, none failed, all ranked by the service.
  The 20-at-once harness step not run: the script hung in its own `wait` (it also waits for the log's `tee`), and the
  owner's stop came first.
- ~18:45 **Stopped after T2 by DEC-1070 (1):** the script and the trial service stopped by named pids (TERM; the service
  stopped in 2 s); GPU back at 5,990 MiB. **T6:** the live reranker restored under class 3 (`GOV_RERANK_IDLE_S=43200`):
  two searches ranked, `rerank.by` service on cuda:0; both backstops stopped; the hold file ended
  (`log/act-in-progress.ended-*-rerank-trial-1.txt`). The trial venv, `svc/` and the downloads kept as they are. T3, T4
  wait for the 0.6B's new record (DEC-1070 (10)).

## The choice rule from DEC-1070 (9), written before any further choice
- **Order:** visible hit@5 first; on a tie, the visible **mean reciprocal rank of the first gold source** (1/rank,
  0 when not in the kept ranks), computed from the kept ranked outputs, no new runs. Full evidence is reported, no longer
  the tie-break. It applies to the methods (M1-M5, the recall fixes) and to the rerankers when they return.
- **The checks:** the hidden half reported in counts (hit@5, full evidence, MRR) beside each; a method that helps the
  visible half but not the hidden half is marked **suspect** and comes to the owner, not adopted on the visible figure.
  Before window 4, each kept method is also confirmed on the new measurement set (DEC-1070 (11)).
- **The baseline under this rule:** m6 (= T2); its visible MRR to be computed from m6's kept ranks before the first
  comparison.
- **Until the recall diagnosis is in, no new method is chosen** (DEC-1070 (7)).

## DEC-1070's order (accepted later, ~19:10)
1. The recall diagnosis (every never-retrieved question; the misses beyond the 20; the closure's unranked set), the
   hidden half by W2-61h's role in kinds only.
2. Generic fixes, chosen by the rule above on the visible half, checked on the hidden half.
3. The 0.6B re-measured with the fixes on the tuning sets and on memory-verdict (60, once written and cross-checked):
   its new record.
4. mxbai-rerank-large-v2, then Qwen3-Reranker-4B in 8-bit, trialled the same way (`trial_model.sh`; fix its final
   `wait` first: it also waits for the log's `tee`).
5. The results to the owner, who decides. **The target: 95 % hit@5, 85 % the floor, to be achieved.**

## The generic fixes, stage A: query-time levers in the harness (DEC-1070 (7)); written before any run
- **Baseline (m6 = T2):** visible 36/40, MRR 0.6907, full 34; hidden 29/40, MRR 0.4842, full 32 (`score.py`).
- **The runs:** the research harness (`rx.py`) over m6's clone (`measure_rx.sh fix-a 1 ...`), each lever alone, one run,
  all 80, the live 0.6B, kept ranks:
  - c0 `{"k":60}`: a no-op on the harness's own fusion path. It must reproduce m6 on every question, or the custom
    variants (v3, v5) are void.
  - v1 `{"sem_uncut":true}`: L1, the meaning route not cut after fusing the phrasings.
  - v2 `{"sem_k":60,"lex_k":60}`: L2a, routes 60 deep.
  - v3 `{"depth":40}`: L2b, the first 40 fused reranked once.
  - v4: v1 + v2 + v3 together.
  - v5 `{"perfile":2}`: crowding (K5), at most 2 chunks of a file in the first 10.
  - v6 `{"dedup":true}`: crowding, an item inside an earlier item of the same file dropped.
- **The rule (DEC-1070 (9)):**
  - A lever is **kept** if its visible hit@5 beats 36, or ties at 36 with a visible MRR above 0.6907.
  - The hidden half is reported beside each, counts only. A kept lever whose hidden hit@5 falls below 29, or whose
    hidden MRR falls, is **suspect** and goes to the owner, not adopted.
  - Speed: the median search is reported, and a lever above 3.0 s is not kept.
- **Then:** the kept levers together, three runs. Then stage B: the widening (L4, a harness or product change first),
  and the index-time methods (M1-M5, DAY.md's rule, now with MRR as the tie-break).

## Stage A's result (20:25-21:13; `~/gov-os-runs/D4B/fix-a/`)
- **c0** reproduced m6 on every question: the harness's own fusion path is faithful.

| Run | Visible hit@5 | Visible MRR | Hidden hit@5 | Hidden MRR | Median search |
|---|---|---|---|---|---|
| m6 | 36 | 0.6907 | 29 | 0.4842 | 753 ms |
| v1 meaning uncut | 35 | 0.6828 | 30 | 0.4904 | 737 ms |
| v2 routes 60 deep | 34 | 0.6646 | 30 | 0.4893 | 704 ms |
| v3 40 reranked | 34 | 0.6182 | 30 | 0.5404 | 342 ms |
| v4 = v1+v2+v3 | 33 | 0.6475 | 33 | 0.5994 | 337 ms |
| v5 per-file 2 | 36 | 0.6924 | 29 | 0.4844 | 746 ms |
| v6 drop nested | 36 | 0.6921 | 29 | 0.4914 | 754 ms |

- **By the rule:** v1-v4 are not kept, because the visible half falls. v5 and v6 are kept: ties at 36 with a higher MRR,
  and the hidden half not lower.
- **The pattern, for the owner:** every recall lever raises the hidden half and lowers the visible one.
  - v4's visible losses are edge questions pushed out by a wider pool reranked by the 0.6B: Q03 4→12, Q20 2→11,
    q25 3→8.
  - Over all 80, v4 against m6: 5 gained, 4 lost. That is no difference a sign test can see.
  - The MRR moves: visible −0.043, hidden +0.115.
- **Next:** v5+v6 together, three runs (the rule); then stage B.
- 21:14-21:34 **v56** (`{"perfile":2,"dedup":true}`), three runs, identical:
  - visible 36/40, MRR 0.6925, full 34; hidden 29/40, MRR 0.4912, full 32; median search 755 ms.
  - **Kept by the rule:** a tie at 36 with the visible MRR up (0.6907 → 0.6925), and the hidden half not lower.
  - It is a harness lever. Adopting it needs a product change (W2-32's fusion) and the re-pin; it goes to the owner
    with the stage's result.
- 21:35 **Stage B begun:** the index-time methods M1-M5, each alone (`measure_m.sh m6-Mk 24f06026 <flag>`: one rebuild,
  one run on the product's path, all 80, kept ranks). The rule as written above, with MRR as the tie-break.

## DEC-1071/1072: structural fixes, judged on all 80 (h24 apart)
- **Baseline** (m6 without h24): 65/79, visible 36/40 (90.0 %), hidden 29/39 (74.4 %), a **gap of 15.6**; MRR 0.6907 /
  0.4966.
- **Adopted when:** the 79 do not fall, and the gap does not widen. Then MRR is the tie-break. **Stop** when the gap is
  ≤ 3 points.
- **Step 0 so far (one run each):**
  - M1 36/40, 30/40 (MRR 0.7015 / 0.4835);
  - M2 = m6 (only 50 embedded chunks changed);
  - M3-M5 running.
- **Step 1:** queued (fix-b v456, three runs).
- **Step 2:** `decorate` on the best.
- **Step 4:** `dedup_text` (harness `f38402a7`).
- **Steps 5-6:** W2-32's engineer builds the C1 `heading_path_everywhere` and C2 `answer_units` switches on
  `w2/W2-32-proto` (never merged).
- **Step 7:** the research census of stated links runs (`docs/research/D4B-link-census.md`).
- **W2-88** owns the practice record: `docs/research/W2-88-memory-practice.md` (`547df6dd`).
- **M1-M5 on the 79** (one run each):

  | Method | Total | Visible | Hidden | Gap | MRR visible / hidden | Verdict |
  |---|---|---|---|---|---|---|
  | M1 | 66 | 36 | 30 | 13.1 | 0.7015 / 0.4959 | **adopted** |
  | M2 | 65 | 36 | 29 | 15.6 | unchanged | no effect |
  | M3 | 66 | 37 | 29 | 18.1 | | gap widens |
  | M4 | 65 | 36 | 29 | 15.6 | MRR lower | not adopted |
  | M5 | 64 | 34 | 30 | 8.1 | 0.7221 / 0.5399 | not adopted: the 79 fall by 1 |

- 23:17-23:39 **fix-b v456** (v4 + v5 + v6, three identical runs):
  - the 79 at 67; visible 34/40 (85.0 %), MRR 0.6480; hidden 33/39 (84.6 %), MRR 0.6141; **gap 0.4**; median 0.34 s.
  - **Adopted** (DEC-1071 (2)): the 79 rise and the gap narrows. **The halves agree within 3 points.**
- 23:45 **fix-c**: M1 + v456 (both adopted, never measured together), three runs. If it agrees within 3, the
  measurement set runs on it; else on v456. `memory-verdict` is declared in the sets root's path map (validated).
- **The measurement set:** the cross-check is done (52 as written, 4 minor, 4 major fixes, 0 drops; unresolved 0;
  overlap 0).

## The night (2026-11-05): see `NIGHT2.md`
- The final structure is v456 + the stated links: 67/79, gap 0.4.
- The measurement set was used once: 40/59 (67.8 %). It disagrees, so the trial was not run.
- The morning package is `packages/LIFT-1/D4B-MORNING-2026-11-05.md`.
