---
id: DAEO-g0ip
status: closed
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
  - 'A hand-resolved merge that changes probed code still refuses the probe gate, for the cases its acceptance suite holds: a hand-resolved inward merge; a merge-back that changes, drops or replaces probed code, whatever task it names; and a later merge holding the probed commit that rewrites or removes probed code present in both parents. A later merge measured against git''s own merge of its parents is W2-53''s (DEC-754).'
  - An accepted-history entry without an ACCEPTED owner decision is refused.
profile: FULL
sources:
- DEC-704
- DEC-436
- DEC-738
- DEC-739
- DEC-750
- DEC-754
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
  - A hand-resolved merge that changes probed code still refuses the probe gate, for the cases its acceptance suite holds: a hand-resolved inward merge; a merge-back that changes, drops or replaces probed code, whatever task it names; and a later merge holding the probed commit that rewrites or removes probed code present in both parents. A later merge measured against git's own merge of its parents is W2-53's (DEC-754).
  - An accepted-history entry without an ACCEPTED owner decision is refused.
- **Round 3 (DEC-739, 2026-10-17):** the owner allows one review round beyond DEC-413 and no fourth: a merge-back that names no task, or another ticket's task, and drops or replaces probed code refuses, naming the merge. Row W2-M263 left this ticket for W2-07 (DEC-738 item 4).
- **Split (DEC-750 item 2, DEC-754, 2026-10-17):** the fourth and last probe (`PR-DAEO-g0ip-round-4.md`, probed `09a01912`) failed on a later merge that removes or reverts probed code through a parent made before the ticket (findings 1 to 3, P-5). That case moves to W2-53 (DAEO-7rr2); the failure line above is narrowed to the cases held, and all 88 acceptance cases stay. A judgement-only re-probe of the final head against this card precedes the close.
- **Closed by the owner's decision DEC-757 (P-W2-19 (a), 2026-10-17), the one named exception to exit criterion 1.** Reviewed (`docs/probes/DAEO-g0ip/PR-DAEO-g0ip-split.md`, probed `a2bc5e35`), merged (`3022c2df`), acceptance suite 88 passed, regression 13478 passed. `gov close` on `3022c2df` refused (`log/W2-01-close.json`) with six findings, none of them this ticket's work: (1) PROBE_INVALID, the ticket file changed after the probe only through the orchestrator's integration commits `d09e8c1b` and `ee30c9de` (probed code byte-identical); (2, 3) W1-42's two named reds (DEC-713, DEC-714); (4) W1-05's p95 latency case, which passed alone; (5) CHECKPOINT_STALE; (6) CONTEXT_FAILED, DEC-750 not yet in the store. Residuals: W2-M360, W2-L344 to W2-L348. Round-4 findings 1 to 3 and P-5 are W2-53's (DEC-754).
