---
id: DAEO-mb2t
status: open
deps: [DAEO-blwa]
links: [DAEO-blwa, DAEO-qzrq]
created: 2026-11-02T10:37:58Z
type: task
priority: 1
assignee: engineer
external-ref: W2-124
tags: [wave-2, implementation, rebuild, standard]
wbs_id: W2-124
title: 'A rebuild without its semantic store fails named, and adoption finishes and records it: KPI 5 split from W2-122 (DEC-1027 C)'
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on:
- DAEO-blwa
allowed_paths:
- src/gov/rebuild/command.py
- src/gov/adopt/stages.py
- src/gov/close/rebuild_gate.py
- tests/unit/rebuild/test_w2_124*
- tests/unit/adopt/test_w2_124*
kpis:
  success:
  - '`gov rebuild` exits non-zero, named (`REBUILD_FAILED`, `store: semantic`), when the semantic store was asked for and not recreated (the embedder unavailable, hung or failing part way); only `--no-embeddings` skips it; never an ok answer over a partial store [DEC-1015 item 4, DEC-1027 C]'
  - 'A project with nothing to embed (no path map, or no embedded namespace) is not asked for a semantic store, so its rebuild answers ok [DEC-1027 C]'
  - 'Adoption never fails for a missing embedder: stage A6 finishes, and its record and the adoption report carry a named finding (the semantic store not recreated, with the reason) and the command to rebuild it later [DEC-1027 C]'
  - 'The close (and the merge queue''s prepare) treats a rebuild without its semantic store as failed, as the CTO''s `rebuild_slot.sh` does today (exit 75) [DEC-1015 item 4, DEC-1027 C]'
  failure:
  - 'An ok answer, or a close, over a partial semantic store.'
  - 'An adoption that fails, or reports success without the finding, when the embedder is unavailable.'
profile: STANDARD
sources:
- DEC-1027
- DEC-1015
- DEC-1014
est_loc: 80
acceptance_tests:
  path: tests/acceptance/W2-124/
  author: independent-test-designer (MR-3)
track: A
list_rows: []
---
# W2-124 A rebuild without its semantic store fails named; adoption finishes and records it

The owner's DEC-1027 C (P-W2-122-K5 (c)): W2-122's KPI 5 turned 100 earlier cases red (adoption's A6 among them), so it
is split out and W2-122's seeding lands without it. This ticket brings it back with the owner's rule: `gov rebuild` and
the close fail on a missing semantic store; adoption does not, it records the gap as a named finding. Earlier suites
that build projects without an embedder are revised by the test designer where they rebuild for real
(`Rewrite-Reason: DEC-1027 C`); a project with nothing to embed is not asked for one. Until it lands, the CTO's
`tools/rebuild_slot.sh` enforces the rule here (exit 75). The close's gate file is named for the engineer to place;
if the close's own code must change instead, the lead returns a package (W2-115 holds `src/gov/close`).
