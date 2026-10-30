---
id: DAEO-cy5o
status: in_progress
deps: []
links: []
created: 2026-10-23T09:08:45Z
type: task
priority: 1
assignee: engineer
external-ref: W2-57
tags: [wave-2, close, load, serial, full]
wbs_id: W2-57
title: 'Load out of the close: the rulesync probe, the serial-only list, and a route out for every list entry'
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on: []
allowed_paths:
- src/gov/adapters/portability.py
- src/gov/doctor/command.py
- src/gov/close/serial.py
- src/gov/close/command.py
- tests/unit/close/test_serial*
- tests/unit/adapters/test_portability*
- docs/changes/W2-57-CIT-E.md
kpis:
  success:
  - 'First item, the rulesync probe, with its four effects (DEC-892 item 2, P-I4-5 (a)): the portability check''s two rulesync calls get a limit a loaded machine meets, measured under the close''s parallel load; W1-38''s session fixture fails, never skips, when rulesync times out (a timeout is not "not installed"); the 9 cases whose "not green" assertion a timeout satisfies assert the reason; W1-33''s research case fails, not skips, the same way. Three closes'' worth of parallel runs show 0 rulesync skips and 0 timeouts [I4 F2, DEC-871, DEC-892]'
  - 'The doctor probes (src/gov/doctor/command.py, the probes only) get limits a loaded machine meets, and a probe exception gov doctor does not catch fails with its failure text kept, so W1-07 [doctor]''s cause shows if it recurs [I4 F5, I2 F12]'
  - 'The serial-only list is reworked as the two tables of P-IS-6 (I-SYNTHESIS): every entry kept serial names its reason in the list; W1-16''s 94 cases that start no daemon, W1-09''s two race cases (after one green nightly in parallel) and W1-50''s read-merge latency case run in parallel; the live and real-model files (W1-46, W1-50''s two freeze cases, W1-19''s real-model file, W1-21''s dev-tier file and family check, W1-49''s and W1-25''s live files, W2-58''s five launched sessions, W2-62''s live resume, W2-54''s sandboxed worker and real embedder) leave the close for the nightly, as DEC-889 item 5 orders; true latency cases stay alone [DEC-883 item 5, DEC-889 item 5, I1 F-2, I3 F6, F7, I4 §4.2]'
  - 'W1-30''s r11 test, which holds today''s serial entries one by one, is revised to read the reworked list and its reasons (Rewrite-Reason: DEC-889 item 5) [I2 F9]'
  - 'W1-30''s r13 case gets a limit a loaded start meets (Rewrite-Reason: W2-M384) [I2 §2.2]; W1-50''s two live freeze cases remove every CLAUDE* variable, as DEC-784 requires [I1 F-7]; one p95 case covers a test designer''s read [I1 F-10]; W2-M332 times W1-19''s queries without its memory sampler in the same process [I3 O3 (b)]'
  - 'The close''s resource gate covers the wall-clock limits that went red under load: W1-02''s 5-second bound (168 cases), by a limit a loaded machine meets or by running them alone; the guard''s 20-second deadline is left to the resource gate (W2-20) and the quiet window, with no new serial entries (owner, DEC-925 item 3, P-W2-57-B B2 (b)) [I1 F-14]'
  - 'Run 2 (owner, DEC-925 item 3, P-W2-57-B B1 (a)): the close''s serial phase in src/gov/close/command.py (its call to serial.py only; gate (h)''s line is W2-07''s round 2) takes only the entries not routed to the nightly, so a nightly: entry is collected and left out of both phases [DEC-889 item 5, DEC-925]'
  - 'The network check probes the live tests'' hosts through the route the session uses, close to when it runs [I1 F-1]'
  - 'Then the orchestrator commits the removal of every load_sensitive entry this ticket makes unnecessary (DEC-861: a removal only shrinks the list): W1-38''s three, W1-07 [doctor], W1-30''s r13, the unit close follow-up (not reproducible in 6 runs), and W1-46''s 23 and W1-19''s warm p95 once their files run in the nightly. W1-02''s and W1-05''s p95 entries are already removed by the owner''s commit (DEC-899 item 3): their cases stay alone in the serial phase, and W2-M332 keeps its date before W2-24 [DEC-766, DEC-813, DEC-899]'
  failure:
  - A rulesync or doctor timeout that skips or passes a case; a serial entry without its reason; a live or real-model file left in the close; a case weakened, skipped or serialised by marker alone to pass; a list entry added (only the owner adds, DEC-862).
