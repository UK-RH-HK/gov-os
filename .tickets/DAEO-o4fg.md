---
id: DAEO-o4fg
status: open
deps: [DAEO-6cc2]
links: []
created: 2026-10-03T13:05:33Z
type: task
priority: 2
assignee: engineer
external-ref: W1-47
tags: [wave-1, implementation, full]
wbs_id: W1-47
title: 'Guard hardening: escape hatch, failed commands, oracle path'
class: implementation
role: engineer
depends_on:
- W1-45
allowed_paths:
- src/gov/guard/**
- template/governance/kernel/hooks/pretooluse*
- template/governance/kernel/hooks/posttooluse*
- template/governance/kernel/settings*
- .claude/settings.json
- tests/unit/guard/**
kpis:
  success:
  - 'The guard''s PreToolUse hook denies any Bash call carrying dangerouslyDisableSandbox: true, whatever the role [CAP-62.a]'
  - The containment check is registered on PostToolUseFailure as well as PostToolUse, in this repository's settings and in the kernel template; a command that writes a file and then fails is caught [CAP-58.f]
  - The repository's committed .claude/settings.json carries a Read deny rule with the qualification oracle's absolute path (DEC-162) [CAP-49.c]
  - The guard denies any Read, Grep, Glob or Bash call whose input names the oracle path, for every role, the orchestrator included; the path is a guard configuration value and the tests use a stand-in
    path (DEC-162) [CAP-49.c]
  failure:
  - 'A Bash call carrying dangerouslyDisableSandbox: true reaches execution'
  - A session started in the repository root reads the oracle through Read, Grep, Glob or a Bash command that names its path
  - An acceptance test or implementation file of this ticket reads the qualification oracle
profile: FULL
sources:
- DEC-152
- DEC-153
- DEC-162
- EXP-001
- CAP-49
- CAP-58
- CAP-62
est_loc: 60
acceptance_tests:
  path: tests/acceptance/W1-47/
  author: independent-test-designer (MR-3, DEC-069); to be written before implementation
---
# W1-47 Guard hardening: escape hatch, failed commands, oracle path

DEC-153 ticket 2 and DEC-162. Follows W1-45 because both change the same guard files.

- `PostToolUseFailure` for Bash is already registered in this repository's settings by W1-05; this ticket makes the
  registration a tested requirement, here and in the kernel template.
- The oracle is hidden from every session started in the repository root by two layers: the committed `Read` deny rule
  and the guard rule. An opaque Bash read in the orchestrator's own session is an accepted residual (DEC-162,
  `governance/project/bootstrap.md`).
