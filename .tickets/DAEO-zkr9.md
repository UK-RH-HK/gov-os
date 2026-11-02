---
id: DAEO-zkr9
status: open
deps: [DAEO-wq2b, DAEO-emq1, DAEO-r30l]
links: []
created: 2026-10-31T23:52:57Z
type: task
priority: 1
assignee: engineer
external-ref: W2-117
tags: [wave-2, implementation, close, full, smart-work, after-examin]
wbs_id: W2-117
title: 'The merge queue in the product: gov queue enqueues, tests the merged result once, advances or ejects, and records, from W2-97''s tool (SMART-WORK-1)'
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on:
- DAEO-wq2b
- DAEO-emq1
- DAEO-r30l
allowed_paths:
- src/gov/queue/**
- src/gov/cli/main.py
- tests/unit/queue/**
kpis:
  success:
  - '`gov queue` gives W2-97''s queue in the product: the commit tested is the commit landed; one run per batch on the merged result, in a heavy-job slot (W2-20); a run skipped when the merged code is identical to what the lead tested, with its reason; a red batch''s culprit ejected and the rest advanced (W2-115''s attribution) [DEC-959 item 1, DEC-983, DEC-982]'
  - 'Each green run lands and closes in one step: the ticket merges, its close record (the run, its counts, every red with its verdict, the baseline traced against) is written and the ticket closed on that run, the close citing the queue''s record instead of running its own tests on the same code; no ticket sits merged but not closed [DEC-989, DEC-959 item 1, DEC-983, DEC-982, DEC-1003, SMART-WORK-2]'
  - 'Nothing project-specific: no branch, path or ticket of this repository is named in the code; this repository''s queue moves onto it and W2-97''s tool is retired [DEC-983, DEC-982]'
  - 'After each landing, the queue starts the integration store''s refresh (W2-116) and seeds its own warm clones from it [DEC-1014 items 4 and 6, SMART-WORK-5 E, DEC-1015 item 3]'
  - 'When the integration branch moved during a run only by record or governance files (the record places and the governance overlay), the queue merges onto the new head and re-runs only the record-reading suites (named in the test map), then advances; any other file in the move re-runs the whole selection; a record-reading set that cannot be read re-runs the whole selection [DEC-1001 (a), DEC-1003, SMART-WORK-2]'
  - 'The queue keeps its work clones between runs (reset to the head, untracked files removed, the stores kept, so a rebuild is incremental); a clone that cannot be reset is replaced by a fresh one; measured: the rebuild''s seconds per run, warm against fresh [DEC-1001 (b), DEC-1003, SMART-WORK-2]'
  - 'A ticket''s review rounds are counted from its probe records; a candidate with a blocking finding after two rounds is refused with "to the owner, once, with options", never queued for a third round [DEC-1010 item 1, SMART-WORK-3]'
  failure:
  - 'A branch advanced to a commit that was not the one tested, or after a red.'
  - 'A second run on identical code, or a skip without its reason.'
profile: FULL
sources:
- DEC-983
- DEC-982
- DEC-959
est_loc: 250
acceptance_tests:
  path: tests/acceptance/W2-117/
  author: independent-test-designer (MR-3); from the spec and KPIs, in parallel with the implementer (DEC-963); planted repositories with queued branches, a red batch, a moving head
track: B
list_rows: []
---
# W2-117 The merge queue in the product

The owner's SMART-WORK-1 decision 3 (DEC-983); moved before EXAMIN's copy by DEC-1010 item 5, so the dispatcher (W2-121) lands batches through it and EXAMIN gets test-before-merge.

- **Why:** W2-97 builds this repository's queue as its own tool (`governance/project/orchestration/tools/`), which is right for now; an adopted product with streams needs it as a `gov` command. EXAMIN's copy runs one LITE ticket, which needs no queue.
- **Order:** after W2-97 (measured in use here first), W2-115 (its attribution), W2-20 (its slots) and W2-27 (EXAMIN's copy).
