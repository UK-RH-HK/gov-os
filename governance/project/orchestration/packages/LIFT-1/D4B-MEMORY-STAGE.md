# D4B-MEMORY-STAGE: the re-plan, memory first (P1, for the owner; nothing starts until it is approved)

By the CTO (session 33b3628c), 2026-11-03 ~15:00, at the owner's order of ~14:40. Sources: three read-only research
reports of this session (the built branches W2-92, W2-91, W2-13; the measure, W2-61h, D-7 and D-8; the chain's
membership); the tickets' front matter; `P1-PLAN.md`; `docs/research/W2-61-baseline.md` §8; `dispatch/peaks.json`.
**(est.)** marks an estimate, with how it was reached.

## 1. Context
The owner moved memory ahead of the templates and the WBS refactor: D-5 to D-9 search the repository constantly and
gain from memory at full coverage. A new stage, **D-4b**, runs beside D-4's test cut. No tickets or leads (DEC-1051).
It builds what the remaining memory tickets' specs and KPIs require, reusing their built branches, as D-1 did: the
tickets' later closes adopt it and redo nothing. The floor stays (independent acceptance tests from the KPIs, an
engineer to the spec, one review with READY by `verdict.py`, DEC-1010). D-7 (M-4) and D-8 (G-3) belong to it. W2-61's
measure runs three times: before D-7, after D-7, and at the end.
The order becomes: G-14, D-3, **D-4 and D-4b in parallel**, the final memory measure, D-5 to D-9, D-10 and the lift.

## 2. What the research found (the facts that shape the plan)
- **Most of memory is already built.** W2-92 and W2-91 returned DONE and were approved to land; the emergency stopped
  the queue before it ran. W2-13 is about 90 % built and waits for W2-92 to land. W2-61h returned DONE. None of the four
  has a review record, and none has been verified on today's `w2/integrate` (290 to 350 commits newer).
- **Memory is far from its floor today.** The last visible figure is 11 of 20 hit@5 (55 %) with the branches' code;
  the hidden half has never been measured; nothing has been measured on `w2/integrate` since D-1. W2-32's bounded
  improvements are what must close the gap from about 55 % to 85 %. This is the stage's main risk.
- **The pin carries none of this.** Agents' `gov retrieve` runs the pinned copy (`pin-9894b0cf`). D-5 to D-9 gain
  from D-4b only after a **re-pin (window 3)** carries W2-92's routes, W2-13's ranking and W2-32's fixes, and the
  integration store is rebuilt with the new embedding scope. The plan adds that step.
- **The hidden half sits inside the repository.** W2-61h's commit `c5c10072` holds h01–h24 under
  `fixtures/evaluation/memory-retrieval/hidden/`; it is in the shared object store (reachable from every worktree) and
  in the nightly clone `~/gov-os-runs/W2-00/nightly/20261102-0400`. Landing W2-61h as built would put it into
  `w2/integrate` and every later clone, against G-3. It is listed in `dispatch/land.pending.txt`, a parked note the
  dispatcher does not read (it lands only from `land.txt`, which does not exist), so nothing can land it by accident.
- **W2-91 and M-4 disagree.** W2-91 embeds all of `governance/**`, close records included; M-4 says close records are
  not embedded. M-4 also takes `tests/**` (38,603 chunks) and `docs/close`, `docs/checkpoints`, `docs/probes` out of
  the vectors: about 57,600 vectors fall to about 13,500 (−77 %), so rebuilds get much faster. No visible gold source
  is under `tests/` or in those records. The keyword index keeps every chunk; D-7 is path-map configuration, no code.