profile: FULL
sources:
- DEC-813
- DEC-823
- DEC-871
- DEC-883
- DEC-889
- DEC-890
- DEC-892
- DEC-784
est_loc: 250
acceptance_tests:
  path: tests/acceptance/W2-57/
  author: independent-test-designer (MR-3); written before implementation
track: A
list_rows: [W2-M364, W2-M384, W2-M332, W2-L352, W2-L409, W2-L415]
---
# W2-57 Load out of the close: the rulesync probe, the serial-only list, and a route out for every list entry

Card: `docs/plan/WAVE_2_WBS.md` §2 (W2-57). Sources: DEC-813, DEC-823, DEC-883 item 5, DEC-889 item 5, DEC-890 item 2, DEC-892 item 2, and lens I's P-IS-6 (I-SYNTHESIS, which merges P-I2-1 B and C, P-I4-5, P-I1-8 and I3 O3).

- **Why:**
  - The serial phase takes about 31 minutes of every close.
  - Most refused closes since 2026-10-20 came from cases on the two lists, or from load-caused reds.
  - The rulesync probe's timeout silently skips up to 181 W1-38 cases, and the close still passes. That is a live fail-open (I4 F2).
  - The card of DEC-813 asked W1-46's live cases to pass under the close's parallel load. That is replaced: DEC-889 item 5 moves live and real-model tests to the nightly (I2 F14).
- **Starts** in a free slot after the review point, the rulesync probe first. It **closes** before W2-24 starts (DEC-813).
- **Paths widened (I2 F12):** the old card's paths could not reach four of its entries (W1-38 ×3 and W1-07's `[doctor]`), nor the list it must change.
- **Until it lands (the orchestrator's interim guard, no product change):** the close queue checks that a close's skip count equals the expected 31, so a silent rulesync skip stops the queue (P-IS-6, from I4 F2).
- **Route out for every entry:** P-IS-6's second table. The two `accepted_reds` are W1-42's, not this ticket's (P-IS-8).
- **The 28 entries that name list rows** rather than a ticket are outside W2-19's check. Their removal rests on the orchestrator's commit, on the dates DEC-890 gives rows (P-IS-6, the W2-57 block).
- **The test designer's files (MR-3: named here, never in the implementer's `allowed_paths`; DEC-899):** `tests/acceptance/serial-only.txt`, `tests/acceptance/W1-30/test_w1_30_r11_declared_here.py`, `tests/acceptance/W1-30/test_w1_30_r13_probe_findings.py`, `tests/acceptance/W1-38/**`, `tests/acceptance/W1-33/w1_33_support.py`, `tests/acceptance/W1-07/**`, `tests/acceptance/W1-46/**`, `tests/acceptance/W1-50/**`, `tests/acceptance/W1-02/**`, `tests/acceptance/W2-57/**`; and for run 2 (DEC-925 item 3, delegated: P-W2-57-B B3 (a) and R2) `tests/acceptance/W1-19/test_w1_19_real_models.py` (W2-M332: the query times taken without the memory sampler) and `tests/acceptance/W1-30/test_w1_30_r15_policy_pairs.py` (its rulesync case must not accept a timeout as its red after the fault). Each change carries a `Rewrite-Reason:`; no expectation is lowered.
