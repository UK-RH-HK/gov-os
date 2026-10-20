---
id: DAEO-7rr2
status: closed
deps: [DAEO-g0ip]
links: []
created: 2026-10-17T10:55:10Z
type: task
priority: 1
assignee: engineer
external-ref: W2-53
tags: [wave-2, implementation, full]
wbs_id: W2-53
title: The probe gate measures every later merge against git's own merge of its parents
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on:
- DAEO-g0ip
allowed_paths:
- src/gov/close/**
- tests/unit/close/**
kpis:
  success:
  - "After a FULL ticket's probed commit, every later merge that holds it refuses, naming the merge, whatever task it names (or none), when a probed path (the ticket's allowed paths, its acceptance folder, its ticket file) at the merge is not what git's own merge of its parents gives, a removal or a return to a version from before the ticket included; on the integration branch, inward on the ticket's branch, and for an octopus merge [DEC-750, DEC-754]."
  - "A later merge that takes another ticket's whole version of a probed file is measured the same way, against git's own merge of its parents (P-5 (c)) [DEC-754]."
  - "A reopened FULL ticket whose earlier round was merged back before its final probe closes when the probed code at the closed head is the final probed code [DEC-754]."
  - "A merge whose probed paths are what git's own merge of its parents gives, and another ticket's merge holding the probed commit on neither side, pass as before; W2-01's acceptance cases stay green [W2-H047, W2-M202]."
  failure:
  - An acceptance test added on the ticket's branch before the probe and removed or changed by a later merge refuses the close.
  - A merge whose own merge git cannot compute, or cannot read, is judged against the probed code and never passes by default.
profile: FULL
sources:
- DEC-750
- DEC-754
- DEC-757
- DEC-704
- DEC-498
est_loc: 160
acceptance_tests:
  path: tests/acceptance/W2-53/
  author: independent-test-designer (MR-3); written before implementation
track: A
closes:
- DEC-750 (item 2)
- DEC-757 (item 2)
list_rows: []
---
# W2-53 The probe gate measures every later merge against git's own merge of its parents

Card: `docs/plan/WAVE_2_WBS.md` §2 (W2-53), added by DEC-750 item 2 and DEC-754 (2026-10-17): the merge-back case split from W2-01 after its fourth and last probe (`docs/probes/DAEO-g0ip/PR-DAEO-g0ip-round-4.md`). Layer 2, right after W2-01 closes; test designer first.

- **Why:** W2-01's fourth probe found that a later merge holding the probed commit, bringing another ticket's branch made before the merge-back and naming that ticket's `Task:`, can delete a probed file, set it back to its text from before the ticket, or remove an acceptance test, and `gov close` passes (findings 1 and 2). A reopened ticket whose first round was merged back before its final probe cannot close (finding 3). Judging a merge parent by parent is weak whenever one parent predates the ticket; git's own merge of the parents is the measure.
- **Starts** after W2-01 closes (the same paths), alone, ahead of every held ticket (DEC-757). W2-07, W2-41 and W2-48 share `src/gov/close/` and run after it. Until it closes, DEC-750 item 3's merge rule, as DEC-754 extends it, holds every merge.
- **Allowed paths:** `src/gov/close/**`, `tests/unit/close/**`.
- **KPIs, success:**
  - After a FULL ticket's probed commit, every later merge that holds it refuses, naming the merge, whatever task it names (or none), when a probed path (the ticket's allowed paths, its acceptance folder, its ticket file) at the merge is not what git's own merge of its parents gives, a removal or a return to a version from before the ticket included; on the integration branch, inward on the ticket's branch, and for an octopus merge [DEC-750, DEC-754].
  - A later merge that takes another ticket's whole version of a probed file is measured the same way, against git's own merge of its parents (P-5 (c)) [DEC-754].
  - A reopened FULL ticket whose earlier round was merged back before its final probe closes when the probed code at the closed head is the final probed code [DEC-754].
  - A merge whose probed paths are what git's own merge of its parents gives, and another ticket's merge holding the probed commit on neither side, pass as before; W2-01's acceptance cases stay green [W2-H047, W2-M202].
  - **The accepted-red ratchet (DEC-757 item 2.1).** A red whose exact test id the path map's `accepted_reds` lists, with an ACCEPTED owner decision naming it, a reason and the ticket that fixes it, does not refuse the close; the close names it with its decision and fixing ticket. An entry counts only when the commit that added it carries `Role: owner`. Its core is one function W2-19 reuses for declared test commands (DEC-736) [DEC-757].
  - **Integration-side ticket edits (DEC-757 item 2.2).** A change to the ticket's file after its probed commit, made by a commit carrying `Role: orchestrator` or `Role: owner`, naming the ticket in `Task:` and changing only that file, is not a change to the probed code [DEC-757].
  - **The load-sensitive quarantine (DEC-757 item 2.3).** A test the path map's `load_sensitive` lists that fails in the close is re-run alone, in its own process, inside the same close; it counts as passed only if that re-run passes, and the close reports it by name with both results [DEC-757, DEC-372].
  - W2-53 closes through `gov close` with its own merged mechanism, its only reds the listed ones [DEC-757].
- **KPIs, failure:**
  - An acceptance test added on the ticket's branch before the probe and removed or changed by a later merge refuses the close.
  - A merge whose own merge git cannot compute, or cannot read, is judged against the probed code and never passes by default.
  - A red not on `accepted_reds` refuses the close. A listed red that passes refuses the close, naming the entry to remove. An entry added by a commit without `Role: owner`, or whose decision is not an ACCEPTED owner entry naming that test id, is refused, naming the entry; the list never grows without an owner decision [DEC-757].
  - A ticket-file change on the ticket's own side after the probe, or an integration-side commit that changes more than the ticket's file, still refuses [DEC-757].
  - A load-sensitive test that fails its isolated re-run refuses; a test not on `load_sensitive` is never re-run; no re-run is silent [DEC-757].
- **DEC-757 (owner, 2026-10-17):** scope widened by P-W2-19 (a): the owner-accepted known-red ratchet (`accepted_reds` in the path map, whose first entries the owner commits), integration-side ticket edits, and the named load-sensitive quarantine (`load_sensitive`); est. 40 -> 160. W2-53 closes through `gov close` with its own merged mechanism. W2-19 reuses the ratchet's core.
