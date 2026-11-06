---
id: DAEO-4k3l
status: open
deps: []
links: []
created: 2026-10-29T19:07:34Z
type: task
priority: 1
assignee: engineer
external-ref: W2-82
tags: [wave-2, implementation, readiness, standard, keystone-9]
wbs_id: W2-82
title: 'A Definition of Ready: gov claim checks it, and gov launch refuses a lead on a ticket that is not ready'
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on: []
allowed_paths:
- src/gov/tasks/dor.py
- src/gov/claim/__init__.py
- src/gov/claim/command.py
- src/gov/launch/launcher.py
- template/governance/kernel/templates/ticket.md
- template/governance/kernel/schemas/ticket.schema.json
- tests/unit/tasks/test_dor*
- tests/unit/claim/**
- tests/unit/launch/test_w2_82*
- docs/changes/W2-82-CIT-P.md
- docs/changes/W2-82-CIT-E.md
kpis:
  success:
  - 'Fail closed: a ticket file, the register or the store that cannot be read, or a condition that cannot be judged, is NOT_READY with the code UNJUDGED and its reason; nothing is ready by default [DEC-944 item 2, DEC-820]'
  - 'Nothing else changes: the vendored tk is byte-identical; no containment or guard rule rewrites a ticket file (Wave 3, DEC-944 item 2); gov.tasks.queue''s READY rule and W1-13''s gov readiness are unchanged; the scoped set in the close''s form is green; every red the ticket did not cause is named for the CTO [DEC-968, DEC-983, DEC-982] [DEC-880, DEC-866]'
  - 'A light readiness check the dispatcher (W2-121) calls before it starts a session: it calls W2-128 S10''s ready check, the one home of a ticket''s readiness (W-2), and answers READY or NOT_READY with that check''s codes, holding no readiness rule of its own [DEC-944 item 2, DEC-1052, DEC-1083] [re-scoped, DEC-1083]'
  failure:
  - 'A condition that cannot be judged treated as met.'
  - 'The vendored tk changed, or a rule of this repository written into the judge or the kernel.'
  lifted:
  - 'gov claim <ticket> judges the Definition of Ready and, when every condition holds, sets the ticket in_progress through the project''s vendored tk and writes nothing else; when any condition fails it exits 3 (NOT_READY), names every failing condition by its code and field, and writes nothing; gov claim --check judges only [DEC-944 item 2, CAP-31.a, CAP-31.d] [lifted (was S1), DEC-1083: the full `gov claim` Definition of Ready; a ticket''s readiness has one home, W2-128 S10''s check (W-2)]'
  - 'The six conditions, each with its code: SOURCES_UNRESOLVED (sources empty, or an id that neither the register, read as gov.close.history.register_entries reads it, nor the record store holds); PATHS_INVALID (allowed_paths empty, or a path that is absolute, holds .. or ~ or $, or covers tests/acceptance/** for a role other than the independent test designer, the rule of gov.tasks.bridge); KPIS_INCOMPLETE (success or failure empty, or no success line citing a decision or Contract id: at least one, not every line); PROFILE_MISSING (not LITE, STANDARD or FULL); ACCEPTANCE_PATH_MISSING (no acceptance_tests.path under tests/acceptance/, unless the class is one the close judges on evidence and acceptance_tests.evidence is set); DEPENDENCY_OPEN (a ticket in deps or depends_on, by ticket id or wbs_id, that is not closed, unless stacked_on names it with a decision the register holds ACCEPTED) [DEC-944 item 2, DEC-786 item 1, DEC-892, DEC-896 item 3] [lifted (was S2), DEC-1083: the full `gov claim` Definition of Ready; a ticket''s readiness has one home, W2-128 S10''s check (W-2)]'
  - 'gov launch refuses to launch a lead (GOV_ROLE orchestrator with a GOV_TICKET) on a ticket that is not ready, with the same codes, before any session starts; a ticket already in_progress whose file was ready at its claim and has not changed since is launched as before [DEC-944 item 2] [lifted (was S3), DEC-1083: the `gov launch` refusal; W2-82 is a light check the dispatcher calls (D9-FATES)]'
  - 'The kernel carries it, so an adopted product inherits it: the ticket template states each field the Definition of Ready reads, with its rule; ticket.schema.json gains stacked_on (the base and the decision); the judge reads the register''s place from the path map and holds no rule of this repository [DEC-944 item 2, CAP-44.a] [lifted (was S5), DEC-1083: the kernel ticket template and the schema are W2-128''s (TPL-5, its S10), under its one CIT-P (its S17)]'
  - 'CIT-P for the kernel template and the schema only (docs/changes/W2-82-CIT-P.md), written before either file changes, reviewed independently and approved by the owner before the merge; the CIT-E after [CAP-33.a, DEC-944 item 2] [lifted (was S6), DEC-1083: the kernel ticket template and the schema are W2-128''s (TPL-5, its S10), under its one CIT-P (its S17); the CIT-P of the kernel template and schema]'
  - 'gov claim sets in_progress on a ticket that fails a condition. [lifted (was F1), DEC-1083: the full `gov claim` Definition of Ready; a ticket''s readiness has one home, W2-128 S10''s check (W-2)]'
  - 'gov launch starts a lead on a ticket that is not ready. [lifted (was F2), DEC-1083: the `gov launch` refusal; W2-82 is a light check the dispatcher calls (D9-FATES)]'
  - 'A ticket file changed by anything but gov claim''s status line. [lifted (was F4), DEC-1083: the full `gov claim` Definition of Ready; a ticket''s readiness has one home, W2-128 S10''s check (W-2)]'
profile: STANDARD
sources:
- DEC-944
- DEC-941
- DEC-942
- DEC-786
- DEC-892
- DEC-896
- DEC-820
- DEC-880
- DEC-866
- CAP-31.a
- CAP-31.d
- CAP-33.a
- DEC-983
est_loc: 200
acceptance_tests:
  path: tests/acceptance/W2-82/
  author: independent-test-designer (MR-3); written before implementation; planted tickets, register and store in a temporary repository, never this repository's .tickets/
track: B
list_rows: []
---
# W2-82 A Definition of Ready: gov claim checks it, and gov launch refuses a lead on a ticket that is not ready

Card: `docs/plan/WAVE_2_WBS.md` §2 (W2-82), from the owner's decision of 2026-10-29 (DEC-944 item 2, the lighter form the owner set on review), which adds it to the minimum for EXAMIN's copy (K9's entry criteria).

- **Why:** a ticket can be claimed today with any file at all. `tk start` only rewrites the status line (the vendored `tk`, `cmd_start`). Nothing checks the file before `gov launch` hands the ticket's paths to a lead. Of the 70 open or in-progress tickets on 2026-10-29, 23 have no failure line, 17 have no acceptance-test path, and 3 have no profile and no sources. Adopted products need the check from their first ticket.
- **What exists:**
  - `gov.tasks.bridge._fault` already refuses a task contract with no role, class, profile, paths or KPIs, or with paths over `tests/acceptance/**`.
  - `gov.close.traceability._record_ids` and `gov.close.history.register_entries` already resolve ids.
  - `gov.close.gates` already knows the evidence classes and the declared acceptance path (W2-07).
  - The new module reuses all three and copies none of them.
- **Lighter by the owner's review (DEC-944 item 2):** two checks, at claim (`gov claim`) and at launch (`gov launch`). No containment rule rewrites ticket files: that is Wave 3. STANDARD, not FULL.
- **Order of work:**
  1. CIT-P (`docs/changes/W2-82-CIT-P.md`) for the kernel template and the ticket schema only, before either changes (CAP-33).
  2. Tests first, checked red.
  3. The module, the command, and the launcher's one call.
  4. The CIT-E.
- **Place:** priority 5 of the owner's standing priorities (DEC-946). `src/gov/launch/launcher.py` is held by W2-60a and W2-56, so this ticket starts once both have merged; it changes only the launcher's ticket check, with the judgement in `src/gov/tasks/dor.py`. `template/governance/kernel/schemas/**` is held by W2-64 and W2-78 as a glob; this ticket changes only `ticket.schema.json` (split by file, DEC-942).
- **After the merge, the orchestrator's own edits:** the prompt's claim step becomes `gov claim`; the claim tool calls it; until then the orchestrator checks the six conditions by hand at every claim (DEC-944).
- **The test designer's files:** `tests/acceptance/W2-82/`. The planted repository holds one ticket per failing condition, a fully ready ticket, a stacked ticket with and without its decision, and a launch of a lead on each.

**D9-FATES (DEC-1083):** Re-scoped to a light readiness check the dispatcher calls, which calls W2-128 S10's check, the one home of a ticket's readiness (W-2); it leaves K9. The full `gov claim` Definition of Ready (S1, S2, F1, F4), the `gov launch` refusal (S3, F2), the kernel template and schema (S5) and their CIT-P (S6) are under `kpis.lifted` with their old positions; S4, S7, F3 and F5 stay, and the light check is a new success line.
