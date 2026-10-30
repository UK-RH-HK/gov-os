---
id: DAEO-0uhh
status: in_progress
deps: []
links: []
created: 2026-10-29T15:55:50Z
type: task
priority: 1
assignee: engineer
external-ref: W2-64
tags: [wave-2, implementation, standard, keystone-4]
wbs_id: W2-64
title: 'W2-02''s widening: the record validator through check-jsonschema; docs/imported/ out of the schema check'
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on: [DAEO-zflj]
allowed_paths:
- template/governance/kernel/schemas/close.schema.json
- src/gov/check/schema.py
- tests/unit/check/test_schema*
kpis:
  success:
  - 'core-schema validates every record against its schema through check-jsonschema (pinned in the tool registry), not a subset; lens G''s planted ticket (a field the schema refuses that the subset passed) is refused [lens G R2 (a), F2, DEC-872 item 2]'
  - 'docs/imported/ is left out of the schema check, as history, and the check says so by name [DEC-844]'
  - 'Every record on w2/integrate today, the close records of docs/close/ included, still validates [DEC-872 item 2]'
  - 'The close schema states the evidence block W2-66''s close writes (scope, base commit, head, tree, what ran, what was left out and why, every skip and the skip count, failure text kept, the JUnit XML file); a close record with an incomplete evidence block is refused, and the close records written before W2-66 still validate [DEC-890 item 1]'
  - 'W2-61''s 20-question measure is run again after the merge and reported beside its baseline, both figures together [DEC-941, DEC-833 item 3]'
  failure:
  - A record that its schema refuses passes core-schema; a refusal that does not name the record and the rule.
  - check-jsonschema missing or failing to run reported as anything but RED.
profile: STANDARD
sources:
- DEC-831
- DEC-844
- DEC-872
- DEC-890
- DEC-833
- DEC-941
est_loc: 120
acceptance_tests:
  path: tests/acceptance/W2-64/
  author: independent-test-designer (MR-3); written before implementation
track: A
list_rows: []
---
# W2-64 W2-02's widening: the record validator through check-jsonschema; `docs/imported/` out of the schema check

Card: `docs/plan/WAVE_2_WBS.md` §2 (W2-64), from the accepted plan's widening of W2-02 (§5 and §4.4 order 1; DEC-831), moved out of W2-02's resume by DEC-872 item 2; keystone 4, order 1. Ticket file at its start; placed in the memory chain by the re-plan the owner accepted on 2026-10-29 (DEC-941).

- **Why:** lens G R2 (a), F2: the 169-line subset validator in `src/gov/check/schema.py` passes what the schemas refuse, which fails open.
- **Place:** W2-02 (`DAEO-zflj`) is merged and closed, so its paths are free. In block B of the re-plan it follows W2-61's baseline and W2-55; it shares no path with W2-55.
- **Paths:** the card's own: the paths W2-02 held. check-jsonschema 0.38.2 is already pinned in `governance/project/tool-registry.yaml` (DEC-074), so the registry is not in the paths.
