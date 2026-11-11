---
id: DAEO-neam
status: open
deps: [DAEO-g0ip]
links: []
created: 2026-10-16T16:35:12Z
type: task
priority: 4
assignee: engineer
external-ref: W2-45
tags: [wave-2, implementation, standard]
wbs_id: W2-45
title: gov check runner semantics and scale
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on:
- DAEO-g0ip
allowed_paths:
- src/gov/check/runner.py
- src/gov/check/commands.py
- src/gov/decisions/checker.py
- tests/unit/check/**
kpis:
  success:
  - 'The decision checker runs within the gov check budget on a 200-decision, 20k-commit repository Verify: a planted repository of 200 decisions and 20,000 commits: `gov check` runs the decision checker and its recorded time is within the gov check budget (the budget''s value printed beside it) [W2-H018].'
  - 'A check that exits 0 with findings, or with "unmeasured" in its result, is not green Verify: planted checks, one exiting 0 with a finding and one exiting 0 with "unmeasured" in its result: both are reported not green; a planted clean check exiting 0 is green [W2-M129, W2-M212].'
  - 'An absent tool of a hard-block check is red, not yellow Verify: a planted hard-block check whose tool is absent from the path: its result is red, never yellow [W2-M130, W2-M265].'
  - 'A hard-block key is covered only by a check of hard-block tier Verify: a planted check map that covers a hard-block key only by a check of a lower tier is refused naming the key; the same key covered by a hard-block-tier check is accepted [W2-M211, W2-M259].'
  - 'The time limit is stated and tested Verify: the limit''s value is printed in the runner''s result, and a planted check that runs past it is stopped and reported as timed out, by a unit test [W2-M151].'
  failure: []
profile: STANDARD
sources:
- DEC-729
est_loc: 160
acceptance_tests:
  path: tests/acceptance/W2-45/
  author: independent-test-designer (MR-3); written before implementation
track: C
closes:
- W2-H018
list_rows:
- W2-H018
- W2-L096
- W2-L098
- W2-L104
- W2-L118
- W2-L167
- W2-L168
- W2-L169
- W2-L171
- W2-L223
- W2-M063
- W2-M128
- W2-M129
- W2-M130
- W2-M131
- W2-M132
- W2-M144
- W2-M146
- W2-M151
- W2-M170
- W2-M211
- W2-M212
- W2-M259
- W2-M265
- W2-M268
- W2-M315
---
# W2-45 gov check runner semantics and scale

**Deferred to Wave 3 (DEC-953 item 10b, approved by DEC-954, 2026-10-30).** K8 (DEC-941); W2-26 found no trigger (indexing about 30 % of the envelope).

Card: `docs/plan/WAVE_2_WBS.md` §2 (W2-45), as approved (DEC-729). The list rows it takes in are in `list_rows` and in `docs/plan/WAVE_2_TRIAGE.md`; a row's state is re-checked against the code when the ticket picks it up (DEC-718).

- **Allowed paths:** `src/gov/check/runner.py`, `src/gov/check/commands.py`, `src/gov/decisions/checker.py` (speed only), `tests/unit/check/**`.
- **KPIs:**
  - The decision checker runs within the `gov check` budget on a 200-decision, 20k-commit repository [W2-H018].
  - A check that exits 0 with findings, or with "unmeasured" in its result, is not green [W2-M129, W2-M212].
  - An absent tool of a hard-block check is red, not yellow [W2-M130, W2-M265].
  - A hard-block key is covered only by a check of hard-block tier [W2-M211, W2-M259].
  - The time limit is stated and tested [W2-M151].
