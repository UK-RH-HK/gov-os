---
id: DAEO-0mtg
status: open
deps: []
links: []
created: 2026-10-31T01:22:30Z
type: task
priority: 0
assignee: engineer
external-ref: W2-106
tags: [wave-2, implementation, template, guard, fail-open, full]
wbs_id: W2-106
title: 'The template''s hook lines pinned: each runs the guard with the installed gov''s own interpreter, ignoring PYTHONPATH, and refuses when no pinned gov is found'
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on: []
allowed_paths:
- template/governance/kernel/settings.json
- template/.rulesync/hooks.jsonc
- tests/unit/hooks/test_w2_106*
kpis:
  success:
  - 'Each of the template''s hook lines (pre-tool and the two post-tool lines, in `template/governance/kernel/settings.json` and their rulesync source `template/.rulesync/hooks.jsonc`) takes this repository''s pinned form (DEC-822, W2-59): it finds the installed gov (`$HOME/.local/bin/gov`, else `gov` on PATH), reads the interpreter its first line names, and runs the hook with that interpreter and `-E`; the line''s exit codes are kept (0 and 2 pass through; any other ends in a refusal) [DEC-966 item 2, DEC-822]'
  - 'Fail closed: with no gov found, or a first line that names no interpreter that runs, the line refuses (exit 2) with a message naming what is missing; it never falls back to a bare `python3` [DEC-966 item 2, DEC-822]'
  - 'A session''s PYTHONPATH cannot change which guard code runs: in a generated project, a planted PYTHONPATH pointing at an edited copy of gov that would allow a refused write, the hook still refuses it (the measurement of P-W2-90-1 P1-B, now refused) [DEC-966 item 2, DEC-957]'
  - 'A generated project''s hook lines equal the template''s source after `rulesync generate` (the two sources stay in step), and the template''s own suites (W1-38, W1-39) pass [DEC-966 item 2, DEC-616]'
  failure:
  - 'A template hook line that runs a bare `python3`, or one without `-E`.'
  - 'A missing or broken gov lets the hook pass, or falls back to another interpreter.'
  - 'An edited gov on PYTHONPATH lets a refused write through.'
  - 'The settings and the rulesync source out of step, or W1-38 or W1-39 red.'
profile: FULL
sources:
- DEC-966
- DEC-822
- DEC-957
- DEC-965
- DEC-801
- DEC-616
est_loc: 60
acceptance_tests:
  path: tests/acceptance/W2-106/
  author: independent-test-designer (MR-3); from the spec and KPIs, in parallel with the implementer in its own tests worktree (DEC-959 item 7, DEC-963)
track: A
list_rows: []
---
# W2-106 The template's hook lines pinned

Card: the owner's answer to P-W2-90-1 P1-B, (a) (DEC-966 item 2): a fail-open must not ship in EXAMIN's copy.

- **Why:** the template's lines run `python3 "$h"` (`template/governance/kernel/settings.json` lines 8, 20 and 32; the same in `template/.rulesync/hooks.jsonc`). W2-90's test designer measured that a session whose PYTHONPATH points at an edited gov gets a refused write through (exit 0). This repository's lines carry the pinned form (DEC-822, W2-59).
- **No adoption step is needed:** this repository's form resolves the pin when the hook runs, from the installed gov's first line (the release the product installed, W2-16's frozen release once cut), so nothing under `src/gov/adopt/` changes and no dependency on W2-16 is needed. If the lead finds a reason for an adoption step, it is a package (W2-52 and W2-88 hold `src/gov/adopt/`).
- **Then:** after it merges, W2-90's next round moves its 4 W2-59 cases, with W2-105's 3 and the 14 ids of DEC-965 item 4.
- **Profile FULL:** the guard's wiring in every adopted product; an independent review of the final code (the QA step), on the fail-open and fail-closed paths.
