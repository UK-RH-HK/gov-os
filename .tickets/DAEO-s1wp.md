---
id: DAEO-s1wp
status: open
deps: [DAEO-c1uz]
links: []
created: 2026-10-27T19:52:51Z
type: task
priority: 2
assignee: Usain
parent: DAEO-c1uz
state_class: AUTHORITATIVE
disposition: unclassed
role: engineer
allowed_paths:
- src/gov/close/select.py
- src/gov/close/nightly.py
- src/gov/close/evidence.py
- src/gov/close/command.py
- governance/project/test-map.yaml
- template/governance/kernel/schemas/test-map.schema.json
- template/governance/project/test-map.yaml
- tests/unit/close/test_select*
- tests/unit/close/test_nightly*
- tests/unit/close/test_evidence*
- docs/research/W2-66-scoped-close.md
kpis:
  success:
  - 'gov close DAEO-c1uz no longer refuses for: tests/acceptance/W2-66/test_w2_66_live_test_map.py::test_every_record_of_each_of_dec_891_s_places_is_record_only[governance/project/orchestration/] is red (failed) and accepted_reds does not list it'
  failure:
  - gov close DAEO-c1uz refuses again for a finding of this ticket
repair_of_findings: findings-1519c203817db5ca
---
# Repair DAEO-c1uz: tests/acceptance/W2-66/test_w2_66_live_test_map.py::test_eve

Findings of the refused close of DAEO-c1uz (disposition: unclassed):
- tests/acceptance/W2-66/test_w2_66_live_test_map.py::test_every_record_of_each_of_dec_891_s_places_is_record_only[governance/project/orchestration/] is red (failed) and accepted_reds does not list it

