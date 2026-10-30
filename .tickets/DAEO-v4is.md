---
id: DAEO-v4is
status: open
deps: []
links: []
created: 2026-10-29T15:55:50Z
type: task
priority: 4
assignee: engineer
external-ref: W2-78
tags: [wave-2, close, records, standard, parked, wave-3]
wbs_id: W2-78
title: 'Governance edits stop widening closes: the path map''s lists in record files of their own; prompts and briefs record-only'
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on: []
allowed_paths:
- src/gov/close/ratchet.py
- src/gov/close/history.py
- src/gov/close/gates.py
- src/gov/close/traceability.py
- src/gov/close/select.py
- governance/project/records/**
- governance/project/test-map.yaml
- template/governance/kernel/schemas/**
- tests/unit/close/test_w2_78*
kpis:
  success:
  - 'The path map''s four lists (load_sensitive, accepted_reds, accepted_history, acceptance_exemptions) live in record files of their own under governance/project/records/, and the judge''s readers (gov.close.ratchet, history, gates, traceability) read them there; their entries are unchanged, entry for entry, and the path map keeps its configuration as shared core [DEC-941 item 5, DEC-929 item 1]'
  - 'An edit of those record files is record-only for the close''s selection: a scoped close after such an edit stays scoped, and runs the record-reading set, which holds every test that reads them (a sweep case lists the readers, as W2-66''s live test map does for DEC-891''s places) [DEC-929 item 1, DEC-889 item 2]'
  - 'governance/project/prompts/** and governance/project/briefs/** are on the test map''s record_only list, and every test that reads them is in the record-reading set (for example W2-62''s session-start case) [DEC-929 item 1]'
  - 'A removal from load_sensitive runs the ratchet''s own suites; a growing entry is still refused unless the owner''s commit adds it (the ratchet''s rule unchanged) [DEC-757, DEC-766, DEC-862]'
  - 'Nothing else changes: the path map''s configuration, the shared core and every other selection rule; the full regression in the close''s form is green apart from reds the ticket does not own [DEC-880, DEC-866]'
  failure:
  - A list entry lost or changed in the move; a reader of the moved lists or of the prompts and briefs missing from the record-reading set; a growing ratchet entry accepted without the owner's commit; the path map's configuration made record-only.
profile: STANDARD
sources:
- DEC-941
- DEC-929
- DEC-889
- DEC-880
- DEC-757
- DEC-766
- DEC-862
est_loc: 150
acceptance_tests:
  path: tests/acceptance/W2-78/
  author: independent-test-designer (MR-3); written before implementation
track: A
list_rows: []
---
# W2-78 Governance edits stop widening closes: the path map's lists in record files of their own; prompts and briefs record-only

**Parked by the owner (DEC-954 Q5; P-W2-78-PARK (a), 2026-10-30).** The branch w2/W2-78 and its worktree's commits are kept unmerged for Wave 3's hardening or for when the lifted gates come back. Nothing on w2/integrate changes. DEC-953 item 4a gets the effect: the selection leaves governance files out. Its discoveries are filed as Wave 2 list rows (W2-H064, W2-L453, W2-L454). For whoever resumes it: (1) src/gov/close/command.py:233-234 decides from the path map's own accepted_reds and load_sensitive keys whether runs report each test's result, so a move of the lists must move that reading too; (2) W1-01's support (w1_01_support.acceptance_exemptions) reads the path map itself; (3) W2-66's live case test_the_record_only_paths_are_dec_891_s_places_and_nothing_else enforces DEC-891's place list; (4) the merge needed about half a day of test revisions in 79 earlier-suite cases, two path-map ACTs, a re-pin and the outside readers' updates (P-W2-78-PARK §2).

Card: `docs/plan/WAVE_2_WBS.md` §2 (W2-78), from package P-SCOPE-RECORDS-1 (a) (owner, DEC-941 item 5).

- **Why:** a governance edit between closes turns the next close into a full run, because the path map is shared core and prompts and briefs are unplaced. W2-66's close of 10-27 ran full on records alone: 4,186 s of tests against about 300 s for the scoped closes after it (P-SCOPE-RECORDS-1 §2).
- **Place:** block A (fast closes) of the re-plan (DEC-941), after W2-77; it rides the next re-pin.
- **The migration:** the move of entries the owner committed is itself the owner's commit, or accepted by decision before the merge. The ticket prepares it; the orchestrator sends it as an ACT, validated with the pinned readers (DEC-895).
- **The test map** (`governance/project/test-map.yaml`) is shared core and W2-66's and W2-68's; this ticket edits only its `record_only` and `record_reading` lists, which DEC-941 places here.
