---
id: DAEO-a3u2
status: open
deps: [DAEO-jsg1]
links: []
created: 2026-10-30T22:14:08Z
type: task
priority: 1
assignee: engineer
external-ref: W2-91
tags: [wave-2, implementation, memory, standard, keystone-4]
wbs_id: W2-91
title: 'Full embeddings: the root files, the governance overlay and schemas/ embedded; the hidden half, the generated copies and the old carried cli/ stay out'
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on: [DAEO-jsg1]
allowed_paths:
- governance/project/path-map.yaml
- tests/unit/retrieval/test_w2_91*
- docs/research/W2-91-memory-measure.md
kpis:
  success:
  - 'After a rebuild with the embedder, the tracked root files (CLAUDE.md, README.md, AGENTS.md and the rest the root-files namespace holds), every tracked file under governance/** and every tracked file under schemas/** have vectors; the count of chunks with vectors under each is recorded from the clone''s store [DEC-957, DEC-954 Q9c, CAP-10.a]'
  - 'What stays out stays out: fixtures/** (the hidden half), .claude/** and .rulesync/** (generated copies), template/.rulesync/** and the vendored parts W2-86 placed, and cli/** (the old carried code) have no vector; schemas/** gets a namespace of its own so cli/** keeps not embedded [DEC-957, DEC-388, DEC-820 (d)]'
  - 'The restricted overlay stays restricted: governance/** keeps sensitivity restricted and export_policy denied; the ticket shows, from the code, that the indexer reads embedding_policy only and the export path still refuses the overlay, with a planted export case; embedding it changes no export or sharing rule [DEC-957, DEC-856, DEC-887]'
  - 'The path map states it in its two valid values only, every tracked path matches exactly one namespace, and the indexer''s code is not changed [DEC-694, DEC-388]'
  - 'Nothing else moves: for every tracked path outside the newly embedded sets, the embedding verdict is the same at the head as at the base; the vector sets differ only by the newly embedded files [DEC-381]'
  - 'W2-61''s measure is re-run on the visible half, control at the base and the head, both figures together (hit@5 against CAP-10''s floor of 85 and the owner''s target of 95 %, full evidence against 99 %) and the in-the-bundle count, per question, beside the last measure, in docs/research/W2-91-memory-measure.md [DEC-957, DEC-833, DEC-860]'
  failure:
  - 'A file under fixtures/, .claude/, .rulesync/ or cli/ embedded.'
  - 'The overlay''s sensitivity or export policy changed, or the overlay exported.'
  - 'A namespace with a value other than embedded or not embedded, or a tracked path in no namespace or in two.'
  - 'A figure of the measure reported without the other, or the hidden half read or run.'
profile: STANDARD
sources:
- DEC-957
- DEC-954
- DEC-388
- DEC-694
- DEC-381
- DEC-856
- DEC-887
- DEC-820
- DEC-833
- DEC-860
- CAP-10.a
est_loc: 30
acceptance_tests:
  path: tests/acceptance/W2-91/
  author: independent-test-designer (MR-3); written before implementation; reads this repository's path map and tracked files and a planted export case, writes nothing in this repository; no embedder needed
track: B
list_rows: []
---
# W2-91 Full embeddings: the root files, the governance overlay and schemas/

Card: MEMORY-SPEC-MAP gap 1, resolved by the owner in DEC-957 ("full embeddings: the root files, `governance/**` and `schemas/**`; the hidden half and generated copies stay out"); one of the seven gaps closed before memory is called ready.

- **Why:** after W2-86, only `template/` joins the embedded set. The root files, the governance overlay (prompts, briefs, packages, the plan's record, session summaries) and `schemas/**` are still lexical-only, so a question phrased in other words than theirs misses them (MEMORY-SPEC-MAP §A.1 row 4).
- **What changes:** the path map's `namespaces:` block only: `root-files` and `project-overlay` say `embedded`; `carried-code` is split so `schemas/**` has its own namespace (embedded) and `cli/**` stays not embedded. No code changes.
- **The one check first:** `project-overlay` is `sensitivity: restricted`, `export_policy: denied`. The ticket shows from the code that sensitivity is read by export, not by the indexer, and keeps both as they are.
- **Order:** after W2-86 (same block of the same file; it depends on it). W2-87 adds a different top-level block: split by lines; whichever merges second merges back.
- **The re-measure:** W2-61's procedure, as W2-86's.
