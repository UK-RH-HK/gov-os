---
id: DAEO-c4pb
status: in_progress
deps: []
links: [DAEO-0pyc, DAEO-k4wm]
created: 2026-11-06T19:40:00Z
type: task
priority: 0
assignee: engineer
external-ref: W2-135
tags: [wave-2, implementation, retrieval, memory, standard]
wbs_id: W2-135
title: 'A line over 4,000 characters in a bundle item is sent as its first 4,000, the item marked cut, its lines cited unchanged: a guard against one-line files only (BUNDLE-BUDGET-1 (a), DEC-1086 B)'
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on: []
allowed_paths:
- src/gov/retrieval/retrieve.py
- src/gov/decisions/register.py
- tests/unit/retrieval/test_w2_135*
- docs/changes/W2-135-evidence.md
kpis:
  success:
  - 'S1 In an evidence item, each line over 4,000 characters is sent as its first 4,000 characters; every other line of the item is sent whole, so an item of ordinary lines is never cut however long it is; an item with a cut line carries cut: {"chars": <the item''s full text length>, "sent": <the length of the text sent>, "lines": [<the line numbers cut>]}; its path, start_line, end_line, id, chunk_id and sha256 (of the full span, as today) are unchanged, so a citation still names the whole span. Verify: unit tests on a planted repository with a one-line file of 24,575 characters, a 10,631-character line among ordinary lines in a Markdown file (only that line cut, its neighbours whole, in an item sent alone and in an expanded section), and an expanded section of 11,000 characters of ordinary lines (sent whole, no cut key) [DEC-1086 B, BUNDLE-BUDGET-1] [re-worded, DEC-1086 B: one-line files only, the review''s F1]'
  - 'S2 An item with no line over 4,000 characters is sent as today, with no cut key, whatever its total length; a register item narrowed from a cut parent carries a cut key only if its own lines hold a cut line (W2-135 review F2). Verify: unit tests [DEC-1086 B] [re-worded, DEC-1086 B, the review''s F2]'
  - 'S3 Nothing else changes: the same items in the same order, the batches, the expansions and their left-out spans, the repeats, the gaps, the continuation, and the budget''s used figure (still counted on the full text, as today). The reranker''s input is unchanged. Verify: a unit test comparing bundles field by field before and after on the planted repository, the cut text and the cut key apart [DEC-1086 B]'
  - 'S4 It lands on w2/integrate before re-pin window 4 is built, and the window carries it. Verify: the CTO''s check after the re-pin [DEC-1087 (1)]'
  failure:
  - 'An item over 4,000 characters sent whole, or a cut item without its cut key.'
  - 'A change to which items a bundle holds, their order, or their cited lines.'
profile: STANDARD
sources:
- DEC-1087
- DEC-1086
- DEC-1085
est_loc: 30
acceptance_tests:
  path: tests/acceptance/W2-135/
  author: independent-test-designer (MR-3), from these KPI lines, before the engineer
track: A
list_rows: []
---
# W2-135 A cap per item in the bundle

BUNDLE-BUDGET-1 (`governance/project/orchestration/packages/LIFT-1/BUNDLE-BUDGET-1.md`), option (a), approved by
DEC-1086 B as a guard against one-line files only. The bundle's total size is tested separately (the experiments' E5).

- **The cause:** a chunk is never shorter than one line (`src/gov/retrieval/chunking.py:102`), and the 6,000-token
  budget governs parent expansions only (`retrieve.py`, the expansion's `used + cost <= limit`). A one-line JSON file
  of 24,575 characters went out whole: m29's first call, 8,886 tokens. 13 of 688 calls were over the budget, all from
  one-line items.
- **Where:** `retrieve.py`'s `item()`, where an evidence item's `text` is set. The cut is of the sent text only. The
  budget's `used` keeps counting the full text, so S3 holds.
- **Order:** the independent test designer, then the engineer, then one review.

**Round 2 (CTO, 2026-11-06, DEC-1086 B; the review `reviews/w2-135.md`, READY by its verdict):** the review's F1 showed
that S1 as first worded cut any item over 4,000 characters, ordinary expanded sections included. In its probe, the line
that matched sat past character 4,000 of its section, so an agent would not see it. DEC-1086 B says "a guard against
one-line files only", so the first wording was the CTO's error.
- **S1 and S2 are re-worded to cut lines, not items.** `register.py` is added to the paths for F2: a narrowed register
  item kept its parent's stale `cut` key.
- **The designer** revises the cases to the new S1 and S2, and re-checks W2-133's pinned comparison (F3), which may no
  longer be touched once only long lines are cut. Then the engineer revises, then the same reviewer reviews round 2
  (the last, DEC-1010).
- **F4** (the measure's stack figures read the sent text) is noted for window 4's comparison with the pin.
