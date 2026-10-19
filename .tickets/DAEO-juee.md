---
id: DAEO-juee
status: in_progress
deps: []
links: []
created: 2026-10-19T21:21:16Z
type: task
priority: 1
assignee: engineer
external-ref: W2-62
tags: [wave-2, implementation, standard]
wbs_id: W2-62
title: 'Resume in full: the session-start hook delivers the whole RESUME HERE block and names the prompt in force'
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on: []
allowed_paths:
- template/governance/kernel/hooks/sessionstart.py
- template/governance/kernel/skills/checkpoint/**
- tests/unit/hooks/**
- docs/changes/W2-62-CIT-P.md
kpis:
  success:
  - 'The whole RESUME HERE section reaches the resumed session, however long: never a cut of its first 9,000 characters, and no "[truncated]" line in its place [W2-M372, DEC-837 item 1]'
  - 'Research first, recorded in docs/changes/W2-62-CIT-P.md: whether Claude Code 2.1.292 caps or moves a SessionStart hook''s additionalContext above a size, measured in a headless session. If it does,
    the hook delivers the section by a route that arrives whole (for example the section''s first part with the exact file, line range and size to read before anything else), and a live resumed
    session shows the whole section read'
  - The overall cap never cuts the RESUME HERE section or the instruction to read it; the optional parts (context packet, ready list, checkpoint brief) are the ones trimmed.
  - The hook names the prompt of the wave in progress, read from the project's configuration, not a constant; with no such setting it names none rather than a wrong one [W2-M373].
  - 'The checkpoint skill states the resume rule: RESUME HERE holds the full session state (what is happening, what was decided, what is next, where things are), repository knowledge comes from
    retrieval and the context packets, and a checkpoint is written at every handover (a worker''s return, a merge, a package, a compaction) [DEC-837 items 2 and 3]'
  failure:
  - A RESUME HERE section of 50,000 characters reaches the resumed session with no character lost; a checkpoint with no such section still says so; unreadable input still exits 0 and never blocks the
    session; a role other than orchestrator still gets no RESUME HERE injection.
profile: STANDARD
sources:
- DEC-837
- DEC-792
- DEC-838
- DEC-851
est_loc: 60
acceptance_tests:
  path: tests/acceptance/W2-62/
  author: independent-test-designer (MR-3); written before implementation
track: A
closes:
- W2-M372
- W2-M373
list_rows:
- W2-M372
- W2-M373
---
# W2-62 Resume in full: the session-start hook delivers the whole RESUME HERE block and names the prompt in force

Card: `docs/plan/WAVE_2_WBS.md` §2 (W2-62), from the accepted revised plan (`docs/plan/WAVE_2_REVISED_PLAN.md` §4.3) and DEC-837 (owner, 2026-10-19): split out of W2-10 as a small first ticket in keystone 3, so it lands sooner. It is a kernel hook and skill change, so it goes through CIT-P (CAP-33); the owner approved its scope in DEC-837. The list rows it takes in are in `list_rows`; a row's state is re-checked against the code when the ticket picks it up (DEC-718).

- **Allowed paths:** `template/governance/kernel/hooks/sessionstart.py`, `template/governance/kernel/skills/checkpoint/**` (the resume rule only), `tests/unit/hooks/**`, `docs/changes/W2-62-CIT-P.md`.
- **Depends on:** nothing. No ticket in flight shares these paths (W2-10, which also holds `template/governance/kernel/hooks/**`, has not started and starts after this one).
- **KPIs, success:**
  - The whole RESUME HERE section reaches the resumed session, however long: never a cut of its first 9,000 characters, and no "[truncated]" line in its place [W2-M372, DEC-837 item 1].
  - **Research first,** recorded in `docs/changes/W2-62-CIT-P.md`: whether Claude Code 2.1.292 caps or moves a SessionStart hook's `additionalContext` above a size, measured in a headless session. If it does, the hook delivers the section by a route that arrives whole (for example the section's first part with the exact file, line range and size to read before anything else), and a live resumed session shows the whole section read.
  - The overall cap never cuts the RESUME HERE section or the instruction to read it; the optional parts (context packet, ready list, checkpoint brief) are the ones trimmed.
  - The hook names the prompt of the wave in progress, read from the project's configuration, not a constant; with no such setting it names none rather than a wrong one [W2-M373].
  - The checkpoint skill states the resume rule: RESUME HERE holds the full session state (what is happening, what was decided, what is next, where things are), repository knowledge comes from retrieval and the context packets, and a checkpoint is written at every handover (a worker's return, a merge, a package, a compaction) [DEC-837 items 2 and 3].
- **KPIs, failure:** a RESUME HERE section of 50,000 characters reaches the resumed session with no character lost; a checkpoint with no such section still says so; unreadable input still exits 0 and never blocks the session; a role other than orchestrator still gets no RESUME HERE injection.
- **Once it lands,** DEC-792's 8,000-character limit on RESUME HERE is lifted (DEC-837 item 2).
