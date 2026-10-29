# B. Progress since Wave 2 started (2026-10-16 to 2026-10-29 13:00 GMT)

Research agent B's findings (read-only, 2026-10-29), written down by the orchestrator.

**Anchors:**
- plan approved `7d60dec6` (2026-10-16 17:29 +0100, DEC-719 to DEC-729);
- tickets created `4190c39e` (2026-10-16 17:35 +0100, "52 tickets").

**Abbreviations:** `LOG` = `.gov-runtime/scratch/orchestrator/log/`; `Q-<stamp>` = `LOG/close-queue-<stamp>/`; `REG` = `docs/DECISION_REGISTER.md`; `PKG` = `governance/project/orchestration/packages/`.

**Times:** queue logs and file times are local (BST until 10-25, GMT after); a close record's `created` field is UTC.

## 1. Tickets

70 `.tickets/*.md` carry `wbs_id: W2-…`: `4190c39e` created 52, and 18 were added later.

| Status | Count | Notes |
|---|---|---|
| closed | 15 | 13 by `gov close` exit 0; W2-01 by owner decision; W2-48 withdrawn |
| in_progress | 17 | 7 merged into `w2/integrate` but not closed (§1.2) |
| open | 38 | includes W2-00, the coordination ticket |

### 1.1 Closed tickets, by date

| Date | WBS | Ticket | How it closed | Commit | Close record |
|---|---|---|---|---|---|
| 10-17 | W2-01 | DAEO-g0ip | owner decision (`tk close`), its six findings named | `f15ac648` (DEC-757) | none |
| 10-20 | W2-53 | DAEO-7rr2 | `gov close` exit 0, 8th attempt (counting the 10-18 sweep) | `a1565e56` | `docs/close/DAEO-7rr2/CL-DAEO-7rr2.md` |
| 10-21 | W2-48 | DAEO-xxgp | withdrawn, not delivered | `6cce71bb` (DEC-880) | none |
| 10-21 | W2-02 | DAEO-zflj | exit 0, 4th attempt | `e52ad8a2` | `CL-DAEO-zflj.md` |
| 10-21 | W2-54 | DAEO-0rfi | exit 0, 2nd attempt (and one gate stop) | `55162ea2` | `CL-DAEO-0rfi.md` |
| 10-22 | W2-62 | DAEO-juee | exit 0, 1st attempt (after two gate stops) | `d7daf01b` | `CL-DAEO-juee.md` |
| 10-22 | W2-50 | DAEO-kl5e | exit 0, 2nd attempt | `01488b72` | `CL-DAEO-kl5e.md` |
| 10-27 | W2-70 | DAEO-uzme | exit 0, 2nd attempt | `23c24700` | `CL-DAEO-uzme.md` |
| 10-27 | W2-66 | DAEO-c1uz | exit 0, 2nd attempt (after one gate stop) | `f8d1f60a` | `CL-DAEO-c1uz.md` |
| 10-27 | W2-72 | DAEO-ye2a | exit 0, 1st attempt | `6c439d8a` | `CL-DAEO-ye2a.md` |
| 10-27 | W2-59 | DAEO-kh9l | exit 0, 1st attempt | `f0f933e1` | `CL-DAEO-kh9l.md` |
| 10-27 | W2-65 | DAEO-e82f | exit 0, 1st attempt | `be18d1c7` | `CL-DAEO-e82f.md` |
| 10-27 | W2-73 | DAEO-qty6 | exit 0, 1st attempt | `74c08ed8` | `CL-DAEO-qty6.md` |
| 10-27 | W2-74 | DAEO-2azm | exit 0, 1st attempt | `182823e4` | `CL-DAEO-2azm.md` |
| 10-27 | W2-69 | DAEO-rmbe | exit 0, 1st attempt | `07a8d624` | `CL-DAEO-rmbe.md` |

**Clean closes per day:** 10-20: 1; 10-21: 2; 10-22: 2; 10-27: 8.

**Of the 52 plan tickets** (W2-00 to W2-50), `gov close` has closed only W2-02 and W2-50 (W2-01 was closed by owner decision; W2-48 withdrawn). The other 11 clean closes are tickets added after the plan (W2-53 and later).

### 1.2 Merged, not closed (7)

