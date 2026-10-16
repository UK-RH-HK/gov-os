---
id: DAEO-g0ip
status: open
deps: []
links: []
created: 2026-10-16T16:35:10Z
type: task
priority: 1
assignee: engineer
external-ref: W2-01
tags: [wave-2, implementation, full]
wbs_id: W2-01
title: 'gov close and traceability: trailers base, merge form, owner-accepted history, the probe gate after a merge-back'
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on: []
allowed_paths:
- src/gov/close/**
- template/governance/kernel/checks/product-traceability-trailers.yaml
- tests/unit/close/**
kpis:
  success:
  - gov close's own trailer gate reads the project's trailers_base and does not judge commits before it [DEC-704, W2-M238, W2-M250].
  - 'A merge of the integration branch into a ticket branch in DEC-436''s merge form (Task: and Role:) passes the trailer gate [W2-M165].'
  - History commits that an ACCEPTED owner decision names are accepted history. They are listed in the close and check output as accepted, with the decision id. They fail neither gov close nor the product-traceability
    check of a later commit [AR-3, W2-M147, W2-L235].
  - A ticket branch probed, then merged with the integration branch and merged back, passes the probe gate when the probed code is unchanged [W2-H047, W2-M202].
  - A reopened FULL ticket with an earlier-round probe record and a passing later one passes the probe gate [W2-M209, W2-L111].
  - The ticket-creating commit and clone path maps without a trailers base are judged as the base rule says, and the output names the base used [W2-M251, W2-M266].
  failure:
  - 'A commit after the base without Task:, Role: or Implements: still refuses.'
  - A merge that adds its own change outside the merged side still refuses.
  - A hand-resolved merge that changes probed code still refuses the probe gate.
  - An accepted-history entry without an ACCEPTED owner decision is refused.
profile: FULL
sources:
- DEC-704
- DEC-436
est_loc: 180
acceptance_tests:
  path: tests/acceptance/W2-01/
  author: independent-test-designer (MR-3); written before implementation
track: A
closes:
- AR-8 fix
- AR-3 (history)
- DEC-704
list_rows:
- W2-H047
- W2-L111
- W2-L175
- W2-L235
- W2-M147
- W2-M165
- W2-M202
- W2-M209
- W2-M238
- W2-M250
- W2-M251
- W2-M263
- W2-M266
- W2-M353
---
# W2-01 gov close and traceability: trailers base, merge form, owner-accepted history, the probe gate after a merge-back

Card: `docs/plan/WAVE_2_WBS.md` §2 (W2-01), as approved (DEC-729). The list rows it takes in are in `list_rows` and in `docs/plan/WAVE_2_TRIAGE.md`; a row's state is re-checked against the code when the ticket picks it up (DEC-718).

- **Why first:** every later ticket must close cleanly (exit criterion 1); W1-42 met 22 close findings, 15 of them trailer findings on history and merge commits.
- **Allowed paths:** `src/gov/close/**`, `template/governance/kernel/checks/product-traceability-trailers.yaml`, `tests/unit/close/**`.
- **KPIs, success:**
  - `gov close`'s own trailer gate reads the project's `trailers_base` and does not judge commits before it [DEC-704, W2-M238, W2-M250].
  - A merge of the integration branch into a ticket branch in DEC-436's merge form (`Task:` and `Role:`) passes the trailer gate [W2-M165].
  - History commits that an ACCEPTED owner decision names are accepted history. They are listed in the close and check output as accepted, with the decision id. They fail neither `gov close` nor the product-traceability check of a later commit [AR-3, W2-M147, W2-L235].
  - A ticket branch probed, then merged with the integration branch and merged back, passes the probe gate when the probed code is unchanged [W2-H047, W2-M202].
  - A reopened FULL ticket with an earlier-round probe record and a passing later one passes the probe gate [W2-M209, W2-L111].
  - The ticket-creating commit and clone path maps without a trailers base are judged as the base rule says, and the output names the base used [W2-M251, W2-M266].
- **KPIs, failure:**
  - A commit after the base without `Task:`, `Role:` or `Implements:` still refuses.
  - A merge that adds its own change outside the merged side still refuses.
  - A hand-resolved merge that changes probed code still refuses the probe gate.
  - An accepted-history entry without an ACCEPTED owner decision is refused.
