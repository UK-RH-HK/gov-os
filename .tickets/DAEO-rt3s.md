---
id: DAEO-rt3s
status: deferred
deps: [DAEO-rt2s]
links: [DAEO-5rgj, DAEO-rt2s]
created: 2026-11-19T02:30:00Z
type: task
priority: 1
assignee: engineer
external-ref: W2-200
tags: [dispatch, msg, checkpoint, run-time-tool, emergency-2]
wbs_id: W2-200
title: "The run-time tool, slice 3: across sessions: every end messaged within 2 minutes (RT-2), a session that died resumes at its recorded next step (RT-5), messages between CTOs, leads, workers and the operator never through the owner (RT-6)"
class: implementation
state_class: AUTHORITATIVE
role: engineer
profile: FULL
depends_on: [DAEO-rt2s]
waits_on: []
allowed_paths:
- src/gov/dispatch/**
- src/gov/msg/**
- src/gov/launch/launcher.py
- src/gov/checkpoint/**
- template/governance/kernel/hooks/stop.py
- template/governance/kernel/hooks/sessionstart.py
- tests/unit/dispatch/test_w2_200*
- tests/unit/msg/**
- tests/unit/launch/test_w2_200*
- tests/unit/checkpoint/**
est_loc: 600
kpis:
  success:
  - 'RT-2 Every end reaches the watching session within 2 minutes: a lead, a worker (a session `gov launch` started, whoever started it) or a heavy job (W2-199''s runs) that ends gives one `wake` message to its launcher''s address, in the runtime log with the end time and the message time, and `gov dispatch waits --ends` prints each end''s gap and exits 3 for a gap over 120 s. Verify: a fixture HOME with a lead, a worker and a job ended at known times, the watch pass run once a minute (planted clock `GOV_RUNTIME_NOW`): every gap is 120 s or less, the report lists all three, and a planted end whose message is 200 s late exits 3 naming it. [EMERGENCY-2 6.3 RT-2; audit 3 D4; W2-199 gives the job end]'
  - 'RT-2 The wake carrier: a session is woken when its inbox holds an unread `wake` message past its mark, and a Stop check (`gov msg stop-check`, the one hook, replacing `stop_waiter_check.py` and `stop_idle_check.py`) blocks a turn end once while an unread wake message exists or no `gov msg wait` is armed for the session; it never blocks twice in a row for the same message and never blocks a session with no address. Verify: a fixture HOME and a planted hook input: unread wake message, check blocks once with the message text, the same input again passes; no wait armed (no registered wait process for the address), blocks once naming it; with a wait armed and nothing unread, passes; no `GOV_MSG_ADDRESS`, passes. [audit 3 D7, rows 15 and 16]'
  - 'RT-5 A session that died resumes at its recorded next step: the watch pass, on a session of the registry whose process is gone without a return (no `ended` end message from the session itself and no exit file with code 0), relaunches it once through `gov launch` with `--resume` and its checkpoint, naming the checkpoint''s next step in the relaunch message; a second death of the same ticket is not relaunched and becomes one wake message to the launcher naming that it died twice. Verify: a fixture project with a checkpoint record holding `next_step: S`, a planted registry entry whose pid is dead and no return: the pass starts one launch (a stub CLI) whose arguments carry the resume session and whose first input names S, and the log holds one `relaunched` event; a second pass adds none; a second death gives one wake message `died twice`, no launch; a session that ended with code 0 is not relaunched. [EMERGENCY-2 6.3 RT-5; Contract CAP-37; audit 3 D5]'
  - 'RT-5 After a compaction the session resumes at the recorded next step without the owner restating it: the PreCompact hook writes a checkpoint record holding the next step and the SessionStart hook injects it as the first context of the resumed session. Verify: the two hooks run in order on a planted transcript and a planted checkpoint: the injected text names the checkpoint''s next step and the ticket, with no text from the owner needed; with no checkpoint it injects nothing and exits 0. [EMERGENCY-2 6.3 RT-5; CAP-37; audit 3 row 22]'
  - 'RT-6 No message passes through the owner: `gov msg send` accepts the addresses `cto`, `examin-cto`, `lead:<ticket>`, `worker:<ticket>:<role>` and `operator`, an inbox is read at each checkpoint by a lead (`gov msg read` is in the checkpoint hook''s output) and each message keeps a read mark; `gov msg digest` prints one line a day for the `notice` kind (structural, idle, GPU info) and no notice ever wakes a session; `gov msg audit --days <n>` counts, from the inbox files, the messages that name the owner as sender or receiver as relays (a message of kind `relay`, or one whose from or to is `owner`) and exits 3 when any exists. Verify: a fixture HOME with messages among the five address kinds: each read once, in the order sent; five notices give one digest line and no wake; an owner-addressed relay makes the audit exit 3 naming it, without one the audit exits 0. [EMERGENCY-2 6.3 RT-6; audit 3 D6]'
  failure:
  - 'F1 A relaunch never loops and never loses work: a session that dies every time is relaunched at most once per ticket and boot, the checkpoint is not rewritten by the relaunch, and a pass killed between the relaunch and its log line does not relaunch again (the relaunch id `relaunch:<ticket>:<boot>:<pid>:<start_ticks>` makes it idempotent). Verify: a pass killed after the launch and before the log write, then a second pass: one launch in all. [audit 3 D5]'
non_goals:
- 'Dispatching tickets from `gov plan --ready` through `gov launch` with a `ready_at` record, and RT-1 across tickets and leads (the rest of audit 3 D2, D9), RT-8 beyond what slice 1 built'
- 'The spend brake called from the pass (D8) and the cut-over of the cron line (`run_tick.sh`) to the product, which retires the CTO''s dispatcher: slice 4'
- 'The CTO''s live scratch tools and the stall check in the tick (DEC-1214 T1): not touched until the cut-over'
done_when: [DOD-1, DOD-2, DOD-3, DOD-4, DOD-5, DOD-6]
sources: [EMERGENCY-2 6.3, A-5, docs/emergency-2/audits/03-run-time-tool.md, DEC-1214, DAEO-5rgj, DAEO-rt2s]
acceptance_tests:
  path: tests/acceptance/W2-200/
  author: independent-test-designer (MR-3); written before implementation
track: A
---
# W2-200: the run-time tool, slice 3: across sessions

Written 2026-11-19 by the slice 2 lead at the end of W2-199 (the night's brief: "if time remains, write slice 3's ticket and stop"). Not built; status `deferred` until the CTO starts it.

**What is already there.** Slice 1 (`DAEO-5rgj`): `gov msg send|read|wait|watch`, the watch pass and its one state file, the launcher's end message to its launcher, the stall check. Slice 2 (`DAEO-rt2s`): the load admission and the runtime log with its job events (`ready`, `wait`, `admitted`, `started`, `ended`), a job's end message, `gov dispatch waits`. This slice closes the loop **across sessions**: the end of every kind of session or job is a message inside 2 minutes (RT-2), the one wake carrier is checked at the end of every turn (D7), a dead session resumes at its recorded next step (RT-5, D5) and the messages among the roles never pass through the owner (RT-6, D6).

**Interface notes for the test designer.** The hooks are `template/governance/kernel/hooks/stop.py` and `sessionstart.py` (the kernel text: the CTO approves the change by starting this ticket, EMERGENCY-2 3.5); the relaunch uses `gov launch`'s existing `--resume` path (read `src/gov/launch/launcher.py` for the form that exists; if none, the first line of work is naming it); `gov msg` addresses are `src/gov/dispatch/inbox.py`'s. Plant everything through a fixture HOME, a stub CLI and `GOV_RUNTIME_NOW`; no model and no network.

**Open question for the owner (one line):** the Stop check blocks a turn end for an unread wake message; should it also block when the CTO's ready list has a launchable ticket (today's `stop_idle_check.py`)? Options: (a) no: slice 2/4's dispatcher starts ready work itself (audit 3 row 16), recommended; (b) yes, until the cut-over.