| WBS | Ticket | Merge (date) | Why not closed |
|---|---|---|---|
| W2-63 | DAEO-pl6k | `50c08ae3` (10-20) | refused 10-21/22 NO_ACCEPTANCE_TESTS; waited for W2-07's class close (DEC-892 item 1); in today's queue |
| W2-58 | DAEO-5j8b | `4845b9b8` (10-21) | refused 10-22 and 10-28; repair DAEO-pr0y; re-close decided (DEC-939 item 3) |
| W2-67 | DAEO-9nys | `4da40b60` (10-24, round 1) | in progress |
| W2-07 | DAEO-r9ss | `2a9d1a11` (10-24), `8555aafc` (10-28) | in today's queue |
| W2-57 | DAEO-cy5o | `57e363c5`, `4904a60f` (10-28) | its re-probe after W2-68's merge is running |
| W2-75 | DAEO-ebmh | `b52e3a96` (10-29) | closing (`Q-20261029-1228`) |
| W2-68 | DAEO-2gc7 | `848f5ab3` (10-29) | in today's queue; batch not switched on (P-W2-68-PRUNE) |

No merge names the other 10 in-progress tickets: W2-03, W2-05, W2-16, W2-20, W2-26, W2-37, W2-49, W2-51, W2-52, W2-71.

## 2. Close times

### 2.1 Every committed close record (13)

Total test s = sum of `test_runs[].seconds`; scope = `evidence.scope` (records before W2-66's evidence block ran the whole suite, REG DEC-925); wall = queue log "check ok; close X" to "close X exit 0".

| Close record | created (UTC) | scope | why_full | targets | test runs (s) | total test s | wall s (log) |
|---|---|---|---|---|---|---|---|
| CL-DAEO-7rr2 | 10-20 14:53 | full (no block) | — | — | 24.28; 1849.18; 1746.13 | 3619.59 | 4345 (`Q-20261020-1422`) |
| CL-DAEO-zflj | 10-21 19:58 | full (no block) | — | — | 2.43; 2020.14; 1883.68 | 3906.25 | 4432 (`Q-20261021-1924`) |
| CL-DAEO-0rfi | 10-21 21:28 | full (no block) | — | — | 464.65; 2095.54; 1943.30 | 4503.49 | 4750 (`Q-20261021-1924`) |
| CL-DAEO-juee | 10-22 15:44 | full (no block) | — | — | 16.25; 1812.92; 1799.49 | 3628.66 | 4277 (`Q-20261022-1511`) |
| CL-DAEO-kl5e | 10-22 21:17 | full (no block) | — | — | 306.20; 2046.46; 1909.67 | 4262.33 | 4509 (`Q-20261022-2044`) |
| CL-DAEO-uzme | 10-27 17:12 | full | BASE_UNKNOWN | 2 | 4.45; 16.60; 2356.80; 942.40 | 3320.25 | 3990 (`Q-20261027-1546`) |
| CL-DAEO-c1uz | 10-27 21:29 | full | SHARED_CORE, UNPLACED | 2 | 47.63; 3024.90; 1113.64 | 4186.17 | 4564 (`Q-20261027-1957`) |
| CL-DAEO-ye2a | 10-27 21:50 | scoped | — | 30 | 3.53; 292.13 | 295.66 | 597 |
| CL-DAEO-kh9l | 10-27 22:12 | scoped | — | 30 | 7.84; 291.95 | 299.79 | 603 |
| CL-DAEO-e82f | 10-27 22:33 | scoped | — | 30 | 1.03; 292.66 | 293.69 | 599 |
| CL-DAEO-qty6 | 10-27 22:55 | scoped | — | 30 | 18.30; 296.04 | 314.34 | 626 |
| CL-DAEO-2azm | 10-27 23:16 | scoped | — | 30 | 10.55; 295.42 | 305.97 | 620 |
| CL-DAEO-rmbe | 10-27 23:56 | scoped | — | 30 | 962.61; 65.80; 296.84 | 1325.25 | 1683 |

**Tests per close (`tests_run.passed`):** full about 14,650 to 16,555; scoped 3,320 to 3,669.

### 2.2 Full and scoped compared (no batched close has run)

| Kind | n | test s mean / median | wall mean / median |
|---|---|---|---|
| Full, passed | 7 | 3918 / 3906 s (65.3 min) | 4410 / 4432 s (73.5 min) |
| Scoped, passed | 6 | 472 / 303 s | 788 / 612 s |
| Scoped, without W2-69 | 5 | 302 / 300 s (5.0 min) | 609 s (10.2 min) |
| Full, refused after a full run | 13 (14 with the 10-18 sweep) | 3782 / 3700 s | about 66 to 80 min |

- **Test-seconds:** a scoped close used about 13 times fewer than a full one, 302 s against 3,918 s (W2-69 excluded: its own acceptance suite ran 962.61 s).
- **The queue's pre-close steps take about 11 to 12 minutes per close** (rebuild, collection, record tests, network, gov check): 717 s before W2-72's close (`Q-20261027-1957`, 21:29:05 to 21:41:02); 678 s before W2-53's of 10-20 12:30 (`Q-20261020-1212`).
- **A whole slot:** a scoped close's slot was therefore about 22 minutes (W2-72: 21:29:05 to 21:50:59, 1314 s), against about 85 minutes for a full one (W2-53's passing slot: 14:27:52 to 15:53:19, 5127 s).
- **The 10-27 queue run** closed 7 tickets (1 full, 6 scoped) in 3 h 54 min (`Q-20261027-1957`, 20:02:02 to 23:56:04).
- **The only scoped closes so far are the six of 10-27.** W2-58's close of 10-28 ran full (`why_full: SHARED_CORE`; `Q-20261028-2007/close-DAEO-5j8b.json`).
- **No batched close has run** (W2-68 merged `848f5ab3`, batch off).

