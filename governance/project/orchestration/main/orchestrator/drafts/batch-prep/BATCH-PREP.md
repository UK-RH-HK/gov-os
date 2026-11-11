# BATCH-PREP: batches 1 to 3 after the lift, each ticket's true state, next step, brief and cost

Written 2026-11-11 (about 14:30 UTC) by the orchestration helper (Sonnet, high, class C1) for the CTO, from `gov plan --open`
read fresh (99 tickets, 21 batches; batches 1 to 3 hold the same 26 tickets as READY-AFTER-LIFT-1) at `w2/integrate` `8c18fa300`,
live pin. Nothing launched, claimed, committed or created outside this folder. **M** measured, **E** estimated, basis named.

## 1. The finding that comes first: no lead brief can be built today

I ran `gov brief lead <ticket> --run <kind>` for all 12 tickets whose next step starts a lead. **All 12 refuse**
(`briefs/<W2>-<kind>.md` holds each refusal, copied). The refusals are the live pin's ready check (`src/gov/brief/build.py:155-188`):

| refusal | tickets | what it means |
|---|---|---|
| `KPI_NO_VERIFY` (a KPI line with no `Verify:` text) | all 12: 95 lines in all (W2-04 8, W2-105 8, W2-11 19, W2-66b 2, W2-66c 3, W2-81 17, W2-90b 7, W2-94 8, W2-93 7, W2-98 11, W2-40 1, W2-173 4) | the old tickets' KPI lines are plain strings; the new reader wants `Verify:` after each. New tickets carry it on success lines only (W2-170, W2-60a's S3 and S4 pass; their failure lines do not). The same refusal holds for W2-115, W2-154, W2-33, W2-156 (I tried 6 more): **no ticket of the plan is READY by code today** |
| `DEPENDS_NOT_CLOSED` | W2-93 (needs W2-81 closed), W2-98 (needs W2-11 closed) | a dependency must be **closed**, not merged |
| `READS_MISSING` | W2-173 | created after `ready.new_since`: needs a `reads:` list (empty is allowed) |
| warnings only | all: `NON_GOALS_MISSING`, `SIZE` 4,090 to 4,884 of 4,000, W2-81 `EST_LOC_OVER 1200` | not refusals (`ready_check` puts them in `warn`) |

**Proposed fix (the CTO's call):** one ticket-edit pass, a C1 record edit (Sonnet, high), adding `Verify:` to the 95 lines. For the
ten tickets with acceptance folders the text is "`gov accept <W2>`: the cases the README map names for this line", which the
README KPI maps already give; for W2-94, W2-93, W2-40 it is the named record or check. About 95 lines, 1 to 1.5 helper-hours,
about $3 to 5 (0.1 to 0.2 points, E). The alternative is the older scratch route (`tools/build_lead_brief.py`; old briefs such as
`briefs/W2-66b-A5-run1.md` and `W1-01b-A5-run1.md` still exist), which skips the code check DEC-1083 made standard: not
recommended.

Other prerequisites before any `ready.txt` line is valid (dispatcher README: claim committed, worktree merged, brief built):
- **Six tickets are `open` and need a claim** (`tk start`, committed on integrate): W2-94, W2-93, W2-98, W2-40, W2-66c, W2-173.
- **A review round on a merged ticket needs a fresh worktree** from integrate (W2-04: none exists; W2-96, W2-122, W2-123 only).
- **W2-00 (`DAEO-sdxk`) is the CTO's own ticket and never closes before W2-46**, yet the plan makes W2-149 (`52ku`), W2-173
  (`qz4p`) and later W2-172 and W2-154 "wait" on it (shared tool paths). Treat those waits as advisory, or narrow W2-00's paths.
- **W2-173 vs W2-149:** the plan puts W2-173 after W2-149's close (shared `indep_launch.py`); MEMORY-AUDIT-1 says W2-173 need
  not wait. Cheapest way to settle it: close W2-149 first (a probe record, about 1 h).

## 2. The table

State words: **merged** = work is in `w2/integrate` (`git branch --merged`, M). Closes are the CTO's (`gov close` in the
main tree; no lead, no model beyond the CTO's own session). Classes follow RUBRIC-2 and RUBRIC-2-APPLY (through D-10,
engineers on C2/C1 stay Opus high; designers C3 Opus, else Sonnet; reviewers C3 Opus, C2 Opus if FULL, else Sonnet; auditors Opus;
product-spec and research Sonnet; leads Opus high). "h" is lead-hours, "pt" is points of the week (1 point = $27.3 at list price,
USAGE-RUBRIC-2, M).

