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
- src/gov/check/commands.py
- src/gov/launch/gate*
- tests/unit/resources/**
kpis:
  success:
  - gov resources reads free memory, load, and every live Gov OS session on the machine from a machine-wide registry under ~/.gov-os/machine/, whichever repository started it.
  - The gate opens or shuts with a named reason.
  - A stale entry (dead PID) is cleared [W2-M244, W2-M188, W2-M262].
  - 'The gate also reads the shared disk: it shuts below a floor of free space and of free inodes (100 GiB and 10,000,000, set in the gate''s one configuration file); gov launch refuses to start a session while it is shut, naming the reading, and the reading is one function gov close can call before a close (its call is W2-07''s or W2-66''s, whose paths hold the close) [DEC-898 item 1]'
  - 'The gate opens on load only while min(1-minute load, 15-minute load) < nproc: a short peak does not shut it; both at or above nproc does [DEC-942 item 2, DEC-942 item 3, DEC-950 item 2]'
  - 'The gate opens on memory only while MemAvailable plus the running sessions'' live memory (each one''s whole process tree, read at the check) is at least the floor + one verification run''s peak (reserved once) + a working size for each running session and for the new one; a session inside another live session''s process tree is counted in that one and charged no working size of its own [DEC-947, DEC-942 item 2, DEC-950 item 2]'
  - 'No fixed number: no ceiling on leads or sessions, weighted or not; only the load, memory, disk, inode and (for a start that declares one) GPU conditions shut the gate [DEC-942 item 1, DEC-950 item 2]'
  - 'All values in one configuration file (floor, verification peak, working size, disk and inode floors, verification lock, GPU margin), each with its date and source; a value missing or malformed shuts the gate, naming it; the reading names a measured figure older than seven days as due for re-measure [DEC-947 item 3, DEC-950 item 2]'
  - 'The re-measure: gov resources records samples of each live session''s process-tree memory, noting whether a verification run holds the configured lock, and from them writes the verification peak (largest sample) and the working size (largest outside verification) with the date into the configuration file, showing old and new side by side [DEC-947 items 2 and 3, DEC-950 item 2]'
  - 'GPU, minimal: a start that declares a GPU need opens only when a GPU''s free memory, read with nvidia-smi, is at least the need plus 10%; no nvidia-smi or no GPU shuts such a start, named; a start with no declared need never reads the GPU [DEC-950 item 2, DEC-941 item 6]'
  failure:
  - A session in another repository counts against the gate; a start while the gate is shut is refused with the reading.
  - A launch or a close that starts with the disk below either floor; a gate that reads disk space but not inodes.
  - 'Any fixed ceiling on leads or sessions.'
  - 'A value the gate uses not taken from the configuration file, or a reading that cannot be taken treated as met.'
  - 'A worker''s memory charged twice (in its lead''s tree and as its own session).'
profile: STANDARD
sources:
- DEC-729
- DEC-742
- DEC-747
- DEC-898
- DEC-941
- DEC-942
- DEC-947
- DEC-950
- DEC-954
est_loc: 320
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

**DEC-954 Q12:** in Wave 2, built on the owner's measured rule for this machine (DEC-950). Machine-agnostic in Wave 3: a parking-list row (W3-P12).

Card: `docs/plan/WAVE_2_WBS.md` §2 (W2-20), as approved (DEC-729). The list rows it takes in are in `list_rows` and in `docs/plan/WAVE_2_TRIAGE.md`; a row's state is re-checked against the code when the ticket picks it up (DEC-718).

- **The values (DEC-942 item 2 and DEC-947, replacing DEC-742's; DEC-950 item 2):** floor 3 GiB; one verification peak reserved once; a working size per running session and the new one, re-measured weekly; min(1-, 15-minute load) below `nproc`; disk and inode floors (DEC-898); no session ceiling; a GPU check only for a declared need (+10%); all in one configuration file.
- **Allowed paths:** `src/gov/resources/**` (new), `src/gov/launch/gate*`, `tests/unit/resources/**`.
- **KPIs, success:**
  - `gov resources` reads free memory, load, and every live Gov OS session on the machine from a machine-wide registry under `~/.gov-os/machine/`, whichever repository started it.
  - The gate opens or shuts with a named reason.
  - A stale entry (dead PID) is cleared [W2-M244, W2-M188, W2-M262].
- **KPIs, failure:** a session in another repository counts against the gate; a start while the gate is shut is refused with the reading.
- **DEC-747 (delegated, 2026-10-17):** `src/gov/check/commands.py` is in the paths for the one line that records `resources` (P-A). "At most 8 sessions" holds after the start: the start check adds the new session's weight (P-B). DEC-742's load value stands (P-C). P-B's "at most 8" superseded by DEC-942 item 1.
