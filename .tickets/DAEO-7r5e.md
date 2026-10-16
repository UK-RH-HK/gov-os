---
id: DAEO-7r5e
status: open
deps: [DAEO-g0ip, DAEO-zflj, DAEO-kia7]
links: []
created: 2026-10-16T16:35:11Z
type: task
priority: 1
assignee: orchestrator
external-ref: W2-08
tags: [wave-2, integration, standard]
wbs_id: W2-08
title: 'Hooks back on: F-M4 restated, gov check green here, a report commits through the hook'
class: integration
state_class: AUTHORITATIVE
role: orchestrator
depends_on:
- DAEO-g0ip
- DAEO-zflj
- DAEO-kia7
allowed_paths:
- docs/plan/wave-2/hooks-back-on/**
kpis:
  success:
  - The independent test designer restates test_no_lefthook_hook_is_installed_in_this_repository so that installed hooks are the expected state. This is a rewrite after implementation, with its reason [F-M4,
    MR-3, DEC-136].
  - The owner reinstalls the hooks (an owner act). The orchestrator asks; the operator restores .claude/settings.json only if W2-05 did not fix the re-sort [AR-3, W2-M013].
  - A commit of a report in DEC-441's form passes the pre-commit hook, straight after staging, with no hand rebuild [AR-3, F-M13].
  - 'gov check on this repository: 17 of 17 families, no RED, no unexplained YELLOW [W2-H020, W2-L106, W2-L335, W2-M142, W2-L017].'
  - DEC-709 is retired by a register entry (DEC-719 item 4).
  failure:
  - Any hook refusal is reported to the owner and never worked round.
profile: STANDARD
sources:
- MR-3
- DEC-136
- DEC-441
- DEC-709
- DEC-719
est_loc: 0
acceptance_tests:
  judged_by: 'its class (WBS §0 rule 1, W2-07): its named evidence files'
track: A
closes:
- AR-3
- F-M4
- F-M13
list_rows:
- W2-H020
- W2-L017
- W2-L106
- W2-L335
- W2-M013
- W2-M142
---
# W2-08 Hooks back on: F-M4 restated, gov check green here, a report commits through the hook

Card: `docs/plan/WAVE_2_WBS.md` §2 (W2-08), as approved (DEC-729). The list rows it takes in are in `list_rows` and in `docs/plan/WAVE_2_TRIAGE.md`; a row's state is re-checked against the code when the ticket picks it up (DEC-718).

- **Allowed paths:** `docs/plan/wave-2/hooks-back-on/**` (evidence), `tests/acceptance/W1-40/**` (test designer only).
- **Steps and KPIs:**
  - The independent test designer restates `test_no_lefthook_hook_is_installed_in_this_repository` so that installed hooks are the expected state. This is a rewrite after implementation, with its reason [F-M4, MR-3, DEC-136].
  - The owner reinstalls the hooks (an owner act). The orchestrator asks; the operator restores `.claude/settings.json` only if W2-05 did not fix the re-sort [AR-3, W2-M013].
  - A commit of a report in DEC-441's form passes the pre-commit hook, straight after staging, with no hand rebuild [AR-3, F-M13].
  - `gov check` on this repository: 17 of 17 families, no RED, no unexplained YELLOW [W2-H020, W2-L106, W2-L335, W2-M142, W2-L017].
  - DEC-709 is retired by a register entry (DEC-719 item 4).
- **Failure:** any hook refusal is reported to the owner and never worked round.
