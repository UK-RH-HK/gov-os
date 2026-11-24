---
id: DAEO-d3sr
status: in_progress
deps: []
links: [DAEO-l78m, DAEO-d3d4]
created: 2026-11-24T09:00:00Z
type: task
kind: feature
priority: 1
assignee: engineer
external-ref: W2-212
tags: [adoption, retrieval, stale-route, emergency-2, release-0.1.6]
wbs_id: W2-212
title: "The route that keeps stale, superseded and legacy documents out of default memory (D3): a declared class on a path-map namespace, the default bundle without it, found on purpose by path or flag, set by adoption, named by doctor"
class: implementation
state_class: AUTHORITATIVE
role: engineer
profile: STANDARD
depends_on: []
waits_on: []
closes: []
allowed_paths:
- src/gov/retrieval/**
- src/gov/adopt/**
- src/gov/doctor/**
- src/gov/config/**
- src/gov/check/pathmap.py
- src/gov/cli/**
- template/governance/kernel/schemas/path-map.schema.json
- template/governance/kernel/skills/adopt/**
- template/.rulesync/skills/adopt/**
- tests/unit/retrieval/**
- tests/unit/adopt/**
- tests/unit/doctor/**
- tests/acceptance/W2-212/**
est_loc: 450
specification: docs/emergency-2/W2-81-PROVING-RUN-0.1.4-ANALYSIS.md
kpis:
  success:
  - 'SR-1 Out of the default bundle. In an adopted repository, a document in a namespace the path map marks superseded, historical or legacy (a declared class on the namespace, the optional field `stale_class`, never a guess from its name) is absent from `gov retrieve`''s default bundle, lexical and semantic alike, and a current document on the same topic is present. Verify: the python-app stand-in''s `docs/design/lending.md` absent for the lending question, `lending-v2.md` present.'
  - 'SR-2 Still findable on purpose. Such a document is still found when asked for by path or by `gov retrieve --include-stale`, and the bundle says it is stale (`stale: true` and its `stale_class`) when it shows it. Verify: the same repository, the lending question with `--include-stale` and a question naming `docs/design/lending.md`: the bundle lists it under `stale`, marked.'
  - 'SR-3 Adoption sets it. The adopt skill and the A3 form give such namespaces `stale_class` with `lexical_policy: not indexed` and `embedding_policy: not embedded`, and say so; A3 refuses a namespace whose name or paths say superseded, historical, legacy or archive and that lacks the class (`ADOPT_STALE_CLASS`), and gives a notice where only its description fields say so. Verify: a path map with `docs/legacy/**` unclassed is refused naming the namespace; the same with the class and policies is recorded.'
  - 'SR-4 Every adopted repository gets it. `gov update` carries the route (the schema and the skill are kernel files it copies); in an adopted repository whose path map has such namespaces without the class, `gov doctor` names each with the line to add, as a notice that never fails the run. Verify: a planted unclassed `legacy` namespace: doctor exits 0 and names it with the three lines.'
  failure:
  - 'F1 The class cannot fail open. A namespace with `stale_class` and a policy that keeps its files in the index or the vectors is CONFIG_INVALID naming the namespace, and a class value other than superseded, historical or legacy is too; a stale-class file already in the index (built before the class) is still left out of the default bundle.'
non_goals:
- 'The imports feature, a content-reading A2, and the refresh of the index after a path-map change (the Phase 0 lead''s)'
- 'Editing Gov OS''s or EXAMIN''s live path map'
sources: [DEC-1227, DEC-1228, docs/emergency-2/W2-81-PROVING-RUN-0.1.4-ANALYSIS.md, DAEO-l78m]
acceptance_tests:
  path: tests/acceptance/W2-212/
  author: independent-test-designer (MR-3); written before implementation
track: A
---
# W2-212: the stale route (D3)

The owner, 2026-11-24: build the route that keeps stale and superseded documents out of default memory now, on its own, in 0.1.6. DEC-1227 D3 (a). Spec: row A6 and fix 6 of `docs/emergency-2/W2-81-PROVING-RUN-0.1.4-ANALYSIS.md`.

## Design (the lead's choices)
- Namespace field `stale_class: superseded | historical | legacy` (optional). It requires `lexical_policy: not indexed` and `embedding_policy: not embedded`.
- Retrieval drops chunks of stale-class paths from every route unless `include_stale`; `--include-stale` and a path named in the question add a `stale` list to the bundle, read from the files, each entry `stale: true`.
- A3 refuses a name or path match without the class; a description-field match is a notice. `gov doctor` notices the same for an adopted repository.
