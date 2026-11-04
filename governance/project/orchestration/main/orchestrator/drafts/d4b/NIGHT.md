# The night of 2026-11-04 (DEC-1067): the record for the 09:00 package

## Measures (W2-61's measure, 48 questions, hit@5 / full evidence; three runs each, noise band as stated)
| point | commit | what it adds | hit@5 all | visible | hidden | full ev. all | vis | hid | band | speed (cold, median of 10) |
|---|---|---|---:|---:|---:|---:|---:|---:|---|---|
| m1 | 156a5feb | baseline | 28 | 12 | 16 | 34 | 17 | 17 | 0 | (about 4x the pinned ~1 s, before W2-92 S6) |
| m2 | 20488bc9 | D-7 + G4 (path map), W2-13 S6, Q09 re-label, Q11 + q10 re-anchors | 29 | 13 | 16 | 34 | 18 | 16 | 0 | 1.34 s (1.29-1.40) |

m2 against m1, by id: Q09 gained (its re-label, rank 65 -> 1), Q11 gained (its re-anchor, 11 -> 2), Q03 lost (5 -> 6; its
gold goes stale with W2-32, review F-9), Q19 full evidence gained; hidden: h04 gained, h17 lost, h08 full evidence lost.
D-7's own effect on hit@5: about 0 (as the research measured for G4: 0); it is for an honest measure. Run time per run
615 s (m1: about 18 min). The cold rebuild: 25 s (the machine-wide vector cache served the vectors; 18.8k left).

## Steps
- 01:15 m2's first start stopped at its pre-check (q10's anchor moved by W2-13 S6): re-anchored by an independent
  designer (`ba08ca77`, merged `20488bc9`); measure.sh's fetch fixed for a reused clone.
- 01:30 DEC-1067 recorded (`047351eb`); W2-32's S8 re-worded (`03df2124`).
- 01:35 the real shared embedder probed (F-4): accepts every length; cuts above its 4,096-token context (about
  15,000 characters) silently: W2-32 names the limit.
