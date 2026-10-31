---
id: DAEO-drhj
status: open
deps: []
links: []
created: 2026-10-30T23:20:54Z
type: task
priority: 1
assignee: engineer
external-ref: W2-104
tags: [wave-2, implementation, skills, standard]
wbs_id: W2-104
title: 'The skill evaluation harness: each skill''s three scenarios run on a fresh session and recorded, and every imported skill''s licence check recorded before adoption'
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on: []
allowed_paths:
- src/gov/skilleval/**
- tests/unit/skilleval/test_w2_104*
- governance/project/skill-imports.yaml
kpis:
  success:
  - 'gov skilleval <skill> runs each of the skill''s three committed scenarios on a fresh session with only that skill loaded (the model and effort from the role defaults), judges each against its stated pass line, and writes a scenario record (skill version, scenario, verdict, cost, time) beside the skill; it is the evidence CIT-E reads [DEC-959 item 5, ROLES-RESEARCH-1 §5.3 item 13]'
  - 'An imported skill (Anthropic''s collection or another source) is adopted only when governance/project/skill-imports.yaml records its source, version, licence and the licence''s verdict for this use, and its three scenarios pass; the harness refuses to mark an import adopted otherwise [DEC-959 item 5]'
  - 'A scenario run that cannot reach a model (no network, no key) is recorded as not run with its cause, never as a pass; the harness reads no secret and prints none [DEC-959 item 5, DEC-820 (a)]'
  - 'Planted skills with a passing and a failing scenario give the expected verdicts, in a temporary project, with a stub model [DEC-959 item 5]'
  failure:
  - 'A scenario reported as passing that did not run, or failed.'
  - 'An import marked adopted with no licence record or a failing scenario.'
  - 'A secret read or printed.'
profile: STANDARD
sources:
- DEC-959
- DEC-820
est_loc: 250
acceptance_tests:
  path: tests/acceptance/W2-104/
  author: independent-test-designer (MR-3); from the spec and KPIs, in parallel with the implementer (DEC-959 item 7); planted skills and a stub model, no network
track: B
list_rows: []
---
# W2-104 The skill evaluation harness

Card: ROLES-RESEARCH-1 §5.3 item 13, approved (DEC-959 items 5 and 8): with or just after W2-11 r1, so the template's scenarios have a runner.

- **Paths:** a new command module `src/gov/skilleval/` (`gov skilleval`), and the import record `governance/project/skill-imports.yaml` (new). No overlap.
