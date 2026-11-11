---
id: DAEO-6lid
status: open
deps: []
links: [DAEO-cb2b, DAEO-fd0p]
created: 2026-11-11T01:20:18Z
type: task
priority: 3
assignee: engineer
external-ref: W2-159
tags: [wave-2, implementation, standard, after-the-lift, orchestration, hooks]
wbs_id: W2-159
title: 'The orchestrator''s two Stop checks in the product: a turn does not end with the inbox waiter unarmed, nor idle while unblocked work remains, each a reminder blocking at most once a turn (EMERGENCY-TOOLS-1 A8, A9; DEC-1027 E, DEC-1110 (1))'
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on: []
allowed_paths:
- src/gov/session_watch/**
- src/gov/check/commands.py  # the one line that records `session-watch` (the precedent: W2-20's `resources`)
- tests/unit/session_watch/**
- docs/changes/W2-159-evidence.md
reads:
- src/gov/dispatch/**
- src/gov/plan/**
- governance/project/orchestration/tools/stop_waiter_check.py
- governance/project/orchestration/tools/stop_idle_check.py
needs:
- src/gov/check/commands.py
waits_on:
- ref: DAEO-cb2b
  reason: 'S2''s open items and S1''s waiter name come from the dispatcher''s inbox and ready list (W2-121); until it lands the check reads a configured file'
kpis:
  success:
  - 'S1 `gov session-watch stop-check waiter`, run as a Stop hook, answers "block" with a reason that names the inbox waiter and its command when all hold: the session is the orchestrator''s registered session (the id its start wrote to the project''s session file), no stand-by note younger than its limit (default 2 hours) is present, and no process of any configured waiter command is running; in every other case, and on any error, it says nothing. Verify: planted process lists and session files: waiter absent gives a block naming it; waiter present, a younger stand-by note, another session''s id, and a file that cannot be read each say nothing [DEC-1027, DEC-1028]'
  - 'S2 `gov session-watch stop-check idle`, run as a Stop hook, answers "block" naming each unblocked item when nothing of the orchestrator''s is running while its list of open items shows unblocked ones, and lets a turn end when a legitimate wait holds, naming which: the resource gate shut or the machine full (the dispatcher''s status, at most 5 minutes old), every remaining item waiting on the owner, or a running job. "Running" is a live background agent, a live background task or a live launched worker or run (a pid file whose process is alive, started under 3 hours ago, with no exit file); one past 3 hours is named as stale and not counted. Verify: planted status files, pid files and open-items lists: one case per legitimate wait, one with a stale pid, one with unblocked items and nothing running (a block naming them) [DEC-1110 (1), DEC-1109 (3), DEC-936]'
  - 'S3 Both checks block at most once per turn: never when `stop_hook_active` is set, never twice for the same turn (kept in a state file); a line `IDLE-REASON: <why>` in the orchestrator''s messages of the turn lets the idle check end it, and the line is recorded in the check''s log; neither a block nor a reason carries into the next turn. Verify: a planted turn: first call blocks, second with `stop_hook_active` says nothing, a third in the same turn says nothing, a new turn blocks again; a turn with the IDLE-REASON line ends and is logged [DEC-1110 (1), DEC-1027]'
  - 'S4 A check never traps a session and never fails open silently: on any error the turn ends and the error is named to the owner (`systemMessage`) and in the check''s log; a stand-by note does not let a turn end idle in S2 (unblocked work moves while the owner decides). Verify: a planted unreadable state file: the turn ends, the error named and logged; a stand-by note beside unblocked items: still a block [DEC-1110 (1), DEC-1109 (3)]'
  - 'S5 Where the open items come from is the project''s configuration, never a file name in the code: the default is the dispatcher''s ready list (W2-121, `gov plan --ready`); a project may name a file and a reader. Verify: a planted project with each source: the same block text naming the items; a search of src/gov/session_watch for this repository''s file names finds none [DEC-1110 (1), DEC-1088]'
  failure:
  - 'A turn blocked twice in a row, or blocked for a legitimate wait.'
  - 'A check that fails with no message, or that traps a session it cannot read.'
  - 'A file name, folder or ticket of this repository named in the code.'
  - 'Any change outside the paths above.'
profile: STANDARD
sources:
- DEC-1027
- DEC-1028
- DEC-1110
- DEC-1109
- DEC-936
- DEC-1088
- DEC-1119
- DEC-994
- W2-121
est_loc: 330
acceptance_tests:
  path: tests/acceptance/W2-159/
  author: 'independent-test-designer (MR-3), from these KPI lines; planted process lists, pid files, status files and transcripts, never a live session'
track: A
list_rows: []
---
# W2-159 The orchestrator's two Stop checks

Filed by the product-spec helper of the night audit (DAEO-sdxk's anti-drift audit (d), 2026-11-11) on EMERGENCY-TOOLS-1 rows A8 and A9; **after the lift**, not before EXAMIN's copy.

- **Problem.** This repository's CTO has two Stop-hook reminders (`governance/project/orchestration/tools/stop_waiter_check.py`, `stop_idle_check.py`; registered in the untracked `.claude/settings.local.json`, EMERGENCY-TOOLS-1 §4.1). They keep a turn from ending while the inbox waiter is unarmed (DEC-1027) and while unblocked work remains with nothing running (DEC-1110 (1)). An adopted product's orchestrator has neither. The idle check also reads this repository's DECIDED-NOT-DONE tables, so it cannot be copied as it is.
- **Approach.** One module, two checks, one state and log; the open items and the waiter come from the project's configuration, defaulting to W2-121's dispatcher. Alternative: copy the two scripts into the kernel template (rejected: the idle check names this repository's file; a kernel change needs its CIT-P).
- **Interface.** `gov session-watch stop-check waiter|idle`, reading the Stop hook's JSON on standard input and answering in the hook's form; the session file, the stand-by note and the state and log files are the project's runtime folder's. Installing the hook into a project's settings is an owner's ACT (class (b)), not this ticket.
- **Non-goals.** The dead-man's switch is not here: it is parked as W3-P16 by decision (DEC-994 item 3, W2-121's moved line). The helper watch and the bounded wait are W2-160.
- **Rabbit holes.** Reading a transcript's text (entry types and times only); a block that cannot be lifted (S3's once-a-turn bound is the guard against it).

[DEC-1027, DEC-1110 (1), DEC-1109 (3), DEC-1119 (5)]
