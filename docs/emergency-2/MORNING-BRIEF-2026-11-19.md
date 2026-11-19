# Morning brief, 2026-11-19 (the Gov OS CTO)

`docs/emergency-2/MORNING-BRIEF-2026-11-19.md` · the night of 18 to 19 November · written from 06:05, completed at 13:17

**Not delivered at 08:00.** The plan stood at 100 % from 05:47, and this session was stopped by the limit from 07:02 until the owner's message at 13:09. The page was finished then; the figures below are the night's, and the status block is counted at 13:17.

**In one line.** All six of your priorities are landed, eight tickets closed, and the register is archived. The base is
not green yet: the full suite of 05:18 gave 18,610 passed, 9 failed and 94 skipped. Two of the nine wait for your answer G1-X; the other seven are being fixed.

**Needs you first:** the plan read 100 % at 05:57 and is not reset (pushed 05:15, 05:41, 05:59). It still read 100 % (Fable 30 %) at 13:09.

---

## 1. What landed overnight

Every landing was merged, then checked on the merged tree through the slot, then closed. `gov accept` is each ticket's own acceptance run.

| Your priority | Ticket | What it is | Merged | `gov accept` on the merged tree | State |
|---|---|---|---|---|---|
| 1 | W2-199 | Run-time tool, slice 2: load admission in the product, slots and workers from the machine, GPU admission | 02:09 | 75 of 75 | closed |
| 1 | W2-205 | Run-time tool, slice 3: every end messaged, the Stop check, relaunch (off), resume after a compaction | 03:38 | 38 of 38 | closed |
| 1, 4 | W2-201 | The rubric in code (K1) and audit 09's usage rules: role files, criticality list, launcher and helper rule | 02:15 | 240 of 240 | closed |
| 2 | (fixes) | W2-130's marks case; the two flaky W2-94 reds (a race in the launcher's tree build); W2-61h's notice | 23:35, 00:44, 01:29 | n/a | landed |
| 3 | W2-200 | M1: `gov context`, its module and its check retired; the close records the decisions a ticket cites | 05:59 | 57 of 57 | closed |
| 5 | G1, G2 | 184 retired files out of the tree, kept on `archive/pre-emergency-2`; `record/w2`'s worktree removed | 00:34 | n/a | landed |
| 5 | G4 | Audit 8's class on every register entry (155 kept, 183 superseded, 34 retired, 834 history) | 23:27 | n/a | landed |
| 5 | W2-203 | The old register archived and out of memory's index; the kept register (161 entries) in force | 03:58 | 61 of 61 | closed |
| 5 | G5 | Charter v6 and Contract v5, on branch `e2/g4-g5` | not merged | n/a | waits for your yes by group |
| 6 | W2-202 | L2's A1, A3, A4, A5: base reds recorded, acceptance at the landing, hand-merged branches, the pause | 02:01 | 39 of 39 | closed |
| 6 | W2-206 | L2's A6, A8: `gov queue --dry-run`, `--select`, `--full`; the after-landing rebuild and check | 04:21 | 45 of 45 | closed |
| new | W2-204 | The memory measure on any adopted repository (EXAMIN's release-blocking finding) | 05:17 | 169 of 169 | closed |

Also done: the T2 proposal page; the install rule (G7) in the tool registry; DEC-1216 (your night orders and the reporting rule); a `gov doctor` fix.

## 2. The green base and the full suite

- **First full suite** (23:05 to 00:28, on the tree before the batch): 18,233 passed, 2 failed, 112 skipped. Both failures passed alone; the cause was a race in the question-set launcher, fixed and landed at 00:44.
- **Second full suite** (from 05:17, on the integration branch without W2-200 and W2-204, which landed after it started), 3 workers, 103 minutes: **18,610 passed, 9 failed, 94 skipped**. The nine: the two W1-01 cases below; five cases in W2-13, W2-61, W2-86 and W2-158 that still assert the state before the register's exit and the landing's after-step (a test designer is revising them); one Stop-hook case from slice 3 (fixed, `1fcaac1c8`); one W2-76 watchdog case that passes alone (cause not found yet).
- **Known reds on the base now:** two W1-01 test-authorship cases, since the G1 landing. They need your exemption (G1-X below); nothing else clears them.
- **Not yet in any full suite:** W2-200 and W2-204. Each passed its own folders on the merged tree. A third full suite follows your G1-X answer.
- **The green-base record** is not committed, and Gov OS's own landing is not moved onto `gov queue` (L2-4 waits for your yes and a green base).

## 3. The build list, item by item

| Item | State | Next |
|---|---|---|
| The run-time tool (EMERGENCY-2 §6.3) | slices 1 to 3 landed; the live dispatcher and slot are still the scratch ones | slice 4, the cut-over (W2-207): today, by day; relaunch on after one day |
| The usage rules in code (audit 09) | done (W2-201) | one fix owed: a role promoted to Opus is not substituted under DEC-1215 |
| The rubric in code (K1) | done (W2-201) | K1-1 below |
| `gov context` retired (M1) | done (W2-200) | leftover mentions and the kernel's `context` policy key |
| The landing and the close as one action (L2) | A1, A3, A4, A5, A6, A8 done | A2 (one close record) can start now; A7 and the B items wait for L2-1 to L2-6 |
| Retired history out of the tree (G1, G2) | done | G1-2 below |
| The register (G4, §11.3) | done (classes, archive, kept register) | strip 271 lines of old version tables from 43 kept entries |
| Charter v6 and Contract v5 (G5) | written, on its branch | your yes by group; then 11 tests retired or rewritten by a test designer |
| Installs (G7), release authenticity (L3) | G7 done; L3 is in Contract v5 | — |
| The escalation rubric and pushes (T2) | proposal written | T2-1 to T2-3; then the kernel text |
| Memory's index cleaned | done with W2-203 (main store rebuilt; a search returns nothing from the archive) | — |
| The first fresh 80 on Gov OS | not started; the measure's two faults are fixed (W2-204) | after a green base: about 6 to 9 hours |
| The proving run on the synthetic repositories (W2-81) | not started | after the release candidate |
| The 43 GB beside the repository (G3) | later, as you decided | — |
| Release acceptance (§8.2) | 1: waits for G5. 2: the proving run. 3: EXAMIN's fresh 80, waits for release 0.1.4. 4: one EXAMIN feature ticket, after 3 | R-1 below |

W2-00, W2-15b, W2-46, W2-47 and W2-82 were closed on their records at 13:10, at your word (retired, replaced or folded by EMERGENCY-2 §6.2).

## 4. EXAMIN's Wave 0, in two lines

- Step 5 is done and green by test id on every group (0 new reds in six runs); the records are in the graph, memory is rebuilt on the refactored tree, and 22 as-built specs are written. This is its CTO's report of 03:35, which I have not re-measured.
- Its memory measure is blocked on W2-204, landed here at 05:17; it reaches EXAMIN only through a release and `gov update` (R-1).

## 5. Usage and the machine

- **Plan:** 78 % at 23:04; 99 % at 02:04 (pushed 02:05); your first Fable reset at 02:06 took it to 84 %; 99 % again at 05:14; 100 % from 05:47. Still 100 % at 13:09.
- **Lead sessions' own reported cost:** $334 for the eleven leads (the largest: M1 $69, the memory measure $65, L2's first build $49). By model: Fable $227, Opus $58, Sonnet $49. The two CTO sessions are estimated at about $160 (this one) and $123 (EXAMIN's, Fable part) from their token counts.
- **Peak load:** 35.8 at 23:49, against the gate of 20. 18 of 403 one-minute samples since 23:00 were over 20, in four windows: 23:40, 23:44 to 23:49, 23:58 to 00:03, 02:46 to 02:51. Memory never fell below 11 GB available.
- **Cause:** secret-scan tests start one gitleaks process per CPU they may use. **Now:** each test slot has 4 CPUs and 2 workers, runs start only under load 10, and the full suite runs on 3 workers confined to 6 CPUs.

## 6. What went wrong

1. **Load over the gate, four times** (above). The first two peaks were the first full suite on 20 CPUs.
2. **I killed the fresh EXAMIN CTO** at 23:40 with a tmux command that matched its name by prefix. Resumed from its transcript within a minute; nothing lost.
3. **I merged G1 without checking who changed acceptance tests.** Its commit deleted a retired acceptance folder under the lead's role, so two W1-01 cases are red until you exempt it (G1-X). I check every branch for this before merging now.
4. **The common lead brief said test runs use the slot's workers without `-n`.** They did not: every run was one process until 01:30, so runs queued while the load sat at 3 to 5.
5. **The resource gate shut on inodes twice** (01:42 and 04:59): leftover pytest folders, then 1,050 per-run temp folders. Both cleared; runs now remove their temp folder.
6. **W2-201's helper rule would have refused the leads' Fable helpers** for two minutes after it merged (their tickets were on their branches). Fixed, test first.
7. **M1 clashed with the register's exit:** its close refused any ticket citing an archived decision. I held it on a landing branch, fixed it, and changed one of its rules: an unknown decision id is recorded, never refused.
8. **The usage logger slept an hour at 94 %**, so the ten-minute readings started late; I restarted it at 96 %.

Fixes still owed, none needing you: tests that leave read-only folders behind; one test that writes to the live CTO inbox; two test folders that clash when run in one command; `gov doctor` unhealthy on five checks; EXAMIN's four smaller requests.

## 7. Decisions waiting on you

Answer by code. The L2 table first, as you asked.

### L2, the command table (`docs/emergency-2/L2-COMMANDS.md`): 37 `gov` commands become 34

| Code | Question | Options | Recommendation |
|---|---|---|---|
| L2-1 | `gov close` merges into `gov queue`; the strict close retires | yes / no | **yes** |
| L2-2 | The path map's `accepted_reds` and `load_sensitive` lists retire (the landing records base reds itself) | yes / no | **yes** |
| L2-3 | Must a lead run the landing's selected tests before returning a ticket? | (a) no, `gov accept` only; (b) yes, as today | **(a)** |
| L2-4 | Gov OS's own landing moves onto `gov queue` after one green proving landing; the scratch landing tools retire | yes / no / keep `merge_queue.py` for now | **yes**, once the base is green |
| L2-5 | The name of the one action | keep `gov queue` / rename `gov land` | **keep** |
| L2-6 | Direct commits (chores) checked how? | (a) `gov queue --direct` after the fact, a notice; (b) through the queue first; (c) no check | **(a)** |

### The rest

| Code | Question | Options | Recommendation |
|---|---|---|---|
| G1-X | Exempt G1's commit `2c31268e4` from the test-authorship rule (it deleted the retired `tests/acceptance/W2-148` under the lead's role). Only your entry in the path map's list clears the two W1-01 reds | yes / no | **yes**: it is the deletion you decided in G1; the same was done for W2-84's cases (DEC-1123 (3)) |
| R-1 | Cut release 0.1.4 and re-pin, so EXAMIN gets the memory-measure commands by `gov update` | (a) as soon as the full suite is green; (b) wait for A2 and the cut-over too | **(a)** |
| G5-0 to G5-13 | Charter v6 and Contract v5, by group (`docs/emergency-2/G5-APPROVAL.md` on branch `e2/g4-g5`) | yes or no per group, or "G5 all yes" | **all yes**; worth a look: G5-4 (two rounds; a path outside a ticket's allowed paths is a notice, never a refusal) and G5-10 (seven new capabilities that need tickets) |
| G5-0 | File names for the two documents | (a) new names `CONTRACT_v5.md`, `CHARTER_v6.md`; (b) keep the old names, bump the version | **(a)**; (b) leaves four tests green that (a) turns red |
| G4 | Four rows the lead classed differently from audit 8: DEC-109 to history; DEC-409, DEC-1149, DEC-089 to kept | confirm / change | **confirm** |
| T2-1 | The rewritten escalation rubric replaces DEC-957's (`docs/emergency-2/T2-ESCALATION-RUBRIC.md`) | yes / no / yes with changes | **yes** |
| T2-2 | A decision that stops work, at night | (a) it waits for the morning brief; (b) it pushes at any hour | **(a)** |
| T2-3 | A decision that stops nothing | (a) the morning brief only; (b) a push as well | **(a)** |
| G1-2 | Also remove the P-* decision packages and the October assessment (27 % of memory's embedded chunks; history, not retired code) | yes / no | **yes**, before the first fresh 80, with the tests that read them revised in the same change |
| K1-1 | The senior engineer's model | Opus (audit 4's Table 3) / Sonnet (as every lead) | **Opus** until one runs |

Answer form: "L2-1 yes, L2-2 yes, L2-3 a, L2-4 yes, L2-5 keep, L2-6 a, G1-X yes, R-1 a, G5 all yes, G5-0 a, G4 confirm, T2-1 yes, T2-2 a, T2-3 a, G1-2 yes, K1-1 Opus".

## 8. Status block

- Progress: 199 closed / 0 merged, not closed / 1 in flight / 1 not started, of 201. In flight: W2-81. Not started: W2-207. Out of the count: 3 moved to Wave 3, 6 to EXAMIN's Wave 0.
- Leads running: 0 (none).
- Closes since the last report (11-19 06:56): 5 ticket(s) closed (W2-82, W2-47, W2-46, W2-00, W2-15b); 0 branch(es) merged.
- Reopened: none.
- New tickets: none on the integration branch.
- Waiting on me: 8: NOW: reset the plan, your second Fable reset (100 % at 05:57; pushed 05:15, 05:41 and 05:59); L2-1 to L2-6, the command table (docs/emergency-2/L2-COMMANDS.md): morning; G5-0 to G5-13, Charter v6 and Contract v5 by group (G5-APPROVAL.md on branch e2/g4-g5): morning; T2-1 to T2-3, the escalation rubric (docs/emergency-2/T2-ESCALATION-RUBRIC.md): morning; G1-2, also git rm the P-* decision packages and the October assessment (27 % of memory's embedded chunks; history, not retired code), from the G1 lead: morning; G1-X, W1-01's two test-authorship cases are red since the G1 landing: G1's commit 2c31268e4 deleted the retired tests/acceptance/W2-148 folder with Role: orchestrator, not the test designer's; the exemption list takes only the owner's entry (as DEC-1123 (3) did for W2-84's cases): exempt it yes / no: morning; K1-1, the senior engineer's model: Opus as audit 4's Table 3 has it (set so, none runs today) or Sonnet as 'every lead' (DEC-1212 (3)); recommended Opus until one runs: morning; R-1, cut release 0.1.4 and re-pin once the full suite is green: EXAMIN gets the memory-measure commands (W2-204) only through a release and gov update, and its fresh 80 is item 3 of the release acceptance: morning.