### Batch 1 (18 tickets)

| ticket | state (from the records) | next step | role, class, model | brief | cost |
|---|---|---|---|---|---|
| W2-96 `ouet` FULL | merged (3 branches, 0 ahead); `gov accept` 190/190 on integrate (LIFT-CLOSES-1); probes exist (5 records); in LIFT-CLOSES-1 | **formal close**, CTO: `gov close DAEO-ouet`, from a shell that does not ignore SIGHUP; may need one fresh probe if the gate sees the 3 README commits after the last probe. S6 is "met in half" (D9-FATES): CTO reads it | CTO, C1; Opus high | none needed | 20-25 min; 0.05 pt |
| W2-105 `zpdj` STANDARD | **not merged**: `w2/W2-105` 7 ahead, verified DONE at `fa653609c` on 11-01 (run 2); one real change (2 deny lines out of `template/.rulesync/permissions.jsonc`); 28 cases pass, but 3 KPI lines read "fail" because `gov accept` could not read the README map (R-W2-105-1, 11-01); overlaps integrate in 3 files (permissions.jsonc, two W1-38 files) | **test-design round for the README map, then land**: first re-run `gov accept DAEO-zpdj` on a merge of integrate (the reader was fixed since 11-01; it may read now: then only the land); merge integrate (3 overlaps); CTO lands. Gates W2-90c | lead (Oh high) + independent-test-designer, **C3** (permissions) Opus high | `briefs/W2-105-tests.md`: REFUSED (KPI_NO_VERIFY x8) | 1.5-3 h; $4-9; 0.15-0.33 pt (E: W2-105's own runs were 2.2 h and 2.3 h, $3 and $6, M) |
| W2-122 `blwa` STANDARD | merged; accept 22/22; in LIFT-CLOSES-1 "yes"; **`gov close` refused 13:38 today** (CHECK_FAILED: six old merges without `Task:`, a `load_sensitive` entry citing DONE DEC-757); repair ticket `DAEO-feon`; row 127 | **formal close after the owner's path-map edit** (`accepted_history`, the W1-19 entry), DECIDED-NOT-DONE rows 126, 127 | CTO, C1 | none | 15-20 min; 0.05 pt |
| W2-123 `qzrq` STANDARD | merged; accept 50/50; "yes" | **formal close** after the same edit; close first (W2-126 depends on it) | CTO, C1 | none | 15-20 min; 0.05 pt |
| W2-131 `r8vq` STANDARD | merged `03336f19`; accept 29/29 (11-06); review READY; **not in LIFT-CLOSES-1, so its close was not rehearsed**; S4 is the CTO's measure after window 4 (done by the 80, DEC-1098 (1)) | **formal close**; run `gov accept W2-131` first on integrate; close before W2-133 (dep) | CTO, C1 | none | 15-20 min; 0.05 pt |
| W1-01b `vhad` LITE | the work is on integrate (`10025b210`, ancestor M; path-map entry `0568d91baf56` present); D9-FATES: "closes now"; DEC-1126 (7): D-10's ruled red is the green run | **formal close** (`gov close DAEO-vhad`) | CTO, C1 | none | 10-15 min; 0.04 pt |
| W2-00 `sdxk` | the CTO's coordination ticket (open by design) | nothing: closes last (W2-46) | n/a | none | n/a |
| W2-04 `u4oz` FULL | merged `70965cf61` as "accepted as built" (D-1, DEC-1052 M-1); an old review at `b37b5c8f1741` **failed** (F1, F2, `ready_check` False); the repair merged (`de81824be`, `a0c79a6c9`) with **no review of the final code and no `docs/probes/DAEO-u4oz/`**: `gov close` would answer `PROBE_MISSING` | **review round, then close**: one fresh independent reviewer on integrate's head, probe record committed by the orchestrator. **On the critical path:** W2-05 waits for W2-04 (`src/gov/context/__init__.py`) | lead (Oh high) + independent-auditor as reviewer, **C2 FULL**, Opus high | `briefs/W2-04-review.md`: REFUSED (KPI_NO_VERIFY x8) | 0.5 h; $6; 0.22 pt (E: W2-04's own review lead was 0.4 h, $1.6, plus one reviewer about $4-5, M) |
| W2-11 `k7hz` STANDARD, kernel | **not merged**: `w2/W2-11` 26 ahead, round 1 verified DONE at `c9f99b28b` (11-01, `gov accept` passes every line); round 2's four KPIs (DEC-983: brief gaps, anti-drift kit, scope control, timing tests) not seen done; **27 files overlap integrate**, among them the 5 brief templates (W2-128 and W2-153 rewrote them), 4 kernel skills, the orchestrator role and all their generated copies. Gates W2-98, W2-120, W2-52, W2-113 | **resume round**: merge integrate (real conflicts in the templates and the orchestrator role), re-verify, a product-spec round for what W2-128 already did, an independent review, then the owner's CAP-33 approval and a class (b) ACT for the generated `.claude/**` copies (as DEC-991 did). Check round 2 first | lead Oh high; product-spec Sonnet high; reviewer **Opus high; C3** (kernel) | `briefs/W2-11-resume.md`: REFUSED (KPI_NO_VERIFY x19) | 4-6 h; $18-26; 0.7-0.95 pt (E: its run 1 was 3.4 h, $15.8; its resume 0.5 h, $8.2, M) |
| W2-66b `zuiy` LITE | no branch; ticket says add `.ps1` to W2-66's code suffixes (`CODE_SUFFIXES`, `test_w2_66_live_test_map.py:34`): **not built that way** (no `.ps1`). But D-10 fixed the same case by another route (W2-66c-d10: a file under a `tools/` folder that a `.py` names, `dc5c0fd87`, which covers `win_toast.ps1` read by `deadman.py`); DEC-1126 (7): D-10's ruled red is its green run. Old brief exists (`briefs/W2-66b-A5-run1.md`) | **CTO's reading first:** does S1 hold through W2-66c-d10's route? If yes, formal close with that evidence; if the owner wants the literal suffix, one designer round | CTO; else designer **C2**, Sonnet high, `Rewrite-Reason: DEC-1027 B` | `briefs/W2-66b-tests.md`: REFUSED (KPI_NO_VERIFY x2) | 0 to 1 h; $0-3.5; 0-0.13 pt (E) |
| W2-81 `l78m` FULL | **not merged**: `w2/W2-81` 19 ahead, **0 files overlap integrate**; last return DONE at `e78e6af75` (probe records valid, scoped run green, review moderated READY, 11-02). Only the land is left; its first real run is the CTO's in W2-27. Gates W2-93 (needs it **closed**), then W2-88 | **land round**: merge integrate, scoped run, CTO lands, then close | lead Oh high, **C2** (test code, FULL) | `briefs/W2-81-land.md`: REFUSED (KPI_NO_VERIFY x17, EST_LOC_OVER) | 1.5 h; $4; 0.15 pt (E: its resumes were 1.7-1.9 h, $3.3-4.3, M) |
| W2-90b `nqa2` LITE | **not merged**: `w2/W2-90b` 6 ahead, round done, verified head `d2408361d`; the one package (S4's two stand-in homes) was answered by DEC-1022 item 2 (`3a4203e56` on integrate); 6 test files overlap integrate; its four cases for W2-90c need W2-105 | **land round**: merge integrate (6 overlaps), scoped run, CTO lands, close | lead Oh high; **C2** | `briefs/W2-90b-land.md`: REFUSED (KPI_NO_VERIFY x7) | 1.5-2 h; $4; 0.15 pt (E; its run was 6.1 h but the work is done, M) |
| W2-94 `g87r` STANDARD | open, no branch; EXAMIN's question set, audit-kind | **owner's decision first**: (a) the path map has **no `examin` entry in `evaluation_sets`** (a class (a) ACT, SANDBOX-SEAL-1 allows it); (b) the independent launch script runs only briefs on the owner's approved list (set-up A's five and the operator's two, ACT-W2-149-INSTALL-1): a writer brief for this set needs the owner's approval, like MEMORY-AUDIT-1's three | independent-auditor, Opus high | `briefs/W2-94-build.md`: REFUSED (KPI_NO_VERIFY x8) | 3-4 h; $15-25; 0.55-0.9 pt (E: MEMORY-AUDIT-1 puts a full audit at $20-30) |
| W2-139 `ongl` STANDARD | merged `fa2737766` (one batch with W2-140, accept 160/160, review READY); close at the lift (row 63) | **formal close in one batch with W2-140**, one green run, outside an experiment window | CTO, C1 | none | 25 min both; 0.08 pt |
| W2-140 `5ce2` STANDARD | merged with W2-139 | the same close | CTO, C1 | none | with W2-139 |
| W2-151 `qzca` LITE | merged `6990f7f3e`; no acceptance folder; `gov close` would refuse twice (`SPECIFICATION_NOT_FOUND`, `NO_ACCEPTANCE_TESTS`) (LIFT-CLOSES-1) | **recorded CTO close** on `docs/changes/W2-151-evidence.md` (DEC-1112 (3)); do not run `gov close` | CTO, C1 | none | 10 min; 0.03 pt |
| W2-40 `6ox0` FULL research | open, no branch; re-scoped to its S3 (the harness at a hook's time limit; S1, S2, S4 lifted, D9-FATES); not on W2-27's path; P2 | **research run, later** (after the path): one research session, then one FULL review (probe) | research, **Sonnet high**; reviewer **C2 FULL, Opus high** | `briefs/W2-40-build.md`: REFUSED (KPI_NO_VERIFY S1) | 2 h; $10-13; 0.4-0.5 pt (E) |
| W2-66c `btcs` LITE | open; ACT-SELECT-FIXES-1 **applied 11-09** (row 37), so the ticket may start; its designer round was revised in D-10 (`2979f3607`); no `Verify:` on 3 failure lines | **test-design round** (S6: every pinning case shown red on the ACT's parent map), CTO's scoped run, formal close | lead Oh high + designer **C2, Sonnet high** | `briefs/W2-66c-tests.md`: REFUSED (KPI_NO_VERIFY F1-F3) | 1.5 h; $4.5; 0.16 pt (E: ticket says about 2 h) |

### Batch 2 (5 tickets)

| ticket | state | next step | role, class, model | brief | cost |
|---|---|---|---|---|---|
| W2-126 `jpr0` STANDARD | merged; accept 28/28; a probe record exists; in LIFT-CLOSES-1 "yes"; depends on W2-123 | **formal close** right after W2-123 (same blocker, row 127) | CTO, C1 | none | 15-20 min; 0.05 pt |
| W2-133 `k4wm` STANDARD | merged `c39197b6b`; accept 48 cases pass (W2-135 note); not rehearsed; depends on W2-131 | **formal close** after W2-131 | CTO, C1 | none | 15-20 min; 0.05 pt |
| W2-93 `6y0x` STANDARD | open; W2-81's hidden half; depends on W2-81 **closed** | **owner's decision first** (the same two as W2-94: an `adoption-proving-ground` entry in `evaluation_sets`, a writer brief on the approved list), then after W2-81's close: designer/auditor run | hidden half by independent-auditor, Opus high; form tests by designer **C2**, Sonnet high | `briefs/W2-93-tests.md`: REFUSED (KPI_NO_VERIFY x7, DEPENDS_NOT_CLOSED W2-81) | 3 h; $10-15; 0.4-0.55 pt (E) |
| W2-98 `wi46` STANDARD, kernel skill | open; depends on W2-11 **closed**; new skill folder + generated copies | **product-spec round after W2-11 closes**: skill, tests in parallel, review, then CAP-33 and a class (b) ACT for the copies | product-spec **Sonnet high**; designer **C3 Opus high**; reviewer **Opus high** | `briefs/W2-98-build.md`: REFUSED (KPI_NO_VERIFY x11, DEPENDS_NOT_CLOSED W2-11) | 3 h; $12-16; 0.45-0.6 pt (E) |
| W2-149 `52ku` FULL | merged (`b4de529b`, F18-F23 `90c1fea6c`, F36/F38 `2f98aecbc`; accept 206/206, 3 live skipped); stays `in_progress` by design for rows F37 (log omits the rule check's word) and F40 (CTO's one search of the auditor's tree before its first run); **no `docs/probes/DAEO-52ku/`**; reviews READY exist only in scratch (`.gov-runtime/scratch/orchestrator/reviews/W2-149-sgx-review-r1.md`, `-f18`, `-f36`) | **probe record, then close**: commit the READY review as a probe record if its form allows (CTO), else one fresh FULL review; F37 as a small engineer round or a named row; F40 stays the CTO's. Close it before W2-173 | CTO; if a fresh review: reviewer **C3 FULL, Opus high (max allowed as the FULL probe)**; engineer for F37 Opus high | none (F37 round: not briefed) | 1-2 h; $0-10; 0-0.37 pt (E) |

### Batch 3 (3 tickets)

| ticket | state | next step | role, class, model | brief | cost |
|---|---|---|---|---|---|
| W2-135 `c4pb` STANDARD | merged (round 2 `bd62b8aa2`); accept 7 test files; review round 2 done; not rehearsed | **formal close** (after W2-133 if the plan orders it) | CTO, C1 | none | 15-20 min; 0.05 pt |
| W2-148 `xafn` FULL | merged (`511a4a17`, F21, replay `a170641e`); operator ACTs applied (rows 58, 76); accept 166/166 then 169; four READY reviews exist as scratch (`log/W2-148-review-r1..r3, f21.md`); **no `docs/probes/DAEO-xafn/`** | **probe record, then close**: as W2-149; the CTO commits the READY review in probe form, or one fresh FULL review | CTO; else reviewer **C3 FULL, Opus high or max** | none | 0.5-1 h; $0-8; 0-0.3 pt (E) |
| W2-173 `qz4p` FULL | open, "after the lift"; on W2-27's path (memory audit chain W2-170 to 173); waits (plan) for W2-149 and W2-00; no `reads:` field | **test-design round, engineer round, FULL review** (three rounds); needs claim, `reads: []`, `Verify:` on F1-F4 | lead Oh high; designer **C2 Sonnet high** (ticket says so); engineer **Opus high** (C3 launch script); reviewer **Opus high** | `briefs/W2-173-tests.md`: REFUSED (KPI_NO_VERIFY F1-F4, READS_MISSING) | 5-6 h; $18-26; 0.65-0.95 pt (E) |

## 3. Cost: how I estimated

Basis (M): the 170 finished lead logs (`log/*-A5-*.json`): median 3.1 h and $5.70, mean 3.7 h and $6.83; a first run
(tests then build) median 4.3 h and $8.28; a resume 2.5 h and $5.70; a review round 0.4 h and $1.6. A launched worker run
(`spend.jsonl`): median $3.15 (designer about $1-3, engineer $3.2, reviewer $4.9 at max). A point is $27.3 (USAGE-RUBRIC-2,
M, fit to 11-10 16:00). Each step is its lead plus its workers, then converted. The CTO's own closes are about $1.2 of
session tokens each (E; the heavy part is the machine, not the meter).

| group | lead-hours | dollars | points |
|---|---:|---:|---:|
| Lead steps (12 tickets above, plus W2-149 and W2-148 probes) | 34 (range 27-45) | 150 (range 105-250) | 5.5 (3.8-9.2) |
| 14 formal closes by the CTO (96, 123, 126, 122, 131, 133, 135, 139+140, 151, W1-01b, 66b, and the two probe closes) | 0 (CTO time about 5 h serial) | 17 | 0.6 |
| `Verify:` ticket-edit pass (95 lines) | 1-1.5 | 4 | 0.15 |
| **Total, batches 1 to 3** | **about 35** | **about 171** | **about 6.3 (range 4.6-10)** |

**Against the 80 % brake.** The week stood at 64 % at 13:47 (`log/usage.txt`, M); the reset is 11-15 09:00. Batches 1 to 3
would take it to **about 70 % (range 69-74 %)**, leaving 6 to 11 points under 80 %. FORECAST-W2-3 puts the path after the
lift at about 30 points, so the brake, not the plan, decides where batches 4 and 5 stop: expect it to bind near W2-05's
batch and the batch after, unless the reset comes first (11-15). Not in these figures: the CTO's own watching (about 0.4 to
0.8 points a day, E, USAGE-RUBRIC-2 §2), W2-11's round 2 if it proves large, any promotion to Opus after two failed rounds
(DEC-1120 (3)), and set-up A's run (about 4 points, E).

## 4. Order I recommend, and the critical path to EXAMIN's copy (W2-27, `DAEO-h4rh`)

W2-27's `depends_on` closure holds **48 tickets not closed (M)**; of the 26 here, **W2-04, 11, 81, 90b, 93, 94, 96, 98, 105,
122, 123, 126, 131, 133 and 173 are in it**; W2-139, 140, 148, 149, 135, 151, 66b, 66c, 40, W1-01b and W2-00 are not.
Batch 4's W2-05 waits on W2-96, 122, 123, 126, 131, 133, 135 and 04 (shared files), and batch 5's nine tickets wait on W2-05,
so **those eight closes are the gate for everything after**: the plan cannot move until they are closed.

1. **Step 0 (the CTO, about 1.5 h, before any launch):** the `Verify:` pass; six claims; the owner's two asks (the path-map edit
   of row 127 for the W2-122/123/126 closes; the `examin` and `adoption-proving-ground` entries and the writer briefs for W2-94
   and W2-93).
2. **Critical path, now, in parallel with each other:**
   - **Track A, the CTO's closes, serial, main tree:** W2-96, then W2-123, W2-126, W2-122 (when the owner's edit is in), then
     W2-131, W2-133, W2-135, then W1-01b, W2-151, W2-139+140. About 5 h of CTO time; the dispatcher lands only when no close runs.
   - **Track B, leads in worktrees, start first:** **W2-04 review** (0.5 h, gates W2-05), **W2-11 resume** (longest, 4-6 h; gates
     W2-98, W2-120, W2-52, W2-113), **W2-81 land** (1.5 h; gates W2-93 and, later, W2-88), **W2-105** (gates W2-90c).
3. **Second wave:** W2-90b land, W2-66c tests, W2-149 probe and close (then W2-173), W2-148 probe and close.
4. **After W2-81 and W2-11 close:** W2-93 and W2-98; W2-173 (three rounds) once W2-149 is closed; W2-94 once the owner has settled
   the writer route.
5. **Last, off the path:** W2-40, W2-66b (if it needs a round).

Estimated end of batches 1 to 3: about one working day from step 0's end (E: 35 lead-hours is about 14 helper-hours at the
FORECAST-W2-3 ratio of 0.4, three at once, plus 5 h of serial closes); W2-11 is the long pole. After it the plan's batch 4 is
W2-05 alone (its own fix: five rows in `AR-2-git-sweep.md`, a fresh probe, DECIDED-NOT-DONE row 125), then batch 5.

