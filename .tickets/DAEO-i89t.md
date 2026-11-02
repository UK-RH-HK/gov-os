---
id: DAEO-i89t
status: open
deps: [DAEO-k7hz]
links: [DAEO-k7hz]
created: 2026-11-01T15:16:06Z
type: task
priority: 2
assignee: engineer
external-ref: W2-120
tags: [wave-2, implementation, skills, standard]
wbs_id: W2-120
title: 'The skill validator refuses a brief without the twelve-field rule and a skill whose front matter carries a permission field (W2-11''s child engineer ticket, DEC-995)'
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on: [DAEO-k7hz]
allowed_paths:
- src/gov/check/skill_validator.py
- tests/unit/check/test_w2_120*
kpis:
  success:
  - 'gov check''s skill validator refuses a brief template without the twelve-field rule (the twelve labelled return fields, the payload-after rule and the two-refusal stop), naming the file and what is missing; the kernel''s five brief templates as W2-11 leaves them pass [AR-5, AR-6, W2-L097, DEC-995]'
  - 'The validator checks every `gov` command a skill or brief names against the reserved command list, not the gov installed on the machine [W2-L097]'
  - 'gov check''s skill validator refuses a skill whose front matter has no output class or carries a key outside the skill template''s list (allowed-tools, permissions, paths, sandbox, network, model, effort or any other), naming the file and the key; it reads the kernel skills and every generated copy, and names each vendored skill so found [DEC-995, DEC-996, CAP-24.b]'
  failure:
  - 'A brief template without the twelve-field rule, or a skill with allowed-tools or another permission key in its front matter, that the validator passes [DEC-995]'
profile: STANDARD
sources:
- DEC-995
- DEC-996
- DEC-992
- CAP-24.b
- DEC-718
est_loc: 80
acceptance_tests:
  path: tests/acceptance/W2-120/
  author: independent-test-designer (MR-3)
track: A
list_rows: [W2-L097]
---
# W2-120 The skill validator: the twelve-field rule and closed skill front matter

The owner's decision on P-W2-11-9 (c) (DEC-995, DEC-996): W2-11 (a product-spec ticket) cannot hold code, so its
validator failure line and row W2-L097 move here, to an engineer, after W2-11 lands (W2-11's skill template and
briefs are what this validator checks). The closed skill front matter is DEC-996 item 4's line for this ticket.
