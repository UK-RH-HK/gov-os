---
id: DAEO-6n5k
status: in_progress
deps: [DAEO-g0ip, DAEO-ym8a]
links: []
created: 2026-10-16T16:35:11Z
type: task
priority: 2
assignee: engineer
external-ref: W2-37
tags: [wave-2, implementation, full]
wbs_id: W2-37
title: gov impact
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on:
- DAEO-g0ip
- DAEO-ym8a
allowed_paths:
- src/gov/impact/**
- src/gov/closure/**
- tests/unit/impact/**
- template/governance/kernel/skills/change/SKILL.md
- template/.rulesync/skills/change/SKILL.md
- src/gov/check/commands.py  # P-7 (a), DEC-812 item 6: the RECORDED_GOV_COMMANDS line records `impact` only
- tests/acceptance/W1-07/w1_07_support.py  # P-7 (a): W1-07's lists gain `impact`, by a test designer with a Rewrite-Reason
- tests/acceptance/W1-07/test_w1_07_recorded_commands.py  # the same (its count test renamed)
- tests/acceptance/W1-07/README.md  # the same
- tests/acceptance/W1-32/test_w1_32_command_set.py  # P-7 (a): W1-32's command-set assertion gains `impact`
- tests/conftest.py  # _CBM_SUITES gains W2-37 (its code-graph cases run with the tool on PATH), CTO, DEC-1156 (7)
kpis:
  success:
  - '"What''s the impact of X?" in plain language runs gov impact [CAP-33.g, DEC-167]. Verify: a planted question "what is the impact of DEC-NNN?" given to the plain-language entry runs gov impact on DEC-NNN and prints its result [Verify clause added, DEC-1157 (12)]'
  - 'It also takes the S0b2 glue G-16 (id mapping) and G-24 (deletable-class join). Verify: planted records with mapped ids and a deletable-class row: gov impact resolves the mapped ids (G-16) and joins the deletable class (G-24) in its result; G-24''s "no record names the item" counts the store''s stated links too (a ticket''s sources and closes, the register''s Under and Changes lines): a planted decision named only by a ticket''s sources is not deletable [Verify clause added, DEC-1157 (12); F1 (a), DEC-1163]'
  failure: []
  lifted:
  - 'A decision change raises a CIT-P that lists the affected specifications, decisions, tickets, tests and code from both graphs, with a radius [CAP-33.b, W2-M285]. [lifted (was S1), DEC-1083: the query only, no CIT-P (INVESTIGATION-1 §5, W-3)]'
  - 'After apply or archive, the CIT-E record matches the proposal or lists the differences [W2-L319]. [lifted (was S2), DEC-1083: the query only, no CIT-P (INVESTIGATION-1 §5, W-3)]'
profile: FULL
sources:
- CAP-33.b
- CAP-33.g
- DEC-167
- DEC-1083
est_loc: 280
acceptance_tests:
  path: tests/acceptance/W2-37/
  author: independent-test-designer (MR-3); written before implementation
track: C
closes:
- CAP-33.b
- CAP-33.g
- DEC-167
list_rows:
- W2-L319
- W2-M056
- W2-M150
- W2-M285
- W2-M320
---
# W2-37 gov impact

Card: `docs/plan/WAVE_2_WBS.md` §2 (W2-37), as approved (DEC-729). The list rows it takes in are in `list_rows` and in `docs/plan/WAVE_2_TRIAGE.md`; a row's state is re-checked against the code when the ticket picks it up (DEC-718).

- **Allowed paths:** `src/gov/impact/**` (new), `src/gov/closure/**` (read API only), `tests/unit/impact/**`.
- **KPIs:**
  - A decision change raises a CIT-P that lists the affected specifications, decisions, tickets, tests and code from both graphs, with a radius [CAP-33.b, W2-M285].
  - After apply or archive, the CIT-E record matches the proposal or lists the differences [W2-L319].
  - "What's the impact of X?" in plain language runs `gov impact` [CAP-33.g, DEC-167].
  - It also takes the S0b2 glue G-16 (id mapping) and G-24 (deletable-class join).
