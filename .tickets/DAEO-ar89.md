---
id: DAEO-ar89
status: in_progress
deps: []
links: [DAEO-zqvn]
created: 2026-11-11T01:07:01Z
type: task
priority: 4
assignee: engineer
external-ref: W2-155
tags: [wave-2, implementation, after-the-lift, performance]
wbs_id: W2-155
title: 'The warm query path profiled against W1-19''s 0.5 s budget; a simple cause fixed, or the evidence and options to the owner within a short time box'
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on: []
allowed_paths:
- src/gov/retrieve/**
- src/gov/retrieval/**
- tests/unit/retrieve/**
- tests/unit/retrieval/**
kpis:
  success:
  - 'S1 A profile of the warm real-model query path (the case of W1-19 and W2-13 that measures warm p95 with the real models) names where the time goes, stage by stage, and which retrieval changes since the budget last held added to it; the profile is kept as an evidence note in the ticket''s folder. Verify: the evidence note exists in the ticket''s folder and holds a table of the warm query''s stages with a time for each, a total, and a list of the retrieval changes since the budget last held with the time each adds [DEC-1125 (1)]'
  - 'S2 If a simple cause is found within the time box: it is fixed, and W1-19''s and W2-13''s warm real-model cases pass at 0.5 s p95 on an idle machine, with no other case made red. Verify: where a fix is made, the run of W1-19''s and W2-13''s warm real-model cases on an idle machine prints a p95 at or under 0.5 s for each, and the scoped test run of the changed paths has no new red; where none is made, the note says no simple cause was found [DEC-1125 (1), W1-19]'
  - 'S3 If no simple cause is found within the time box (2 lead-hours): work stops and the evidence and options go to the owner; the budget is not changed by this ticket. Verify: the lead''s checkpoint records show at most 2 lead-hours before a stop; the evidence note lists the options for the owner; the diff holds no change to the 0.5 s figure in W1-19''s or W2-13''s case [DEC-1125 (1), DEC-105]'
  failure:
  - 'More than the time box spent without stopping and reporting. Verify: the lead''s checkpoint records sum to at most 2 lead-hours, or a stop-and-report record exists at or before the 2 hours; work recorded past 2 hours with no report is this failure'
  - 'The 0.5 s budget, the case or its measure changed to make it pass. Verify: the ticket''s diff of W1-19''s and W2-13''s warm real-model cases and of the measure they call is empty; any changed line there is this failure'
  - 'Any change outside the paths above. Verify: `git diff --name-only` of the ticket''s branch against its base lists only paths matched by the ticket''s allowed_paths'
profile: LITE
sources:
- DEC-1125
- DEC-1123
- DEC-105
- DAEO-t6hf
est_loc: 60
acceptance_tests:
  path: tests/acceptance/W1-19/
  author: 'existing: W1-19''s and W2-13''s warm real-model latency cases (no new acceptance tests; MR-3 holds for any case change)'
track: A
list_rows: []
needs: []
reads:
- src/gov/retrieve/**
- src/gov/retrieval/**
plan_override: DEC-1157  # its waits (W2-138, W2-145) are merged into w2/integrate; merged counts as met for starting (DEC-1157 (9)); closing still waits for them
waits_on:
- DAEO-rmhj  # W2-138 and W2-145 write the retrieval and reranker paths first (P1); the profile follows them
- DAEO-2tfd
---
# W2-155 The warm query path profiled: W1-19's 0.5 s budget

Filed by the CTO on the owner's decision DEC-1125 (1), 2026-11-11: **after the lift, low priority.**

- **Why:** D-10 run 2 (11-10, head `078e972d5`) measured the warm real-model query p95 at 0.543 s (W1-19) and 0.587 s
  (W2-13) against the 0.5 s budget; both red alone on an idle machine, no `src` change since run 1, the query server
  on the GPU. Earlier D-10 measures on 11-10 read 0.54-0.58 s even at low load. The owner ruled it a named red for the
  re-pin and the lift; the budget stays as written (DECIDED-NOT-DONE row 110).
- **The owner's note for whoever takes it:** profile the warm query path, including the retrieval changes since the
  budget last held, but do not over-spend time on it: the gap is not noticeable and does no harm. If a simple cause is
  found, fix it; if not within a short time box, stop and bring the owner the evidence and options instead.

## Interface (stated at claim by the CTO, DEC-1157 (3), 2026-11-12 23:55)

- **No interface change:** every public function and command in `src/gov/retrieve/**` and `src/gov/retrieval/**` keeps its signature, its output and its exit codes; `gov retrieve`'s results for the same store and query are unchanged (same items, same order, same fields), only faster.
- **The profile record:** `docs/research/` is outside the paths, so the profile (where the warm query's 0.54-0.59 s goes, by stage, with the method and the machine's load) is returned in the lead's DONE or PACKAGES, not committed; a fix, if any, is in the paths above with a unit case that pins the result unchanged.
- **The time box** (the owner's note): about two hours of the lead's work; with no simple cause found by then, PACKAGES with the evidence and the options.
- **The measure:** W1-19's and W2-13's warm real-model latency cases, run alone through heavy_slot.sh, at the machine's load recorded; never generating load.
