---
id: DAEO-rt3s
status: in_progress
deps: [DAEO-rt2s]
links: [DAEO-5rgj, DAEO-rt2s]
created: 2026-11-19T02:30:00Z
type: task
priority: 1
assignee: engineer
external-ref: W2-205
tags: [dispatch, msg, checkpoint, run-time-tool, emergency-2]
wbs_id: W2-205
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
- tests/unit/dispatch/test_w2_205*
- tests/unit/msg/**
- tests/unit/launch/test_w2_205*
- tests/unit/checkpoint/**
est_loc: 600
kpis:
  success:
  - 'RT-2 Every end reaches the watching session within 2 minutes: a lead, a worker (a session `gov launch` started, whoever started it) or a heavy job (W2-199''s runs) that ends gives one `wake` message to its launcher''s address, with an `end` event in the runtime log (`ended_at`, `id`, `to`, `kind`), and `gov dispatch waits --ends` prints each end''s gap (the message''s time less `ended_at`) and exits 3 for a gap over 120 s. Verify: a fixture HOME with a lead, a worker and a job ended at known times, the watch pass run once a minute (planted clock `GOV_RUNTIME_NOW`): every gap is 120 s or less, the report lists all three, and a planted end whose message is 200 s late exits 3 naming it; an end with no message yet is a gap to now. [EMERGENCY-2 6.3 RT-2; audit 3 D4; W2-199 gives the job end]'
  - 'RT-2 The wake carrier: a session is woken when its inbox holds an unread `wake` message past its mark, and a Stop check (`gov msg stop-check`, called by the one Stop hook `stop.py`) blocks a turn end only for an unread `wake` message, once per message: it never blocks twice for the same message, never blocks for a notice, never blocks a session with no address, and never because nothing is waited on (the owner retired inbox waiters and idle-check wake-ups, DEC-1212 (4)). It does not block for a launchable ticket (the dispatcher starts ready work). Verify: a fixture HOME and a planted hook input: unread wake message, the check blocks once with the message text, the same input again passes; an unread notice only, passes; a session with nothing unread and no `gov msg wait` armed, passes; no `GOV_MSG_ADDRESS`, passes; a second, newer wake message blocks once more. [audit 3 D7, rows 15 and 16; the CTO''s rulings 1 and 2]'
  - 'RT-5 A session that died resumes at its recorded next step (off by default until the cut-over, switched by the key `relaunch` in `~/.gov-os/runtime/config.json`; the key absent or false: no relaunch, only the wake message): the watch pass, on a session of the registry whose process is gone without a return (no end message for it from the launcher''s address, and no exit file of the entry holding 0), with the key true relaunches it once through `gov launch` with `--resume <its session id>` and its checkpoint, naming the checkpoint''s next step in the relaunch''s last argument; a second death of the same ticket in the same boot is not relaunched and becomes one wake message to the launcher naming that it died twice; an entry with no recorded session id is not relaunched and becomes one wake message naming that it cannot resume. Verify: a fixture project with a checkpoint record holding `next_action: S`, a planted registry entry (a session id, a dead pid, no return) and `relaunch` true: the pass starts one launch (a stub CLI) whose arguments carry the resume session and whose last argument names S, and the log holds one `relaunched` event; a second pass adds none; a second death gives one wake message `died twice`, no launch; a session whose launcher message says exit code 0 is not relaunched; the key false or absent: no launch and the wake message of slice 1 only. [EMERGENCY-2 6.3 RT-5; Contract CAP-37; audit 3 D5; the CTO''s ruling 4]'
  - 'RT-5 After a compaction the session resumes at the recorded next step without the owner restating it: the PreCompact hook writes a checkpoint record holding the next step (`gov checkpoint`''s automatic record, as it does now) and the SessionStart hook injects it as the first context of the resumed session (source `compact`, `clear` or `resume`, any role with a ticket), ahead of every other part. Verify: the two hooks run in order on a planted transcript and a planted checkpoint: the injected text begins with the checkpoint''s next step and the ticket, with no text from the owner needed; with no checkpoint it injects nothing of the kind and exits 0. [EMERGENCY-2 6.3 RT-5; CAP-37; audit 3 row 22]'
  - 'RT-6 No message passes through the owner: `gov msg send` accepts the addresses `cto`, `examin-cto`, `lead:<ticket>`, `worker:<ticket>:<role>` and `operator`, an inbox is read at each checkpoint by a lead (`gov msg read` is in the checkpoint hook''s output: the SessionStart injection names it) and each message keeps a read mark; `gov msg digest` prints one line a day for the `notice` kind (structural, idle, GPU info) and no notice ever wakes a session; `gov msg audit --days <n>` counts, from the inbox files, the messages that name the owner as sender or receiver as relays (a message of kind `relay`, or one whose from or to is `owner`) and exits 3 when any exists. Verify: a fixture HOME with messages among the five address kinds: each read once, in the order sent; five notices give one digest line and no wake; an owner-addressed relay makes the audit exit 3 naming it, without one the audit exits 0. [EMERGENCY-2 6.3 RT-6; audit 3 D6]'
  failure:
  - 'F1 A relaunch never loops and never loses work: a session that dies every time is relaunched at most once per ticket and boot, the checkpoint is not rewritten by the relaunch, and a pass killed between the relaunch and its log line does not relaunch again (the relaunch id `relaunch:<ticket>:<boot>:<pid>:<start_ticks>` is claimed in a file before the launch, so the pass is idempotent). Verify: a pass killed after the launch and before the log write, then a second pass: one launch in all. [audit 3 D5]'
  - 'F2 The stall check, the push and the live tick are untouched, and nothing live is switched: the stall check in the pass (`check_stall`) and its push behave as W2-121c tests them, the cron line, the scratch dispatcher and `heavy_slot.sh` and this repository''s own `.claude/settings.json` are not edited (DEC-1214 T1, T2; DEC-1216 (5)). Verify: `tests/acceptance/W2-121c` stays green and `git diff` of the branch touches none of those paths.'
non_goals:
- 'Dispatching tickets from `gov plan --ready` through `gov launch` with a `ready_at` record, and RT-1 across tickets and leads (the rest of audit 3 D2, D9), RT-8 beyond what slice 1 built'
- 'The spend brake called from the pass (D8) and the cut-over of the cron line (`run_tick.sh`) to the product, which retires the CTO''s dispatcher: slice 4'
- 'The CTO''s live scratch tools and the stall check in the tick (DEC-1214 T1): not touched until the cut-over'
- 'The 99 % plan push and the owner''s decision pushes (the CTO''s own); the hooks registered in the repository''s own `.claude/settings.json` (the cut-over, slice 4)'
done_when: [DOD-1, DOD-2, DOD-3, DOD-4, DOD-5, DOD-6]
sources: [EMERGENCY-2 6.3, A-5, docs/emergency-2/audits/03-run-time-tool.md, DEC-1214, DAEO-5rgj, DAEO-rt2s]
acceptance_tests:
  path: tests/acceptance/W2-205/
  author: independent-test-designer (MR-3); written before implementation
track: A
---

# W2-205: the run-time tool, slice 3: across sessions

Written 2026-11-19 by the slice 2 lead; started by the CTO's brief the same night (the CTO's rulings: the Stop check blocks only for an unread wake message, the ready-list question is answered (a), the stall check and push stay, RT-5's relaunch is off by default, nothing live is switched).

**What is already there.** Slice 1 (`DAEO-5rgj`): `gov msg send|read|wait|watch`, the watch pass and its one state file, the launcher's end message to its launcher, the stall check. Slice 2 (`DAEO-rt2s`): the load admission and the runtime log with its job events (`ready`, `wait`, `admitted`, `started`, `ended`), a job's end message, `gov dispatch waits`. This slice closes the loop **across sessions**.

## Interface (the lead's decisions, so tests and code agree)

- **End events.** Every end is one `end` event in `~/.gov-os/runtime/log.jsonl`: `{at, event: "end", id, kind: "lead"|"worker"|"job", to, ended_at, ticket|job}`. `id` is the message id (`end:...` for a session, `job:<job>` for a job); `to` the recipient address; `ended_at` ISO-8601. Writers: the launcher's `_end_message` (`ended_at` = now), `admission.wake` (`ended_at` = now), and the watch pass for an end it detects (`ended_at` = the previous pass's time for a registry entry or a pid watch, the file's mtime for an exit-file watch; the pass's own events carry `estimated: true`). A lead has `kind` `lead` when its registry role is `orchestrator`, else `worker`. A duplicate id writes no second `end` event.
- **`gov dispatch waits --ends [--json]`**: for each `end` event, the gap = the `at` of the message with that `id` in the inbox `to` (the first one) less `ended_at`; with no such message, the gap is now (`GOV_RUNTIME_NOW` or the clock) less `ended_at` and the row says `unsent`. One line per end (`<id> <kind> <to> gap <n> s`), `finding:` lines for gaps over 120 s; exit 3 on any finding, else 0. Without `--ends`, `waits` is as W2-199 made it.
- **`gov msg stop-check`**: reads the Stop hook's JSON on stdin; the address is `$GOV_MSG_ADDRESS`. It prints the Claude Code hook decision `{"decision": "block", "reason": "<the unread wake messages' text>"}` on stdout and exits 0 to block, prints nothing and exits 0 to pass. A message blocked once is recorded by id in `~/.gov-os/inbox/<address>/stop-seen` and never blocks again. `stop.py` runs the check after it writes its checkpoint and prints the check's output; it always exits 0.
- **Addresses.** `inbox.check`'s grammar already accepts `cto`, `examin-cto`, `lead:<ticket>`, `worker:<ticket>:<role>` and `operator`: no address is newly refused (W2-121c's own addresses stay valid); the tests prove all five send and read. The kinds are `wake`, `notice` and `relay` (`gov msg send` accepts `relay` so that the audit can name one; a relay never wakes).
- **`gov msg digest [--day <YYYY-MM-DD>]`**: one line per day for the unread-or-read `notice` messages of the address (`$GOV_MSG_ADDRESS` or an argument): `<day> <n> notices`. **`gov msg audit --days <n>`**: scans every inbox file; a relay is a message of kind `relay` or one whose `from` or `to` is `owner`; one line each naming its id, from and to; exit 3 when any, else 0.
- **Relaunch.** The pass reads `~/.gov-os/runtime/config.json` (`{"relaunch": true}`; absent, unreadable or false means off). The launcher records `session_id` in a worker's registry entry (and a lead's when it has one). A death: the entry's process is gone, no message with the entry's end id from `entry.address` in `entry.notify`'s inbox, and no `exit_file` of the entry holding 0. The pass claims `~/.gov-os/runtime/relaunch/<id>` (O_EXCL) before it starts `gov launch <role> <ticket> -- --resume <session id> "<text naming next_action>"` in `entry.repository` (detached, the `gov` the pass itself runs as), then logs `relaunched`. Any earlier claim for the same ticket and boot makes a death `died twice` (one wake message to `entry.notify`, id `died-twice:<ticket>:<boot>`).
- **Hooks.** `sessionstart.py` for source `compact`, `clear`, `resume` with a ticket: its first context part is `Resume at the recorded next step (<ticket>): <next_action> (checkpoint <path>)` plus the line `Read your inbox: gov msg read`; no checkpoint, no such part. `precompact.py` is not changed (the CTO approved two kernel hooks, `stop.py` and `sessionstart.py`): it keeps writing the automatic record, and the inbox line `gov msg read` is carried by SessionStart alone.

