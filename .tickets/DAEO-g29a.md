---
id: DAEO-g29a
status: open
deps: [DAEO-3r1j, DAEO-siiz]
links: [DAEO-3r1j]
created: 2026-10-31T23:05:58Z
type: task
priority: 1
assignee: engineer
external-ref: W2-113
tags: [wave-2, implementation, adoption, standard]
wbs_id: W2-113
title: 'An adopted product''s CTO is named at adoption: the adopt step writes the coordination-ticket key, the orchestrator role file states the CTO-only install rule, the refusal names GOV_TICKET (W2-110''s P-W2-110-2)'
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on:
- DAEO-3r1j
- DAEO-siiz
allowed_paths:
- src/gov/adopt/stages.py
- template/governance/kernel/hooks/permission_request.py
- src/gov/guard/install.py
- template/governance/kernel/roles/orchestrator.md
- template/.rulesync/subagents/orchestrator.md
- tests/unit/adopt/test_w2_113*
kpis:
  success:
  - 'Adoption writes the project''s `coordination_ticket` key from the coordination ticket it creates, so in a freshly adopted planted repository the orchestrator on that ticket is asked for an install and every other session is refused, with no hand edit [DEC-971 item 4, DEC-982]'
  - 'Both copies of the template''s orchestrator role file state the CTO-only install rule, name the key and the CTO''s `GOV_TICKET`, and no longer say the guard asks on every install (W2-110''s review F3) [DEC-971 item 4, DEC-957]'
  - 'The refusal, when the rule cannot run (no key, or a key naming no ticket), names `GOV_TICKET` and says how to set the key, in words that are true in that case (W2-110''s review F5); it stays closed [DEC-971 item 4]'
  - 'The kernel ships a quiet-hours permission hook (the host''s PermissionRequest event; this repository''s `governance/project/orchestration/tools/permission_request.py` as the model): inside the configured quiet hours it refuses at once, with a message naming the morning package, and queues the call under `.gov-runtime/`; outside them it gives no answer (the normal prompt); any error inside them refuses; every prompt is recorded; adoption wires it into the adopted CTO''s local settings only, with onFailure block; in a freshly adopted planted repository a prompting call at a forced 03:00 is refused and queued, and at 12:00 is not [DEC-991, DEC-994 item 3]'
  failure:
  - 'An adopted project whose CTO''s installs are refused until the key is written by hand.'
  - 'A role file that tells the CTO the old rule.'
  - 'Any session but the CTO''s asked or let through.'
profile: STANDARD
sources:
- DEC-971
- DEC-957
- DEC-982
- DEC-974
est_loc: 60
acceptance_tests:
  path: tests/acceptance/W2-113/
  author: independent-test-designer (MR-3); from the spec and KPIs, in parallel with the implementer (DEC-963); a planted repository adopted from the template
track: B
list_rows: []
---
# W2-113 An adopted product's CTO is named at adoption

The owner's decision on P1-NEW-TICKETS-2026-10-31 T1 (DEC-982), from W2-110's P-W2-110-2.

- **Why:** W2-110 makes the kernel's guard ask the owner for an install only from the orchestrator on the project's coordination ticket (DEC-971 item 4), with the key "set at adoption", but nothing writes it at adoption; the role file still states the old rule (review F3) and the refusal's words mislead when the rule cannot run (F5).
- **The work:** a product-spec worker rewrites the role file's lines (both copies), then an engineer makes the adopt step write the key and the refusal's words, one after the other.
- **Order:** after W2-110 (`DAEO-3r1j`) and W2-52 (`DAEO-siiz`, which holds the adopt files); before EXAMIN's copy (W2-27). W2-33 holds the rest of the role file: this ticket changes only the install lines.
