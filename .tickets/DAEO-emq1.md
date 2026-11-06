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
  - 'The scoped close runs only the selection: the ticket''s own suite and every suite its change can reach, a shared-core change included (its mapped suites, never the full); records and governance files (the record places, the governance overlay) select nothing by themselves; a change to records alone selects the record-reading suites (named in the test map) and nothing else [DEC-1001 (a), SMART-WORK-2]; a selection that cannot be made is refused with its reason, never widened; the full suite runs only in the nightly [DEC-953 item 4, DEC-968, DEC-983, DEC-982]'
  - 'One selection command for every level: `gov close --select <ticket>` prints the scoped set and its `pytest` options for a lead or a worker, the same set the close runs [DEC-953 item 4, DEC-983, DEC-982]'
  - 'Every failing test is run again alone; a red alone is judged against a known baseline (the last nightly with a verdict until a green one exists, then the last green one), never against code made by undoing merges: it is not the change''s only if the baseline had it red with the same failure (read from the nightly''s recorded results where they hold it, else traced there) and the head without the batch has it red the same way; an unknown failure (a timeout, no record) never matches; otherwise it is the change''s [DEC-988, DEC-989, DEC-1001 (c), DEC-1003, SMART-WORK-2]'
  - 'A red the change did not cause is named in the close record and opened as a repair ticket for the orchestrator to fix at once or escalate; no list is read or written in the scoped close [DEC-968, DEC-983, DEC-982]'
  - 'A batch''s culprit is found before anything lands, by building the merged result without each candidate (never by taking merged code out); only the culprits go back and the rest land on the same run; a red no single candidate explains, or a candidate that cannot be isolated, refuses the batch [DEC-979 item 3, DEC-988, DEC-1002, SMART-WORK-2]'
  - 'Each close writes its close record (the commit closed, the runs and their counts, the review''s verdict, every red with its reason, the culprits sent back): the audit''s practice 9 [DEC-953 item 5, DEC-983, DEC-982]'
  - 'The nightly rebuilds its worktree''s stores with the full secrets scan (`GOV_SECRETS_FULL_SCAN=1`) before its run, and its record says so [DEC-966 item 4, DEC-983, DEC-982]'
  - 'Measured, in docs/research/W2-115-smart-close.md: the CTO''s `close_build.py` and this close give the same verdict on three of this repository''s recorded batches (one clean, one with a caused red, one with an unowned red) [DEC-983, DEC-982]'
  - 'The close''s clean clone is a warm one kept between closes (reset, stores kept), replaced by a fresh one when it cannot be reset [DEC-1001 (b), SMART-WORK-2]'
  - 'READY is computed, not declared: each reviewer''s probe record carries a structured verdict per KPI line (pass or fail, each finding''s scope in or out, ordinary work yes or no, consequence fails open, loses work or other); the close refuses only on a finding that is in scope, reachable in ordinary work and fails open or loses work; a malformed or incomplete verdict refuses (fail closed); a verdict written by the ticket''s lead over a reviewer''s is refused [DEC-1010 item 1, SMART-WORK-3] (folds W2-117 S7)'
  - 'A round whose in-scope blocking findings are not fewer than the previous round''s is reported as not converging, at once [DEC-1014 item 2, SMART-WORK-4 line 5]'
  - 'A test revision shows case and assertion counts before and after; a deleted case, a new skip or xfail, or a loosened comparison blocks unless the owner named it [DEC-1014 item 2, SMART-WORK-4 line 7]'
  - 'A test that refuses a close has passed 3 runs in a row on the baseline; otherwise it is quarantined and named, never a refusal; a quarantined test is never left on a list; it is fixed at once or escalated, like any red (DEC-968) [DEC-1014 item 2, SMART-WORK-4 line 8]'
  - 'Each close record carries governance time as a share of the ticket''s time [DEC-1014 item 2, SMART-WORK-4 line 15]'
  - '`gov queue` gives W2-97''s queue in the product: the commit tested is the commit landed; one run per batch on the merged result, in a heavy-job slot (W2-20); a run skipped when the merged code is identical to what the lead tested, with its reason; a red batch''s culprit ejected and the rest advanced (W2-115''s attribution) [DEC-959 item 1, DEC-983, DEC-982] [moved from W2-117 S1, DEC-1083]'
  - 'Each green run lands and closes in one step: the ticket merges, its close record (the run, its counts, every red with its verdict, the baseline traced against) is written and the ticket closed on that run, the close citing the queue''s record instead of running its own tests on the same code; no ticket sits merged but not closed [DEC-989, DEC-959 item 1, DEC-983, DEC-982, DEC-1003, SMART-WORK-2] [moved from W2-117 S2, DEC-1083]'
  - 'Nothing project-specific: no branch, path or ticket of this repository is named in the code; this repository''s queue moves onto it and W2-97''s tool is retired [DEC-983, DEC-982] [moved from W2-117 S3, DEC-1083]'
  - 'After each landing, the queue starts the integration store''s refresh (W2-116) and seeds its own warm clones from it [DEC-1014 items 4 and 6, SMART-WORK-5 E, DEC-1015 item 3] [moved from W2-117 S4, DEC-1083]'
  - 'When the integration branch moved during a run only by record or governance files (the record places and the governance overlay), the queue merges onto the new head and re-runs only the record-reading suites (named in the test map), then advances; any other file in the move re-runs the whole selection; a record-reading set that cannot be read re-runs the whole selection [DEC-1001 (a), DEC-1003, SMART-WORK-2] [moved from W2-117 S5, DEC-1083]'
  - 'The queue keeps its work clones between runs (reset to the head, untracked files removed, the stores kept, so a rebuild is incremental); a clone that cannot be reset is replaced by a fresh one; measured: the rebuild''s seconds per run, warm against fresh [DEC-1001 (b), DEC-1003, SMART-WORK-2] [moved from W2-117 S6, DEC-1083]'
  failure:
  - 'A scoped close refused by a red its change did not cause, or closed with a red its change caused.'
  - 'A scoped close that runs the full suite, or reads or writes an accepted-reds or load-sensitive list.'
  - 'A batch that closes a culprit, or closes the rest when a red is unexplained.'
  - 'The strict close changed in any verdict.'
  - 'A branch advanced to a commit that was not the one tested, or after a red. [moved from W2-117 F1, DEC-1083]'
  - 'A second run on identical code, or a skip without its reason. [moved from W2-117 F2, DEC-1083]'
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