## 3. Close success rate: every gov close attempt on a Wave 2 ticket since 10-16

**Sources:**
- the queue folders' `close-*.exit` and `queue.txt` files;
- for attempts before the queue: `LOG/W2-01-close.json`, `LOG/close-DAEO-7rr2.json`, `LOG/sweep-close-DAEO-7rr2.json`, `LOG/close-DAEO-7rr2-2.json`, `LOG/close-DAEO-7rr2-3.json`;
- the repair tickets in `LOG/repair-tickets/` and `.tickets/`.

Lens H's table (`docs/assessment/2026-10/H-test-strategy.md` lines 396-410) agrees with the first 13 rows.

| # | When (local) | Ticket | Exit / code | Test s | Wall | Repair | Source |
|---|---|---|---|---|---|---|---|
| 1 | 10-17, ended 13:46 | W2-01 | refused, CHECK_FAILED, 6 findings | 4834.6 | ≤ 5257 s | DAEO-ax5o | `LOG/W2-01-close.json` |
| 2 | 10-18 01:53 | W2-53 | refused, CHECK_FAILED, 7 | 3105.1 | n/a | DAEO-lbrx | `LOG/close-DAEO-7rr2.json` |
| 3 | 10-18 15:39 | W2-53 (scratch-merge sweep) | refused, 17 | 3338.0 | n/a | none | `LOG/sweep-close-DAEO-7rr2.json` |
| 4 | 10-19 10:44 | W2-53 | exit 1, STORE_STALE | 0 | 1 s | — | `LOG/close-DAEO-7rr2-2.json` |
| 5 | 10-19 12:01 | W2-53 | refused, CHECK_FAILED, 1 | 3539.6 | n/a | DAEO-c6ir | `LOG/close-DAEO-7rr2-3.json` |
| 6 | 10-20 08:38 | W2-53 | exit 3, 20 findings | 3870.1 | 4592 s | DAEO-8em0 | `Q-2026-10-20` |
| 7 | 10-20 11:07 | W2-53 | exit 4, ESCALATION_BLOCKED | 0 | 0 s | — | `Q-run2` |
| 8 | 10-20 11:52 | W2-54 | exit 1, TREE_NOT_COMMITTED | 0 | 0 s | — | `Q-20261020-1108` |
| 9 | 10-20 12:30 | W2-53 | exit 3, 10 findings | 3982.0 | 4749 s | DAEO-2ah0 | `Q-20261020-1212` |
| 10 | 10-20 14:40 | W2-53 | **exit 0** | 3619.6 | 4345 s | — | `Q-20261020-1422` |
| 11 | 10-21 02:37 | W2-02 | exit 1, TREE_NOT_COMMITTED | 0 | 1 s | — | `Q-20261021-0108` |
| 12 | 10-21 14:20 | W2-02 | exit 3, 2 | 3832.8 | 4536 s | DAEO-ke7i | `Q-20261021-1401` |
| 13 | 10-21 16:11 | W2-02 | exit 3, 3 | 3716.7 | 4486 s | DAEO-e8r9 | `Q-20261021-1550` |
| 14 | 10-21 19:44 | W2-02 | **exit 0** | 3906.3 | 4432 s | — | `Q-20261021-1924` |
| 15 | 10-21 21:09 | W2-54 | **exit 0** | 4503.5 | 4750 s | — | `Q-20261021-1924` |
| 16 | 10-21 22:57 | W2-63 | exit 3, 8 | 4062.6 | 4421 s | DAEO-nkk9 | `Q-20261021-2241` |
| 17 | 10-22 10:28 | W2-50 | exit 3, 2 | 3662.8 | 4305 s | DAEO-h8r2 | `Q-20261022-0952` |
| 18 | 10-22 12:17 | W2-58 | exit 3, WORK_WITHOUT_TASK | 3597.4 | 4243 s | DAEO-aneq | `Q-20261022-1153` |
| 19 | 10-22 15:33 | W2-62 | **exit 0** | 3628.7 | 4277 s | — | `Q-20261022-1511` |
| 20 | 10-22 21:02 | W2-50 | **exit 0** | 4262.3 | 4509 s | — | `Q-20261022-2044` |
| 21 | 10-26 22:16 | W2-70 | exit 3, 9 | 3700.3 | 4109 s | DAEO-2upp (open) | `Q-20261026-2157` |
| 22 | 10-27 16:05 | W2-70 | **exit 0** | 3320.3 | 3990 s | — | `Q-20261027-1546` |
| 23 | 10-27 18:43 | W2-66 | exit 3, 1 | 3632.9 | 4191 s | DAEO-s1wp (open) | `Q-20261027-1823` |
| 24 | 10-27 20:13 | W2-66 | **exit 0** | 4186.2 | 4564 s | — | `Q-20261027-1957` |
| 25–30 | 10-27 21:41 to 23:56 | W2-72, W2-59, W2-65, W2-73, W2-74, W2-69 | **exit 0 ×6** (scoped) | §2.1 | §2.1 | — | `Q-20261027-1957` |
| 31 | 10-28 20:25 | W2-58 | exit 3, 3 | 3624.5 | 3958 s | DAEO-pr0y (open) | `Q-20261028-2007` |
| — | 10-29 12:57 | W2-75 | running | — | — | — | `Q-20261029-1228` |

