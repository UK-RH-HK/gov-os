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
- governance/project/held-out.yaml
- tests/unit/guard/**
kpis:
  success:
  - 'The guard''s PreToolUse hook denies any Bash call carrying dangerouslyDisableSandbox: true, whatever the role [CAP-62.a]'
  - The containment check is registered on PostToolUseFailure as well as PostToolUse, in this repository's settings and in the kernel template; a command that writes a file and then fails is caught [CAP-58.f]
  - 'The repository''s committed .claude/settings.json carries a Read deny rule with the qualification oracle''s absolute path; the path is held in one file, governance/project/held-out.yaml, and the acceptance test checks the committed rule statically, by its presence and its exact path in the file: it reads the configured value from held-out.yaml and asserts that the committed rule is built from it, so the test file carries no literal path and opens nothing under that path (DEC-162) [CAP-49.c]'
  - 'The guard denies any tool call whose input names the oracle path (a Read, Grep, Glob or Bash call, or any other tool), for every role, the orchestrator included; the guard takes the path from governance/project/held-out.yaml, and the guard''s behaviour is tested against a stand-in path, never the qualification oracle (DEC-162) [CAP-49.c]'
  failure:
  - 'A Bash call carrying dangerouslyDisableSandbox: true reaches execution'
  - Any tool call whose input names the oracle path is allowed, whatever the tool and whatever the call does (a read, a listing, a search, a write or a command), in a session started in the repository root
  - The committed Read deny rule is missing from .claude/settings.json, or its path differs from the oracle's absolute path
  - An acceptance test of this ticket reads or names the qualification oracle
  - An implementation file of this ticket reads the qualification oracle, or names its path anywhere but governance/project/held-out.yaml and the committed Read deny rule
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
- **How the two oracle layers are tested (S2-A round 1, F-04).** The committed `Read` deny rule is tested statically:
  the test reads the configured path from `governance/project/held-out.yaml`, the one file that holds it, and checks
  that the rule in `.claude/settings.json` is present and built from that exact value. The guard rule is tested by
  behaviour, against a stand-in path set through the same configuration. No test opens or names the oracle. The
  launcher (W1-46) takes the path from the same file.
- The failure KPI covers any allowed tool call that names the oracle path, not only reads.
- The oracle is hidden from every session started in the repository root by two layers: the committed `Read` deny rule
  and the guard rule. An opaque Bash read in the orchestrator's own session is an accepted residual (DEC-162,
  `governance/project/bootstrap.md`).
