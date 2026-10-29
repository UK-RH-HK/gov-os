# State of the Gov OS — Part A: capabilities and keystones (draft, 2026-10-29)

Research agent A's findings (read-only, `w2/integrate` at `2f2fb03e`), written down by the orchestrator. Hashes are given as 8 hex digits.

**Orchestrator's corrections:**
- Close wall times ARE recorded, in the queue logs (`log/close-queue-*/queue.txt`; see B-progress §2).
- W2-71's branch head is `1598a1c0` at run 1's DONE; `c9939587` is from run 2, which is in flight.

## 0. How to read this

**The pin:**
- Today gov is the wheel of `5c401220` (DEC-935; registry `bc37c419`; `governance/project/tool-registry.yaml` lines 229–236).
- Earlier pins: `6a4696eb` (DEC-922, registry `82f2d453`) and the bootstrap `fecb870c` (DEC-822, registry `70aea435`, 2026-10-19).
- Merged after the pin: W2-75 (`b52e3a96`, tests only) and W2-68 (`848f5ab3`).
- W2-71 is built on its branch and not merged; its run 2 is in flight (P1-MORNING-2026-10-29 item 4).

**Status words:**
- **built, pinned and proven:** in the pin, its tickets closed, its measure present where the Contract asks for one, and no open independent finding against its acceptance check;
- **built and merged but not pinned:** on `w2/integrate` after `5c401220`;
- **built and held:** built on a branch, not merged;
- **partial:** something due by the end of Wave 2 is missing, or an open finding says the acceptance check fails here;
- **not started.**

**Grades of "proven":**
- **W1 grade:** no Wave 1 ticket closed through a clean `gov close` (all 50 by `tk close`; `docs/audit/wave-1/W1-43-wave-1-exit-audit.md` lines 267 and 312, F-M3), and the Wave 1 exit verdict was FAIL (line 443). A W1-grade row rests on four things:
  - W1-43 rated it OK (table, lines 59–286);
  - no later finding contradicts it;
  - its code is in the pin;
  - its acceptance tests pass in Wave 2's clean closes' full regressions and in the nightly (for example `CL-DAEO-c1uz.md`: 16,555 passed, 1 accepted red; the 2026-10-29 nightly GREEN, 16,478 passed, 0 failed).
  
  This is weaker than the requested definition, and each such row is marked.
- **W2 grade:** exercised and evidenced by clean Wave 2 closes under a pin.

**Scope:** W1 and W2 capabilities are rated on the items due by the end of Wave 2, with their W3 items listed as remaining by plan; W3 capabilities are rated on everything.

**The Contract text:**
- `docs/contract/contract.yaml` is still version 4.1.
- Version 4.2 (lite CAP-43.b and CAP-44.h, and the re-baseline of nine W2 items; DEC-841; `docs/plan/WAVE_2_REVISED_PLAN.md` §8) rides W2-49, which is held (`19d45246`, 2026-10-17).
- "Moved to W3" therefore means moved by the accepted plan, not yet by the Contract text.

### 0.2 Wave 2 ticket ledger

**Clean `gov close` (exit 0) under a pin.** Close records are `docs/close/<id>/CL-<id>.md`.

