---
id: DAEO-rmhj
status: in_progress
deps: []
links: [DAEO-f58b, DAEO-0pyc]
created: 2026-11-07T15:48:35Z
type: task
priority: 1
assignee: engineer
external-ref: W2-138
tags: [wave-2, implementation, retrieval, standard]
wbs_id: W2-138
title: 'The store''s commit in every search result, and the worker''s check of each item''s line hash against its own file (DEC-1090 (3), PAT-1 G2 and G4)'
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on: []
allowed_paths:
- src/gov/retrieve/command.py
- src/gov/retrieval/retrieve.py
- src/gov/retrieval/validate.py
- template/governance/kernel/skills/retrieval/SKILL.md
- tests/unit/retrieve/test_w2_138*
- tests/unit/retrieval/test_w2_138*
- docs/changes/W2-138-evidence.md
kpis:
  success:
  - 'S1 Every gov retrieve result names the store it answered from: --json carries result.store = {"commit": <the full commit the store was built at>, "root": <the store folder, the link resolved once>}, and the text form a first line "store: <commit, 12 digits> (<folder>)". Verify: a planted store built at a known commit, and a link to it [DEC-1090 (3)]'
  - 'S2 The store is resolved once per search: every facet of one search reads the same folder, even when the link is switched during the search (W2-116''s R2-F1). Verify: a test that switches a planted link between the facets'' reads [DEC-1090 (3)]'
  - 'S3 CONTINUATION_INVALID names the commit the token was made on and the store''s commit now (the token carries its store''s commit). Verify: a token made on one planted store and replayed on another [DEC-1090 (3)]'
  - 'S4 Each evidence item''s sha256 is the sha256 of exactly the lines start_line to end_line of its path at result.store.commit, so a worker can compare it with the same lines in its own tree. Verify: for every item of a planted search, hashing those lines of the file at that commit gives its sha256 [DEC-1090 (3)]'
  - 'S5 The retrieval skill (template/governance/kernel/skills/retrieval/SKILL.md, step 5) gains one line: before relying on an evidence item, compare its sha256 with the sha256 of the same lines in your own tree; if they differ, your tree is behind or ahead of the store at result.store.commit: read the store''s text with git show <commit>:<path>, and never cite the store''s line numbers as your tree''s. The generated .claude copy follows at the lift''s re-pin ACT. Verify: the skill''s text, and the skills check [DEC-1090 (3)]'
  failure:
  - 'A result without the store''s commit.'
  - 'Two facets of one search answered from two store folders.'
  - 'An evidence item whose sha256 is not the hash of its own lines at the named commit.'
profile: STANDARD
sources:
- DEC-1090
- DEC-1087
- DEC-1072
est_loc: 150
acceptance_tests:
  path: tests/acceptance/W2-138/
  author: independent-test-designer (MR-3), from these KPI lines, before the engineer; planted stores and links in a temporary folder, no real model
track: B
list_rows: []
needs:
- src/gov/retrieve/command.py
- src/gov/retrieval/retrieve.py
waits_on: []
---
# W2-138 The store's commit in every search result, and the line-hash check

The owner's DEC-1090 (3), from PAT-1's gaps G2 and G4 (`governance/project/orchestration/packages/LIFT-1/PAT-1-RESULT.md`
§6).

- **Why:** in PAT-1, two agents in two worktrees could not tell from a search result which commit the shared store
  held, and both were misled by line numbers once integrate moved past their trees (DEC-1089's lines are the
  register's version table in a tree one commit behind). Each item's `sha256` already settles "same or not" (found by
  PAT-1's agent A); nothing tells a worker to use it.
- **The brief line now:** the CTO adds the same line to its agents' common brief
  (`.gov-runtime/scratch/orchestrator/briefs/EMG-common.md`) at the same time as this ticket lands (DEC-1090 (3)).
- **Riding along:** W2-116's R2-F1 (the link resolved once per facet), which PAT-1 never saw happen but S1 needs, is
  S2 here. W2-116 (`DAEO-f58b`) keeps its S2 pass for the rest.
- **Timing (DEC-1090 (3), as W2-137):** tests first; built beside the experiments (CPU); live at the lift's re-pin,
  before the three layers start.
- **Est.:** about 150 lines with tests, half a day with its review.

[DEC-1090]
