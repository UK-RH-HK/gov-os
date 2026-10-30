---
id: DAEO-g87r
status: open
deps: [DAEO-m1u3]
links: []
created: 2026-10-30T22:14:09Z
type: task
priority: 1
assignee: independent-auditor
external-ref: W2-94
tags: [wave-2, audit, evaluation, held-out, standard, examin-minimum]
wbs_id: W2-94
title: 'EXAMIN''s question set: memory questions with gold sources about the owner''s copy, a visible and a hidden half, by a session independent of the adopting team, before W2-27'
class: audit
state_class: AUTHORITATIVE
role: independent-auditor
depends_on: [DAEO-m1u3]
allowed_paths:
- fixtures/evaluation/examin/visible/**
- fixtures/evaluation/examin/hidden/**
kpis:
  success:
  - 'Between 10 and 20 questions about EXAMIN''s code and governance, each with its gold answer and the source or sources an answer must cite (file and section or line), in the form W2-61''s visible half takes; after writing, a recorded seeded draw, stratified by category, sends half to the visible folder and half to the hidden folder [DEC-957, DEC-828 items 3 and 4, DEC-954 Q9f]'
  - 'Written from a clone of the owner''s copy made by exact path under ~/gov-os-runs/W2-94/examin/; the copy is only read by that clone; nothing written in the workbench or in EXAMIN''s real repository [DEC-723, DEC-728]'
  - 'Written by a session independent of the adopting team: no session of W2-26, W2-27, W2-88 or a retrieval ticket writes or reads the hidden half; nothing hidden quoted in a commit message, a return, a log or a ticket note [DEC-820 (d), DEC-845]'
  - 'Every gold source exists at the copy''s recorded commit and holds the answer [DEC-828 item 4]'
  - 'W2-61''s KPI 6 ("the same split for EXAMIN''s set") is met by this ticket; W2-61''s close record names it as moved here [DEC-954, DEC-957]'
  failure:
  - 'A hidden question or answer readable by a measured session by a route an honest agent takes in ordinary work.'
  - 'A write in the workbench, the owner''s copy or EXAMIN''s real repository; a clone outside ~/gov-os-runs/W2-94/.'
  - 'A gold source that does not hold its answer.'
profile: STANDARD
sources:
- DEC-957
- DEC-954
- DEC-828
- DEC-820
- DEC-845
- DEC-723
- DEC-728
est_loc: 0
acceptance_tests:
  path: tests/acceptance/W2-94/
  author: independent-test-designer (MR-3); form only (count, fields, sources named), never printing a question or an answer
track: B
list_rows: []
---
# W2-94 EXAMIN's question set

Card: MEMORY-SPEC-MAP gap 7, resolved by the owner in DEC-957; W2-61's KPI 6 moves here. The set measures memory on EXAMIN's copy at W2-27 (with W2-88's tools) and W2-15b.

- **Before it starts, the orchestrator adds an `evaluation_sets` entry** `examin` to the path map (`visible: fixtures/evaluation/examin/visible/**`, `hidden: fixtures/evaluation/examin/hidden/**`, `measures` by tickets: W2-26, W2-27, W2-88, W2-15b and the retrieval tickets), so the guard refuses the hidden half from every worktree (W2-84).
- **The clone:** made by the orchestrator or the auditor by exact path, `git clone --no-hardlinks` from the owner's copy (DEC-723, DEC-728); removed at the end.
- **Started by the orchestrator,** never by an adoption or retrieval ticket's lead.
