---
id: DAEO-8qvp
status: closed
deps: [DAEO-emkd]
links: []
created: 2026-09-30T22:49:58Z
type: task
priority: 1
assignee: engineer
external-ref: W1-03
tags: [wave-1, implementation, full]
wbs_id: W1-03
title: Post-command containment check
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on:
- W1-02
allowed_paths:
- src/gov/guard/containment*
- template/governance/kernel/hooks/posttooluse*
- template/governance/kernel/hooks/pretooluse*
- tests/unit/containment/**
kpis:
  success:
  - After every Bash call and at gov close, git status --porcelain is compared with allowed_paths; a change outside them is reported to the agent and recorded as a containment finding [CAP-58.a]
  - Changes under tests/acceptance/** by a non-test-designer role are restored from HEAD and the breach is recorded
  - All nine Bash write forms from S0b2 I-06 are caught
  failure:
  - Any out-of-scope change survives without a finding
  - A legitimate in-scope change is reverted
profile: FULL
sources:
- G-02
- DEC-076
- CAP-58
- MR-3
est_loc: 100
acceptance_tests:
  path: tests/acceptance/W1-03/
  author: independent-test-designer (MR-3, DEC-069); to be written before implementation
---
# W1-03 Post-command containment check

Second line of defence for Bash writes the guard cannot parse (G-02, moved to W1 by DEC-076).

## Notes

**2026-10-02T18:46:34Z**

Reopened and claimed 2026-10-02 as a repair for DEC-142 (W1-03 KD-5: a snapshot of another actor's call known to be over no longer blocks restoration) and DEC-143 (W1-03 KD-6: an acceptance test changed in a call that also moves HEAD non-forward is restored from the pre-call HEAD when attribution is certain). Claimed before the test design request (DEC-133); implementation waits for TESTS READY. KPIs unchanged.

**2026-10-03T13:41:57Z**

S2 repair 2026-10-03 (S2-A round 1, F-01). W1-45 replaces the orchestrator rule (DEC-156). The acceptance tests in tests/acceptance/W1-03/ that assert the old orchestrator rule are revised by the Independent Test Designer under W1-45, as rewrites after implementation (reason: owner correction, DEC-156). KPIs unchanged for every other role; no status change.
