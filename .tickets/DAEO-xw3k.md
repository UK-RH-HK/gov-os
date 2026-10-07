---
id: DAEO-xw3k
status: closed
deps: [DAEO-78bn, DAEO-lkeb, DAEO-rxln, DAEO-8nue]
links: []
created: 2026-09-30T22:49:59Z
type: task
priority: 2
assignee: engineer
external-ref: W1-27
tags: [wave-1, implementation, standard]
wbs_id: W1-27
title: gov doctor and gov rebuild
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on:
- W1-04
- W1-16
- W1-17
- W1-22
allowed_paths:
- src/gov/doctor/**
- src/gov/rebuild/**
- src/gov/config/**
- tests/unit/doctor/**
- template/governance/kernel/checks/recovery-rebuild*
kpis:
  success:
  - doctor reports pinned vs found tool versions, hooks wired, path map with zero unclassified paths, index freshness, canaries, framework.lock MATCH/DRIFT, per-repository isolation; non-zero on any failure
    [CAP-02.a, CAP-06.a, CAP-25.a]
  - rebuild recreates every derived store; two rebuilds give the same digest; a fresh clone plus doctor plus rebuild works [CAP-07.a, CAP-20.a, CAP-46.a]
  - 'Path-map compliance is checked by doctor: every tracked path matches a path-map entry, and a recorded reference to a moved path is reported [CAP-06.d]'
  - 'Registers the recovery/rebuild family check: derived state deleted and rebuilt gives the same digest [CAP-38.b]'
  - 'doctor reports an adoption level: a repository with only the kernel installed passes at the minimal level, and each completed adoption stage raises it toward ADOPTED_HEALTHY [CAP-54.a]'
  - doctor reports Claude Code drift (DEC-210, DEC-214); the CLI at ~/.local/bin/claude and the active VS Code extension differing from each other, either being newer than the registry's record, or the extension's bundled binary
    at the recorded version with another sha256, is reported as drift; the CLI or the active extension below the minimum, 2.1.285, or the CLI at the recorded version with another sha256, is a failure
  - doctor reports a missing governance/project/held-out.yaml in this repository, because the guard treats a missing file as no held-out rule (DEC-223)
  - gov validates governance/project/path-map.yaml against the kernel's path-map schema of W1-08, which replaces the minimal schema of W1-07 in src/gov/config/; the W1-07 acceptance cases that depend on the provisional shape
    are revised in this ticket's test design (DEC-185, DEC-189, DEC-228)
  failure:
  - doctor passes with a tool at the wrong version
  - rebuild needs anything not in git
profile: STANDARD
sources:
- S0a-G-04
- DEC-083
- CAP-02
- CAP-06
- CAP-07
- CAP-20
- CAP-25
- CAP-46
- CAP-48
- CAP-54
- CAP-38
- MR-4
est_loc: 230
acceptance_tests:
  path: tests/acceptance/W1-27/
  author: independent-test-designer (MR-3, DEC-069); to be written before implementation
---
# W1-27 gov doctor and gov rebuild

Installation health (MR-4) and the rebuild guarantee.
