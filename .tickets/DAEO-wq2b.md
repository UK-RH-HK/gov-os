---
id: DAEO-wq2b
status: open
deps: []
links: []
created: 2026-10-30T23:20:53Z
type: task
priority: 1
assignee: engineer
external-ref: W2-97
tags: [wave-2, implementation, orchestration, standard]
wbs_id: W2-97
title: 'The local merge queue: each candidate merge tested before w2/integrate moves, advanced only on green, ejected on red; tests run once per level'
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on: []
allowed_paths:
- governance/project/orchestration/tools/merge_queue.py
- tests/unit/orchestration/test_w2_97*
- governance/project/orchestration/tools/README.md
kpis:
  success:
  - 'A ticket enters the queue only with its Senior Engineer''s approval (until the three layers start, the CTO''s); the queue makes the --no-ff merge of the ticket onto w2/integrate''s current head in a clean clone, runs the scoped set once on that merged result under the test lock, and on green advances w2/integrate to that same merge commit (--ff-only), so the commit tested is the commit landed [DEC-959 item 1, DEC-848]'
  - 'On red, w2/integrate does not move: the ticket is ejected back to its Senior Engineer (or the CTO) with the failing tests'' names and the run''s log path; a red that passes alone is a flaky candidate, named, and decides nothing on its own [DEC-959 item 1, DEC-953]'
  - 'Tests run no more than this: the queue runs the scoped set once per batch on the merged result, and skips the run when the merged code is identical to what the lead tested (same tree for the code paths, governance records left out), recording why it skipped; the full suite runs only for a change to the core (the selection''s own rule) [DEC-959 item 1]'
  - 'A batch of queued tickets on one head gives one merged result and one run; a red batch is bisected by ticket, the good ones advance and the causing one is ejected [DEC-959 item 1]'
  - 'Each advance writes the record the close cites (the head, the tickets, the selection, the counts, the time); close_build cites it instead of running its own tests on the same code [DEC-959 item 1]'
  - 'When the head moves while a candidate is under test, the candidate is re-merged and re-tested, never advanced onto a head it was not tested on [DEC-959 item 1]'
  failure:
  - 'w2/integrate advanced to a commit that was not the one tested, or after a red.'
  - 'A second run on code identical to the lead''s tested code, or a skip without its recorded reason.'
  - 'A red batch that advances its causing ticket.'
  - 'A close that re-runs tests the queue already ran on the same code.'
profile: STANDARD
sources:
- DEC-959
- DEC-953
- DEC-848
- DEC-954
est_loc: 250
acceptance_tests:
  path: tests/acceptance/W2-97/
  author: independent-test-designer (MR-3); from the spec and KPIs, in parallel with the implementer (DEC-959 item 7); planted repositories with a fake integration branch and stub test commands
track: A
list_rows: []
---
# W2-97 The local merge queue

Card: ROLES-RESEARCH-1 §5.3 item 5 and option (c), approved by the owner (DEC-959 item 1): the "not rocket science rule" built locally, one writer kept (the CTO's tool), the push the owner's.

- **Its home is tracked:** `governance/project/orchestration/tools/merge_queue.py`. The orchestrator's tools under `.gov-runtime/scratch/` are not tracked; the queue is a project tool others rely on, so it lives with the orchestration record, with unit tests under `tests/unit/orchestration/`.
- **It reuses** `close_build.py`'s steps (clone, rebuild, selection, test lock, flaky re-run) and `select_tests.py`'s selection; those stay in scratch until this lands, then call into it or are retired.
- **Until it lands,** closes run as DEC-953 item 4 and `close_build.py` state.
- **Overlaps:** none.