| W2 | Ticket | Merge (in pin) | Close commit, time UTC | Tests |
|---|---|---|---|---|
| W2-53 | DAEO-7rr2 | `c9537e39` | `a1565e56`, 10-20 14:53 | 14,652 passed, 2 failed (accepted reds); 3,620 s |
| W2-02 | DAEO-zflj | `94ac7951` | `e52ad8a2`, 10-21 19:58 | 15,729 passed, 2 failed; 3,906 s |
| W2-54 | DAEO-0rfi | `6f7d4f9e` | `55162ea2`, 10-21 21:28 | 15,729 passed, 2 failed; 4,503 s |
| W2-62 | DAEO-juee | `6e4b2750`, `0e686111` | `d7daf01b`, 10-22 15:44 | 15,729 passed, 2 failed; 3,629 s |
| W2-50 | DAEO-kl5e | `2bf30b7c` | `01488b72`, 10-22 21:17 | 15,729 passed, 2 failed; 4,262 s |
| W2-70 | DAEO-uzme | `efdc4188`, `3ff8ba51` | `23c24700`, 10-27 17:12 | 16,555 passed, 1 failed; 3,320 s |
| W2-66 | DAEO-c1uz | `c60c9704` | `f8d1f60a`, 10-27 21:29 | 16,555 passed, 1 failed; 4,186 s |
| W2-72 | DAEO-ye2a | `4a57bf6b` | `6c439d8a`, 10-27 21:51 | 3,379 passed (scoped); 296 s |
| W2-59 | DAEO-kh9l | under `6a4696eb` | `f0f933e1`, 10-27 22:12 | 3,361 passed (scoped); 300 s |
| W2-65 | DAEO-e82f | `6a4696eb` | `be18d1c7`, 10-27 22:33 | 3,320 passed (scoped); 294 s |
| W2-73 | DAEO-qty6 | `214dc9d6` | `74c08ed8`, 10-27 22:55 | 3,669 passed (scoped); 314 s |
| W2-74 | DAEO-2azm | `6ee7b4d0` | `182823e4`, 10-27 23:16 | 3,367 passed (scoped); 306 s |
| W2-69 | DAEO-rmbe | `2d5a829a`, `4c4dd6d2` | `07a8d624`, 10-27 23:56 | 3,658 passed (scoped); 1,325 s |

**Closed, but not by a clean `gov close`:**
- W2-01 (DAEO-g0ip): merged `3022c2df`; `gov close` refused it with six findings, and the owner then closed it by decision DEC-757 (`.tickets/DAEO-g0ip.md` line 88; `f15ac648`).
- W2-48 (DAEO-xxgp): withdrawn by DEC-880, never merged (branch `2c3c46b5`).

**Merged into the pin, not closed:**
- W2-58 (`4845b9b8`): refused once (DEC-937, repair DAEO-pr0y).
- W2-63 (`50c08ae3`).
- W2-07 (`2a9d1a11`, `8555aafc`).
- W2-57 (`57e363c5`, `4904a60f`): re-probe run 4 in flight.
- W2-67 round 1 (`4da40b60`): the rest is held at `d0140d4d` with a stale probe.

A queue is closing W2-75, W2-63, W2-07 and W2-68 (CHECKPOINT line 3).

**Merged after the pin, not closed:** W2-75 (`b52e3a96`); W2-68 (`848f5ab3`, its batch off until W2-M406, P1-MORNING item 5 (b)).

**Built and held, not merged.** Each was last touched between 10-17 and 10-19, so 10 or more days behind `w2/integrate`, and each needs a merge-back and re-verification (`git log -1 w2/<id>`):
- W2-03 `9a3e3456`: "held for the close order";
- W2-05 `f19f156e`: review F1 and F2 fixed;
- W2-16 `1908149d`: review passed, its probe on the branch;
- W2-20 `1a54976c`: loop green;
- W2-37 `2ff873b2`: before its final probe; resume owed (DEC-812);
- W2-49 `19d45246`;
- W2-51 `c2c80e6c`: green, a counting fix owed;
- W2-52 `a21f06a7`: probe passed;
- W2-26 `62c4e477`: re-scoped (DEC-827);
- W2-71: run 2 in flight.

**No ticket file:** W2-55 (WBS line 892), W2-56 (line 903), W2-60 (no card; plan §4.3 only), W2-61 (line 986), W2-64 (line 997).

**Open, not started:** W2-04, 06, 08–14, 15a (DAEO-rd0g), 15b (DAEO-swdu), 17–19, 21–25, 27–30, 46 and 47. W2-31, 34–36, 38, 39, 41 and 44 moved to Wave 3 (plan §8). W2-33 stays in Wave 2, cut down (DEC-832).

