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
    path map [CAP-31.a, CAP-53.a]
  - Every record type has a template that validates against its schema; this repository path map classifies every tracked path [CAP-06.a]
  - The path-map schema gives each namespace a sensitivity class, permitted roles, retention, export policy, embedding policy, provenance and deletion/rebuild behaviour (Framework §16); the artefact identity
    fields of Contract v3 W1 are in the shared frontmatter; lesson records carry a lifecycle state (candidate → corroborated → scoped → proposed → validated → approved) [CAP-03.a, CAP-03.c, CAP-41.a, CAP-50.a]
  - The path-map schema classes every namespace as governance/development memory or customer/runtime product data, and one namespace cannot be both [CAP-03.b]
  - The overlay schema carries the project floor (enabled capabilities and policy strengths); it identifies each constitutional system at least minimally, and no overlay value may go below the kernel floor
    [CAP-06.e, CAP-54.b]
  - The shared frontmatter records state_class for every record type [CAP-07.b]
  - Lesson records carry a scope of PROJECT, PRODUCT or FRAMEWORK [CAP-41.c]
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
- CAP-03
- CAP-07
- CAP-29
- CAP-31
- CAP-50
- CAP-53
- CAP-54
est_loc: 200
acceptance_tests:
  path: tests/acceptance/W1-08/
  author: independent-test-designer (MR-3, DEC-069); to be written before implementation
---
# W1-08 Record schemas and templates

One shared frontmatter convention and the schemas every checker uses.
