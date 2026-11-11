---
id: DAEO-emq1
status: open
deps: [DAEO-arrl]
links: []
created: 2026-10-31T23:52:57Z
type: task
priority: 1
assignee: engineer
external-ref: W2-115
tags: [wave-2, implementation, close, full, smart-work]
wbs_id: W2-115
title: 'gov close, the smart close: scoped runs only, a close refused only by a red its own change caused, the culprit of a batch sent back, no lists, a close record, the nightly''s full secrets scan; the strict close kept built (SMART-WORK-1)'
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on:
- DAEO-arrl
allowed_paths:
- src/gov/close/command.py
- src/gov/close/select.py
- src/gov/close/batch.py
- src/gov/close/nightly.py
- src/gov/close/tool.py
- src/gov/close/attribution.py
- template/governance/project/test-map.yaml
- tests/unit/close/test_w2_115*
- docs/research/W2-115-smart-close.md
- src/gov/close/traceability.py  # the trailers family's on-demand report [added, DEC-1123 (3)]
- template/governance/kernel/checks/product-traceability-trailers.yaml  # the family's declaration: a kernel file, changed only under this ticket's CIT-P (CAP-33), named in the commit body [added, DEC-1123 (3), CAP-33]
kpis:
  success:
  - 'A project setting chooses the close: `close: scoped` (the default of a new project) or `close: strict` (today''s close, unchanged, every lifted gate kept built); this repository runs scoped Verify: planted projects with `close: scoped`, `close: strict` and no setting: a new project''s config holds `close: scoped`; the scoped project runs the selection only, the strict project''s close gives today''s verdicts (every lifted gate still built); this repository''s config reads `close: scoped`. [DEC-953 item 1, DEC-983, DEC-982]'
  - 'The scoped close runs only the selection: the ticket''s own suite and every suite its change can reach, a shared-core change included (its mapped suites, never the full); records and governance files (the record places, the governance overlay) select nothing by themselves; a change to records alone selects the record-reading suites (named in the test map) and nothing else [DEC-1001 (a), SMART-WORK-2]; a selection that cannot be made is refused with its reason, never widened; the full suite runs only in the nightly Verify: planted changes: to a shared-core file (its mapped suites selected, never the full suite), to the ticket''s own file (its suite and the reachable suites), to record places or governance files alone (the record-reading suites named in the test map and nothing else, or nothing by themselves for governance files); a planted change with no mapping exits with the refusal and its reason and no widened set; the close''s record shows no full-suite run. [DEC-953 item 4, DEC-968, DEC-983, DEC-982]'
  - 'One selection command for every level: `gov close --select <ticket>` prints the scoped set and its `pytest` options for a lead or a worker, the same set the close runs Verify: `gov close --select <ticket>` on a planted ticket prints the scoped set and its `pytest` options, and the set equals the one a scoped close of the same ticket runs (compared in the close record). [DEC-953 item 4, DEC-983, DEC-982]'
  - 'Every failing test is run again alone; a red is judged against the head without the batch (tested code), one run each way: it is not the change''s only if the head without the batch has it red with the same failure type; the nightly''s recorded results stay the free first step, and no nightly-baseline clone is built; only the load-sensitive cases get 3 rounds; an unknown failure (a timeout, no record) never matches; otherwise it is the change''s (Q-1) Verify: planted batches: a red the head without the batch also has with the same failure type is not the change''s; a red the head does not have is the change''s; a timeout or a failure with no record never matches (the change''s); a load-sensitive case gets 3 rounds and others one each way; no clone is built for the nightly baseline (no such folder after the run); the nightly''s recorded result is read first. [DEC-988, DEC-989, DEC-1001 (c), DEC-1003, SMART-WORK-2, INVESTIGATION-1 Q-1, DEC-1050 (4)] [re-scoped, DEC-1083]'
  - 'A red the change did not cause is named in the close record and opened as a repair ticket for the orchestrator to fix at once or escalate; no list is read or written in the scoped close Verify: a planted unowned red: the close record names it, a repair ticket for the orchestrator exists in `.tickets/`, and no accepted-reds or load-sensitive list was read or written (file times unchanged). [DEC-968, DEC-983, DEC-982]'
  - 'A batch''s culprit is found before anything lands, by building the merged result without each candidate (never by taking merged code out); only the culprits go back and the rest land on the same run; a red no single candidate explains, or a candidate that cannot be isolated, refuses the batch Verify: a planted batch of three candidates, one causing a red: the build without that candidate is green, only it goes back, the other two land on the same run; a planted red no single candidate explains, and a candidate that cannot be isolated, each refuse the batch; no landing happens before the culprit is found. [DEC-979 item 3, DEC-988, DEC-1002, SMART-WORK-2]'
  - 'Each close writes its close record (the commit closed, the runs and their counts, the review''s verdict, every red with its reason, the culprits sent back): the audit''s practice 9 Verify: a close of a planted ticket writes a record holding the commit closed, the runs and counts, the review''s verdict, each red with its reason and the culprits sent back; a field missing from the record is a failed check. [DEC-953 item 5, DEC-983, DEC-982]'
  - 'The nightly rebuilds its worktree''s stores with the full secrets scan (`GOV_SECRETS_FULL_SCAN=1`) before its run, and its record says so Verify: a planted nightly run with `GOV_SECRETS_FULL_SCAN` unset in the caller''s environment: the stores are rebuilt with it set to 1 before the run, and the nightly''s record says the full secrets scan ran. [DEC-966 item 4, DEC-983, DEC-982]'
  - 'Measured, in docs/research/W2-115-smart-close.md: the CTO''s `close_build.py` and this close give the same verdict on three of this repository''s recorded batches (one clean, one with a caused red, one with an unowned red) Verify: the document holds, for three recorded batches (one clean, one with a caused red, one with an unowned red), the verdict of `close_build.py` and of this close side by side, and the two verdicts are equal on all three. [DEC-983, DEC-982]'
  - 'The close''s clean clone is a warm one kept between closes (reset, stores kept), replaced by a fresh one when it cannot be reset Verify: two planted closes in a row: the second reuses the first''s clone (same folder, reset, stores kept); a planted clone that cannot be reset is replaced by a fresh one and the record says so. [DEC-1001 (b), SMART-WORK-2]'
  - 'READY is computed, not declared: each reviewer''s probe record carries a structured verdict per KPI line (pass or fail, each finding''s scope in or out, ordinary work yes or no, consequence fails open, loses work or other); the close refuses only on a finding that is in scope, reachable in ordinary work and fails open or loses work; a malformed or incomplete verdict refuses (fail closed); a verdict written by the ticket''s lead over a reviewer''s is refused Verify: planted probe records: a complete structured verdict per KPI line with only out-of-scope or non-ordinary findings gives READY; one in-scope, reachable, fails-open finding refuses; a malformed or incomplete verdict refuses; a verdict written by the ticket''s lead over a reviewer''s is refused. [DEC-1010 item 1, SMART-WORK-3] (folds W2-117 S7)'
  - '`gov queue` gives W2-97''s queue in the product: the commit tested is the commit landed; one run per batch on the merged result, in a heavy-job slot (W2-20); a run skipped when the merged code is identical to what the lead tested, with its reason; a red batch''s culprit ejected and the rest advanced (W2-115''s attribution) Verify: a planted queue of two batches, one green and one red with a culprit: the commit landed equals the commit tested (the same hash in both records), one run per batch on the merged result in a heavy-job slot, a run on identical merged code skipped with its reason, the red batch''s culprit ejected and the rest advanced. [DEC-959 item 1, DEC-983, DEC-982] [moved from W2-117 S1, DEC-1083]'
  - 'Each green run lands and closes in one step: the ticket merges, its close record (the run, its counts, every red with its verdict, the baseline traced against) is written and the ticket closed on that run, the close citing the queue''s record instead of running its own tests on the same code; no ticket sits merged but not closed Verify: a planted green run: the ticket''s merge, its close record (run, counts, each red with its verdict, the baseline traced against) and its `closed` status all come from that run, the close cites the queue''s record and runs no tests of its own; after the run no planted ticket is merged and not closed. [DEC-989, DEC-959 item 1, DEC-983, DEC-982, DEC-1003, SMART-WORK-2] [moved from W2-117 S2, DEC-1083]'
  - 'Nothing project-specific: no branch, path or ticket of this repository is named in the code; this repository''s queue moves onto it and W2-97''s tool is retired Verify: grep of the close and queue code for this repository''s branch names, paths and ticket ids finds 0 lines; a planted second repository''s queue runs with the same code; this repository''s queue runs on it and W2-97''s tool is no longer called. [DEC-983, DEC-982] [moved from W2-117 S3, DEC-1083]'
  - 'After each landing, the queue starts the integration store''s refresh (W2-116) and seeds its own warm clones from it Verify: a planted landing: the integration store''s refresh (W2-116) is started once afterwards and the queue''s own warm clones are seeded from that store, both visible in the queue''s record. [DEC-1014 items 4 and 6, SMART-WORK-5 E, DEC-1015 item 3] [moved from W2-117 S4, DEC-1083]'
  - 'When the integration branch moved during a run only by record or governance files (the record places and the governance overlay), the queue merges onto the new head and re-runs only the record-reading suites (named in the test map), then advances; any other file in the move re-runs the whole selection; a record-reading set that cannot be read re-runs the whole selection Verify: planted moves: only record or governance files changed: the queue merges onto the new head and re-runs only the record-reading suites, then advances; any other file in the move: the whole selection re-runs; an unreadable record-reading set: the whole selection re-runs. [DEC-1001 (a), DEC-1003, SMART-WORK-2] [moved from W2-117 S5, DEC-1083]'
  - 'The trailers switch: the check family `product-traceability-trailers` counts as a warning, not a hard block. Its declaration (`template/governance/kernel/checks/product-traceability-trailers.yaml`, a kernel file: the change goes by this ticket''s CIT-P, independent review and the owner''s approval first) reads `severity: warning`; `gov close` names a missing trailer as a notice and never refuses on it; `src/gov/close/traceability.py` stays an on-demand report that lists each commit without its trailers. Verify: a planted history with commits that carry no trailers: `gov check` reports the family YELLOW with the finding count and never RED; `gov close` exits 0 and names no `TRAILER_MISSING` refusal; `python3 -m gov.close.traceability` lists each such commit [DEC-1123 (3), CAP-33, LIFT-1 P1-PLAN Q-8] [added, DEC-1123 (3)]'
  - '`gov close --verify <ticket>` runs a lead''s whole verify: the scoped selection, the parallel phase and then the serial phase (W2-154''s), each in a heavy-job slot; it writes `select.json`, one JUnit file per phase and one summary line, and writes its exit file last; exit 0 green, 1 a red, 2 the selection refused, 3 a run that did not complete. Verify: a planted tree with one red and one serial entry: exit 1, both JUnit files and the summary line; a refused selection: exit 2; a killed run: exit 3 [DEC-1052, DEC-1079, DEC-1050] [added, DEC-1125 (3)]'
  - 'The queue keeps its work clones between runs (reset to the head, untracked files removed, the stores kept, so a rebuild is incremental); a clone that cannot be reset is replaced by a fresh one; measured: the rebuild''s seconds per run, warm against fresh Verify: two planted runs: the second finds its clone reset to the head, untracked files removed, stores kept and the rebuild incremental; an unresettable clone is replaced by a fresh one; the record holds the rebuild''s seconds per run, warm against fresh. [DEC-1001 (b), DEC-1003, SMART-WORK-2] [moved from W2-117 S6, DEC-1083]'
  failure:
  - 'A scoped close refused by a red its change did not cause, or closed with a red its change caused. Verify: a planted unowned red in a scoped close: the close does not refuse on it; a planted red the change caused: the close does not close.'
  - 'A scoped close that runs the full suite, or reads or writes an accepted-reds or load-sensitive list. Verify: a scoped close of a planted ticket: the test runner''s call list holds no full-suite run, and the accepted-reds and load-sensitive lists are neither opened nor written (file access or file times show none).'
  - 'A batch that closes a culprit, or closes the rest when a red is unexplained. Verify: a planted batch with one culprit, and one with a red no candidate explains: the culprit is not closed, and the unexplained batch closes nothing.'
  - 'The strict close changed in any verdict. Verify: the strict-mode close run on the recorded planted cases from before the change: every verdict and every refusal is the same as the recorded one.'
  - 'A branch advanced to a commit that was not the one tested, or after a red. Verify: a planted queue run where the branch head moves after the test, and one where the run is red: the branch is not advanced in either; the advanced hash always equals the tested hash. [moved from W2-117 F1, DEC-1083]'
  - 'A second run on identical code, or a skip without its reason. Verify: a planted queue with two batches whose merged code is identical: only one test run is recorded, and the skip carries its reason. [moved from W2-117 F2, DEC-1083]'
  lifted:
  - 'A round whose in-scope blocking findings are not fewer than the previous round''s is reported as not converging, at once [DEC-1014 item 2, SMART-WORK-4 line 5] [lifted (was S12), DEC-1083: re-scoped by D9-FATES (INVESTIGATION-1 §5)]'
  - 'A test revision shows case and assertion counts before and after; a deleted case, a new skip or xfail, or a loosened comparison blocks unless the owner named it [DEC-1014 item 2, SMART-WORK-4 line 7] [lifted (was S13), DEC-1083: re-scoped by D9-FATES (INVESTIGATION-1 §5)]'
  - 'A test that refuses a close has passed 3 runs in a row on the baseline; otherwise it is quarantined and named, never a refusal; a quarantined test is never left on a list; it is fixed at once or escalated, like any red (DEC-968) [DEC-1014 item 2, SMART-WORK-4 line 8] [lifted (was S14), DEC-1083: re-scoped by D9-FATES (INVESTIGATION-1 §5)]'
  - 'Each close record carries governance time as a share of the ticket''s time [DEC-1014 item 2, SMART-WORK-4 line 15] [lifted (was S15), DEC-1083: re-scoped by D9-FATES (INVESTIGATION-1 §5)]'
