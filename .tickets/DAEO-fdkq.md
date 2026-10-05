---
id: DAEO-fdkq
status: open
deps: [DAEO-8nue, DAEO-fygv, DAEO-2lwj]
links: []
created: 2026-09-30T22:49:59Z
type: task
priority: 2
assignee: engineer
external-ref: W1-40
tags: [wave-1, config, standard]
wbs_id: W1-40
title: lefthook and CI workflow
class: config
state_class: AUTHORITATIVE
role: engineer
depends_on:
- W1-22
- W1-26
- W1-30
allowed_paths:
- lefthook.yml
- template/lefthook.yml.jinja
- .github/workflows/**
- template/.github/workflows/**
- src/gov/ci/**
- tests/unit/ci/**
kpis:
  success:
  - pre-commit runs G1-G2; pre-push runs G3 including model-dependent tests and writes an evidence record bound to the head commit [CAP-39.a]
  - GitHub Actions runs the deterministic checks and fails when the evidence record is missing or for another commit; carrier (git note or commit) chosen and documented [CAP-39.a]
  - pre-commit also runs the second gitleaks scan, with the project's rules alone (DEC-347, DEC-369)
  failure:
  - CI downloads models or needs a GPU
  - A push with a failing G3 check leaves CI green
profile: STANDARD
sources:
- S0a-G-11
- DEC-075
- DEC-087
- CAP-39
est_loc: 80
acceptance_tests:
  path: tests/acceptance/W1-40/
  author: independent-test-designer (MR-3, DEC-069); to be written before implementation
---
# W1-40 lefthook and CI workflow

G1-G5 tiers (DEC-075, DEC-087).
