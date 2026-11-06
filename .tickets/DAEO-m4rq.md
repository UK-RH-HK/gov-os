---
id: DAEO-m4rq
status: open
deps: [DAEO-h2k3]
links: [DAEO-h2k3]
created: 2026-11-06T15:40:00Z
type: task
priority: 1
assignee: engineer
external-ref: W2-134
tags: [wave-2, implementation, retrieval, memory, evaluation, standard]
wbs_id: W2-134
title: 'The memory measure re-anchors line-cited gold in memory for the commit it measures, and never writes the sets root (W2-61h S8''s code, DEC-1085 (2))'
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on:
- DAEO-h2k3
allowed_paths:
- src/gov/retrieval/measure.py
- tests/unit/retrieval/test_w2_134*
- docs/changes/W2-134-evidence.md
kpis:
  success:
  - 'S1 Before it scores, the measure finds each line-cited gold source''s block again in the commit it measures: the block is read at the source''s own commit, found once at the measured root (as repin_gold.py finds it), and the question is scored against those lines. A source whose block is unchanged keeps its lines. Verify: a unit test on a planted repository with two commits where a cited block moves down by inserted lines; the measure on the second commit scores a hit on the moved lines [DEC-1085 (2), DEC-1084, W2-61h S8]'
  - 'S2 The measure never writes the sets root or any label file. Two measures on different commits, run one after the other, score each commit against its own lines, and every file under a planted sets root is byte for byte as it was (hashed before and after). Verify: a unit test [DEC-1084, DEC-820 (d)]'
  - 'S3 A source whose block cannot be found at the measured root is named by question id and entry number only (never its text, path or lines), and counts as not found. Verify: a unit test with a planted source whose block is deleted in the second commit; the output holds the id and entry number and no text of the label [DEC-1084, DEC-1052 G-3]'
  - 'S4 Nothing else changes: with every cited block unmoved, the per-question lines and totals equal today''s output for the same run, and source families (W2-61h S7) are scored as before. Verify: a unit test comparing the output before and after on the planted repository [DEC-1085 (2)]'
  failure:
  - 'A measure that writes a label file or the sets root.'
  - 'A commit scored against another commit''s lines.'
  - 'Label text, path or lines printed for an unresolved hidden source.'
profile: STANDARD
sources:
- DEC-1085
- DEC-1084
- DEC-1083
- DEC-820
est_loc: 60
acceptance_tests:
  path: tests/acceptance/W2-134/
  author: independent-test-designer (MR-3), from these KPI lines, before the engineer
track: A
list_rows: []
---
# W2-134 The measure re-anchors in memory

W2-61h's S8 (DEC-1084) states what the measure must do. The owner filed its code as an engineer's ticket of its own,
small, tests first (DEC-1085 (2)). W2-61h keeps the independent test designer's role, which its S2 requires.

- **Why:** `repin_gold.py` re-anchored h23 on 11-05 at 14:40 to another clone's commit by rewriting the label. The
  score-once clone then misjudged it. A measure that re-anchors in memory for its own commit cannot do that.
- **The pattern:** `repin_gold.py`'s block search (`.gov-runtime/scratch/orchestrator/drafts/d4b/repin_gold.py`), done
  in memory inside `gov.retrieval.measure`, once per source per run.
- **Order:** an independent test designer writes `tests/acceptance/W2-134/` from S1 to S4, on a planted repository
  and a planted sets root, then the engineer builds. It follows W2-61h S7's merge (both touch `measure.py`), so it
  starts from integrate after S7 lands.
- **Hidden-half rule:** the tests plant their own sets. No test, log or return reads or prints the real sets.
