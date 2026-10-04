---
id: DAEO-lc4q
status: in_progress
deps: [DAEO-uudf]
links: []
created: 2026-09-30T22:49:58Z
type: task
priority: 2
assignee: product-spec
external-ref: W1-12
tags: [wave-1, schema, standard]
wbs_id: W1-12
title: Readiness schema and proposal templates
class: schema
state_class: AUTHORITATIVE
role: product-spec
depends_on:
- W1-08
allowed_paths:
- template/openspec/schemas/**
- template/openspec/config.yaml
kpis:
  success:
  - The forked OpenSpec schema carries all 26 rows x 5 states exactly as docs/contract/readiness-dimensions.yaml [CAP-30.a]
  - Proposal templates pass openspec validate --strict on first use
  - The schema carries the capability-type table for STANDARD rows; a change to the taxonomy or to readiness-dimensions.yaml is accepted only with a linked CIT-E record [CAP-30.e]
  failure:
  - A row name or state differs from readiness-dimensions.yaml
  - A template fails validate --strict
profile: STANDARD
sources:
- G-07
- G-09
- DEC-085
- CAP-30
- MR-1
est_loc: 110
acceptance_tests:
  path: tests/acceptance/W1-12/
  author: independent-test-designer (MR-3, DEC-069); to be written before implementation
---
# W1-12 Readiness schema and proposal templates

The feature-readiness artefact (G-07) and the proposal templates (G-09).