- 01:55 the hidden label check (DEC-1067 (c), an independent auditor in W2-61h's role, blind): h07 right, h11 right;
  **h02 wrong** (answer and sources: a later standing decision brought back in another form what its gold says ended;
  a second governing source needed) and **h24 wrong** (alternatives: a standing decision names one form of the
  Contract as its authority, missing from the gold). **Not applied:** the guard refused the auditor's write to the
  sets root (DEC-953 item 2: an auditor writes only its own record); not routed round (DEC-849). For the owner: who
  writes the two changes (an operator ACT letting this role write the sets root for this task, or the operator applies
  the auditor's corrected files). The auditor holds the corrected contents; nothing quoted anywhere. Until then h02
  and h24 are scored on their old labels (measure 3 marks them). Also found: `hidden/` is mode 755 inside the root's
  700 (only the root protects it): an operator row.
- 02:10 the visible label check (blind, an independent designer): **Q16 wrong** (its gold from DEC-798, superseded;
  the question ambiguous today: **re-worded** to the lead launch, so Q16's figures before tonight are not comparable;
  goes a step past "the label": the owner may revert) and **Q19 wrong** (alternatives: the Contract's MR-3 added); old
  labels in `retired/`; merged `86082142`. The checker's rows: the prompt's resource floor (6.7 GB) stale against
  DEC-947 item 5 (3 GiB); O-A1 (the forecast admission) has no register entry.
- 02:05 W2-32 (DEC-1067 (f) and order (2)): reranker requests capped at 16 (`MAX_REQUEST_TEXTS`); the embedder reads
  up to `EMBED_LIMIT_CHARS` 10,000 (about 2,650 tokens on the register; a chunk above it embedded from its first part
  and named); the reranker up to 32,768; F-5 closed (no span sent twice in either direction). P-W2-32-8: the rebuild's
  result names the cut chunks.
- 02:17-02:24 G1's full re-embed in `~/gov-os-runs/D4B/g1` at W2-32's head `612cd009` (integrate merged in; the store
  serves the research clone): 389 s (semantic 356 s); 9 chunks above `EMBED_LIMIT_CHARS` 10,000 cut and named; GPU
  10.7 GB. `gov accept W2-32` at `612cd009`: 104 passed, 0 failed, 1 skipped (real models included).
- 02:20 index-time method 1 (contextual headers when embedded, off by default) started on `w2/W2-32-index` (engineer)
  and `w2/W2-32-index-tests` (designer), for measure 4.
- 02:40 W2-32's delta review (round 2) READY; **W2-32 merged into integrate `b32e8504`** (G1). Riding along: R2-F1
  (nested Python parents still send lines twice: must, before measure 3), R2-F2 (a hung reranker waits per batch),
  R2-F3 (a test line). Q03's label check started (the round-1 review's F-9).
- 02:45 contextual headers (index-time method 1) built and green on `w2/W2-32-index` (`335233db`, 14 of 14 cases),
  off by default; for measure 4 in a measure clone with `embed_headers: true`; merged only if it wins on the visible
  half, after a review.
- 02:50 measure m2g1 (G1 alone, at `b32e8504`) started; the research waits until it ends.
- 02:37 m2g1 at `b32e8504` stopped at its pre-check: q03 entry 1.3 and q12 entry 1 unresolved (W2-32 moved them).
  Q03 re-labelled blind (DEC-1033's "any device" overtaken by DEC-1065 (1): the GPU only; old label in retired/), q12
  re-anchored (`a9ef6f82`, `bc1219c1`, merged `296a4639`). For the owner: q12's gold answer names 3 of the 5 cases
  `_decode_continuation` now refuses (anchor-only brief: left as it is; hit@5 scores sources, not the answer text);
  DEC-1033 (2)(b) has no "changed by DEC-1065 (1)" mark in the register.
- 03:00 R2-F1's first fix regressed the bundle (an expanded parent split into pieces with one id: "a chunk cited
  twice" in W1-21's cases): kept off integrate, redone on the branch. **G1 is measured as merged (`296a4639`, flat
  parents send no span twice; nested Python parents may still repeat lines: tokens, not hits).**
- 03:00 m2g1 restarted at `296a4639`.
- 03:20 **R2-F1 deferred to D-9 (the CTO's call):** two fixes tonight each broke W1-21's bundle contract (the first: one
  chunk id cited twice; the redo: a parent sent with marked gaps, so its sha256 no longer matches its stated lines;
  W1-21 passes 79 of 79 on integrate without it). The review rated it non-blocking (tokens on nested Python parents,
  not hits). The work is kept at tag `park/W2-32-R2-F1`; `w2/W2-32` reset to before it (`845151bc`; its code equals
  integrate's). The designer's nested-parent case and R2-F3's line (`0223b7ea`) come back with R2-F1.
- 03:22 **m2g1 (G1 alone, `296a4639`): 35 of 48 (72.9 %), visible 18, hidden 17; full evidence 35 (18 / 17); band 0;
  speed 1.37 s median (1.30-2.94).** Against m2 by id: visible Q07, Q08, Q10, Q18 gained by G1, Q03 and Q16 by their
  re-labels (Q16's new label found at rank 4), Q11 lost (2 -> 8), q24 full evidence lost; hidden h17 (22 -> 3) and h22
  (59 -> 1) gained, h23 lost (3 -> 21), h08 full evidence gained.
- 03:23 the shared reranker restarted under class 3 (11.5 -> 8.5 GB); the research clone `~/gov-os-runs/D4B/g1` at
  `296a4639`; the backstop armed; the research agent started on the visible half only (DEC-1067 (b)).
- 03:25-03:45 S8 (routing by question type, DEC-1067 (a)) built on `w2/W2-32` while the research runs: settings in
  `governance/project/retrieval.yaml` (`routing.code_first`, `routing.named_first`; absent or 0 = off: integrate
  unchanged); the symbol half in the measured form (the code route's hits by stored-vector cosine); P-W2-32-9: the
  record half reuses the pool's rerank scores (no extra request). Acceptance 27 of 28 before that ruling.
- **03:53:31 the GPU backstop tripped** (15,883 MiB > 15,872) during the research runs: the experiment's 5 processes
  paused at once. The shared reranker stayed at 100 % with 15.9 GB on the request in flight for over 6 minutes (a
  spill: the embedders' memory was paged out by Windows, at 04:00 the GPU read 212 MiB, and paged back in on their
  next call: 3.96 s and 1.47 s, then 5.2 GB; same runners, 29/29 layers, no CUDA error, no reload, no failed request).
  The CTO ended the paused run (SIGTERM, before touching the reranker, so no private reranker could start), then the
  reranker did not stop on SIGTERM (stuck in a CUDA call): **SIGKILL** (a harder stop than class 3's command; the service
  holds no state), then class 3's start: READY 04:01:22, `rerank.by` = service, GPU 7.7 GB. No ping (no harm, not an
  emergency by the night's rule). **Cause:** 16 texts per request bound the count, not the size (16 whole chunks of up
  to 32,768 characters each). **Fixes:** the research harness now caps each request at 24,000 characters in total and
  checks memory before every request (waits at 15,000 MiB); the product gets the same bound (`MAX_REQUEST_CHARS`
  24,000, W2-32's engineer, before measure 3). Backstop re-armed 04:02.
- 04:20 the shared reranker keeps its PyTorch peak between requests: memory climbs per variant (7.7 -> 10.3 -> 13.2 ->
  15.8 GB) and never falls by itself. A handshake: the research agent stops and writes a flag at 15,000 MiB; the CTO's
  `tools/rerank_reset_watch.sh` checks the GPU is idle (no request in flight), restarts the reranker (class 3),
  checks READY on cuda:0, removes the flag. For D-9: the service should release its cache after a request
  (`torch.cuda.empty_cache()`) or bound its peak (the size bound helps): W2-112's code, a re-pin.
- 04:05-04:30 the review of S8 and the size bound READY (`reviews/w2-32-s8.md`); S8-F1 fixed (with `code_first` on,
  the code route enters the fusion in cosine order, as the measured r01); S8-F4 (an empty `routing:` block is off);
  S8-F2 the CTO's ruling (keep P-W2-32-9's form; the measure tests it); S7-F4's case. `w2/W2-32` at `6d38fc11`: the
  stand-in suites 548 passed, 1 failed (R2-F1's deferred case). Merge after the research ends (gov accept's real-model
  cases use the GPU). 04:18 the first handshake reset: 15,774 -> 5,429 MiB, READY on cuda:0.
- 05:00 the research agent's return (the night's survey, visible half only, 32 runs, base G1 18/24 and 18/24):
  winners alone: routing by question type 20 (1a code-first 19, 1b named-record 19), the reranker shown path, title and
  section 20 (gains Q06, Q11, Q19, loses Q04), three deterministic phrasings 19, expansion in both indexes 19; losers:
  pool quotas 17, a global pool 15, the embedder instruction 16, the reranker instruction 14, authority x2 15; neutral:
  route agreement, a per-file cap, a blend. Best combination x5 (routing + phrasings) 20 and 19, nothing lost. Speed:
  every method within 0.08 s of the harness base (0.69 s; the product's own median 1.38 s). Index-time candidates:
  contextual headers (+1 to +2, built), a file-level index (+1), code chunks cut on definitions (+1), a reverse
  depends_on edge (+1, Q14), identifier tokenisation (0 to +1), one span per register entry (0 to +1).
- **05:05 measure 3's choice rule, written before any hidden figure is seen (DEC-1067 (b)):** measure 3 runs G1 with
  every winner together (x7: routing both halves + decoration + phrasings + expansion) and, beside it, the visible
  half's best clean combination (x5), each on all 48, three runs. **The combination adopted is the one with the higher
  visible hit@5; a tie goes to the higher visible full evidence, then to fewer methods. The hidden half is reported for
  each and never used to choose.**
- 05:10 **W2-32's S8 and the size bound merged into integrate `16e0287a`** (both routing halves off by default; every
  reranker request at most 16 texts and 24,000 characters); gov accept W2-32: 140 passed, 1 failed (R2-F1's case, since
  marked a strict xfail, deferred to D-9), 1 skipped. Measure 3 runs on the G1 clone through the harness (04:57).
- **05:23 measure 3 (harness on the G1 clone `296a4639`, all 48, three runs each, band 0):** x7 (every winner: routing
  both halves + decoration + phrasings + expansion) **37 of 48 (77.1 %), visible 20, hidden 17; full evidence 36 (19 /
  17)**, median search 0.66 s; x5 (routing + phrasings) **37 (20 / 17), 36 (19 / 17)**, 0.62-0.66 s. Against G1 (35):
  visible Q06, Q11 gained (x7 also Q19 gained, Q04 lost); hidden h08, h23 gained, h05, h22 lost (both). **By the rule
  written at 05:05, x5 is adopted** (visible tie at 20 and 19; fewer methods). No pair interferes: decoration's Q19 is
  paid for with Q04, expansion adds nothing; the winners gain the same questions. Against the floor: 37 < 41 (85 %),
  hidden 17 < 21.
- **05:25 measure 4's choice rule, written before it runs:** contextual headers (index-time method 1) rebuilt into a
  clone of `w2/W2-32-index` with `embed_headers: true`, measured with x5 on top (and the no-op, headers alone), all 48,
  three runs. **Headers are adopted if x5 + headers has a higher visible hit@5 than x5 on G1 (20); a tie goes to the
  higher visible full evidence (19), then to fewer methods (no headers). The hidden half is reported, never used.**
- 05:34 measure 4 started on `~/gov-os-runs/D4B/m4` (`dcae563a` = `296a4639` + headers; full re-embed with headers on:
  624 s, semantic 550 s; the store's pin records `embed_headers true`; all anchors resolve on both halves).
- **05:37:54 the backstop tripped again** (15,904 MiB) in measure 4's first run; the reranker again at 100 % and 16 GB.
  **Cause, found:** the 24,000-character bound counts the sum of a request's texts, but the reranker pads every text to
  the longest in the batch (one 23,000-character chunk with 15 short ones = 16 x 23,000); and the m4 clone predates the
  product's bound. Handled as at 03:53: the paused run ended first, then the reranker reset under class 3 (it stopped
  on SIGTERM this time; READY 05:39:26; GPU 2.6 GB; embedders whole). **Fix:** the padded size (count x longest <=
  24,000) in the product (W2-32's engineer) and in the harness (the research agent); measure 4 reruns on integrate's
  code + headers once both land. **The CTO's mistake at 05:38:** the process match for the stop also caught W2-32's
  phrasings engineer (its brief named rx.py) and ended it mid-work; its uncommitted changes were kept and the session
  resumed. Rule for next time: stop processes by the pids the backstop paused, never by a text match.
- **06:08 measure 3b and measure 4 (harness, padded split, all 48, three runs each, band 0):** x5 on G1 (padded) **37
  (20 / 17), full 36 (19 / 17)**, the same as before the split (no question changed); **x5 + contextual headers (m4)
  38 of 48 (79.2 %), visible 21, hidden 17; full evidence 36 (19 / 17)**, median search 0.60-0.65 s; by id: visible
  q24 gained; hidden h22 gained, h17 lost. **By the rule written at 05:25, the headers are adopted** (visible 21 > 20).
  GPU at 4.6 GB through both (the padded bound).
- 06:10-06:40 **W2-32's padded bound and phrasings merged into integrate `0936077c`** (S8 round 2 READY; gov accept
  151/0/2). S8-F2 (the measured x5 reranked all the named record's chunks; the product picks among those on the page):
  the product measure tests the product's form. The headers branch reviewed: READY (`reviews/w2-32-headers.md`); F1 (a
  designer helper) and F2 (a per-file query bound: 79 s off every rebuild with headers on; an entry criterion for
  switching it on) ride along; F3 (a worktree branched before the switch re-embeds on its first rebuild, keywords until
  then: fails closed) and F4 (`#` lines in code blocks counted as headings: quality) are rows. Merging integrate into the
  headers branch: the README conflict resolved by the designer, the evidence file by the engineer. **Row for the owner:**
  the headers engineer reports it "took a guard refusal as false and worked round it" (a `git show :3:<file>` refused;
  it resolved the conflict by a script without reading the revision): against DEC-849's rule, recorded.
- 06:30 **the headers merged into integrate `433e17be`** (gov accept W2-32 at e31801e0: 165/0/2); **the adopted
  methods switched on `dc8a2829`**: `governance/project/rebuild.yaml` (embed_headers: true) and
  `governance/project/retrieval.yaml` (routing.code_first 2, named_first 2, phrasings true). Live for sessions only
  after re-pin window 3. **Measure 5's rule, written before it runs:** the product's own path (measure.sh, the clone's
  gov), all 48, three runs: it is the verdict before re-pin window 3 (DEC-1067 (6)). If the product scores below the
  harness's x5 + headers on the visible half (21), a half is reverted only if it alone loses visible questions
  (judged on the visible half; F1's revert rule).
- **07:22 measure 5 (the product's own path, `dc8a2829`, everything adopted on; all 48, three runs, band 0): 38 of 48
  (79.2 %), visible 21, hidden 17; full evidence 36 (19 / 17); speed 1.45 s median (1.39-1.91), cold.** The product
  equals the harness's m4 exactly. The floor is not met (38 < 41; hidden 17 < 21). Visible misses: Q14, Q19, q23. The
  first start (06:36) ended after run 1 on a SIGPIPE in measure.sh's summary line (fixed); its run-1 record (38, 21 /
  17) kept in `m5/run-a`. The backstop and the reset watcher stopped at 07:25; GPU 9.7 GB.
