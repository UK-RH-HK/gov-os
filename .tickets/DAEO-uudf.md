---
id: DAEO-uudf
status: open
deps: [DAEO-m7u4]
links: []
created: 2026-09-30T22:49:58Z
type: task
priority: 2
assignee: product-spec
external-ref: W1-08
tags: [wave-1, schema, standard]
wbs_id: W1-08
title: Record schemas and templates
class: schema
role: product-spec
depends_on:
- W1-05
allowed_paths:
- template/governance/kernel/schemas/**
- template/governance/kernel/templates/**
- governance/project/path-map.yaml
kpis:
  success:
  - JSON Schemas exist for MADR decision, ticket (class, role, depends_on, allowed_paths, kpis, profile, sources, est_loc, acceptance_tests), lesson, failure, research record, gate/decision package, checkpoint,
    path map
  - Every record type has a template that validates against its schema; this repository path map classifies every tracked path
  - The path-map schema gives each namespace a sensitivity class, permitted roles, retention, export policy, embedding policy, provenance and deletion/rebuild behaviour (Framework §16); the artefact identity
    fields of Contract v3 W1 are in the shared frontmatter; lesson records carry a lifecycle state (candidate → corroborated → scoped → proposed → validated → approved)
  failure:
  - A schema accepts a ticket without kpis, role or allowed_paths
  - Two schemas define the same id grammar differently
profile: STANDARD
sources:
- DEC-012
- G-04
- CAP-06
- CAP-08
- CAP-14
- CAP-41
- CAP-29
est_loc: 200
acceptance_tests:
  path: tests/acceptance/W1-08/
  author: independent-test-designer (MR-3, DEC-069); to be written before implementation
---
# W1-08 Record schemas and templates

One shared frontmatter convention and the schemas every checker uses.
