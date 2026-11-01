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
kpis:
  success:
  - 'A project setting chooses the close: `close: scoped` (the default of a new project) or `close: strict` (today''s close, unchanged, every lifted gate kept built); this repository runs scoped [DEC-953 item 1, DEC-983, DEC-982]'
  - 'The scoped close runs only the selection: the ticket''s own suite and every suite its change can reach, a shared-core change included (its mapped suites, never the full); records and governance files (the record places, the governance overlay) select nothing by themselves; a selection that cannot be made is refused with its reason, never widened; the full suite runs only in the nightly [DEC-953 item 4, DEC-968, DEC-983, DEC-982]'
  - 'One selection command for every level: `gov close --select <ticket>` prints the scoped set and its `pytest` options for a lead or a worker, the same set the close runs [DEC-953 item 4, DEC-983, DEC-982]'
  - 'Every failing test is run again alone; a red alone is traced with and without the change, interleaved, three rounds and three more unless decisive; the close is refused only by a red the change caused (green without it every round, or red with it at least half the rounds more than without; a case that cannot be collected without the change is the change''s only if it is red with the change alone) [DEC-968, DEC-983, DEC-982]'
  - 'A red the change did not cause is named in the close record and opened as a repair ticket for the orchestrator to fix at once or escalate; no list is read or written in the scoped close [DEC-968, DEC-983, DEC-982]'
  - 'A batch close finds the culprit of each caused red (its merges taken out, the red re-run alone, the merge refused as a candidate when it brings another ticket''s commits); the rest close on the same run and the culprits go back; a red no single ticket explains, or a candidate that cannot be isolated, refuses the batch [DEC-979 item 3, DEC-983, DEC-982]'
  - 'Each close writes its close record (the commit closed, the runs and their counts, the review''s verdict, every red with its reason, the culprits sent back): the audit''s practice 9 [DEC-953 item 5, DEC-983, DEC-982]'
  - 'The nightly rebuilds its worktree''s stores with the full secrets scan (`GOV_SECRETS_FULL_SCAN=1`) before its run, and its record says so [DEC-966 item 4, DEC-983, DEC-982]'
  - 'Measured, in docs/research/W2-115-smart-close.md: the CTO''s `close_build.py` and this close give the same verdict on three of this repository''s recorded batches (one clean, one with a caused red, one with an unowned red) [DEC-983, DEC-982]'
  failure:
  - 'A scoped close refused by a red its change did not cause, or closed with a red its change caused.'
  - 'A scoped close that runs the full suite, or reads or writes an accepted-reds or load-sensitive list.'
  - 'A batch that closes a culprit, or closes the rest when a red is unexplained.'
  - 'The strict close changed in any verdict.'
profile: FULL
sources:
- DEC-983
- DEC-982
- DEC-979
- DEC-968
- DEC-966
- DEC-953
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
