---
id: DAEO-rxln
status: closed
deps: [DAEO-4yyl, DAEO-7nne]
links: []
created: 2026-09-30T22:49:58Z
type: task
priority: 1
assignee: engineer
external-ref: W1-17
tags: [wave-1, implementation, standard]
wbs_id: W1-17
title: Lexical index and shared store
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on:
- W1-10
- W1-15
allowed_paths:
- src/gov/retrieval/lexical*
- src/gov/retrieval/chunking*
- src/gov/retrieval/store*
- cli/govbridge/**
- tests/unit/retrieval/**
- template/governance/kernel/checks/index-freshness*
kpis:
  success:
  - Carried FTS5 and chunking ported into src/gov; blob-hash incremental index in the shared store; every chunk record carries parent_id (section for documents, function/module for code) (DEC-091) [CAP-18.b]
  - Changed blobs re-index before the next retrieval (2.8 s scale on a-dev); an empty or stale index is reported, never returned as absent [CAP-17.a]
  - 'Registers the index-freshness family check: the index digest matches the tracked blobs, and a stale index is reported [CAP-38.b]'
  - The corpus is the whole tracked repository minus what the secret filter and the path map exclude; there is no hand-kept include list [CAP-03.d]
  - An exact string, identifier or error-message query returns every occurrence with file path and line [CAP-11.a]
  failure:
  - A retrieval returns pre-edit text as current
  - Rebuild digest differs between two runs
profile: STANDARD
sources:
- G-17
- G-20
- G-21
- DEC-091
- CAP-07
- CAP-11
- CAP-17
- CAP-18
- CAP-03
- CAP-38
est_loc: 240
acceptance_tests:
  path: tests/acceptance/W1-17/
  author: independent-test-designer (MR-3, DEC-069); to be written before implementation
---
# W1-17 Lexical index and shared store

Lexical part of R1 in the shared store with zero-result semantics.