## 1. Counts

| Status | Capabilities (62) | Keystones (9) | v4.2 lite (2) |
|---|---|---|---|
| built, pinned and proven | 25 (22 W1 grade; 3 W2 grade: CAP-24, 31, 38) | 0 | 0 |
| built and merged but not pinned | 0 | 0 | 0 |
| built and held | 0 | 0 | 1 (CAP-43.b) |
| partial | 29 | 9 | 1 (CAP-44.h) |
| not started | 6, plus 2 DROP (CAP-26, CAP-60) | 0 | 0 |

By DEC-878 item 2, the keystones are 0 done, 9 in progress and 0 ahead. The orchestrator last recorded 0 / 8 / 1 (`CHECKPOINT-ARCHIVE.md` line 4950, 10-24); the difference is how K8 and K9 are counted, whose only started tickets are ones held from before the re-plan.

## 2. Capability matrix

| Cap | Status | Evidence | What remains, why, waits on |
|---|---|---|---|
| CAP-01 Authority precedence | partial | W1-10/11/24/26 (tk). Audit WEAKENED: approvals transcribed (line 71, F-M6). Lens B F4: every register chunk carries the id DEC-812, so superseded DEC-049 is served at rank 4 and the filter fails open (`B-memory-retrieval.md` line 480; `SYNTHESIS.md` §6 row 4). | W2-03 (held `9a3e3456`), W2-55 (no ticket), W2-12 (open); waits on K4 order 1, K5 and the close order (DEC-806). |
| CAP-02 Release authenticity (lite) | built, pinned and proven (W1 grade) | W1-39, W1-27; audit OK; the wheel's sha256 was verified at re-pin 2 (DEC-935). | CAP-02.c (signed tags) is Wave 3 (WBS §1). |
| CAP-03 Security and sensitivity | partial | Audit OK; W2-69 closed (`07a8d624`). Lens B F7: held-out material is not excluded from indexing (B line 536; fails open). The `indexable` widening is in W2-58 (merged `4845b9b8`, not closed). W2-71 is held with its reviewer's F1, a token candidate sent to the remote in partial clones (P1-MORNING item 4). | W2-58's second close; W2-71's run 2 and merge (re-pin 3); held up by a review defect and a load timeout (DEC-937). |
| CAP-04 Budget (W2) | partial | W1 items (W1-31, W1-21); CAP-04.a and .d belong to W2-31 (open). | Deferred on purpose (plan §8 row 1; DEC-841); the Contract text changes only when W2-49 lands. |
| CAP-05 Emergency controls | built, pinned and proven (W1 grade) | W1-28, W1-02; audit OK. | — |
| CAP-06 Path map | partial | Audit WEAKENED for CAP-06.d (F-M2, line 93). Lens B F13: the map contradicts the adoption rule (line 630). Package P-IS-9 (`I-SYNTHESIS.md` line 767). | The P-IS-9 decision, then W2-23, W2-27. |
| CAP-07 Authoritative vs derived | built, pinned and proven (W1 grade) | W1-17/27/08; audit OK; the rebuild recreated every store (P1-MORNING item 2). | The 10-29 rebuild took 6 h 39 min for an unknown reason; W2-76 is drafted. |
| CAP-08 Structured records | partial | W1-10; W2-02 closed (`e52ad8a2`); lens B F4 as in CAP-01. | W2-03 (held), W2-64 (no ticket; lens G F2, fails open), W2-55. |
| CAP-09 Graph memory | built, pinned and proven (W1 grade) | W1-10, W1-20; audit OK. | — |
| CAP-10 Semantic memory | partial | Audit WEAKENED: hit@5 83.33 against 85. Lens B measures 65 % (SYNTHESIS §6 row 10). Tests hold 78 % of the vectors, the template none (B F6, line 520). DEC-833 sets the floor at 85 and the target at 99 %. No W2-61 measure and no EXP-003 result exist. CAP-10.b belongs to W2-32 (open). | W2-61 (no ticket), W2-15a, W2-32, W2-15b, in the K4 order (DEC-828/829; plan §4.4). |
| CAP-11 Lexical memory | built, pinned and proven (W1 grade) | W1-17; audit OK (exact string with file and line). | Ranked BM25 (W2-13, open) is AR-9 work; lens B F8 (line 556). |
| CAP-12 Code-structural memory | partial | W1-16; OK on the dev tiers. On this repository the query exceeds the 100k-row cap (117,373 edges), with the cause hidden (B F3, line 457). | W2-37's resume (DEC-812, DEC-859); held `2ff873b2`, stacked on W2-03. |
| CAP-13 Temporal and episodic memory | built, pinned and proven (W1 grade) | W1-10/30/25; audit OK. | — |
| CAP-14 Failure memory | built, pinned and proven (W1 grade) | W1-08/21/44; audit OK. | — |
| CAP-15 Context packet | partial | Audit WEAKENED: 814,821 tokens against a 6,000 ceiling, reported ok (F-M5, line 119). Lens B F1: 42 to 168 times the ceiling, ids only (line 413). W2-54 closed (`55162ea2`) but did not fix the ceiling. | W2-04 (open, after W2-03); P-IS-12 (`I-SYNTHESIS.md` line 825). |
| CAP-16 Multi-batch retrieval | built, pinned and proven (W1 grade) | W1-21/36; audit OK. Lens B F11: the budget is exceeded at radius 2–3, by decision (line 601). | — |
| CAP-17 Incremental indexing | partial | Audit WEAKENED for CAP-17.c (line 129). Lens B F2: any edit turns the index off, silently (line 436). CAP-17.b belongs to W2-06 (open). | W2-05 (held), then W2-06; hooks off (K8). |
| CAP-18 Retrieval router | built, pinned and proven (W1 grade) | W1-17/19/21; audit OK. | Lens B F9: the reranker lowers MRR 0.45 → 0.40 (line 570); W2-15a decides whether it stays. Thin. |
| CAP-19 Component separation (W2) | not started | No W1 items; CAP-19.a and .c belong to W2-32 (open). | The chain W2-03 → W2-13 → W2-15a → W2-32. |
| CAP-20 Rebuild guarantee | partial | Audit OK. Lens B F12: the digest covers only the record store, and 14 of 32 vectors are bit-identical (line 616). | W2-04's KPI (open); SYNTHESIS §6 row 13. |
| CAP-21 Owner approval facts | partial | Audit WEAKENED for CAP-21.a (F-M6, line 136); owner decisions are still committed with `Role: orchestrator` (DEC-935 status line). | W2-12 (`gov approve`) open; `main.py` lines 94–105 have no such command; depends on W2-03. |
| CAP-22 Roles and handoffs (W2) | partial | W1 items a and d (W1-33, 05, 46). Lens E F2: no role rules are loaded at launch (`E-roles-context.md` line 562). Items b and c move to Wave 3 (plan §8 row 2). | W2-60 (no card, no ticket), W2-11 (open). |
| CAP-23 Concurrency (W3) | partial | W1 items a and c (W1-09, W1-42); DEC-847. | CAP-23.b is Wave 3. |
| CAP-24 Skill lifecycle | built, pinned and proven (W2 grade) | W1-35/36/37; close records list skill versions (`CL-DAEO-c1uz.md` line 605). | Lens E F15: the skill text sessions load is unversioned (line 856); W2-11. |
| CAP-25 Tool registry (lite) | partial | Audit WEAKENED for CAP-25.a (F-M2, line 146). Lens D F7: doctor misses an editable gov (`D-tool-staging.md` line 522). | W2-22 (open), in K8. |
| CAP-26 Plugin trust | not started (DROP) | DROP. | — |
| CAP-27 Read/act separation | built, pinned and proven (W1 grade) | W1-07/32; audit OK; `main.py` lines 94–105. | — |
| CAP-28 Intent routing | built, pinned and proven (W1 grade) | W1-07/32/35/42; audit OK. | — |
| CAP-29 Spec lineage (W3) | not started | Items a and b are Wave 3. | Wave 3. |
| CAP-30 Readiness (W2) | partial | Four W1 items; .c (W2-34) and .g (W2-35) move to Wave 3 (plan §8). | Deferred (DEC-841). |
| CAP-31 Task DAG | built, pinned and proven (W2 grade) | A failed close under the pin created repair ticket DAEO-pr0y (P1-MORNING item 3; DEC-937); W2-07 merged, not closed. | W2-07's close (queued). |
| CAP-32 Research lifecycle (W3) | partial | W1 item (W1-35); DEC-827; .d moves to Wave 3. | Wave 3. |
| CAP-33 Change impact (W2) | partial | Four W1 items in use (`docs/changes/W2-58-CIT-E.md`). .b and .g belong to W2-37 (held, 12 acceptance files); no `impact` command. | W2-37's resume (DEC-812/859), probe, merge, close. |
| CAP-34 Decision gates | built, pinned and proven (W1 grade) | W1-34/35/09/11; audit OK; in daily use. | — |
| CAP-35 Model routing (W3) | not started | Lite item .c pulled into W2-60, W2-11 and W2-21 (plan §2); nothing merged; model and effort set by hand (plan §6). | W2-60 (no ticket). |
| CAP-36 Telemetry per model (W3) | not started | Lite item .a pulled into W2-60 and W2-07 (plan §2); not built. | W2-60. |
| CAP-37 Checkpoints and resume | partial | Audit OK; W2-62 closed (`d7daf01b`). Lens B F5 (line 500) and lens E F11 (line 775): the next step is lost after a compaction, and sessions share one checkpoint series. .e moves to Wave 3. | W2-10 (open, after W2-09), in K4 order 4. |
| CAP-38 Test families | built, pinned and proven (W2 grade) | `gov check` gives 15 GREEN and 2 known YELLOW (DEC-935); acceptance tests run separately in every close's `test_runs`. W2-53, 59 and 65 closed; W2-66 caught 32 of 32 planted faults (`docs/research/W2-66-scoped-close.md` line 39). | W2-07, 57 and 68 not closed; W2-45 open. |
| CAP-39 Health scheduler (W3) | partial | W1 items a and d. Audit WEAKENED for CAP-39.a (F-M4, line 191). No git hooks are installed and CI cannot pass (lens D F6, line 493; DEC-830). One scheduled nightly, GREEN on 10-29 (DEC-936). | The K8 tickets (W2-05, 06, 08, 43, 22, 45); hooks off on purpose (WBS §0 rule 4). |
| CAP-40 Telemetry | partial | Audit WEAKENED for CAP-40.c (F-M1, line 195); all 13 close records say the governance share is not measured. | W2-07 (not closed), W2-14 (open). |
| CAP-41 Lessons | built, pinned and proven (W1 grade) | W1-08/21/44; audit OK. | Items g–j are Wave 3. |
| CAP-42 Legacy retirement | built, pinned and proven (W1 grade) | W1-41; audit OK. | — |
| CAP-43 Releases | built, pinned and proven (W1 grade) | W1-39; .a audit OK. | .b (lite) is row v4.2-a; no release tag after `wave-1-exit`. |
| CAP-44 init/adopt (W3) | partial | W1 items a–e and j (W1-39, W1-41; audit line 211). | f–i are Wave 3; lite .h is row v4.2-b. |
| CAP-45 gov update (W2) | not started | No `update` command; W2-17 open, depends on W2-16. | W2-16's close, the first release (DEC-772), W2-17. |
| CAP-46 Cross-machine sync | built, pinned and proven (W1 grade) | W1-27; audit OK. | — |
| CAP-47 Independent roles (W3) | partial | W1 items (W1-33, W1-43). | a and c are Wave 3; W2-28 and W2-30 cover the lite part (plan §2). |
| CAP-48 Health SLOs (W3) | not started | No `health` command. | Wave 3. |
| CAP-49 Qualification (W3) | partial | W1 items (W1-46, 47); not examined (held-out material is out of bounds). | .a is Wave 3. |
| CAP-50 Traceability (W3) | partial | Two W1 items (W1-10, 30). | b and d–g are Wave 3. |
| CAP-51 Decisions register | built, pinned and proven (W1 grade) | W1-11/21; audit OK; register v0.320. | W2-03 (held); lens C's S-2 figure not re-measured (SYNTHESIS §1). Thin. |
| CAP-52 Adapters | built, pinned and proven (W1 grade) | W1-38; DEC-922 (`8ba8b231`); W2-74 closed. | — |
| CAP-53 Profiles (W2) | partial | W1 items; .b moves to Wave 3. Its lite form W2-66 closed (`f8d1f60a`), cutting a close's tests from 60 min to 11.5 min (`W2-66-scoped-close.md` lines 31–45). | Deferred (plan §8; DEC-880). |
| CAP-54 Progressive adoption | built, pinned and proven (W1 grade) | W1-39/41/27/08; audit OK. | Shown on the dev tiers only; no product adopted. |
| CAP-55 Stopping reasons | built, pinned and proven (W1 grade) | W1-21/22; audit OK; lens B finds the facets honest. | — |
| CAP-56 Subagent retrieval | partial | Audit WEAKENED: CAP-56.a's acceptance check is untested. | A transcript test; no ticket names it (unplanned). |
| CAP-57 Worklist closure | built, pinned and proven (W1 grade) | W1-20/22; audit OK. | — |
| CAP-58 Path guards | partial | Audit WEAKENED for CAP-58.c (F-M7, line 243). W2-50 (`01488b72`), W2-65 (`be18d1c7`) and W2-72 (`6c439d8a`) closed; W2-58 in the pin, not closed (DEC-937). | W2-58's second close; W2-09, W2-42 (open). |
| CAP-59 Loop budget | partial | Audit WEAKENED: the W1-43 part is untested, and there is no `tests/acceptance/W1-43` (F-M10, lines 249–250). | W2-47, last by design. |
| CAP-60 Break-glass | not started (DROP) | DROP. | — |
| CAP-61 Launcher and sandbox | partial | W1 items OK; workers run sandboxed (DEC-799); leads run unsandboxed (lens E F1, line 539). .f belongs to W2-40 (open). | W2-56 (no ticket), W2-21, W2-40, in K6. |
| CAP-62 Escape hatch denied | built, pinned and proven (W1 grade) | W1-47; audit OK. | — |

