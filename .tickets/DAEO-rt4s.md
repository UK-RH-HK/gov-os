---
id: DAEO-rt4s
status: open
deps: [DAEO-rt3s]
links: [DAEO-5rgj, DAEO-rt2s, DAEO-rt3s]
created: 2026-11-19T03:40:00Z
type: task
priority: 1
assignee: engineer
external-ref: W2-207
tags: [dispatch, run-time-tool, cut-over, emergency-2]
wbs_id: W2-207
title: "The run-time tool, slice 4: the cut-over: the cron line moves to the product's pass, the product slot replaces the scratch heavy_slot.sh, RT-5's relaunch and D8's spend brake switched on, ready work started from `gov plan --ready` through `gov launch` (RT-1 across tickets), the CTO's dispatcher and the scratch watchers retired (RT-7)"
class: implementation
state_class: AUTHORITATIVE
role: engineer
profile: FULL
depends_on: [DAEO-rt3s]
waits_on: []
closes:
- CAP-23.b
- CAP-64.a
allowed_paths:
- src/gov/dispatch/**
- src/gov/resources/**
- src/gov/launch/launcher.py
- template/governance/kernel/hooks/stop.py
- governance/project/orchestration/tools/**
- .claude/settings.json
- tests/unit/dispatch/test_w2_tbd*
- tests/unit/resources/**
est_loc: 500
kpis:
  success:
  - 'RT-1 Ready work starts itself: the pass takes the ready tickets from `gov plan --ready`, and for each with a free admission starts its lead through `gov launch` with a `ready_at` record; a ticket whose lead is running, or whose start is held by the gate, the spend brake or a claim, is not started twice. Verify: a fixture project with three ready tickets and a limit of two leads: two leads start (a stub CLI) within one pass each, the third waits and starts when one ends; the log holds `ready_at` and `started_at` per ticket and `gov dispatch waits` reports each ready-to-start gap. [EMERGENCY-2 6.3 RT-1; audit 3 D2, D9; W2-205 non-goal]'
  - 'RT-5 The relaunch is on: the config key `relaunch` of `~/.gov-os/runtime/config.json` is true in the shipped default, the leads the cut-over starts are started by `gov launch` (so they are in the registry with a session id), and a lead that dies is resumed once at its checkpoint''s next step. Verify: W2-205''s relaunch cases with the default config. [audit 3 D5; CTO ruling 4 of slice 3]'
  - 'D8 The spend brake is called from the pass: a ticket past twice its projection has its next launch held and gets one message to its launcher. Verify: a planted launch record past 2x its projection: the pass starts nothing for the ticket and sends one wake message. [audit 3 D8; W2-156]'
  - 'RT-3, RT-7 The product slot replaces the scratch `heavy_slot.sh`: `heavy_slot.sh` in the repository becomes a one-line call of `gov resources slot` (or the product''s `gov.resources.slots.run`), its sizes come from the detected machine (`heavy_slots` in the gate file only when the owner pins one), and `heavy_slots.conf` and the `REFERENCE` fallback are gone; one cron line runs the pass; `ps` shows one watcher process. Verify: the slot run through the wrapper on two simulated profiles gives different slot and worker counts; no `SLOTS=` or `WORKERS=` constant remains; the crontab lists one run-time line.'
  - 'RT-6 The retirements of audit 3 are done: the CTO''s dispatcher (`dispatcher.py`, `balancer.py`, `run_tick.sh`, `launch_now.sh`, `loop.sh`) after its items are ported, the two dead-man copies, the sentinel check, `waiter_guard.sh`, `stop_idle_check.py`, `stop_waiter_check.py`, the jobs queue, `usage_watch.sh` and the `gate_check` comparison line; this repository''s own `.claude/settings.json` registers the template''s one Stop hook (W2-205) in their place. Verify: a grep of the tree and of the settings for each retired name finds nothing outside history; a Stop at the end of a turn with an unread wake message blocks once (W2-205).'
  failure:
  - 'F1 The cut-over loses nothing: the stall check and the CTO-stall push (DEC-1214 T1, T2; DEC-1216 (5)) run in the pass before the dispatcher''s cron line is removed, the unread items of the old inbox are carried into the per-session inbox, and the old line is removed only after one pass of the new one has run. Verify: a planted silent CTO transcript: one stall message and one push from the new pass; the old inbox''s unread items are in `cto`''s inbox after the cut-over step.'
non_goals:
- 'Anything the owner decides: the 99 % plan push and the decision pushes stay the CTO''s own'
- 'A new design: audit 3 and EMERGENCY-2 6.3 are the design'
done_when: [DOD-1, DOD-2, DOD-3, DOD-4, DOD-5, DOD-6]
sources: [EMERGENCY-2 6.3, A-5, docs/emergency-2/audits/03-run-time-tool.md, DEC-1214, DEC-1216, DAEO-rt3s]
acceptance_tests:
  path: tests/acceptance/W2-207/
  author: independent-test-designer (MR-3); written before implementation
track: A
---
# W2-207: the run-time tool, slice 4: the cut-over

Written 2026-11-19 by the slice 3 lead at the end of W2-205 (the night's brief: "if time remains, write slice 4's ticket and stop"). Not built, `wbs_id` is `W2-207` until the CTO gives the next free W2 number; the test paths are renumbered then.

**What is already there.** Slices 1 to 3 built the product's pieces and left everything live untouched: `gov msg` and the watch pass (slice 1), the load admission, the runtime log and the product slot (slice 2), the end events, the Stop check, the relaunch (off by default) and the per-address messages (slice 3, W2-205). This slice switches the live machine over, in the order F1 requires, and is the owner's/CTO's cut-over: nothing here is run by a worker without the CTO's go.

**Order of the cut-over (for the CTO).** (1) Port what the dispatcher does that the pass does not (the CTO-stall push, inbox items as `gov msg send`, the ready-list start) and run both for one day. (2) Register the template's Stop hook in `.claude/settings.json`, retire `stop_idle_check.py` and `stop_waiter_check.py`. (3) Replace the scratch `heavy_slot.sh` by the product slot. (4) Replace the cron line; remove the old one after one clean pass. (5) The retirements. (6) Turn `relaunch` on.

**Largest part and a split option.** RT-1 across tickets (the first KPI line) is the biggest item (the rest of audit 3 D2 and D9); if it runs long, split it into its own ticket ahead of the cut-over, which then carries RT-3, RT-5, RT-6, RT-7, D8 and F1.

**Open questions for the owner (one line each).** (a) When the cut-over runs (recommended: a day, not a night, so that the CTO watches the first passes). (b) Whether `relaunch` ships on (recommended: yes after one day of the new pass).
