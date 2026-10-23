---
id: DAEO-e82f
status: open
deps: []
links: []
created: 2026-10-21T07:33:34Z
type: task
priority: 1
assignee: engineer
external-ref: W2-65
tags: [wave-2, guard, hooks, lite]
wbs_id: W2-65
title: 'The guard''s hook lines refuse a call when the guard program cannot run'
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on: [DAEO-kh9l]
allowed_paths:
- .rulesync/hooks.jsonc
- template/.rulesync/hooks.jsonc
- tests/unit/hooks/**
- template/governance/kernel/hooks/subagentstop.py
- src/gov/hooks/subagentstop.py
- tests/acceptance/W1-29/test_session_hooks.py
kpis:
  success:
  - 'The preToolUse line and the containment line in .rulesync/hooks.jsonc end with exit 2 whenever their program ends with any exit other than 0 or 2 (a syntax error, an import error, a missing file, a crash), with a message on stderr naming the program; exit 0 and exit 2 and a deny decision pass through unchanged [DEC-880 item 3, P-W2-59-8 (b)]'
  - 'The template''s hook source (template/.rulesync/hooks.jsonc), which adopted projects receive, does the same for its two lines [DEC-880 item 3]'
  - 'One acceptance case per line: a guard program that cannot run blocks the tool call it was asked about [DEC-880 item 3]'
  - 'The SubagentStop hook gives its block reason as Claude Code reads it (on standard error, or as a block decision with its reason), so a helper whose final message lacks the twelve fields learns what is missing; one acceptance case [DEC-889 item 8, P-H-7]'
  - 'src/gov/hooks/subagentstop.py stays byte-identical to the template''s copy (W1-29''s TestHookCopiesIdentical stays green), and W1-29''s SubagentStop case is revised by the test designer to the documented form, with Rewrite-Reason: DEC-889 item 8 [DEC-899, P-IS-5 (a), I3 F4]'
  failure:
  - A preToolUse or containment program that exits 1, or cannot start, lets the call through; a line that turns exit 0 into a refusal.
profile: LITE
sources:
- DEC-880
- DEC-822
- DEC-835
- DEC-884
- DEC-889
- DEC-899
est_loc: 30
acceptance_tests:
  path: tests/acceptance/W2-65/
  author: independent-test-designer (MR-3); written before implementation
track: A
closes:
- P-W2-59-8
list_rows: []
---
# W2-65 The guard's hook lines refuse a call when the guard program cannot run

Card: `docs/plan/WAVE_2_WBS.md` §2 (W2-65), from DEC-880 item 3 (owner, 2026-10-21, P-W2-59-8 (b)).

- **Why:** Claude Code blocks a PreToolUse call only on exit 2 or a deny decision. The hook lines pass their program's exit code on, so a guard program that cannot run (a half-finished edit with a syntax error) exits 1 and the call goes through: an ordinary-work fail-open that predates W2-59 (its second review's R2-D1).
- **Starts (DEC-884):** built stacked on `w2/W2-59` (both change `.rulesync/hooks.jsonc`; DEC-786), in a slot W2-66 does not need. It merges together with W2-59 just before the one combined re-pin, and the owner's settings regeneration follows the re-pin. The change is stricter only; the owner approved it (DEC-880), because it touches the hooks.
- **Allowed paths:** `.rulesync/hooks.jsonc` and `template/.rulesync/hooks.jsonc` (the preToolUse and containment lines' exit mapping only), `tests/unit/hooks/**`.
- **KPIs, success:**
  - The preToolUse and containment lines end with exit 2 whenever their program ends with anything other than 0 or 2, with a message naming the program; 0, 2 and a deny decision pass through unchanged.
  - The template's hook source does the same.
  - One acceptance case per line: a program that cannot run blocks the call.
  - **P-H-7 rides along (DEC-889 item 8):** the SubagentStop hook gives its block reason as Claude Code reads it (on standard error, or as `{"decision": "block", "reason": …}`), so a helper whose final message lacks the twelve fields learns what is missing; one acceptance case.
- **KPIs, failure:** a program that exits 1 or cannot start lets the call through; a line that turns exit 0 into a refusal.
- **Consequence to know:** a session whose guard program is broken then cannot use any tool, Edit included, so the file is fixed from another session (the orchestrator's, or the owner's terminal). No work is lost.
