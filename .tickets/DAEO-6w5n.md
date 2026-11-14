---
id: DAEO-6w5n
status: open
deps: [DAEO-cb2b]
links: [DAEO-cb2b]
created: 2026-11-12T01:50:00Z
type: task
priority: 1
assignee: engineer
external-ref: W2-121d
tags: [wave-2, dispatch, full, wave-3, deferred]
wbs_id: W2-121d
title: "gov dispatch, part d: watch and launch lead: gov watch wakes on key results, merges from integration never wake, gov launch lead builds the invocation"
class: implementation
state_class: AUTHORITATIVE
role: engineer
profile: FULL
depends_on: [DAEO-cb2b]
waits_on: []
allowed_paths:
- src/gov/watch/**
- src/gov/launch/**
- tests/unit/watch/test_w2_121d*
- tests/unit/launch/test_w2_121d*
est_loc: 400
kpis:
  success:
  - '`gov watch` wakes its caller when a lead''s worktree gains a commit whose subject marks a key result (a probe record, a measure, a package, a baseline) and when a lead returns, each once, named [DEC-952 item 3, DEC-983, DEC-982]; where a dispatcher runs, gov watch only reads its inbox and never marks a return seen Verify: a planted lead worktree gains a commit marking a key result (probe record, measure, package, baseline) and a lead returns: `gov watch` wakes its caller once for each, named; with a dispatcher running, `gov watch` only reads the inbox and the return is not marked seen. [DEC-1009, SMART-WORK-3] [moved from W2-118 S1, DEC-1083]'
  - 'A commit brought into a lead''s branch by a merge from the integration branch never wakes the caller Verify: a planted lead branch merged from the integration branch: `gov watch` does not wake its caller for the merged-in commit. [DEC-1003, SMART-WORK-3] [moved from W2-118 S3, DEC-1083]'
  - 'gov launch lead <ticket> builds the whole lead invocation (absolute paths, the identity in --settings, the model, background mode, the log and PID files) and passes the resource gate [DEC-715, W2-H046]. Verify: `gov launch lead <ticket>` on a planted ticket prints or writes an invocation holding absolute paths, the identity in --settings, the model, background mode, and the log and PID files, and the resource gate''s check ran before it started (a planted shut gate refuses). [moved from W2-21 S1, DEC-1083]'
  failure:
  - 'A key result or a return reported twice, or not at all. Verify: a planted key-result commit and a planted return, each present through several passes: each is reported once, and each planted one is reported (none missing). [moved from W2-118 F1, DEC-1083]'
non_goals:
- the dispatcher core (W2-121, part a) and the other parts
done_when: [DOD-1, DOD-2, DOD-3, DOD-4, DOD-5, DOD-6]
sources: [DEC-1007, DEC-1008, DEC-1003, DEC-979, DEC-998, DEC-1009, DEC-1010, DEC-1014, DEC-1015, DEC-1018, DEC-1030, DEC-1031, DEC-1083, DEC-1084, DEC-1088, DEC-715, DEC-944, DEC-952, DEC-982, DEC-983, DEC-989, DEC-995, DAEO-ts4y, DAEO-1ahb]
acceptance_tests:
  path: tests/acceptance/W2-121d/
  author: independent-test-designer (MR-3); written before implementation
track: A
---
# W2-121d gov dispatch, part d

Split from W2-121 (DAEO-cb2b) by the CTO's delegated decision on its run 1's P-W2-121-1 (a) and P-W2-121-3 (a), 2026-11-12: these KPI lines moved word for word; it builds on part a's Interface (in W2-121's ticket) and runs after it. The reference is the CTO's dispatcher (`governance/project/orchestration/tools/dispatch/`), never a target.

## Parked (the owner, DEC-1142 (8), 2026-11-12 ~09:50)

Parked in docs/plan/WAVE_3_PARKING.md as W3-P34: filed or split by the CTO without the owner's P1 (DEC-974; the prompt's §3). Not started again in Wave 2 without the owner's decision.
