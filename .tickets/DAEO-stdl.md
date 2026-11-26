---
id: DAEO-stdl
status: open
deps: []
links: []
created: 2026-11-26T11:30:00Z
type: task
priority: 2
assignee: engineer
external-ref: W2-213
tags: [layout, classification, rubric, path-map, adoption, imports, kit]
wbs_id: W2-213
title: "A standard repository layout and classification by rubric: the path map follows a standard, never words in paths; agents class in parallel in a fixed form, code merges and checks, the owner approves an owned repository's moves, code executes and rolls back"
class: implementation
kind: feature
approved_by: DEC-1255
state_class: AUTHORITATIVE
role: engineer
profile: FULL
depends_on: []
waits_on: [the classification rubric's yes (DEC-1255 (3)), then this ticket's specification]
specification: null
allowed_paths: []
kpis:
  success: []
  failure: []
non_goals:
- Restructuring Gov OS itself (it keeps its classing until restructuring pays; its tests pin its paths)
- Restructuring an imported tool or code (it sits whole in imports/<name>/ with one class)
sources: [DEC-1255, DEC-1254, DEC-1222, DEC-1228, DEC-1252]
acceptance_tests:
  path: tests/acceptance/W2-213/
  author: independent-test-designer (MR-3); written before implementation, from the specification
track: F
---
# W2-213: a standard repository layout and classification by rubric

Approved as a feature by the owner on 2026-11-26 (DEC-1255 (2)); the integration plan's F-5. **Not ready:** its KPI lines and
allowed paths come from its specification, which is written only after the classification rubric (DEC-1255 (3)) has the owner's yes
and joins the rubrics register. It does not hold 0.1.8; at the earliest it rides the release after 0.1.9.

## The owner's scope (DEC-1255 (2), his words in short)
- **The standard, in the kit:** where code, tests, specs (`docs/specs`), research (`docs/research`), governance, everything stale (one
  `archive/` folder) and everything a repository brings in (`imports/<name>/`) live; the path map's namespaces and classes fixed by it.
- **Owned repositories** (EXAMIN, ASMO OS) are restructured to the standard at adoption's A6, with the owner's yes on the moves; their
  path map then follows the standard. **A new repository** starts in it: `gov init` (I-25). **An import** (REA, Startup Launchpad, a
  library) is never restructured: whole in `imports/<name>/`, one class (use, absorb or study). **Gov OS** keeps its classing for now.
- **How:** the rubric becomes code (classes, rules, where each class lives); agents class each file, folder and piece of material in a
  fixed form (path, class, destination, reason), over disjoint chunks by path, up to ten in parallel within the machine's gate; code
  merges and checks (every tracked file classed exactly once, every class valid, every destination where the standard puts it; a gap, a
  double or a conflict back to its agent); the orchestrator reviews the merged classification and the restructuring plan and brings the
  owner an owned repository's moves; code executes the approved plan (moves, path map regenerated from the standard, memory rebuilt, the
  impact-selected tests, rollback on any break). The same flow for adoption, an import, installing a tool, testing a tool before use,
  and retiring.

## Why
D3's adoption check guessed staleness from words in paths (I-40, DEC-1254 E-02): every guess needs a new exception; a standard does not.
