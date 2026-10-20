---
id: DAEO-j8gn
status: open
deps: [DAEO-g0ip, DAEO-ym8a]
links: []
created: 2026-10-16T16:35:11Z
type: task
priority: 1
assignee: engineer
external-ref: W2-12
tags: [wave-2, implementation, full]
wbs_id: W2-12
title: Owner approval facts and gov approve
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on:
- DAEO-g0ip
- DAEO-ym8a
allowed_paths:
- src/gov/decisions/**
- src/gov/approve/**
- src/gov/check/authority.py
- template/governance/kernel/checks/core-authority.yaml
- tests/unit/decisions/**
- tests/unit/approve/**
- tests/unit/check/test_authority*
- src/gov/close/ratchet.py
- src/gov/close/state.py
- tests/unit/close/test_ratchet*
- tests/unit/close/test_owner_entry*
kpis:
  success:
  - 'gov approve [DEC-724]: It is run by the owner in a plain terminal. It shows the staged register entries (ids and titles), asks for a typed one-time code, and commits exactly those entries, with the
    files staged beside them, with Role: owner; It refuses, with a named reason and nothing committed, when it is run with a Claude Code ancestor process, with a launched session''s identity (GOV_ROLE or
    GOV_TICKET set), or without an interactive terminal. This is the freeze lift''s test (DEC-409); It refuses when nothing is staged, or when a staged entry is not an owner entry'
  - 'A register entry reads as the owner''s only when the commit that sets it ACCEPTED carries Role: owner and was made by gov approve, or by the owner''s own commit before W2-12, or (DEC-861, DEC-862 (b)) by the orchestrator''s decision-record commit with Decided-by: owner once it is in the owner''s pushed ref (or, once the owner chooses
    signatures, has a valid owner signature). Otherwise core-authority names it "transcribed" [AR-7, F-M6, W2-M258, W2-M108].'
  - A decision set ACTIVE without an owner approval fact turns core-authority red [W2-H049, W2-M227, W2-M257].
  - '"The decision checker could not run" is a finding, never green [W2-H037, W2-H048].'
  - Body edits that keep an approved decision ACTIVE are flagged [W2-L010]. An author date earlier than the committer date by more than a day is flagged [W2-M107].
  - 'The owner''s push as the acceptance in git: the close counts a ratchet entry (accepted_reds, load_sensitive) or an escalation lift from a commit carrying Task: decision-record and Decided-by: owner
    only once that commit is an ancestor of the owner''s pushed origin/w2/integrate (the remote-tracking ref the owner''s push left); before the push it counts nothing, and says so by name [DEC-862 (b)]'
  - 'A register entry recorded by the orchestrator under DEC-861 (Role: orchestrator, Task: decision-record, Decided-by: owner) reads as the owner''s once its commit is in the pushed ref, and as "recorded,
    not yet pushed" before; it is never read as transcribed without a source [DEC-861, DEC-862]'
  failure:
  - 'A Decided-by trailer alone, on a commit not in the owner''s pushed ref, never counts as the owner''s: no ratchet entry, no escalation lift [DEC-862 (c): never, it fails open]'
  - gov approve run from an agent's Bash call, piped input included, commits nothing.
  - 'A Role: owner trailer on a commit made inside an agent''s call is a containment finding, not an approval.'
profile: FULL
sources:
- DEC-724
- DEC-409
- DEC-861
- DEC-862
est_loc: 340
acceptance_tests:
  path: tests/acceptance/W2-12/
  author: independent-test-designer (MR-3); written before implementation
track: A
closes:
- AR-7
- F-M6
- DEC-724
list_rows:
- W2-H037
- W2-H048
- W2-H049
- W2-L010
- W2-L072
- W2-L126
- W2-L191
- W2-M051
- W2-M059
- W2-M107
- W2-M108
- W2-M109
- W2-M110
- W2-M111
- W2-M148
- W2-M227
- W2-M257
- W2-M258
---
# W2-12 Owner approval facts and gov approve

Card: `docs/plan/WAVE_2_WBS.md` §2 (W2-12), as approved (DEC-729). The list rows it takes in are in `list_rows` and in `docs/plan/WAVE_2_TRIAGE.md`; a row's state is re-checked against the code when the ticket picks it up (DEC-718).

- **Allowed paths:** `src/gov/decisions/**`, `src/gov/approve/**` (new), `src/gov/check/authority.py`, `template/governance/kernel/checks/core-authority.yaml`, `tests/unit/decisions/**`, `tests/unit/approve/**`, `tests/unit/check/test_authority*`.
- **KPIs, success:**
  - **`gov approve`** [DEC-724]:
    - It is run by the owner in a plain terminal. It shows the staged register entries (ids and titles), asks for a typed one-time code, and commits exactly those entries, with the files staged beside them, with `Role: owner`.
    - It refuses, with a named reason and nothing committed, when it is run with a Claude Code ancestor process, with a launched session's identity (`GOV_ROLE` or `GOV_TICKET` set), or without an interactive terminal. This is the freeze lift's test (DEC-409).
    - It refuses when nothing is staged, or when a staged entry is not an owner entry.
  - A register entry reads as the owner's only when the commit that sets it ACCEPTED carries `Role: owner` and was made by `gov approve`, or by the owner's own commit before W2-12, or (DEC-861, DEC-862 (b)) by the orchestrator's decision-record commit with `Decided-by: owner` once it is in the owner's pushed ref (or, once the owner chooses signatures, has a valid owner signature). Otherwise core-authority names it "transcribed" [AR-7, F-M6, W2-M258, W2-M108].
  - A decision set ACTIVE without an owner approval fact turns core-authority red [W2-H049, W2-M227, W2-M257].
  - "The decision checker could not run" is a finding, never green [W2-H037, W2-H048].
  - Body edits that keep an approved decision ACTIVE are flagged [W2-L010]. An author date earlier than the committer date by more than a day is flagged [W2-M107].
  - **The owner's push as the acceptance in git (DEC-862 (b), owner, 2026-10-20):** the close counts a ratchet entry (`accepted_reds`, `load_sensitive`) or an escalation lift from a commit carrying `Task: decision-record` and `Decided-by: owner` only once that commit is an ancestor of the owner's pushed `origin/w2/integrate`; before the push it counts nothing, and says so by name. Paths gain `src/gov/close/ratchet.py` and `src/gov/close/state.py` (the owner-entry reading only) and their unit tests.
  - A register entry recorded by the orchestrator under DEC-861 reads as the owner's once its commit is in the pushed ref, and as "recorded, not yet pushed" before [DEC-861, DEC-862].
- **KPIs, failure:**
  - A `Decided-by` trailer alone, on a commit not in the owner's pushed ref, never counts as the owner's (DEC-862 (c): never, it fails open).
  - `gov approve` run from an agent's Bash call, piped input included, commits nothing.
  - A `Role: owner` trailer on a commit made inside an agent's call is a containment finding, not an approval.
