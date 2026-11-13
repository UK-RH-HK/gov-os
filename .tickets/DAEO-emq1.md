---
id: DAEO-emq1
status: closed
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
- tests/acceptance/W1-39/test_w1_39_copy.py  # PK-1 (a), the owner DEC-1142 (3): the overlay case names close.yaml; a test designer's revision only (dropped after the land)
- tests/acceptance/W1-39/README.md  # the same
- tests/acceptance/W2-77/w2_77_support.py  # PK-2 (a), the CTO: the nightly record's key set allows secrets_full_scan; a test designer's revision only (dropped after the land)
- tests/acceptance/W2-77/test_w2_77_unchanged.py  # the same
- tests/acceptance/W2-77/test_w2_77_failed_removal.py  # the same
- tests/acceptance/W2-77/README.md  # the same
- src/gov/close/command.py
- governance/project/close.yaml
- template/governance/project/close.yaml
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
  - 'The trailers switch: the check family `product-traceability-trailers` counts as a warning, not a hard block. Its declaration (`template/governance/kernel/checks/product-traceability-trailers.yaml`, a kernel file: the change goes by this ticket''s CIT-P, independent review and the owner''s approval first) reads `severity: warning`; `gov close` names a missing trailer as a notice and never refuses on it; `src/gov/close/traceability.py` stays an on-demand report that lists each commit without its trailers. Verify: a planted history with commits that carry no trailers: `gov check` reports the family YELLOW with the finding count and never RED; `gov close` exits 0 and names no `TRAILER_MISSING` refusal; `python3 -m gov.close.traceability` lists each such commit [DEC-1123 (3), CAP-33, LIFT-1 P1-PLAN Q-8] [added, DEC-1123 (3)]'
  - '`gov close --verify <ticket>` runs a lead''s whole verify: the scoped selection, the parallel phase and then the serial phase (W2-154''s), each in a heavy-job slot; it writes `select.json`, one JUnit file per phase and one summary line, and writes its exit file last; exit 0 green, 1 a red, 2 the selection refused, 3 a run that did not complete. Verify: a planted tree with one red and one serial entry: exit 1, both JUnit files and the summary line; a refused selection: exit 2; a killed run: exit 3 [DEC-1052, DEC-1079, DEC-1050] [added, DEC-1125 (3)]'
  failure:
  - 'A scoped close refused by a red its change did not cause, or closed with a red its change caused. Verify: a planted unowned red in a scoped close: the close does not refuse on it; a planted red the change caused: the close does not close.'
  - 'A scoped close that runs the full suite, or reads or writes an accepted-reds or load-sensitive list. Verify: a scoped close of a planted ticket: the test runner''s call list holds no full-suite run, and the accepted-reds and load-sensitive lists are neither opened nor written (file access or file times show none).'
  - 'A batch that closes a culprit, or closes the rest when a red is unexplained. Verify: a planted batch with one culprit, and one with a red no candidate explains: the culprit is not closed, and the unexplained batch closes nothing.'
  - 'The strict close changed in any verdict. Verify: the strict-mode close run on the recorded planted cases from before the change: every verdict and every refusal is the same as the recorded one.'
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

## Interface (DEC-1052; the CTO's delegated decision, DEC-1112 (3), 2026-11-11: run 1's P2 (a) and P3 (a))

- The switch: `governance/project/close.yaml` with `close: scoped|strict`; the template's copy
  `template/governance/project/close.yaml` holds `close: scoped`, and so does this repository's; a project with no file
  runs strict (F4 holds; no W1-30/W2-07 fixture changes).
- Refusal codes: `SELECTION_REFUSED` (S2, S18), `BATCH_UNEXPLAINED` and `CANDIDATE_NOT_ISOLATED` (S6),
  `VERDICT_MALFORMED`, `VERDICT_NOT_REVIEWER` and `FINDING_BLOCKS` (S11).
- The close record at the existing `_close_record_rel` path; the warm clone at `.gov-runtime/close/clone/` (S10).

- **Delegated (the CTO, DEC-1112 (3), 2026-11-11), run 1's packages:** P1 (b): the queue lines (former S12 to S16, S19,
  F5, F6) moved to W2-115b (DAEO-j9z6), which runs after this ticket; P2 (a) and P3 (a): the Interface above; P4: the
  trailers switch (S17, a kernel check file) waits for its CIT-P (`docs/changes/W2-115-CIT-P.md`), its independent review
  and the owner's approval (CAP-33), as a later round; this run builds every other line; P5 (a): S18 builds on today's
  serial phase (`serial.py`, W2-57's); W2-154 extends it later in the command.py chain.

## PK-1 and PK-2 (2026-11-12 ~09:55)

- **PK-1 (a) and (c), the owner (DEC-1142 (3)):** W1-39's `test_copy_creates_the_overlay` revised by the test designer (Rewrite-Reason: DEC-1142 (3), DEC-866) to accept the template's `governance/project/close.yaml` in the overlay; DEC-903's overlay list names it (changed by DEC-1142 (3)).
- **PK-2 (a), the CTO (delegated P2):** W2-77's four key-set cases revised by the test designer to allow the nightly record's `secrets_full_scan` (Rewrite-Reason: DEC-966 item 4, S8).
- One test-design batch for both, then verify, the FULL review and the probe record. The acceptance paths above are for that revision only and are dropped after the land.

## Review round 1's packages (2026-11-12 ~11:25)

- **PK-3 (a), the CTO (delegated P2):** F-1's fix: reds are judged against the green base when it is an ancestor of HEAD, else the parent of the oldest own commit (DEC-988 item 3, DEC-989); F-3 (a culprit whose red is its own new test is blamed once confirmed alone) and F-7 (the research doc states its method, or its script is committed beside it) folded into the same fix round; then review round 2, the last (DEC-1010).
- **PK-4:** a row (who commits the probe record): the CTO's launch tool, not this ticket; it does not block this land.
- **PK-5 (c), the CTO (delegated P2, 14:05):** deferred with W2-115b (parked, W3-P32): the green base in a scoped project while the nightly is red. It blocks only this repository's own scoped close, which nothing uses yet (the queue lands); option (a) would widen this ticket to `governance/project/test-map.yaml`, the owner's (DEC-1142 (8)). Reversible on the owner's word.
- Residuals F-2, F-6, F-8, F-9 as the lead triaged (W2-115b is parked, so they wait with it).

## P1-K decided (the owner, DEC-1150 (2), 2026-11-12)

R2-1 (review round 2, the last): **(a), drop the fallback.** `select.head_without_change` returns the green base when it is an ancestor of HEAD, and nothing otherwise; with no green base every red counts as the change's (fails closed). The fix rides a resume (DEC-802): one acceptance case revised for the not-an-ancestor case, R2-4's two guard cases and R2-5's `-I` fix in the same test-design batch, a fresh engineer, rebuild, lead_verify, gov accept; no review round 3 (DEC-1010). PK-7 deferred with PK-5 (the CTO, delegated P2). Before it lands, the CTO brings the owner how EXAMIN's copy gets its first green base or a recorded list of its standing reds, so W2-27's first closes do not refuse for ever.