**Headline:**
- **Attempts:** 31 finished, 13 passed (42%); without the 10-18 scratch-merge sweep, 30 and 13 (43%).
- **18 refused:**
  - 14 after a full run (13 with repair tickets, plus the sweep);
  - 4 at once (STORE_STALE, ESCALATION_BLOCKED, and TREE_NOT_COMMITTED twice).
- **By period:** 10-17 to 10-22, 5 of 20 passed (25%); 10-26 to 10-28, 8 of 11 (73%).
- **First attempt:** 7 of the 13 closed tickets passed on it (the six scoped closes of 10-27, and W2-62).
- **W2-53** took 8 attempts (7 without the sweep), about 62 hours first to last (lens H line 414).
- **Machine time:** refused full runs used 49,161 test-seconds, **13.7 h** (14.6 h with the sweep); the 13 passing closes used 30,261 s (8.4 h).

**Pre-close gate stops (no attempt spent):**

| When | Ticket | Cause | Source |
|---|---|---|---|
| 10-20 16:04 | W2-54 | gov check red, schema/invariants: core-schema did not know W2-53's new `close` record type | `Q-20261020-1422/check-DAEO-0rfi.json`; lens H line 408; DEC-872 |
| 10-21 22:39 | W2-62 | commits without `Implements:` (`0e686111dd61`, `6e4b27506ad1`, `162f17ea9caf`) | `Q-20261021-1924/queue.txt`; DEC-891 accepted `162f17ea9caf` |
| 10-22 13:56 | W2-62 | gov check red, secrets indexing | `Q-20261022-1335/check-DAEO-juee.json`; cause in neither register nor packages |
| 10-27 17:22 | W2-66 | gov check red, product traceability: `Implements:` named a role | `Q-20261027-1546/check-DAEO-c1uz.json`; DEC-927 |
| 10-21 08:22 | W2-02 | the queue stopped after "rebuild before", no further line | `Q-20261021-0817/queue.txt`; cause unrecorded |