profile: FULL
sources:
- DEC-983
- DEC-982
- DEC-979
- DEC-968
- DEC-966
- DEC-953
- DEC-1001
- DEC-1002
- DEC-1003
- DEC-1010
- DEC-1014
- DEC-1015
- DEC-1050
- DEC-1083
- DEC-959
- DEC-988
- DEC-989
- DEC-1123
- DEC-1125
- DEC-1052
- DEC-1079
- CAP-33
- DAEO-zkr9
est_loc: 400
acceptance_tests:
  path: tests/acceptance/W2-115/
  author: independent-test-designer (MR-3); from the spec and KPIs, in parallel with the implementer (DEC-963); planted repositories with a caused red, an unowned red, a test a ticket added, a batch with one culprit and one unexplained red
track: B
list_rows: []
---
# W2-115 gov close, the smart close

The owner's SMART-WORK-1 decision 1 (DEC-983): the smart close becomes the product's, not only the CTO's tools (`close_build.py`, `select_tests.py`).

- **Why:** the product's `gov close` contradicts five of the practices this repository closes by: it widens to the full suite on a shared-core change (`select.py`), judges reds by the owner-accepted lists (`ratchet.py`), quarantines timing tests on a list (`load_sensitive`), and its batch closes nothing on a red run (`batch.py`). EXAMIN's copy (W2-27) and the proving ground (W2-81) prove "a clean `gov close` at exit 0"; it must be this close they prove.
- **Kept:** DEC-953 deletes nothing: the strict close (`close: strict`) stays built and tested by its own tests, switched off by default.
- **Order:** after W2-55 (its "supersession propagates" check runs first, the owner's order). W2-12 and W2-38 change the same files and follow it, one chain. Before EXAMIN's copy (W2-27).
- **FULL:** it is the judge. The QA engineer probes above all for a caused red that closes.
