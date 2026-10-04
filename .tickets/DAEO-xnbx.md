---
id: DAEO-xnbx
status: in_progress
deps: [DAEO-8qvp]
links: []
created: 2026-10-04T12:38:05Z
type: task
priority: 1
assignee: engineer
external-ref: W1-50
tags: [wave-1, implementation, full]
wbs_id: W1-50
title: Containment attribution by commit trailers
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on:
- W1-03
allowed_paths:
- src/gov/guard/containment*
- template/governance/kernel/hooks/posttooluse*
- template/governance/kernel/hooks/pretooluse*
- tests/unit/containment/**
kpis:
  success:
  - 'A forward HEAD move, including an integration merge by the orchestrator, is judged commit by commit: each commit''s paths against the allowed paths of its own Role and Task trailers, not against the caller (DEC-255) [CAP-58.h]'
  - A merge commit itself is not a finding when every commit it brings passes that check (DEC-255) [CAP-58.h]
  - A worker's commit made during another actor's call is judged by its own trailers (DEC-255) [CAP-58.h]
  - A commit with no Role or Task trailer is judged against the caller, as today (DEC-255) [CAP-58.h]
  failure:
  - An integration merge whose commits each stay inside the allowed paths of their own Role and Task trailers raises a finding
  - A commit that changes a path outside the allowed paths of its own Role and Task trailers raises no finding, whoever the caller is
  - A commit with no Role or Task trailer is judged by anything other than the caller
profile: FULL
sources:
- DEC-255
- DEC-253
- DEC-254
- DEC-182
- DEC-235
- DEC-076
- CAP-58
est_loc: 100
acceptance_tests:
  path: tests/acceptance/W1-50/
  author: independent-test-designer (MR-3, DEC-069); to be written before implementation
---
# W1-50 Containment attribution by commit trailers

Owner decision DEC-255, after the first integration merge of the parallel run (DEC-235): the post-command containment
check (W1-03) judged a HEAD move against the caller and flagged every move that contains a merge commit, and it
attributed a worker's commit to the call of the lead that was waiting for it. With this ticket a forward HEAD move is
judged commit by commit, each commit by its own `Role` and `Task` trailers (DEC-182).

- **Test design first, alone (DEC-256).** The test design batch runs now in its own worktree and is merged on its
  own. It also carries the revision of W1-01's `test_only_the_test_designer_commits_to_acceptance_tests` (DEC-253): an
  integration merge commit passes when every change it brings under `tests/acceptance/` comes from commits on the
  merged side carrying `Role: independent-test-designer`; every non-merge commit is checked as before. That revision
  is a rewrite after implementation, reason "owner decision: integration merges".
- **Implementation after W1-46 is merged (DEC-256)**, because both tickets touch `src/gov/guard/**` and the
  PreToolUse hook.
- Until this ticket closes, merge findings and worker-commit misattributions are records, not defects (DEC-254).