## 5. Proposed `ready.txt` lines (not written to `dispatch/`)

Form: `<W2> <ticket id> <brief in ../briefs/> <log in ../log/>`. **None is valid yet:** each needs its brief to build (section 1),
its claim committed (the six `open` tickets), and, for W2-04, its worktree. Log names are new (an old `W2-04-A5-review.json`
already has a return). Briefs would be built by `gov brief lead <W2> --run <kind>` into `briefs/` under these names.

```
# Track B, in this order, once step 0 is done:
W2-04  DAEO-u4oz  W2-04-A5-r6-review.md   W2-04-A5-r6-review.json
W2-11  DAEO-k7hz  W2-11-A5-r5-resume.md   W2-11-A5-r5-resume.json
W2-81  DAEO-l78m  W2-81-A5-r5-land.md     W2-81-A5-r5-land.json
W2-105 DAEO-zpdj  W2-105-A5-r3-tests.md   W2-105-A5-r3-tests.json
# second wave:
W2-90b DAEO-nqa2  W2-90b-A5-r2-land.md    W2-90b-A5-r2-land.json
W2-66c DAEO-btcs  W2-66c-A5-r2-tests.md   W2-66c-A5-r2-tests.json
# after W2-81 and W2-11 are CLOSED, and the owner's route for W2-93 is settled:
W2-98  DAEO-wi46  W2-98-A5-run1.md        W2-98-A5-run1.json
W2-93  DAEO-6y0x  W2-93-A5-run1.md        W2-93-A5-run1.json
# after W2-149 is closed:
W2-173 DAEO-qz4p  W2-173-A5-run1.md       W2-173-A5-run1.json
# after the owner's route for the EXAMIN set is settled:
W2-94  DAEO-g87r  W2-94-A5-run1.md        W2-94-A5-run1.json
# off the path:
W2-40  DAEO-6ox0  W2-40-A5-run1.md        W2-40-A5-run1.json
```
W2-149, W2-148 (probe records), W2-66b (a reading, maybe a round) have no line: they are the CTO's. W2-04's review would be the
only launch that is also on the critical path of batch 4.

## 6. Open points for the CTO (small)
1. Do the three D-10 "ruled red" tickets close on that red as written? DEC-1126 (7) says yes for W1-01b, W2-66b, W2-90c; for W2-66b
   I could not find the literal `.ps1` suffix, only the W2-66c-d10 route (section 2).
2. W2-04, W2-148, W2-149 are FULL and have no `docs/probes/` record on integrate; LIFT-CLOSES-1 checked only ten closes, so these
   (and W2-131, 133, 135, 139, 140) were never rehearsed. Run `gov accept` for each before its close.
3. W2-11 round 2: I did not find a record that the four DEC-983 round-2 KPIs were done; the resume lead should read it first.
4. Files in this folder: `BATCH-PREP.md`, `briefs/` (12 refusals), `run_briefs.sh` and `fold_refusals.sh` (the two scripts I ran;
   `gov brief` is read-only, `git status` was clean after).
