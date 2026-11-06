---
id: DAEO-r8vq
status: in_progress
deps: []
links: [DAEO-n0wb, DAEO-0pyc]
created: 2026-11-06T11:10:30Z
type: task
priority: 0
assignee: engineer
external-ref: W2-131
tags: [wave-2, implementation, retrieval, memory, drift, standard]
wbs_id: W2-131
title: 'A register chunk in a bundle carries its own entry''s id, not DEC-999 (DEC-1082 (2), a priority fix in re-pin window 4)'
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on: []
allowed_paths:
- src/gov/retrieval/retrieve.py
- tests/unit/retrieval/test_w2_131*
- docs/changes/W2-131-evidence.md
kpis:
  success:
  - 'S1 Every evidence item of a bundle that lies in the decision register carries as its id the entry that holds its first line: a chunk inside DEC-476 is labelled DEC-476, whatever other entries the register holds (DEC-999 and DEC-1082 among them); a chunk in the preface or between entries carries its chunk id; a parent expansion carries the id of its first entry. Where the bundle also names the entry (W2-92 S9''s entry key), the two agree. Verify: a unit test on a planted register with DEC-476, DEC-999 and DEC-1082, a query only DEC-476 answers, a preface hit and an expansion [DEC-1082 (2), DEC-1073]'
  - 'S2 The path-to-record map used for labels and for DEC-424''s ahead paths no longer lets one entry of a many-entry file stand for the file: records that carry a span are left out of it, as supplementary.py already does, so no register entry is judged by another entry''s type or id. Verify: a unit test that the map holds no register entry id for the register''s path, and that DEC-424''s move still lifts a failure or lesson record [DEC-1082 (2), DEC-424]'
  - 'S3 Nothing else in a bundle changes: on the planted repository the evidence set, its order, the batches, the budget used, the gaps and the continuation are identical before and after the fix, but for the ids of register items. Verify: a unit test comparing the two bundles field by field [DEC-1082 (2)]'
  - 'S4 The fix lands on w2/integrate before re-pin window 4 is built, and window 4''s pin carries it; a live search after window 4 labels each register chunk by its own entry. Verify: the CTO''s check after the re-pin, the DEC-476 example of the health check (2026-11-06) [DEC-1082 (2)]'
  failure:
  - 'A register item labelled with another entry''s id (an agent citing a search result cites the wrong decision).'
  - 'A change to which evidence a bundle holds, or its order, from this fix.'
profile: STANDARD
sources:
- DEC-1082
- DEC-1073
- DEC-424
est_loc: 20
acceptance_tests:
  path: tests/acceptance/W2-131/
  author: independent-test-designer (MR-3), from these KPI lines, before the engineer
track: A
list_rows: []
---
# W2-131 A register chunk carries its own entry's id

Found by the CTO's health check, 2026-11-06. A live search through the pin (`8284fb40`) returned register chunks
whose texts are DEC-476, DEC-496, DEC-672, DEC-455 and DEC-487, each labelled `"id": "DEC-999"`. The owner made it a
priority fix, ahead of the levers' work, because an agent citing the wrong decision is drift (DEC-1082 (2)).

- **The cause:**
  - `retrieve()`'s inner `item()` labels an item `record_of.get(rel, chunk_id)` (the pin's `retrieve.py:415`).
  - `_graph()` builds `record_of` as `{path: id}` over every record (`retrieve.py:75`), so the 1,064 register entries
    sharing one path leave one id.
  - `records.records()` sorts by id as text (`records/queries.py:22`), so DEC-999 comes last and wins.
  - The right map exists (`authority.register_entries_of`, used for the routes and the drops), but not for the label.
- **Not fixed in window 4's builds:** the same expression is at `w2/integrate` `retrieve.py:492` and `w2/W2-32` `:506`.
  W2-92 S9's new `entry` key is right, so after window 4, `id` and `entry` would disagree on every register item.
- **The pattern to copy:** `supplementary.py:95` (`id = entry['id'] if entry else chunk_id`).
- **The measure is unaffected:** it scores by path and line span (`measure.py:158-184`), so no recorded figure
  changes.
- **Order:** an independent test designer writes `tests/acceptance/W2-131/` from S1 to S3 on a planted repository,
  then the engineer. It lands on integrate and goes into re-pin window 4 with W2-92, W2-32 and W2-112. It holds
  `retrieve.py`, which W2-92 and W2-32 also hold: keep the change to `item()` and the map, and the merge order settles
  any overlap.