### 2.1 The lite rows Contract v4.2 adds

| Row | Status | Evidence | Remains |
|---|---|---|---|
| v4.2-a CAP-43.b lite | built and held | W2-16 at `1908149d` (30 commits, 5 acceptance files, `PR-DAEO-49o5-last-round.md`); until it lands, re-pins are done by hand (DEC-822, 922, 935). | W2-49's merge (W2-16 is stacked on it, DEC-752), a merge-back, the close, the owner's first release (DEC-772). |
| v4.2-b CAP-44.h lite | partial | W2-02's verdict type closed; W2-52 held (`a21f06a7`, probe passed); W2-49 held; W2-27 to 30 open. | The K9 chain, after K4 (DEC-828). |

## 3. Keystones (DEC-829 item 2, plan §3, the WBS keystone labels)

| K | Status | Evidence | Remains, why |
|---|---|---|---|
| 1 Pinned judge | partial (closest to done) | Pins at `70aea435`, `6a4696eb` (DEC-922) and `5c401220` (DEC-935). W2-59 and W2-65 closed; W2-07 (WBS line 279) in the pin, not closed. | W2-07's close (queued). |
| 2 Close queue | partial | Full closes 3,320–4,503 test-s; scoped 294–1,325 test-s; eight clean closes on 10-27. Closed: W2-66, 69, 53, 54, 02, 50; W2-48 withdrawn (DEC-880); W2-57 merged, not closed; W2-68 merged after the pin, batch off (W2-M406); W2-67 round 1 only. Close success 5/18 at 10-24 (archive line 4950), 8/8 on 10-27; W2-58 refused once on 10-28. | Nine stale held closes; the closes of W2-57, 67 and 68; W2-77 (draft). Slowed by the one-close-at-a-time rule and DEC-896; the DEC-834 recalibration is owed. |
| 3 Agents know what to do | partial | Policies 1 and 2, CLAUDE.md and ADR-0001 in (plan §4.3); W2-62 closed; W2-58 refused once and queued again; W2-63 queued. | W2-60 (no card, no ticket), W2-11, W2-09, W2-33. |
| 4 Memory | partial (mostly not started) | W2-02 and W2-54 closed; W2-03, 05 and 37 held. The only memory measure is lens B's: 13/20 in the first five, 17/20 in the bundle, 20/20 on repeat, 11/20 after a rebuild (SYNTHESIS §6 row 9). No measure of DEC-836's usage found. | W2-55, 64 and 61 (no tickets); W2-04, 06, 10, 13, 15a, 32. Held back by the DEC-829 order and the K2 delays; the DEC-930 re-plan is owed. |
| 5 Decision pipeline | partial | W2-49 held; DEC-842. | W2-55, W2-49's close (after W2-51), W2-12. |
| 6 Sandbox per role | partial | W2-20 held; W2-50 closed; the disk gate is a hand rule (DEC-898). | W2-56, 21, 42, 40; leads unsandboxed (lens E F1). |
| 7 Releases | partial | W2-16 held; three hand re-pins; no release cut. | W2-49 → W2-16's close, the release (DEC-772), W2-18, W2-17. |
| 8 Hooks and CI | partial (only W2-05 started) | Hooks off since 10-16 (F-M13); CI cannot pass (lens D F6); W2-05 held. | W2-05, W2-06, the lefthook measure, W2-08, 43, 22, 45; after W2-06 by design (plan §4.8). |
| 9 Gate run, then EXAMIN | partial (in name only) | Only W2-26 and W2-52 started, both held; the rest open; no product governed yet. | Everything; last by design (DEC-828). |

## 4. The five biggest gaps (agent A)

1. **Memory is not proven and has no measure.** No W2-61 measure and no EXP-003 result. The context packet is 42–168 times over its ceiling, any edit switches the index off, and the superseded-decision filter fails open. W2-55, W2-61 and W2-64 have no tickets.
2. **Nine held tickets are 10 or more days stale.** K4 and K5 wait on them, and so do parts of K6–K8.
3. **ADR-0001's hard boundary is off.** No git hooks are installed and CI cannot pass (K8).
4. **The governance share is unmeasured** in all 13 Wave 2 close records (CAP-40; F-M1).
5. **Leads run unsandboxed and roles are not loaded at launch.** W2-60 has no card or ticket; W2-56 has no ticket (CAP-61, CAP-22).

## 5. Where the evidence is thin

- 22 W1-grade proofs rest on `tk close` and a Wave 1 audit with a FAIL verdict.
- CAP-05, 09, 13, 14, 27, 28, 42, 46, 57 and 62 have had no independent look since 10-16.
- One scheduled nightly.
- No held branch has been re-verified against today's head.
- CAP-49 was not examined (held-out rule); CAP-51's lens C figure has not been re-measured.
