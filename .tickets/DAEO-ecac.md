---
id: DAEO-ecac
status: open
deps: []
links: []
created: 2026-10-29T15:55:51Z
type: task
priority: 1
assignee: engineer
external-ref: W2-60b
tags: [wave-2, implementation, standard, launch, telemetry, keystone-3]
wbs_id: W2-60b
title: 'One record per session: model, effort, window, tokens, cost, minutes, turns, subagents'
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on: [DAEO-cv58, DAEO-r9ss]
allowed_paths:
- src/gov/launch/session_record.py
- src/gov/launch/launcher.py
- src/gov/telemetry/sessionlog.py
- tests/unit/launch/test_session_record*
- tests/unit/telemetry/test_sessionlog*
- docs/changes/W2-60b-CIT-E.md
- src/gov/guard/decide.py
kpis:
  success:
  - 'When a launched session ends, whatever its exit (DEC-392''s signals included), the launcher writes one record keyed by its session id: model (the main session''s and each subagent''s), effort, window, tokens (input, output, cache creation, cache read), cost, minutes, turns, subagents (count and model) and every rate-limit event; role, ticket and task class come from W2-60a''s launch record [CAP-36.a lite, DEC-838 item 3, lens F R6]'
  - 'Each value comes from the harness''s own record of that session (its session log, through W1-31''s reader, and the result line when the session ran with --output-format json), with its source named; a value those forms do not give is not measured, with the reason, never zero or a guess [DEC-655, DEC-495]'
  - 'Counts only, never content: no text of the session''s log reaches the record, the Claude Code version excepted [DEC-495]'
  - 'The window recorded is the one the session ran with, as its log states it (1M for Opus 5.5), and each compaction is counted [DEC-838 items 1 and 2]'
  - 'A record that cannot be written leaves the session''s exit code as it is, with one line on stderr naming it; a record is written whole or not at all [DEC-392]'
  - 'W2-07''s close can join it: the record''s path and keys are stated in the CIT-E, and a test reads a record back by ticket and session id; pass or fail and the repair count stay the close''s [CAP-36.a lite, lens F R6]'
  - 'The launcher''s set of launchable roles (today the fixed WORKER_ROLES and OWN_TICKET_ROLES tuples in launcher.py) is read from the kernel''s role files, so a new role is a file, not a code change; a role file that is missing or unreadable refuses the launch; the five roles launch exactly as before [DEC-946 (W3-P09), DEC-826 Q1]'
  - 'A role named in a ticket but with no role file is refused at launch, naming the role [DEC-946 (W3-P09)]'
  - '`qa-engineer` is a known role: it is in the guard''s KNOWN_ROLES (`src/gov/guard/decide.py`, that set only) and in the reviewer set the session record and launcher read, so a QA engineer is held to rule 5 (it writes only its findings report); this repository''s own hook''s reviewer line is prepared beside it as an owner ACT, not changed here [DEC-959 item 3, DEC-953 item 2]'
  failure:
  - A fixed list of launchable roles left in code.
  - A value the log does not hold reported as measured; a zero for not measured; log text in a record.
  - A changed exit code; a session that started with no record.
profile: STANDARD
sources:
- DEC-946
- DEC-838
- DEC-839
- DEC-826
- DEC-655
- DEC-495
- DEC-392
- DEC-786
- DEC-941
- DEC-954
- DEC-957
- DEC-959
est_loc: 160
acceptance_tests:
  path: tests/acceptance/W2-60b/
  author: independent-test-designer (MR-3); written before implementation
track: A
list_rows: []
---
# W2-60b One record per session: model, effort, window, tokens, cost, minutes, turns, subagents

**DEC-959 (2026-10-30):** `qa-engineer` joins KNOWN_ROLES and the reviewer set (item 3; ROLES-RESEARCH-1 §5.3 item 2). `src/gov/guard/decide.py` is added for the KNOWN_ROLES set only. The repository's own hook (`.claude/hooks/pretooluse.py`, its REVIEWERS line) is the owner's ACT, prepared with this ticket.

**DEC-954, DEC-957:** **Roles spec approved (DEC-957);** builds to ROLES-SPEC-1 as approved, with the work order and the escalation rubric. Its CIT-P is part of the one combined K3 CIT-P (DEC-954 Q7).

Card: the draft card `W2-60` (W2-60b part), from the accepted plan (`docs/plan/WAVE_2_REVISED_PLAN.md` §4.3 and the CAP-36.a lite row of §2; DEC-838 item 3); keystone 3. Filed with W2-60a under the re-plan the owner accepted on 2026-10-29 (DEC-941).

- **Why:** usage, not money, is the limit (DEC-838 item 3). The orchestrator reports weekly usage from tokens, turns and rate-limit events, and Wave 3's routing needs one record per session id (lens F R6). Today the share records hold measured tokens and cost, but nothing ties them to a launch.
- **Profile STANDARD:** the record is written after the session has ended and only reads its log. It changes no sandbox, refusal or settings.
- **Place:** starts after W2-60a merges (the launch record and the session id it gives), and after W2-07 (`DAEO-r9ss`, in its close) closes, since W2-07 holds `src/gov/telemetry/**`. W2-07 adds pass or fail and the repair count from the close.
- **Paths:** `launcher.py` for the one call after the session ends only; `sessionlog.py` for new readings only (turns, compactions, rate-limit events, cost), under W1-31's rules (a form no specimen shows is "not measured", DEC-655).
- **The test designer's files** (MR-3): `tests/acceptance/W2-60b/**`.
