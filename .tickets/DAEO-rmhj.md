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
- tests/acceptance/W2-54/test_w2_54_query_cache.py  # its one-answer case compares two stores' answers whole, and S1's result.store.root names each folder (D-10's red-fix list) [DEC-1090 (3), DEC-1109 (2)]
- src/gov/retrieve/command.py
- src/gov/retrieval/retrieve.py
- src/gov/retrieval/validate.py
- src/gov/cli/main.py  # [DEC-1090] point (1): the text form's store line only
- tests/unit/retrieval/test_w2_131_register_ids.py  # [DEC-1090] the token's s key in the same-as-before guards
- tests/unit/retrieval/test_w2_133_gap_label.py  # [DEC-1090] same
- tests/unit/retrieval/test_w2_135_item_cap.py  # [DEC-1090] same
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

**TESTS-READY:** `tests/acceptance/W2-138/` at `999b12111` on `w2/W2-138-tests`: 18 cases, 13 red (S1 6, S2 1, S3 2,
S4 1, S5 3), 5 green guards. The byte rule and the S2 seam are in the tests' README.

**The designer's points settled (CTO, 2026-11-07, delegated, under DEC-1090 (3)):**
- **(1)** the text form's `store:` line is printed by the command's output path: `src/gov/cli/main.py` joins
  `allowed_paths` for that line only. [DEC-1090]
- **(2)** "the commit the store was built at" is the store's own fingerprint `head`, not the folder's HEAD now. Confirmed.
- **(3)** either commit in full or as 12 digits, in `message` or `details`: accepted; a token from before this change
  (no commit in it) is refused `CONTINUATION_INVALID` as today, with "made before W2-138" in its message.
- **(4)** the chunker's `str.splitlines` against the item's `bytes.splitlines` (line numbers drift in a file with form
  feed, `\x1c`-`\x1e`, `\x85`, U+2028 or U+2029): a Wave 3 row, not ordinary work here.

**Built (engineer, 2026-11-07):** `w2/W2-138` at `dcda2701`; `gov accept W2-138` 18/18. The W2-112 socket cases pass
outside the sandbox (CTO: 34 passed). Left before the review: the 6 unit "same as before" guards of W2-131, W2-133 and
W2-135 compare decoded tokens without the new `s` key (the engineer, paths added); W2-133's acceptance
`test_w2_133_unchanged.py` 4 rows the same, by a test designer (`Rewrite-Reason: DEC-1090 (3)`). The engineer reported
seeing six call-site lines of its own acceptance tests through a repository-wide Grep after its build and accept: the
guard let a Grep tool call into its own ticket's acceptance folder through (to the owner as a guard gap). [DEC-1090]

**Merged (CTO, 2026-11-07):** the six unit guards (`0a20fdc1`) and W2-133's acceptance rows (`9a93f933`, designer)
revised; the scoped regression outside the sandbox 850 passed, 0 failed; review round 1 READY by `verdict.py`
(`governance/project/orchestration/reviews/w2-138.md`; F1-F4 Wave 3 rows: a store built from a dirty tree, two
refreshes within one search, plain output no longer pure JSON, the skill line's byte rule). Merged into `w2/integrate`;
live at the lift's re-pin (the pinned gov then prints the store's commit; the skill's generated `.claude` copy and the
EMG-common brief line go with that ACT). Formal close at the lift. [DEC-1090]
