---
id: DAEO-fygv
status: open
deps: [DAEO-topz, DAEO-be7u, DAEO-w616]
links: []
created: 2026-09-30T22:49:59Z
type: task
priority: 2
assignee: engineer
external-ref: W1-26
tags: [wave-1, implementation, full]
wbs_id: W1-26
title: gov check G0-G2
class: implementation
role: engineer
depends_on:
- W1-09
- W1-11
- W1-13
allowed_paths:
- src/gov/check/**
- tests/unit/check/**
kpis:
  success:
  - Runs schema, id grammar, orphans, path map, adapter drift, openspec validate --strict, decision checker, readiness, ticket DAG acyclicity and field completeness, and the rule that no implementer allowed_paths
    covers tests/acceptance/**
  - Every policy key maps to a check or is declared informational (D-0003); each family is reported RED/YELLOW/GREEN [CAP-39.d]
  - Fails a specification with a required open readiness row that has no linked gap ticket (DEC-089) [CAP-30.b]
  - Each check declares hard-block or warning, and every result records its provenance (commit, check version, inputs hash) [CAP-39.d]
  - Fails a skill file whose content changed without a version change and a linked decision [CAP-24.c]
  - The check registry names all 17 governance test families of Contract v3 O2 (schema/invariants, graph integrity, index freshness, retrieval regression, authority/role limits, mutation scope, path-map
    compliance, context reproducibility, concurrency/claims, adapter/model portability, skill regression, command-contract consistency, secrets indexing, recovery/rebuild, fresh-agent reconstruction, product
    traceability, audit reproducibility), and each has at least one executable Wave 1 check; skill regression validates every skill file (frontmatter, version, size, referenced commands exist), and audit
    reproducibility resolves an audit report's cited commit, rows and evidence paths [CAP-38.b]
  - 'Fails a record that changes authority class without a decision: a research or lesson record cited as a decision or policy, or a superseded record used to satisfy a current requirement [CAP-01.c]'
  failure:
  - A planted defect of any listed family passes
  - The scope of a check is a hand-maintained list [CAP-58.a]
profile: FULL
sources:
- S0a-G-02
- DEC-041
- DEC-046
- DEC-089
- CAP-38
- MR-2
- MR-3
- CAP-01
- CAP-24
- CAP-30
- CAP-39
- CAP-58
est_loc: 310
acceptance_tests:
  path: tests/acceptance/W1-26/
  author: independent-test-designer (MR-3, DEC-069); to be written before implementation
---
# W1-26 gov check G0-G2

Deterministic governance checks, derived from the repository.
