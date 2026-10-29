---
id: DAEO-av72
status: open
deps: []
links: []
created: 2026-10-29T15:55:51Z
type: task
priority: 2
assignee: independent-test-designer
external-ref: W2-79
tags: [wave-2, tests, orchestration, tools, lite]
wbs_id: W2-79
title: 'Acceptance tests for the orchestrator''s lead brief builder'
class: test-design
state_class: AUTHORITATIVE
role: independent-test-designer
depends_on: []
allowed_paths:
- tests/acceptance/W2-79/**
kpis:
  success:
  - 'A non-id IMPL is refused: a role name (each of the six roles), a free word, an empty or blank value, a list mixing an id with a role, and a list with an empty part each make the builder exit non-zero naming the value, and write no brief. Ids the store resolves (a DEC-n the register holds, a CAP-n the Contract holds) are accepted, alone and as a list; an id-shaped value that the register or the Contract does not hold is refused too, since IMPL fills every worker''s Implements: trailer [DEC-927 item 2, P-TOOLS-REVIEW-1 section 4 (a) item 2, DEC-941]'
  - 'A read the role is refused is flagged: where the built brief directs a role to read a path that the guard refuses to that role on this ticket, the builder names the path, the role and the reason, and writes no brief. The planted cases include P2''s own form (a test designer directed to a design note among the ticket''s implementation paths), an engineer directed to the ticket''s acceptance folder, any role directed to a secrets file, and a measured role directed to an evaluation set''s hidden part. The decision is the guard''s own read decision, not a copy of its rules. The committed common brief, with an ordinary ticket part, is not flagged: its own prohibitions direct no read. The held-out material is never named in a case [DEC-820 (c) and (d), DEC-849, DEC-941]'
  - 'The guard-forms block is required: a brief whose text lacks the block naming the command forms the guard refuses (a shell-variable write target, a here-document, backticks, an inline program the guard cannot read) is refused, naming what is missing; with the block, it is written. Each form the block names is refused by the guard''s own decision on a sample command of that form, so the block cannot drift from the guard [P-TOOLS-REVIEW-1 section 4 (a) item 2, slip S10, DEC-941]'
  - 'Every slot is filled: each of the eight slots (ID, W2, PROFILE, PATHS, ROWS, SOURCES, IMPL, EST) missing, empty or blank is refused, naming the slot; an unknown key and a key given twice are refused; a value is inserted as given, and a value holding another slot''s name in braces is never filled by that slot [DEC-824, DEC-941]'
  - 'No placeholder is left: no {SLOT} anywhere in the built brief, the ticket''s own part included (today only the common part is checked), and none of the placeholders DEC-893''s scan refuses (its own list: the to-be-decided and to-do markers, a triple X, an unfilled time or date, three question marks), read from the scan rather than copied; the angle slots the common brief keeps for the lead''s own worker launches (<role>, <name>, <effort>) are not placeholders [DEC-893, DEC-941]'
  - 'A refusal leaves no partial output: no file is written at the output path, and a file already there is unchanged. A brief built from the committed common brief and an ordinary part passes every check above [DEC-868, DEC-941]'
  - 'Hermetic: the cases run the committed tool (governance/project/orchestration/tools/build_lead_brief.py) as a process, with its common brief and its guard decision given through the interface the README states (settable, defaulting to the committed brief and the pinned guard). They write only in their temporary folders, need no network, run under 30 s alone, and are never skipped. Red first: the cases of the checks the tool lacks today (the refused read, the guard-forms block, the part''s own slots, the empty value, the unresolved id) are red for their own reasons until the orchestrator''s change to the tool [DEC-906, DEC-899 item 7, DEC-941]'
  failure:
  - A brief written with a role or an unresolved id in IMPL, a slot unfilled or empty, or a placeholder left.
  - A brief written that directs a role to a read the guard refuses it, or that lacks the guard-forms block.
  - A refusal that leaves a partial or changed output file; a case that writes in this repository or is skipped.
profile: LITE
sources:
- DEC-941
- DEC-936
- DEC-927
- DEC-929
- DEC-868
- DEC-824
- DEC-820
- DEC-893
est_loc: 220
acceptance_tests:
  path: tests/acceptance/W2-79/
  author: independent-test-designer (MR-3); written before the orchestrator's change to the tool; the tests are the deliverable
track: C
list_rows: []
---
# W2-79 Acceptance tests for the orchestrator's lead brief builder

Card: `docs/plan/WAVE_2_WBS.md` §2 (W2-79), from package P-TOOLS-REVIEW-1 §4 (a) item 2, accepted by the owner (DEC-941; DEC-936 item 2.4).

- **Why:** the brief builder fills every lead's brief and every `Implements:` trailer its workers write. It caused T7, a role in IMPL that put 41 commits on DEC-927's correction list. A check against the role's refusals would have caught P2 (W2-68's test designer sent to a read the guard refuses), and a required guard-forms block would have caught S10 (about 45 of 74 leads relearning the command forms). Nothing tests it today.
- **Entry:** the orchestrator first commits the tool under `governance/project/orchestration/tools/`, with a README (P-TOOLS-REVIEW-1 §4 (a) item 1). That move is not this ticket's. The test designer reads the tool as committed on `w2/integrate`.
- **Paths:** `tests/acceptance/W2-79/**` only, with a README that maps each KPI line to its cases and its red reason, and states the interface the cases assume (how the common brief and the guard decision are given).
- **Closes** after the orchestrator's change to the tool turns the red cases green. The change is a record commit under `governance/project/orchestration/tools/`, and the tools' independent audit (P-TOOLS-REVIEW-1 §4 (a) item 3) reads it.
