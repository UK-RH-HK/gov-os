---
id: DAEO-k4wm
status: in_progress
deps: [DAEO-r8vq]
links: [DAEO-r8vq, DAEO-n0wb]
created: 2026-11-06T12:38:09Z
type: task
priority: 0
assignee: engineer
external-ref: W2-133
tags: [wave-2, implementation, retrieval, memory, drift, standard]
wbs_id: W2-133
title: 'A narrowed or gap-starting register item carries its own entry''s id (W2-131''s follow-up, DEC-1083, re-pin window 4)'
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on:
- DAEO-r8vq
allowed_paths:
- src/gov/decisions/register.py
- src/gov/retrieval/retrieve.py
- tests/unit/decisions/test_w2_133*
- tests/unit/retrieval/test_w2_133*
- docs/changes/W2-133-evidence.md
kpis:
  success:
  - 'S1 When the register''s leave_out narrows an expanded register item to its own chunk (the parent touched a superseded or done entry, the chunk does not), the kept item''s id, entry, status, in_force and also are those of the narrowed chunk, computed from its own lines, never the parent''s. Verify: a unit test on a planted register where a parent spans a superseded DEC-100 then DEC-101, the item narrowed to DEC-101''s chunk carries id and entry DEC-101 and DEC-101''s status [DEC-1083, DEC-1082 (2), DEC-1073]'
  - 'S2 A register item whose first line lies in the preface or a gap between entries carries its chunk id, not the first entry it touches further down, as W2-131''s S1 states; an item whose first line lies inside an entry carries that entry. Verify: unit tests on a planted register with an item starting in a gap before DEC-476 and one starting inside it [DEC-1083, DEC-1082 (2)]'
  - 'S3 Nothing else in a bundle changes: the evidence set, its order, the batches, the budget used, the gaps, left_out and the continuation, but for the ids and status fields S1 and S2 name. Verify: a unit test comparing bundles field by field before and after the fix on the planted repository [DEC-1083]'
  - 'S4 It lands on w2/integrate before re-pin window 4 is built, and the window carries it with W2-131. Verify: the CTO''s check after the re-pin [DEC-1083]'
  failure:
  - 'A narrowed register item that carries the id, entry or status of an entry it no longer holds.'
  - 'A change to which evidence a bundle holds, or its order, from this fix.'
profile: STANDARD
sources:
- DEC-1083
- DEC-1082
- DEC-1073
est_loc: 25
acceptance_tests:
  path: tests/acceptance/W2-133/
  author: independent-test-designer (MR-3), from these KPI lines, before the engineer
track: A
list_rows: []
---
# W2-133 A narrowed or gap-starting register item carries its own entry's id

W2-131's independent review (2026-11-06) found two cases its fix does not reach. The owner made them a small ticket of
their own, tests first, in re-pin window 4 (DEC-1083).

- **`leave_out`** (`src/gov/decisions/register.py:160-200`): when an expanded register parent touches a superseded or
  done entry, it is narrowed to its own chunk. The kept item is `{**item, start_line, end_line, sha256, text}`, so
  the parent's `id`, `entry`, `status`, `in_force` and `also` survive, though the narrowed chunk may hold a different
  entry.
- **The first entry touched:** `retrieve.py:581` on integrate labels a register item by the first entry its lines
  touch. An item that starts in a gap therefore takes a later entry's id, where W2-131's S1 says its chunk id.
- **The pattern:** the entry holding the item's first line, by `authority.register_entries_of` (as W2-131 uses).
- **Order:** the independent test designer, then the engineer. It holds `retrieve.py` with W2-92 and W2-32: keep the
  change to the label lines.
