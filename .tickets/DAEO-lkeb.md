---
id: DAEO-lkeb
status: closed
deps: [DAEO-7nne]
links: []
created: 2026-09-30T22:49:58Z
type: task
priority: 2
assignee: engineer
external-ref: W1-16
tags: [wave-1, implementation, full]
wbs_id: W1-16
title: codebase-memory wrapper
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on:
- W1-15
allowed_paths:
- src/gov/codeintel/**
- tests/unit/codeintel/**
- template/.gitleaks.toml
- .gitleaks.toml
- src/gov/secrets/**
- tests/unit/secrets/**
kpis:
  success:
  - The index lives in a per-repository home under .gov-runtime/; list_projects in one repository shows only its own project [CAP-12.b]
  - A secret-exclusion test proves no planted secret enters the codebase-memory index [CAP-03.e, CAP-12.b]
  - 'Definitions, references, callers, impact and dead code are answered across Rust, Python and TypeScript on the dev tiers, before and after a rename: callers/impact hit@5 >= 60 % (S0b2 C1 baseline) [CAP-12.a]'
  - 'The gov-token rule of template/.gitleaks.toml and .gitleaks.toml flags a prefixed string (sk, pk, rk or tok, then _ or -) only when its body holds a digit, or both an upper-case and a lower-case letter: an ordinary identifier with such a prefix is not flagged and its file reaches the index, a token-shaped string is still flagged, and the seven dev canaries are still detected; the requirement is in the rule itself, not in an allowlist; the W1-15 acceptance tests that assert the old rule are revised (DEC-324, DEC-325)'
  failure:
  - A file whose only match is an ordinary identifier with a token prefix is kept out of an index
  - An index file of this repository exists outside .gov-runtime/ after a run
  - A planted secret is found in the code graph
profile: FULL
sources:
- G-06
- DEC-074 Q10
- DEC-076
- CAP-12
- CAP-03
est_loc: 50
acceptance_tests:
  path: tests/acceptance/W1-16/
  author: independent-test-designer (MR-3, DEC-069); to be written before implementation
---
# W1-16 codebase-memory wrapper

Per-repository home and secret exclusion for codebase-memory-mcp 0.11.0 (DEC-076).
