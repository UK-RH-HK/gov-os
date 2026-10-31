---
id: DAEO-3r1j
status: open
deps: []
links: []
created: 2026-10-31T12:40:27Z
type: task
priority: 1
assignee: engineer
external-ref: W2-110
tags: [wave-2, implementation, guard, installs, full]
wbs_id: W2-110
title: 'A product''s CTO-only install rule: in a generated project the kernel''s guard asks the owner only in the CTO''s session, the orchestrator on the project''s coordination ticket, and refuses every other session'
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on: []
allowed_paths:
- template/governance/kernel/hooks/pretooluse.py
- src/gov/guard/install.py
- tests/unit/guard/test_w2_110*
kpis:
  success:
  - 'In a project generated from the template (copier, then rulesync generate), an install by the orchestrator on the project''s coordination ticket is asked of the owner; by any other session, a lead (the orchestrator on another ticket) included, it is refused, and the refusal tells the session to raise it as a P1 escalation, as this repository''s guard does after DEC-957 [DEC-971 item 4, DEC-957]'
  - 'The coordination ticket is named in the project''s own configuration (one key, set at adoption), never written in the code; with no such key, or a key naming no ticket, every session''s install is refused and the refusal says how to set it (fail closed) [DEC-971 item 4]'
  - 'Nothing else in the install rule changes: sudo still refused to every role, the research role''s one exception inside its experiment folder kept, a frozen project still refusing installs, the owner''s record of an approved install unchanged [DEC-971 item 4, DEC-163, DEC-083]'
  - 'The template''s own suites (W1-38, W1-39) and the guard''s own suites pass on the change [DEC-971 item 4]'
  failure:
  - 'A lead''s or a worker''s install in a generated project asked or allowed.'
  - 'The CTO''s install refused when the coordination ticket is set.'
  - 'A missing or unreadable coordination-ticket key read as "ask everyone".'
  - 'sudo, the research exception or the freeze changed.'
profile: FULL
sources:
- DEC-971
- DEC-957
- DEC-966
- DEC-163
- DEC-083
est_loc: 80
acceptance_tests:
  path: tests/acceptance/W2-110/
  author: independent-test-designer (MR-3); from the spec and KPIs, in parallel with the implementer in its own tests worktree (DEC-959 item 7, DEC-963)
track: A
list_rows: []
---
# W2-110 A product's CTO-only install rule

From the owner's DEC-971 item 4 (P1-MORNING-2026-10-31 item 4, W2-105's P-W2-105-1 (a)).

- **Why:** once W2-105 removes the template's install block, a product's kernel guard asks the owner about every orchestrator's install (`template/governance/kernel/hooks/pretooluse.py`, the install branch: `acting_role(...) == "orchestrator"` asks). Only this repository's five-rule hook has the CTO-only rule (DEC-957). In EXAMIN's copy, a lead's install would ask the owner instead of being refused and escalated.
- **The fix:** the kernel's install branch asks only for the orchestrator on the project's coordination ticket, named in the project's configuration; every other session is refused.
- **Paths, split by file:** the kernel hook's install branch, and `src/gov/guard/install.py` for the helper. W2-05 (running) lists `src/gov/**/*.py` for its git-environment sweep; it does not change the install rule, and whichever merges second merges back. W2-60b holds `src/gov/guard/decide.py`, which is not touched. W2-106 (merged) pinned the template's hook lines.
- **FULL:** it is the guard. An independent review probes for any session other than the CTO's that is asked or let through.
