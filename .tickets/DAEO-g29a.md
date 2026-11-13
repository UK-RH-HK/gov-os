---
id: DAEO-g29a
status: closed
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
- tests/unit/adopt/test_w2_113*
- docs/probes/DAEO-g29a/**  # the probe record (the CTO, 2026-11-12)
kpis:
  success:
  - 'Adoption writes the project''s `coordination_ticket` key from the coordination ticket it creates, so in a freshly adopted planted repository the orchestrator on that ticket is asked for an install and every other session is refused, with no hand edit Verify: a planted repository is adopted with no hand edit: the project''s config then holds `coordination_ticket` equal to the id of the coordination ticket adoption created; the guard decision for an install by the session on that ticket is ask, and for any other session is refuse. [DEC-971 item 4, DEC-982]'
  - 'The refusal, when the rule cannot run (no key, or a key naming no ticket), names `GOV_TICKET` and says how to set the key, in words that are true in that case (W2-110''s review F5); it stays closed Verify: planted projects with no key and with a key naming no ticket: the install refusal text names `GOV_TICKET` and says how to set the key, the decision is still a refusal, and the text does not claim a key was set when none was. [DEC-971 item 4]'
  failure:
  - 'An adopted project whose CTO''s installs are refused until the key is written by hand. Verify: a freshly adopted planted repository: the CTO session''s install is asked at once (not refused) with no key edited by hand; a refusal there is the failure.'
  - 'Any session but the CTO''s asked or let through. Verify: planted engineer, test-designer, auditor and a second orchestrator session on another ticket each attempt an install in the adopted planted repository: each is refused, none is asked or let through.'
  moved:
  - 'Both orchestrator role-file copies state the CTO-only install rule (was S2) and no copy keeps the old rule (was F2) [moved to W2-33, DEC-1156 (4): one writer for orchestrator.md, the product-spec role (DEC-995, DEC-996 (1))]'
  lifted:
  - 'The kernel ships a quiet-hours permission hook (the host''s PermissionRequest event; this repository''s `governance/project/orchestration/tools/permission_request.py` as the model): inside the configured quiet hours it refuses at once, with a message naming the morning package, and queues the call under `.gov-runtime/`; outside them it gives no answer (the normal prompt); any error inside them refuses; every prompt is recorded; adoption wires it into the adopted CTO''s local settings only, with onFailure block; in a freshly adopted planted repository a prompting call at a forced 03:00 is refused and queued, and at 12:00 is not [DEC-991, DEC-994 item 3] [lifted (was S4), DEC-1083: re-scoped by D9-FATES (INVESTIGATION-1 §5)]'
profile: STANDARD
sources:
- DEC-971
- DEC-957
- DEC-982
- DEC-974
- DEC-1083
- DEC-991
- DEC-994
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

## Interface (DEC-1052; PKG-1 (a), the owner, DEC-1156 (4), 2026-11-12)

- **I1 Stage A0 creates it,** inside `src/gov/adopt/stages.py` only (no new flag): A0 creates the coordination ticket through `gov.tasks.tickets.create(root, "<project> coordination")` with `class: coordination`, writes `governance/project/roster.yaml` with a top-level `coordination_ticket: <new id>`, and records both in A0's record, committed in A0's commit with its set-up files (`safety.setup`).
- **I2 The three defaults:** a roster that already names an existing ticket: A0 keeps it and creates nothing; a roster without the key: A0 adds the key and changes nothing else; `tk` missing: A0 completes without creating the ticket or the key, and its record says so; the guard stays closed (every install refused, the refusal naming `GOV_TICKET` and how to set the key) (PKG-3 (b), the owner, DEC-1157 (15); was: A0 refuses and writes nothing).
- **I3 "A planted repository adopted"** for the tests: a planted git repository with the template copied in (copier, then `rulesync generate`, as in W2-110's suite), then `gov adopt --lite --stage A0`; then the guard's decisions for the orchestrator on that ticket (ask), and for an engineer, a test designer, an auditor and an orchestrator on another ticket (each refused).
- **Note for W2-88 and W2-174:** A0 gains this output; keep it at merge.
- **PKG-2 (b):** the role-file lines (was S2, F2) moved to W2-33; this ticket is engineer work only.
- **The test designer's readings, confirmed by the CTO (DEC-1112 (3)):** `<project>` is the repository's folder name and the title is exact; a roster key may name its ticket by id or WBS id, as the guard resolves it; A0 keeps the roster's comments and line order. The refusal keeps the sentence "Set the top-level key" (W2-110's unit test at line 172).