- **A cycle in the plan's fates:** P1-PLAN §C re-points W2-32 to W2-15b, but W2-15b depends on W2-32.
- **W2-15a and W2-15b are bigger studies around the same measure:** other corpora (the dev tiers, `~/workspace`,
  EXAMIN's clone), five retrieval modes, the scale probe and the GPU-against-CPU study. EXAMIN's corpus does not exist
  yet, and the scale probe needs W2-88's tools.

## 3. The memory tickets D-4b covers, with their KPI lines and built work

| ticket | KPI lines (short) | built work | what remains in D-4b | who |
|---|---|---|---|---|
| **W2-92** (DAEO-n0wb) knowledge and code graph routes | S1 a record id or title in a question starts the record closure; S2 a symbol queries the code index in pages; S3 a missing index named per route, never ok, never fails the answer; S4 nothing else changes; S5 W2-61's measure, both figures; F1–F4 | `w2/W2-92`, 18 commits at `448a835a`; acceptance tests by the test designer (`5679104a`, `bc7ece7e`, `43336d76`); `gov accept` 7 of 7 lines; measure head 11/20 hit@5, 13/20 full evidence | merge `w2/integrate` into the branch (one import-line conflict in `retrieve.py`: keep both), its acceptance tests and the scoped set, the evidence file; one review | engineer, reviewer; the CTO merges |
| **W2-91** (DAEO-a3u2) full embeddings: root files, governance overlay, `schemas/` | S1 root files, `governance/**`, `schemas/**` have vectors; S2 the stay-out sets have none; S3 the overlay stays restricted; S4 two valid values, every path in one namespace; S5 nothing else moves; S6 the measure | `w2/W2-91`, 13 commits at `55b47e07` (path map `b652fc96`); tests by the designer (`657a264d` … `a5bf211f`); `gov accept` 8 of 8; 2,998 chunks gain vectors, stay-out sets 0, measure unchanged | merges cleanly; a rebuild, the scoped run (never run: the queue was stopped), the evidence file; one review. Then D-7 narrows it (decision 2) | engineer, reviewer; the CTO merges |
| **W2-13** (DAEO-zqvn) ranked lexical route (BM25, FTS5) | S1 BM25 with field weights and an exact-id boost; S2 the fusion receives a ranked list, plus the lexical-only hit@5; S3 "unavailable" instead of raising, and latency; S4 the stated gap; F1 RETR-A-04 unchanged; F2 the canary never indexed | `w2/W2-13`, 11 commits at `bdc4b795`; tests by the designer (`5500ef08`, `15e235d6`); `gov accept` 54 passed, 2 failed (S2's wiring, the latency case under load) | after W2-92: `retrieve.py` line 158 to `answer.get("ranked", answer["hits"])` (its allowed paths widened by one file); the latency case re-run alone; F2's canary re-run (DEC-1045 changed `lexical.py`); S2's hit@5 into an evidence file; a FULL review | engineer, reviewer (max effort); the CTO merges |
| **W2-61h** (DAEO-h2k3) the hidden half | S1 28 questions, 4 visible and 24 hidden, a seeded stratified draw; S2 written by a session independent of the retrieval tickets; S3 the category spread; S4 every gold source exists and holds its answer; S5 nothing written outside `hidden/`; S6 the hidden half used only once refused from every tree (G-3 changes this to "held outside every tree") | `w2/W2-61h`, 7 commits at `ac7dfa17`; the 28 questions in `c5c10072`; W2-61's visible cases revised (DEC-1009); scoped run 4,172 passed | D-8 first (§5); then only q21–q24 and the test edits land; the form tests `tests/acceptance/W2-61h/` (never written); S1, S5, S6 re-worded to G-3 | test designer (form tests), the CTO (D-8's script and landing), reviewer |
| **D-8** (G-3) the hidden half outside every worktree | (no ticket: G-3 as decided by DEC-1052) | — | §5's steps; an owner ACT for the destructive part | the CTO, a test designer (W2-61's and W2-84's cases that expect the hidden half in the tree), reviewer |
| **W2-15a** (DAEO-rd0g) EXP-003 pass 1, the baseline (FULL, judged by its evidence record) | the metric defined before the first run (W2-61's measure, both figures, the 48 questions); corpora (dev tiers, `~/workspace`, EXAMIN); five modes (lexical, semantic, fused, fused plus reranker, the lighter reranker); indexing time, peak RSS, incremental update; the stacking test once; decision-level retrieval; closes naming at most three gaps for W2-32, **chosen with the owner** | only `docs/research/EXP-003/examin/` (W2-26) | **in D-4b, this repository's part:** measure 1 (the baseline) with the five modes, indexing time and RSS from its rebuild, the stacking test, the gaps named. **After the lift, with W2-88:** `~/workspace` and EXAMIN's corpora (a KPI line split, decision 5) | the CTO (runs the measure), research (the evidence record), the owner (the three gaps) |
| **D-7** (M-4) what memory embeds | (no ticket: M-4 as decided) | — | the path map's `embedding_policy` (§6, decision 3); the tests pinned to the path map revised (W2-86's namespace case, W2-91's "nothing else moves"); two rebuilds; measure 2 | the CTO (configuration), test designer (the revised cases), reviewer |
| **W2-32** (DAEO-0pyc) retrieval improvements (STANDARD) | S1 a changed embedder pin means a full re-embed; S2 an unpinned or mismatched model fails closed; S3 a miss recorded as a memory-quality event; S4 a reranker that dies after loading is reported; S5 the fusion limit honoured; S6–S8 at most three of W2-15a's gaps, one round each; S9 below 85 % after two rounds, the owner decides; F1 an improvement that lowers a baseline figure beyond its noise band is reverted | nothing (`MODEL` hard-coded at `semantic.py:49`; S4, S5 maybe partly met) | all of it: test designer from the KPIs (while the baseline runs), engineer for S1–S5 and each gap round, one rebuild and measure per round, a review per round. Its dependency becomes W2-15a's baseline record (the cycle's fix, decision 6) | test designer, engineer, reviewer; the CTO measures |
| **W2-15b** (DAEO-swdu) EXP-003 pass 2, the final measurement | the same metric and modes after W2-32, beside the baseline; every miss classified; the stacking test final; CAP-10's 85 per class; batched stacked retrieval against 99 %; both figures; hit@5 against 95 %, 85 the floor (at 85 or above with room, an escalation); the scale probe (EXAMIN, `~/workspace`); the GPU-against-CPU study | nothing | **in D-4b, this repository's part:** measure 3, the verdict, with the classified misses and both figures. **After the lift, with W2-88:** the scale probe, the other corpora, the GPU-against-CPU study (decision 5) | the CTO (runs the measure), research (the evidence record) |

**The evidence per KPI line, as it goes:** each ticket gets its implementer's evidence file
(`docs/changes/<W2>-evidence.md`, DEC-995): one row per KPI line id with how it is verified, the command, the result
and the commit, and the review record's path. When the ticket later closes, the close checks the rows and redoes nothing;
D-5's DONE-by-code reads the same rows. Basis: question 4 (no work redone) and question 2 (no line left unverified).

**Already done, or paperwork only (no D-4b work):** W2-55 (landed `e0cb7d13`; S1, S3, S6, S8 met; S2, S4, S7 lifted;
S5 to W2-37), W2-05 (landed `b4a747f1`), W2-06 (absorbed: S1, S2, S5, F1 to W2-116 and W2-122, S3 and S4 lifted). Their
records (about 2 h) go with D-9 and the formal closes. W2-04, W2-112, W2-122, W2-123 and W2-126 were merged in D-1 and
need only formal closes.

**Memory tickets left out of D-4b** (none is needed for this repository's 85 % floor; each keeps its D-9 fate):
- W2-88, the store layout and tools for any adopted repository (27–40 lead-h, the heaviest machine user; it needs
  W2-52 and W2-81). It is needed for "memory ready" at 95 % (DEC-957), for K9 and for W2-15b's scale probe.
- W2-93 and W2-94, the exam data. W2-93 waits for W2-81.
- W2-124 (a partial store reported ok), W2-127 (the sandbox's reranker socket; the D-5 to D-9 agents run in the CTO's
  session, outside the launch sandbox) and W2-116 (the double-buffered integration store; it waits for the roles
  tickets).
- M-5, the register split, is held until after the final measure: 9 of the 20 visible questions cite the register, and
  the split would move their gold sources.

## 4. The stage's order, and who does each

**Step 0, before anything runs (the CTO, about 15 min).** A count-only script (it prints numbers, never contents):
how many hidden gold sources lie under `tests/` or in files that D-4 or D-6 will touch. Any such source goes on D-4's
list for the owner, so the cut never breaks the measure.

**Stage A (day 1, three streams in parallel):**
- **A1, D-8:** §5's steps; its destructive part as an owner ACT.
- **A2, W2-92:** an engineer merges `w2/integrate` into the branch, verifies (`gov accept`, the scoped set, through
  `heavy_slot.sh`) and writes the evidence file. Then one reviewer; READY by `verdict.py`. Then the CTO merges it with
  `--no-ff`.
- **A3, W2-91:** the same as A2, once its rebuild has room.

**Stage B (days 1–2):**
- **B1, W2-13:** finished on top of W2-92 (the engineer), then a FULL review, then merged.
- **B2, W2-61h:** the form tests (test designer), then a review; q21–q24 and the test edits land. The visible half
  becomes 24 questions.
- **B3, W2-32's test designer** writes its acceptance tests from the KPIs. It runs in parallel and never reads W2-32's
  code.

**Measure 1, the baseline (day 2).** It runs on the head with W2-92, W2-91, W2-13 and W2-61h merged, before D-7. It is
W2-15a's record on this repository, with the five modes. **The owner then approves at most three gaps** (W2-15a's KPI).

**D-7 (days 2–3).** The path map's embedding scope (decision 3), with the revised cases, then a rebuild. **Measure 2.**

**W2-32 (days 3–5).** S1–S5 first, then up to three gap rounds. Each round gets a rebuild and a measure, F1's revert
rule, and one review. Two rounds below 85 % go to the owner (S9).

**Measure 3, the verdict (about day 5).** It is W2-15b's record on this repository.

**Then:**
- **Re-pin window 3:** an owner ACT, with its checks and rollback.
- **The integration store** rebuilt at the new head with the new scope (`refresh_integration_store.sh`).
- **D-5 to D-9 start**, on full memory.

**Who:** every engineer, test designer and reviewer is an in-session agent of its role under `EMG-common.md`, at most
two or three at a time inside D-4b. The CTO alone runs the measures: `measure.py` refuses `--part hidden` to a measured
role. The CTO merges as D-1 did. No ticket is claimed and no lead starts.

## 5. D-8: the hidden half outside every worktree (half a day plus a review, est. from the research's steps)
1. A CTO script copies h01–h24 to `~/gov-os-eval/memory-retrieval/` with a minimal path map for `measure.py
   --sets-root`. It never prints them. The folder is outside every worktree, outside git and outside every store.
2. W2-61h's landing: a new branch (`w2/W2-61h-d8`) with q21–q24, the test edits and the KPI re-wording, and no hidden
   files.
3. **Destructive (the owner's ACT):**
   - delete `w2/W2-61h` and the hidden files in its worktree;
   - expire the reflog and prune `c5c10072`'s unreachable objects;
   - delete the nightly clone `~/gov-os-runs/W2-00/nightly/20261102-0400`;
   - the ACT's check: `git cat-file -e c5c10072` fails, and no file named `h0*.yaml` remains under any worktree.
4. The path map's `evaluation_sets` points the hidden part outside the tree. A test designer adjusts W2-61's and
   W2-84's cases that expect it inside.
5. **Protection, as G-3 decided:** no guard rule. Honest agents cannot reach the hidden half by ordinary search,
   because it is in no tree, no store and no commit. The guard's current hidden-half rule stays until D-9 re-scopes it.
   Putting the folder in `held-out.yaml` would refuse the CTO's own measure too, so it is not proposed.

## 6. What the machine can run beside D-4
- **Measured (`dispatch/peaks.json`, 7 days, p95 / max):**
  - a scoped test run 4.1 / 6.8 GB;
  - a rebuild with embedding 3.4 / 9.1 GB;
  - an in-session agent costs no separate process.
- **Free today:** 17.9 GB of RAM (floor 3.0), so about 15 GB usable; 0.3 of 20 CPUs busy; GPU 9.5 of 15.9 GB (the two
  embedders and the shared reranker).
- **The split (recommended):**
  - D-4 takes **two** of the three heavy slots for its scoped runs.
  - D-4b takes **one** heavy slot and **the rebuild lock**: one rebuild at a time.
  - Together at p95: 2 × 4.1 + 4.1 + 3.4 ≈ 15.7 GB, about the usable room. The Load Balancer's forecast already
    holds the newcomer when a peak would cross the floor, so at worst a run waits; nothing overloads.
- **The GPU:** rebuilds and measures use the embedders and the shared reranker already loaded, so they need no new GPU
  memory.
- **One rule (from W2-61h's failed rebuild under a contended embedder):** a measure never overlaps a rebuild. D-4's
  CPU runs go on during it.
- **About:** two or three agents for D-4 and two or three for D-4b at a time.

## 7. The measure at its three points

**How each run goes (W2-61's procedure, §8 of its baseline, run by the CTO through `heavy_slot.sh` and `rebuild_slot.sh`):**
1. A clone under `~/gov-os-runs/D4B/<point>/` at the head.
2. A seeded rebuild (W2-122).
3. `measure.py memory-retrieval --part all` on the 48 questions (24 visible, 24 hidden from outside the tree).
4. Two runs on one index, a rebuild, then a third with `--compare`. The spread of the three is the noise band.

**The code measured is the clone's own code** (`PYTHONPATH=<clone>/src`), since the pin carries none of D-4b. At the
baseline the pinned figure is recorded beside it.

**Recorded every time:** both figures (hit@5 and full evidence), per half and per question, plus the commit, the code,
the stores' fingerprints, the timings and the peak RSS.

**Cost:** about 2 to 5 h a point (est.: the 20-question runs took 11 to 38 min each; 48 questions about 2.4 times
that; three runs plus a 10 to 80 min rebuild). M-4's 77 % fewer vectors make measure 2 onward faster.

**What passes:**

| point | when | passes if |
|---|---|---|
| 1, the baseline | after W2-92, W2-91, W2-13, W2-61h are merged and D-8 is done; before D-7 | no bar: the record stands (W2-61 KPI 7), with the noise band; it names W2-15a's gaps for the owner |
| 2, after D-7 | after the new embedding scope's rebuild | hit@5 on the 48, and full evidence, no lower than the baseline beyond its noise band; every question that turns from a hit to a miss is listed with its cause. If lower: D-7's scope is adjusted and re-measured, or it comes to the owner |
| 3, the verdict | after W2-32's rounds | **hit@5 at least 85 % on the 48 (41 of 48) and at least 21 of 24 on the hidden half** (DEC-957's "memory proven"), shown beside the 95 % target and full evidence against 99 %. At 85 or above with room left, the owner is told (W2-15b). Below 85 after W2-32's two rounds: the owner decides with options (W2-32 S9) |

## 8. The estimate (est.)

**Built from:** the research's sizes, W2-32's 2 to 3 days, D-4's cut at 3 to 4 days with its owner list, and the old
plan's post-lift volume less the memory chain's 40 to 55 lead-h.

| date (est.) | steps | the owner |
|---|---|---|
| 11-03 | G-14 returns, its review, ACT-G14; this package | the package; ACT-G14 |
| 11-04 | ACT-G14 applied; D-3 (the CTO); D-4 starts; D-4b stage A (D-8 with its ACT, W2-92, W2-91) | the D-8 ACT; D-3's prompt patch |
| 11-05 | stage B (W2-13, W2-61h, W2-32's tests); measure 1; the gaps | the three gaps (~15 min) |
| 11-06 | D-7 and measure 2; W2-32 starts; D-4 goes on | D-4's list of deletions and merges |
| 11-07 – 11-08 | W2-32's rounds; D-4 done and reviewed; measure 3 | — |
| 11-09 | re-pin window 3; the integration store; D-5, D-6 start | the re-pin ACT (30–60 min) |
| 11-09 – 11-13 | D-5 to D-9 (the templates, the tidy-up, D-7/D-8 already done, the WBS refactor) | D-9's fates and K9 |
| 11-13 – 11-15 | D-10, the full suite on about 5,000 cases (2 to 3 h a run, est. from 5.4 h at 19,000), the reds fixed, a second run | the word |

**The lift: centre 11-15, range 11-13 to 11-19.**

**EXAMIN's copy: centre 11-20, range 11-18 to 11-25.** After the lift the memory chain is done, so its remaining
tickets are:
- W2-115 (the longest chain, 2.5 to 3 days);
- W2-88 then the rest of W2-15b (about 2 days);
- the roles tickets, W2-56, W2-20, W2-121, W2-93 and W2-94;
- in all about 130 to 175 lead-h at 40 to 55 a day, 3 to 5 days, plus the owner's answer time.

**The top of the range comes from:**
- memory missing 85 % after W2-32's two rounds;
- D-10 needing a third run;
- D-4's list or the gaps waiting more than a day.

**Against the earlier figures:**
- The 11-02 estimate was the restart about 11-07 and EXAMIN's copy at centre 11-14 (11-12 to 11-19). It assumed D-3
  to D-9 done by 11-05, and they had not started on 11-03.
- Without D-4b, re-estimated today: the lift about 11-12 to 11-13 and the copy about 11-18 to 11-19, with the memory
  chain after the lift.
- **D-4b moves the lift about 2 days later and the copy about 1 to 2 days later.** In return, D-5 to D-9 run on full
  memory, and the memory chain leaves the post-lift path.

## 9. Options and the recommendation
- **(A) As the owner ordered, with this plan (recommended):** D-4b beside D-4, with the re-pin added before D-5.
  - Cost: the lift about +2 days.
  - Gain: memory proven (or the gap known) before the templates and the WBS refactor are written and searched;
    four built branches finished instead of aging; no work redone at the closes.
- **(B) D-4b without the re-pin:**
  - Saves about 1 h of the owner's time and a day's risk.
  - But D-5 to D-9 search with the old pinned code and the old store, so the order buys nothing. Not recommended.
- **(C) The old order** (memory after the lift, through tickets): the lift about 2 days sooner. D-5 to D-9 work on 55 %
  memory, and the branches age a further week.

**Basis:**
- question 1 (memory, the first of the four things the Gov OS serves);
- question 4 (the agents of D-5 to D-9 deliver more with less drift when memory finds what they need);
- question 2 (no built work lost: four branches finished, not redone);
- question 3 (the measure runs three times, where the risk is, not on every change).

**What it blocks:** nothing runs until it is approved. G-14 goes on as now; D-3 starts after ACT-G14 either way.

## 10. The owner's decisions, in one list
1. **D-4b's scope** as in §3:
   - in: W2-92, W2-91, W2-13, W2-61h, D-8, W2-15a's and W2-15b's parts on this repository, D-7, W2-32;
   - out (D-9's fates, after the lift): W2-88, W2-93, W2-94, W2-124, W2-127, W2-116;
   - paperwork only: W2-55, W2-05, W2-06.
2. **W2-91 against M-4:**
   - (a) W2-91 lands as built, then D-7 narrows it, and W2-91's S1 is re-worded to M-4's scope in D-9 (recommended:
     the baseline includes W2-91 and D-7's effect is measured cleanly);
   - (b) M-4 is folded into W2-91 before it lands: about +0.5 day, one rebuild fewer.
3. **M-4's scope, the recommended list:**
   - Embedded: `.tickets/`, `src/`, the kernel `template/`, `docs/plan`, `docs/contract`, the register, `docs/adr`,
     `docs/research`, `docs/changes`, `docs/assessment`, `docs/audit`, `schemas/`, and `governance/**` except the
     records.
   - Not embedded (keyword search only): `tests/**`, `docs/close/**`, `docs/checkpoints/**`, `docs/probes/**`, and
     `governance/project/orchestration/{closes,reviews,sessions,nightly}/**`.
4. **D-8 as in §5:**
   - the hidden half to `~/gov-os-eval/memory-retrieval/`, outside every tree;
   - W2-61h's commit `c5c10072` pruned and its branch replaced (destructive, an ACT);
   - no guard rule (G-3).
5. **W2-15a's and W2-15b's lines split:**
   - this repository's measure, modes and stacking test in D-4b;
   - the other corpora, the scale probe and the GPU-against-CPU study after the lift, with W2-88;
   - a KPI move, recorded in D-9's list.
6. **The cycle's fix:** W2-32 depends on W2-15a's baseline record, not on W2-15b.
7. **The pass rules** as in §7. Point 2 is "no lower" on both figures in total, beyond the noise band, with per-question
   losses listed; point 3 is 85 % on the 48 and 21 of 24 on the hidden half.
8. **The re-pin window 3 and the integration store** after measure 3, before D-5.
9. **M-5, the register split, held** until after measure 3.
10. **The machine split** as in §6: D-4 two heavy slots, D-4b one slot and the rebuild lock; a measure never overlaps a
    rebuild.
