# P-WALLS-REANCHOR-1: how the weekly re-anchoring request reaches the walled writer (DECIDED-NOT-DONE row 203)

For the owner; short form. It blocks nothing before Monday 2026-11-16's slot, which runs by hand from
`packages/REANCHOR-LIST-20261116.md` either way.

## The question
W2-187's weekly maintenance pass (`gov.memaudit maintain`, item 6) writes `REANCHOR-<week>.json`: the gold questions
whose cited lines changed, by question id and entry number only. Today your operator carries it to the walled writer
by hand. ACT-WALLS-REANCHOR-1 was built to make the walls take it directly: the launcher `indep_launch.py` gains
`--reanchor <week>` on the writer's round 2, and the walls' `kinds.yaml` gains the input. Its built bundle is manifest
`f1b60d35…`, class (O), rehearsal 82 checks with 0 failures. Two of your rulings point different ways: DEC-1179 (6) G2
(the row 203 wording) names an ACT, while your later DEC-1180 (2) says `indep_launch.py` changes by a ticket. That is a
contradiction against a closed decision, so the choice is yours (DEC-105).

## The independent review (`.gov-runtime/scratch/orchestrator/reviews/act-walls-reanchor-1.md`)
**NOT READY, no blocking finding.** All of these held under the reviewer's own probes:
- no hidden text or id leaves the walls on any of 13 launch paths;
- a delivery failing part-way leaves the hidden half byte-identical;
- the APPROVED edit changes exactly one line and refuses 10 malformed variants, touching nothing;
- launches from clones on the old `kinds.yaml` are refused at stage 11, which fails closed.

Findings that need fixing whatever the route:
- **F1:** one manifest check spells out the real home path, so the reviewer brief's check 1 fails.
- **F3:** the request's id rule refuses upper-case ids. Gov OS's memory set uses `Q01`-style ids, so its request could
  never be served.
- **F4:** the new `kinds.yaml` must reach a launch clone (EXAMIN's included) before the audit that writes that week's
  request.

## Options
- **(A) Apply as built,** after F1, F3 and F4 are fixed and a narrow round 2 passes. You re-decide DEC-1180 (2) for this
  change. Cost: about 1 h, then your yes on the new sha8. Your operator applies the whole change by hand (code and tests
  included), with no independently designed acceptance tests for the flow.
- **(B) Code by ticket, walls by ACT.** W2-94 (DAEO-g87r, closed; it held `indep_launch.py` and built the one-question
  fix flow) is reopened within its purpose, so no new ticket. Its independent test designer writes the flow's
  acceptance cases, an engineer builds `--reanchor` from the bundle's after-copy with F3 fixed, and it gets a review and
  lands. Then a small class (O) ACT carries only `kinds.yaml` and the APPROVED line. Cost: one lead run (about 3 h) plus
  the small ACT and its review. It keeps DEC-1180 (2) as you ruled it.
- **(C) Defer:** the hand step continues every Monday.

**Recommendation: (B).** Confidence medium-high. It follows your later ruling, gets independently designed tests, and
nothing waits on it before Monday.

**Also needed for any route:** the re-anchoring brief for the walled writer (product-spec drafts it; you approve its
bytes once, as a fixed brief, DEC-1101 (2)). Without it the flow cannot run for real.

## Your line
`P-WALLS-REANCHOR-1 (B)` (or (A) or (C)), and `yes re-anchoring brief: draft it` to have product-spec draft the brief
for your approval.
