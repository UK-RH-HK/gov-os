---
id: DAEO-r30l
status: in_progress
deps: [DAEO-g0ip]
links: []
created: 2026-10-16T16:35:11Z
type: task
priority: 1
assignee: engineer
external-ref: W2-20
tags: [wave-2, implementation, standard]
wbs_id: W2-20
title: Machine-wide resource gate
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on:
- DAEO-g0ip
allowed_paths:
- src/gov/resources/**
- src/gov/launch/gate*
- tests/unit/resources/**
kpis:
  success:
  - gov resources reads free memory, load, and every live Gov OS session on the machine from a machine-wide registry under ~/.gov-os/machine/, whichever repository started it.
  - The gate opens or shuts with a named reason.
  - A stale entry (dead PID) is cleared [W2-M244, W2-M188, W2-M262].
  failure:
  - A session in another repository counts against the gate; a start while the gate is shut is refused with the reading.
profile: STANDARD
sources:
- DEC-729
- DEC-742
est_loc: 120
acceptance_tests:
  path: tests/acceptance/W2-20/
  author: independent-test-designer (MR-3); written before implementation
track: A
closes:
- W2-M244
- W2-M188
list_rows:
- W2-M188
- W2-M244
- W2-M262
---
# W2-20 Machine-wide resource gate

Card: `docs/plan/WAVE_2_WBS.md` §2 (W2-20), as approved (DEC-729). The list rows it takes in are in `list_rows` and in `docs/plan/WAVE_2_TRIAGE.md`; a row's state is re-checked against the code when the ticket picks it up (DEC-718).

- **The values (DEC-742, 2026-10-17):** at least 4 GiB available, 1-minute load below `nproc`, heavy sessions counting double, at most 8 Gov OS sessions on the machine; taken as configuration, in one place.
- **Allowed paths:** `src/gov/resources/**` (new), `src/gov/launch/gate*`, `tests/unit/resources/**`.
- **KPIs, success:**
  - `gov resources` reads free memory, load, and every live Gov OS session on the machine from a machine-wide registry under `~/.gov-os/machine/`, whichever repository started it.
  - The gate opens or shuts with a named reason.
  - A stale entry (dead PID) is cleared [W2-M244, W2-M188, W2-M262].
- **KPIs, failure:** a session in another repository counts against the gate; a start while the gate is shut is refused with the reading.
