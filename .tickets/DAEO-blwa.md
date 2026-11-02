---
id: DAEO-blwa
status: in_progress
deps: []
links: [DAEO-f58b, DAEO-r30l]
created: 2026-11-01T21:35:00Z
type: task
priority: 0
assignee: engineer
external-ref: W2-122
tags: [wave-2, implementation, rebuild, speed, standard]
wbs_id: W2-122
title: 'Seeded rebuilds: a new worktree''s or a close copy''s store is seeded from a warm base (the integration store), so no rebuild is cold and each copy re-embeds only the files it changed (SIZING-1 option 0, DEC-1014)'
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on: []
allowed_paths:
- src/gov/rebuild/seed.py
- src/gov/rebuild/command.py
- tests/unit/rebuild/test_w2_122*
- docs/changes/W2-122-evidence.md
kpis:
  success:
  - '`gov rebuild --seed <store folder>` copies a warm base''s stores (the lexical, semantic and code-graph stores and the secrets cache''s entries) into the tree before rebuilding, then rebuilds incrementally: only files whose content differs from the base are re-embedded; the result is the same store, entry for entry, as a cold rebuild of the same tree (checked on a planted repository: the digests and every chunk''s vector equal) [DEC-1014, SIZING-1]'
  - 'A seed whose code fingerprint, embedder model or schema differs from the tree''s is refused, named, and the rebuild runs cold (fail closed: never a store that mixes two embedders) [DEC-1014]'
  - 'Measured, in docs/changes/W2-122-evidence.md: a new worktree''s first rebuild seeded from the integration store against a cold one, alone and with two others running, on this repository (the semantic stage''s seconds and the embedding requests sent) [DEC-1014, DEC-996 item 3 A]'
  - 'A product feature for every adopted repository: the warm base is the project''s configured integration store (W2-116''s, a path in the project''s configuration), never a path of this repository in the code; a project without one rebuilds cold, named [DEC-1014 item 6, DEC-982]'
  failure:
  - 'A seeded store that differs from a cold rebuild''s; a seed from another embedder or schema used [DEC-1014]'
profile: STANDARD
sources:
- DEC-1014
- DEC-1011
- DEC-1001
est_loc: 150
acceptance_tests:
  path: tests/acceptance/W2-122/
  author: independent-test-designer (MR-3)
track: A
list_rows: []
---
# W2-122 Seeded rebuilds

The owner's DEC-1014 (SIZING-1 option 0): today's slot waits come mostly from cold rebuilds (a new worktree's or a close
copy's first rebuild re-embeds the whole repository, 3,000 to 3,750 s with three at once). The integration store
(`~/gov-os-worktrees/W2-00-store`, the CTO's `refresh_integration_store.sh`) becomes the warm base every new worktree and
close copy is seeded from; it is refreshed after every landing (the CTO's tools wire the seed into worktree creation,
`close_build.py`, the merge queue's warm clones and the refresh, in the tools lane). This ticket is the product half:
`gov rebuild --seed`. Related: W2-116 (the integration store as a product command), which can build on it.

**DEC-1027 C (owner, 2026-11-02):** KPI 5 (a rebuild without its semantic store fails) moved to W2-124 (`DAEO-mb2t`); this ticket's K5 tests are retired by its test designer under that decision, and its seeding lands without it.
