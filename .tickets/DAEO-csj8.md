---
id: DAEO-csj8
status: open
deps: [DAEO-g0ip, DAEO-h4rh]
links: []
created: 2026-10-16T16:35:11Z
type: task
priority: 1
assignee: independent-auditor
external-ref: W2-28
tags: [wave-2, audit, full]
wbs_id: W2-28
title: Independent verdict on the copy
class: audit
state_class: AUTHORITATIVE
role: independent-auditor
depends_on:
- DAEO-g0ip
- DAEO-h4rh
allowed_paths:
- docs/audit/wave-2/W2-28/**
kpis:
  success:
  - 'A fresh auditor gives the copy''s verdict against the lite conditions of Contract v4.2''s CAP-44.h: ADOPTED_HEALTHY, ADOPTED_WITH_ACCEPTED_EXCEPTIONS or NOT_ADOPTED_HEALTHY. Anything short of ADOPTED_HEALTHY
    goes to the owner before W2-29. Verify: the auditor''s result record names one of the three verdicts, against the CAP-44.h lite conditions it lists; a planted record with ADOPTED_WITH_ACCEPTED_EXCEPTIONS or NOT_ADOPTED_HEALTHY puts one item in the owner''s inbox naming the verdict, and W2-29 does not start until the owner answers.'
  - 'The verdict checks that nothing of the owner''s was lost from EXAMIN''s own CLAUDE.md, AGENTS.md and .claude/commands/, each migrated into EXAMIN''s rulesync sources or kept in place, never silently overwritten.
    Verify: a planted copy in which one rule line of CLAUDE.md, one of AGENTS.md and one command file are missing from both the rulesync sources and the original places is refused by the verdict, naming each; a copy where each is migrated or kept passes; a planted overwritten file (the content differs, no migration record) is named [DEC-736]'
  failure: []
profile: FULL
sources:
- CAP-44.h
- DEC-736
est_loc: 0
acceptance_tests:
  judged_by: 'its class (WBS §0 rule 1, W2-07): its report and the audit validator'
track: B
closes:
- Track B
list_rows: []
---
# W2-28 Independent verdict on the copy

Card: `docs/plan/WAVE_2_WBS.md` §2 (W2-28), as approved (DEC-729). The list rows it takes in are in `list_rows` and in `docs/plan/WAVE_2_TRIAGE.md`; a row's state is re-checked against the code when the ticket picks it up (DEC-718).

- A fresh auditor gives the copy's verdict against the lite conditions of Contract v4.2's CAP-44.h: ADOPTED_HEALTHY, ADOPTED_WITH_ACCEPTED_EXCEPTIONS or NOT_ADOPTED_HEALTHY. Anything short of ADOPTED_HEALTHY goes to the owner before W2-29.
- The verdict checks that nothing of the owner's was lost from EXAMIN's own `CLAUDE.md`, `AGENTS.md` and `.claude/commands/`. Each is migrated into EXAMIN's rulesync sources or kept in place, never silently overwritten [DEC-736].
