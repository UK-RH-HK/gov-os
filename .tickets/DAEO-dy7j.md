---
id: DAEO-dy7j
status: open
deps: []
links: []
created: 2026-10-29T19:07:34Z
type: task
priority: 1
assignee: product-spec
external-ref: W2-83a
tags: [wave-2, template, playbooks, kernel-template, standard, keystone-9]
wbs_id: W2-83a
title: 'A playbook per stream: the form in the kernel template, its schema in gov check, and the adopt step'
class: template
state_class: AUTHORITATIVE
role: product-spec
depends_on: [DAEO-0uhh]
allowed_paths:
- template/governance/kernel/templates/playbook.md
- template/governance/kernel/schemas/playbook.schema.json
- src/gov/check/schema.py
- template/governance/kernel/skills/adopt/**
- .claude/skills/adopt/**
- .rulesync/skills/adopt/**
- template/.rulesync/skills/adopt/**
- tests/unit/check/test_schema_playbook*
- docs/changes/W2-83a-CIT-P.md
- docs/changes/W2-83a-CIT-E.md
kpis:
  success:
  - 'The kernel template carries the form: templates/playbook.md and schemas/playbook.schema.json, a record with the shared frontmatter (type playbook), which requires the stream (its id and name), its purpose, its standing practices (each with its rule, at least one decision or Contract id, and where it is enforced: the judge, the kernel, or the project''s prompt, briefs or tools), its usual ticket classes (each with how the close judges it), and its roles (each with what it does in the stream and the skills it loads) [DEC-944 item 3, DEC-239, CAP-50.a]'
  - 'gov check validates every playbook: core-schema maps the type playbook to its schema, in the record folders it already reads; a planted playbook that lacks any of the five parts, a practice with no id, or a role with no skills is refused, naming the record and the field [DEC-944 item 3, DEC-872 item 2]'
  - 'Adoption creates the form in a product: the adopt skill gains the step that writes one playbook per stream from the kernel form, its four copies kept in step through the adapter, its version raised; a product built from this template at a temporary path passes gov check with one playbook and is refused with a planted faulty one [DEC-944 item 3, CAP-44.a, CAP-24.a]'
  - 'CIT-P first: docs/changes/W2-83a-CIT-P.md before any kernel file changes, reviewed independently and approved by the owner before the merge; the CIT-E after [CAP-33.a, CAP-24.c, DEC-944]'
  - 'Nothing project-specific in the kernel: the form and the adopt step name no keystone, no EXAMIN, no workbench and no path of this repository; gov check is green; the full regression in the close''s form is green apart from reds the ticket does not own [DEC-880, DEC-866]'
  failure:
  - 'A playbook that lacks purpose, practices, ticket classes, roles or skills passes gov check.'
  - 'A practice without a decision or Contract id passes.'
  - 'A rule of this repository in the kernel template.'
  - 'A kernel file changed without its CIT-P and the owner''s approval.'
profile: STANDARD
sources:
- DEC-944
- DEC-941
- DEC-872
- DEC-880
- DEC-866
- CAP-44.a
- CAP-33.a
- CAP-24.a
- DEC-954
- DEC-957
est_loc: 350
acceptance_tests:
  path: tests/acceptance/W2-83a/
  author: independent-test-designer (MR-3); written before implementation; planted playbooks and a product built from the template at a temporary path, never this repository's docs/
track: B
list_rows: []
---
# W2-83a A playbook per stream: the form in the kernel template, its schema in gov check, and the adopt step

**DEC-954, DEC-957:** **Roles spec approved (DEC-957);** builds to ROLES-SPEC-1 as approved, with the work order and the escalation rubric. Its CIT-P is part of the one combined K3 CIT-P (DEC-954 Q7).

Card: `docs/plan/WAVE_2_WBS.md` §2 (W2-83a), from the owner's decision of 2026-10-29 (DEC-944 item 3, the split the owner set on review). In the minimum for EXAMIN's copy (K9's entry criteria); W2-83b, this project's nine playbooks, follows in spare capacity.

- **Why:** what a stream is for, its standing practices, its ticket classes and who works in it with which skills live today in the orchestrator's prompt, its briefs and its untracked tools. An adopted product inherits none of it. This ticket gives the kernel the form, so every product starts with it.
- **What exists:**
  - The kernel already ships templates (`template/governance/kernel/templates/`) and schemas, and products get them on every `copier update`.
  - `gov check`'s core-schema already reads every record under `docs/` and `.tickets/`, and refuses an unknown type, so a playbook needs only its entry in the schema map.
  - W2-64 makes that check validate each record against its whole schema and holds `src/gov/check/schema.py`, so this ticket starts after W2-64.
- **Order of work:**
  1. CIT-P (`docs/changes/W2-83a-CIT-P.md`) on the new template, the new schema and the adopt skill, before any kernel file changes (CAP-33).
  2. Tests first, checked red.
  3. The form, the schema, the schema map's one entry, the adopt skill and its copies.
  4. The CIT-E.
- **Paths shared:** `src/gov/check/schema.py` for the schema map's entry only (after W2-64). `template/governance/kernel/schemas/**` is held as a glob by W2-64 and W2-78; this ticket adds only `playbook.schema.json` (split by file, DEC-942). No open ticket holds the adopt skill. If the product-spec role cannot write `schema.py`, the lead returns a package naming the one line.
- **Place:** priority 5 of the owner's standing priorities (DEC-946).
- **The test designer's files:** `tests/acceptance/W2-83a/`: planted playbooks, one per missing part; a product made from `template/` with Copier at a temporary path, with one playbook and one faulty playbook.
