---
id: DAEO-r9ss
status: open
deps: [DAEO-g0ip, DAEO-zflj, DAEO-7rr2]
links: []
created: 2026-10-16T16:35:11Z
type: task
priority: 1
assignee: engineer
external-ref: W2-07
tags: [wave-2, implementation, standard]
wbs_id: W2-07
title: gov close by ticket class; complete, tracked repair tickets; a share for every close
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on:
- DAEO-g0ip
- DAEO-zflj
- DAEO-7rr2
allowed_paths:
- src/gov/close/**
- src/gov/telemetry/**
- tests/unit/close/**
- tests/unit/telemetry/**
kpis:
  success:
  - 'gov close judges a ticket by its class [W2-H045]: an implementation ticket on its acceptance tests; a specification ticket on its closed readiness record and its acceptance tests; an audit ticket on
    its report and the audit validator; a research ticket on its evidence record; an integration or coordination ticket on its named evidence files'
  - A refused close writes a complete repair ticket (role, allowed paths, KPIs) that stays tracked in .tickets/ [F-m8, W2-L209, W2-L236, AR-9].
  - The close record carries the measured governance share [W2-M166, W2-M286].
  - Adoption-gap and baseline refusals do not count toward the escalation counter; a repeated identical refusal reuses its repair ticket [W2-H038, W2-M249, W2-M252].
  - An interrupted close leaves nothing that blocks the next close [W2-M158].
  - 'The pre-close gate, inside gov close (DEC-868): before its regression, the close collects every suite it will run, in one process, as it runs them (pytest --collect-only), runs gov check with no
    commit since the rebuild, and checks that the ticket''s checkpoint is fresh; any failure refuses at once, naming its cause, before any test runs, and spends no ratchet attempt'
  failure:
  - A research ticket without an evidence record refuses; an audit ticket whose report fails the validator refuses.
  - A tree with a collection error (an import or name clash), a RED gov check or a stale checkpoint is refused by the gate within minutes, not after the regression [DEC-868].
profile: STANDARD
sources:
- DEC-729
- DEC-738
- DEC-868
est_loc: 160
acceptance_tests:
  path: tests/acceptance/W2-07/
  author: independent-test-designer (MR-3); written before implementation
track: A
closes:
- AR-9 (claims)
- F-m8
- W2-H045
list_rows:
- W2-H038
- W2-H045
- W2-L107
- W2-L108
- W2-L123
- W2-L124
- W2-L165
- W2-L196
- W2-L197
- W2-L208
- W2-L209
- W2-L210
- W2-L236
- W2-M149
- W2-M157
- W2-M158
- W2-M166
- W2-M178
- W2-M248
- W2-M249
- W2-M252
- W2-M263
- W2-M276
- W2-M286
- W2-M348
- W2-M349
- W2-M354
---
# W2-07 gov close by ticket class; complete, tracked repair tickets; a share for every close

Card: `docs/plan/WAVE_2_WBS.md` §2 (W2-07), as approved (DEC-729). The list rows it takes in are in `list_rows` and in `docs/plan/WAVE_2_TRIAGE.md`; a row's state is re-checked against the code when the ticket picks it up (DEC-718).

- **Allowed paths:** `src/gov/close/**` (except W2-66's and W2-68's new modules, `select.py`, `nightly.py`, `batch.py` and `fingerprint.py`; W2-48's `cache*` was withdrawn, DEC-880), `src/gov/telemetry/**`, `tests/unit/close/**`, `tests/unit/telemetry/**`.
- **KPIs, success:**
  - `gov close` judges a ticket by its class [W2-H045]:
    - an implementation ticket on its acceptance tests;
    - a specification ticket on its closed readiness record and its acceptance tests;
    - an audit ticket on its report and the audit validator;
    - a research ticket on its evidence record;
    - an integration or coordination ticket on its named evidence files.
  - A refused close writes a complete repair ticket (role, allowed paths, KPIs) that stays tracked in `.tickets/` [F-m8, W2-L209, W2-L236, AR-9].
  - The close record carries the measured governance share [W2-M166, W2-M286].
  - Adoption-gap and baseline refusals do not count toward the escalation counter; a repeated identical refusal reuses its repair ticket [W2-H038, W2-M249, W2-M252].
  - An interrupted close leaves nothing that blocks the next close [W2-M158].
  - **The pre-close gate, inside `gov close` (DEC-868, owner, 2026-10-20):** before its regression, the close collects every suite it will run, in one process, as it runs them (`pytest --collect-only`), runs `gov check` with no commit since the rebuild, and checks that the ticket's checkpoint is fresh; any failure refuses at once, naming its cause, before any test runs, and spends no ratchet attempt. Failure: a tree with a collection error (an import or name clash, as `tests/unit/secrets` shadowing the standard library), a RED `gov check` or a stale checkpoint is refused within minutes, not after the regression.
- **KPIs, failure:** a research ticket without an evidence record refuses; an audit ticket whose report fails the validator refuses.
- **Row W2-M263 (DEC-738 item 4, 2026-10-17):** re-triaged from W2-01. RED stays when nothing comes after the base (DEC-479; W1-30's test); this ticket owns how the close reports it.
