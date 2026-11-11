---
id: DAEO-j9z6
status: open
deps: [DAEO-emq1]
links: [DAEO-emq1]
created: 2026-11-11T23:59:00Z
type: task
priority: 1
assignee: engineer
external-ref: W2-115b
tags: [wave-2, close, queue, full]
wbs_id: W2-115b
title: 'gov queue, the product''s merge queue: the queue lines of W2-115, split by its P1 (b)'
class: implementation
state_class: AUTHORITATIVE
role: engineer
profile: FULL
depends_on: [DAEO-emq1]
waits_on: []
allowed_paths:
- src/gov/queue/**
- tests/unit/queue/test_w2_115b*
est_loc: 300
kpis:
  success:
  - '`gov queue` gives W2-97''s queue in the product: the commit tested is the commit landed; one run per batch on the merged result, in a heavy-job slot (W2-20); a run skipped when the merged code is identical to what the lead tested, with its reason; a red batch''s culprit ejected and the rest advanced (W2-115''s attribution) Verify: a planted queue of two batches, one green and one red with a culprit: the commit landed equals the commit tested (the same hash in both records), one run per batch on the merged result in a heavy-job slot, a run on identical merged code skipped with its reason, the red batch''s culprit ejected and the rest advanced. [DEC-959 item 1, DEC-983, DEC-982] [moved from W2-117 S1, DEC-1083]'
  - 'Each green run lands and closes in one step: the ticket merges, its close record (the run, its counts, every red with its verdict, the baseline traced against) is written and the ticket closed on that run, the close citing the queue''s record instead of running its own tests on the same code; no ticket sits merged but not closed Verify: a planted green run: the ticket''s merge, its close record (run, counts, each red with its verdict, the baseline traced against) and its `closed` status all come from that run, the close cites the queue''s record and runs no tests of its own; after the run no planted ticket is merged and not closed. [DEC-989, DEC-959 item 1, DEC-983, DEC-982, DEC-1003, SMART-WORK-2] [moved from W2-117 S2, DEC-1083]'
  - 'Nothing project-specific: no branch, path or ticket of this repository is named in the code; this repository''s queue moves onto it and W2-97''s tool is retired Verify: grep of the close and queue code for this repository''s branch names, paths and ticket ids finds 0 lines; a planted second repository''s queue runs with the same code; this repository''s queue runs on it and W2-97''s tool is no longer called. [DEC-983, DEC-982] [moved from W2-117 S3, DEC-1083]'
  - 'After each landing, the queue starts the integration store''s refresh (W2-116) and seeds its own warm clones from it Verify: a planted landing: the integration store''s refresh (W2-116) is started once afterwards and the queue''s own warm clones are seeded from that store, both visible in the queue''s record. [DEC-1014 items 4 and 6, SMART-WORK-5 E, DEC-1015 item 3] [moved from W2-117 S4, DEC-1083]'
  - 'When the integration branch moved during a run only by record or governance files (the record places and the governance overlay), the queue merges onto the new head and re-runs only the record-reading suites (named in the test map), then advances; any other file in the move re-runs the whole selection; a record-reading set that cannot be read re-runs the whole selection Verify: planted moves: only record or governance files changed: the queue merges onto the new head and re-runs only the record-reading suites, then advances; any other file in the move: the whole selection re-runs; an unreadable record-reading set: the whole selection re-runs. [DEC-1001 (a), DEC-1003, SMART-WORK-2] [moved from W2-117 S5, DEC-1083]'
  - 'The queue keeps its work clones between runs (reset to the head, untracked files removed, the stores kept, so a rebuild is incremental); a clone that cannot be reset is replaced by a fresh one; measured: the rebuild''s seconds per run, warm against fresh Verify: two planted runs: the second finds its clone reset to the head, untracked files removed, stores kept and the rebuild incremental; an unresettable clone is replaced by a fresh one; the record holds the rebuild''s seconds per run, warm against fresh. [DEC-1001 (b), DEC-1003, SMART-WORK-2] [moved from W2-117 S6, DEC-1083]'
  failure:
  - 'A branch advanced to a commit that was not the one tested, or after a red. Verify: a planted queue run where the branch head moves after the test, and one where the run is red: the branch is not advanced in either; the advanced hash always equals the tested hash. [moved from W2-117 F1, DEC-1083]'
  - 'A second run on identical code, or a skip without its reason. Verify: a planted queue with two batches whose merged code is identical: only one test run is recorded, and the skip carries its reason. [moved from W2-117 F2, DEC-1083]'
non_goals:
- the close itself (W2-115); the trailers switch (W2-115's S17)
done_when: [DOD-1, DOD-2, DOD-3, DOD-4, DOD-5, DOD-6]
sources: [DEC-983, DEC-982, DEC-979, DEC-968, DEC-966, DEC-953, DEC-1001, DEC-1002, DEC-1003, DEC-1010, DEC-1014, DEC-1015, DEC-1050, DEC-1083, DEC-959, DEC-988, DEC-989, DEC-1123, DEC-1125, DEC-1052, DEC-1079, CAP-33, DAEO-zkr9]
acceptance_tests:
  path: tests/acceptance/W2-115b/
  author: independent-test-designer (MR-3); written before implementation
track: A
---
# W2-115b gov queue, the product's merge queue

Split from W2-115 (DAEO-emq1) by the CTO's delegated decision on its run 1's P1 (b), 2026-11-11: the six queue success
lines and two failure lines moved here word for word, with W2-97's queue (`governance/project/orchestration/tools/merge_queue.py`)
as the reference. Runs after W2-115 (the close it lands through). Class C3 (the landing path).
