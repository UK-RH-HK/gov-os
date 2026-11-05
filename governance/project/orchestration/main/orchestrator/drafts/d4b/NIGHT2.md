# The night of 2026-11-04/05 (the owner asleep; DEC-1071 to DEC-1073 hold): the record for the 08:00 package

## The owner's order (00:05)
1. **The structural steps,** each under DEC-1071's rule on the best structure so far:
   - M1 with the adopted pool;
   - the reranker shown title and section (`decorate`);
   - one place per identical text (`dedup_text`);
   - the heading (C1) and answer-unit (C2) prototypes, in measure clones only;
   - the graph links (W2-92's prototype), with M5 retested beside the register links.

   Nothing from the prototypes goes into the product.
2. **The measurement set:** if the halves still agree within 3 points after all of them, it is used once on the final
   structure. If they drift apart, or a step is unmeasured by morning, it is not used.
3. **If it is used and agrees:** the reranker trial (0.6B, mxbai-rerank-large-v2, Qwen3-Reranker-4B 8-bit) on the
   three sets, in the trial's quiet window. Adoption stays the owner's.
4. **The link-integrity draft** reviewed, ready as a package. Nothing is built from it.
5. **Throughout:**
   - one GPU job at a time;
   - waits and stops by pid only (`tools/proc.sh`);
   - no installs;
   - no ping unless an emergency.

   Records are kept per step. The handover and the morning package are due by 08:00.

## The rule (DEC-1071 (2)) and the baseline
- **On the 79** (h24 apart, `score79.py`), a step is adopted if the 79 do not fall and the gap does not widen. MRR is
  the tie-break.
- **The best so far, v456 on m6:** 67/79; visible 34/40 (85.0 %), MRR 0.6480; hidden 33/39 (84.6 %), MRR 0.6141;
  gap 0.4.

## Steps
- 23:40-00:12 **Step 1: M1 + v456** (three identical runs): 67/79, visible 34/40 (MRR 0.6442), hidden 33/39 (MRR
  0.6155), gap 0.4; MRR over the 79 0.6300 against v456's 0.6313; median search 1.03 s against 0.34 s.
  - **Not kept:** the hits and the gap tie, and the tie-break (MRR on all 79 together) is lower.
  - **The best stays v456 on m6.**
- 00:12 **Steps 2 and 4** started (fix-d: v456 + `decorate`; v456 + `dedup_text`; one run each, the m6 clone).
- ~00:25 **The graph links (step 7) built** by W2-92's engineer on `w2/W2-92-proto` (`06479938`, then `e884675b` for
  DEC-1073 (2)):
  - **The links:** CITES 1,657; OF_TASK 381; AMENDS 380; SUPERSEDES 7; UNDER 2,458. They sit in a `stated_links`
    table outside `edges`.
  - **The hop:** one bounded hop, at most 12 records × 2 chunks, appended after the closure.
  - **Status in the bundle:** a record not in force is marked.
  - **Drift under DEC-1073 (2):** 184 drift. 0 are joined to their changer before the links, all 184 after (178 to
    every changer); the 82 with no hint are all joined.
  - **A changed test, by design:** W2-54's `test_an_empty_retrieval_result_gives_one_packet` (a ticket title now
    brings its `sources:`). This goes to the owner.
