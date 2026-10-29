---
id: DAEO-pr0y
status: open
deps: [DAEO-5j8b]
links: []
created: 2026-10-28T21:31:54Z
type: task
priority: 2
assignee: Usain
parent: DAEO-5j8b
state_class: AUTHORITATIVE
disposition: unclassed
role: engineer
allowed_paths:
- src/gov/guard/protected.py
- src/gov/guard/heldout.py
- src/gov/guard/decide.py
- src/gov/guard/reads.py
- src/gov/launch/**
- governance/project/path-map.yaml
- template/governance/kernel/schemas/path-map.schema.json
- tests/unit/guard/**
- tests/unit/launch/**
- docs/changes/W2-58-CIT-E.md
kpis:
  success:
  - 'gov close DAEO-5j8b no longer refuses for: tests/acceptance/W2-54/test_w2_54_green_here.py::test_gov_check_gives_context_reproducibility_green_here is red (error) and accepted_reds does not list it'
  - 'gov close DAEO-5j8b no longer refuses for: tests/acceptance/W2-54/test_w2_54_green_here.py::test_gov_check_gives_core_schema_green_here is red (error) and accepted_reds does not list it'
  - 'gov close DAEO-5j8b no longer refuses for: tests/acceptance/W2-54/test_w2_54_green_here.py::test_the_w1_43_audit_report_is_untouched is red (error) and accepted_reds does not list it'
  failure:
  - gov close DAEO-5j8b refuses again for a finding of this ticket
repair_of_findings: findings-505a66bcf493610e
---
# Repair DAEO-5j8b: tests/acceptance/W2-54/test_w2_54_green_here.py::test_gov_ch

Findings of the refused close of DAEO-5j8b (disposition: unclassed):
- tests/acceptance/W2-54/test_w2_54_green_here.py::test_gov_check_gives_context_reproducibility_green_here is red (error) and accepted_reds does not list it
- tests/acceptance/W2-54/test_w2_54_green_here.py::test_gov_check_gives_core_schema_green_here is red (error) and accepted_reds does not list it
- tests/acceptance/W2-54/test_w2_54_green_here.py::test_the_w1_43_audit_report_is_untouched is red (error) and accepted_reds does not list it

