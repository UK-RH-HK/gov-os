---
id: DAEO-7nne
status: open
deps: [DAEO-drvn, DAEO-uudf]
links: []
created: 2026-09-30T22:49:58Z
type: task
priority: 2
assignee: engineer
external-ref: W1-15
tags: [wave-1, implementation, full]
wbs_id: W1-15
title: Secret rules and pre-index filter
class: implementation
role: engineer
depends_on:
- W1-07
- W1-08
allowed_paths:
- src/gov/secrets/**
- template/.gitleaks.toml
- .gitleaks.toml
- tests/unit/secrets/**
- template/governance/kernel/checks/secrets-indexing*
kpis:
  success:
  - .gitleaks.toml extends the defaults with token and canary rules; ARGUS_TOKEN_CANARY_4WM8 is detected
  - Every indexer calls the content filter before chunking; 0 of 7 dev canaries reach any store [CAP-03.a, CAP-03.e]
  - 'Indexers skip every namespace the path map classes as customer/runtime product data: a planted product-data file is absent from every governance store, packet and bundle [CAP-03.b]'
  - 'Registers the secrets-indexing family check: no planted secret or canary in any derived store [CAP-38.b]'
  failure:
  - Any planted secret appears in a derived store, packet or bundle
  - The filter relies on a hard-coded path list
profile: FULL
sources:
- G-12
- G-18
- DEC-074 Q8
- CAP-03
- CAP-38
est_loc: 70
acceptance_tests:
  path: tests/acceptance/W1-15/
  author: independent-test-designer (MR-3, DEC-069); to be written before implementation
---
# W1-15 Secret rules and pre-index filter

Content-based secret exclusion before every indexer (W1 gate).