- ~00:40 **The link-integrity package** (product-spec's draft) reviewed and committed (`23610a2e`), with the CTO's
  section 0 (drift 184/82 under DEC-1073 (2); the UNLINKED_ID gap; the scratch rule superseded).
- **The queue next** (`drafts/d4b/night_queue.sh`, V = the best after fix-d): p0 control, p1 C1, p2 C2, p3 C1+C2
  (`f8a5fdad`); g1 the links + drift, g2 the links + M5 (`e884675b`).
- 00:12-00:25 **Steps 2 and 4** (one run each, on v456):
  - **`decorate`** (the reranker shown title and section): 66/79, visible 32 (MRR 0.5827), hidden 34 (0.6352); gap
    −7.2; MRR over the 79 0.6086. **Not adopted:** the 79 fall and the gap widens.
  - **`dedup_text`:** identical to v456 on every figure. **Not adopted:** no effect.
  - **The best stays v456.** C1 is measured by its keyword half alone; its reranker half is `decorate`, just measured.
- 00:26-00:33 **p0, the control at the prototypes' commit** (`f8a5fdad` = integrate at `547df6dd`, later content than
  m6: the register's DEC-1070 to DEC-1073, new packages and research):
  - v456 there gives 67/79; visible 33/40 (MRR 0.6312), hidden 34/39 (MRR 0.6150); **gap −4.7**; MRR over the 79
    0.6232.
  - **The same structure, with only the content grown, moves one question each way.** The halves' agreement within
    3 points is within the noise of ordinary content changes (one question in 40 is 2.5 points). This goes to the
    owner.
  - The prototypes are judged against p0 (the same commit).
- ~00:35 the stale waiters: two of W2-92's engineer's own wait loops (on its ended acceptance run) stopped by pid and
  task (`proc.sh`; L-0075). Five deliberate watchers remain.
- 00:33-01:19 **Steps 5-7** (one run each, v456 on each clone):

  | Run | Commit | The 79 | Visible | Hidden | Gap | MRR over the 79 | Verdict |
  |---|---|---|---|---|---|---|---|
  | p0 control | `f8a5fdad` | 67 | 33 | 34 | −4.7 | 0.6232 | the base for p1-p3 |
  | p1 C1 (keyword half) | `f8a5fdad` | 67 | 33 | 34 | −4.7 | 0.6191 | not adopted (tie, MRR lower) |
  | p2 C2 answer units (+26.8k chunks) | `f8a5fdad` | 67 | 35 | 32 | +5.4 | 0.6055 | not adopted (the gap widens) |
  | p3 C1 + C2 | `f8a5fdad` | 66 | 35 | 31 | +8.0 | 0.6102 | not adopted (the 79 fall) |
  | **g1 the stated links** | `e884675b` (m6 + links) | **67** | 34 | 33 | **0.4** | 0.6313 (visible MRR 0.6481) | **adopted** (nothing falls or widens; the drift fixed) |
  | g2 the links + M5 | `e884675b` | 67 | 33 | 34 | −4.7 | 0.5994 | not adopted (the gap widens) |

  - **Drift on g1's rebuilt store:**
    - before: 0 of 184 joined to a changer;
    - after: 184 (178 to every changer); the 82 with no hint all joined; `not_joined` empty;
    - changer pairs 317, of which 304 are joined (13 are stated only in ARCHIVE §A).
- **The final structure: v456 + the stated links (g1),** at m6's commit. 67/79; visible 34/40 (85.0 %), hidden 33/39
  (84.6 %); gap 0.4.
- **Every step is measured, and the halves agree within 3 points: DEC-1073 (1)'s condition is met.**
  - The measurement set is used once, on g1 with v456 (`measure_verdict.sh`, one run).
  - Every one of its 80 gold sources resolves at g1 (dry run).
  - **The caveat for the owner:** p0 shows that content change alone moves the gap by about one question each way.
- 01:20-01:25 **The measurement set, its single use** (`memory-verdict`, 60; g1 + v456; `~/gov-os-runs/D4B/verdict/`,
  kept outputs in `~/gov-os-eval/runs/verdict/`):
  - **hit@5 40/59 (67.8 %)** with m60 (`nonexistent-id`) scored apart;
  - m60 **passes**: `UNRESOLVED_IDS` naming its one id;
  - full evidence 49/60; median search 0.32 s.
  - **It does not agree with the halves** (85.0 % and 84.6 %): about 17 points short. Under DEC-1071 (3) it goes to
    the owner before anything else. **The reranker trial is not run.**
- 01:30 **The sets' profile** (`sets_profile.py`, DEC-1070 (12)'s blind phrasing audit with the gold's traits,
  aggregates only, used for nothing):

  | Set | Question words found in the gold (median; quartiles) | Under a third | Answer a list item | Answer chunk without its heading |
  |---|---|---|---|---|
  | Tuning (40) | 0.50 (0.33-0.73) | 8 (20 %) | 32 % | 32 % |
  | Hidden check (40) | 0.43 (0.26-0.60) | 13 (32 %) | 50 % | 52 % |
  | Measurement (60) | 0.41 (0.21-0.67) | 23 (38 %) | 22 % | 35 % |

  The measurement set is phrased furthest from its gold, as its brief asked ("write the question first, as an agent
  would ask it"). Its answers are list items less often. **Its difficulty reads as vocabulary,** which no structural
  step tonight touched. The levers are the meaning route's quality (the embedder) and the query's phrasing.
- **GPU:** no job after 01:25. The live reranker is kept as it is (class 3), with no trial window.