## 4. Refusal causes by kind

**Kinds:**
- (a) the ticket's own work;
- (b) the judge: gov's own code, including its test suite and fixtures;
- (c) the environment: load, machine, network, settings;
- (d) the orchestrator's own tooling or process.

This is the agent's reading of the cited records; a refusal can carry several kinds.

| # | Ticket, when | Causes, as recorded | Kinds | Source |
|---|---|---|---|---|
| 1 | W2-01, 10-17 | PROBE_INVALID after the orchestrator's integration commits `d09e8c1b`, `ee30c9de` edited the ticket file (no rule yet for integration-side edits, DEC-757 item 2); CHECKPOINT_STALE; CONTEXT_FAILED (DEC-750 not yet in the store); W1-05 p95 (passed alone); W1-42's two reds. "none of them W2-01's work" | b, c, d | REG line 8289; DEC-757 |
| 2 | W2-53, 10-18 01:53 | context-reproducibility over its 60 s limit with an unstable `dropped` order (fixed by W2-54); core-schema red on W1-43's audit record type; traceability red on W1-42's claim commit `93bcb2479905` (later accepted history); stale checkpoint. "none of them W2-53's work" | b, d | REG line 8414; DEC-768 |
| 3 | W2-53 sweep, 10-18 15:39 | run on a scratch merge while leads worked; W2-54 green-here red; three W1-46 cases failed alone under load; stale checkpoint | b, c, d | lens H line 400 |
| 4 | W2-53, 10-19 10:44 | STORE_STALE: no rebuild before the close | d | `LOG/close-DAEO-7rr2-2.json`; lens H line 401 |
| 5 | W2-53, 10-19 12:01 | W1-30 r13 time-limit case at load about 25 | c | `PKG/P-W2-53.md` §2; DEC-823 |
| 6 | W2-53, 10-20 08:38 | "four causes, three of them the orchestrator's own records" (superseded DEC-636 cited; W1-35's tests in W2-11's paths; stale checkpoint) + `tests/unit/secrets` shadowing the stdlib; load 28.87 | b, c, d | DEC-867; `Q-2026-10-20/queue.txt` |
| 7 | W2-53, 10-20 11:07 | ESCALATION_BLOCKED after three refusals (designed stop; DEC-870 lifted it) | designed | `PKG/P-W2-53.md` §2; DEC-870 |
| 8 | W2-54, 10-20 11:52 | TREE_NOT_COMMITTED: the orchestrator's `P-W2-53.md` uncommitted | d | close json; lens H line 405 |
| 9 | W2-53, 10-20 12:30 | the queue's own checkpoint commits lacked `Implements:` ("its fault"); W1-38 rulesync past its 10 s probe under load | c, d | `PKG/P-W2-55.md` §2; DEC-871 |
| 10 | W2-02, 10-21 02:37 | TREE_NOT_COMMITTED: the sync copied W2-48's cache stores | d | close json; lens H line 409 |
| 11 | W2-02, 10-21 14:20 | W1-08 red from copies in no namespace ("the orchestrator's own slip"); W1-07 `doctor` under load | c, d | DEC-885 |
| 12 | W2-02, 10-21 16:11 | W1-07 `doctor` (load); W1-07/W1-25 setup errors: fixtures' copies race git gc, triggered by the orchestration record's growth. "from the environment and the tests' fixtures, not from any ticket's code" | c (b, d contributing) | `PKG/P-W2-02-C3.md` §2–3 |
| 13 | W2-63, 10-21 22:57 | NO_ACCEPTANCE_TESTS: the close did not read `acceptance_tests.path` ("a gap in the close"); W1-38 under load; W1-46 network | b, c | `PKG/P-W2-63-C1.md` §2–3 |
| 14 | W2-50, 10-22 10:28 | PROBE_INVALID: W2-58's merge rewrote W2-50's probed files ("caught as designed"; DEC-895: found at close, not at merge); the DEC-892 entry did not name its test ("the orchestrator's slip") | d | DEC-894; DEC-895 |
| 15 | W2-58, 10-22 12:17 | WORK_WITHOUT_TASK: seven `Task: decision-record` commits changed its paths or ticket file. "the cause is the orchestrator's records and a judge without a rule for decision records" | b, d | `PKG/P-W2-58-C1.md` §2, §5 |
| 16 | W2-70, 10-26 | nine reds from the first re-pin's settings regeneration and a W2-69 case name, "not from W2-70" | d | DEC-925 (REG line 11051); DEC-926 |
| 17 | W2-66, 10-27 18:43 | W2-66's own record-only case refused the orchestrator's ACT `.patch` | d | `PKG/ACT-P-TRACE-IMPL-1.md` line 5 |
| 18 | W2-58, 10-28 | W2-54's green-here fixture ran gov check (about 6 min alone), over the 900 s per-test limit under load; fixed by W2-75 | b, c | DEC-937 (REG line 11401) |

| Kind | Refusals carrying it | Sole cause |
|---|---|---|
| (a) the ticket's own work | **0** | 0 |
| (b) the judge: gov's code and tests | 8 (#1, 2, 3, 6, 12, 13, 15, 18) | 0 |
| (c) the environment, mostly load | 9 (#1, 3, 5, 6, 9, 11, 12, 13, 18) | 1 (#5) |
| (d) the orchestrator's tooling or process | **14** (#1–4, 6, 8–12, 14–17) | **6** (#4, 8, 10, 14, 16, 17) |
| designed stop | 1 (#7) | — |

**No Wave 2 refusal record names the closing ticket's own work.** Lens H found the same for 10-17 to 10-21 (line 416).

## 5. The nightly

Sources: `LOG/nightly/digest.txt`, `history.jsonl`, `status.txt`, `<stamp>/run.txt`, and `cron/2026-10-29.log`.

| Run | Kind | Head | Parallel | Serial | Verdict | Wall | Estimate vs actual |
|---|---|---|---|---|---|---|---|
| 20261021-1743 | manual, quiet window | `dbd3cc53` | exit 1, 2121 s: 15,465 passed, 4 failed | exit 0, 2047 s: 263 passed | **red 2** (W2-54 time-limit and green-here red alone; plus W1-42's two accepted reds) | 4249 s | none |
| 20261025-0501 | manual | `45a6dfd5` | exit 1, 2927 s: 16,295 passed, 3 failed | exit 0, 1087 s: 265 passed | **red 1** (a W1-03 head-move case; fixture later fixed by W2-73) | 5189 s | none |
| 20261028-1011 | day (re-pin 2's ladder) | `5c40122014da` | exit 1, 3077 s: 16,478 passed, 1 failed | exit 0, 1378 s: 180 passed | **flaky-candidates 1** (W2-54 time-limit passed alone) | 5707 s (setup 942) | none |
| 20261029-0200 | night, first cron run | `8fa67ec8468a` | exit 0, 2927 s: 16,478 passed, 32 skipped | exit 0, 1187 s: 180 passed | **green** | 5623 s (setup 1509) | **5214 vs 5623 s (+7.8%)** |

**The one estimate (10-29):**

| Phase | Estimated | Actual | Difference |
|---|---|---|---|
| Parallel | 3041 s | 2927 s | −114 s |
| Serial | 757 s | 1187 s | +430 s |
| Setup | 942 s | 1509 s | +567 s |
| Total (1.1 margin) | 5214 s | 5623 s | +409 s |

The setup figure includes about 25 minutes of lock wait (P1-MORNING-2026-10-29 item 6; DEC-939 item 6 separates it).

## Where the data is incomplete

- **No wall times before the queue existed:** W2-01's and W2-53's earliest attempts (W2-01's is an upper bound from file times).
- **Two causes unrecorded:** the 10-22 13:56 gate stop (secrets indexing red) and the 10-21 08:22 queue run that ended after its rebuild line.
- **A record conflicts with its log:** `PKG/P-W2-53.md` §2 item 2 says the 10-19 10:44 attempt was a W1-30 r13 load refusal; its JSON (`close-DAEO-7rr2-2.json`) says STORE_STALE.
- **The 10-18 15:39 sweep** ran on a scratch merge with no archived repair ticket; totals are given with and without it.
- **The (a)–(d) classification** is the agent's reading; an auditor may dispute it.
- **W2-75's close** was still running at 13:00 on 10-29 and is not counted.
- **Older close records** lack an `evidence` block and are counted as full (they ran the serial phase and about 15,700 tests; DEC-925).
