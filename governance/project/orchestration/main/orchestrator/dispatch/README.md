# The dispatcher (owner, 2026-11-01)

A plain program (Python 3 standard library, git, bash; no AI) that keeps the machine full and the work moving
without any Claude session remembering to watch. One pass a minute:

1. **The truth:** running leads from the processes (the launch form's identity marker `GOV_ROLE":"orchestrator","GOV_TICKET`, as
   `gate_check.py` counts them, and a lead worktree as the working folder), load,
   memory, the gate (`tools/gate_check.py`), the disk gate, the heavy-job slots held (`/proc/locks`, never taken), the
   merge queue busy (its `run.lock` held, or an interpreter running `land.py`; land and close are recognised by their
   arguments, not by text), the main tree clean and on `w2/integrate`. Every external command has a 60 s limit; a
   timeout is a failed check (fail closed).
2. **Returns:** every finished lead log (`log/*-A5-*.json`, non-empty) not yet in `log/returns-seen.txt` becomes an
   inbox item (`inbox/<time>-<log>.txt`: the log, the W2, its `status:` line, the first 600 characters); every log
   `started.txt` names is collected too. A lead started over 5 minutes ago with no process, no launcher waiting and
   no return becomes one inbox item "started but never ran" (once, `never-ran.txt`); it is not retried until the CTO
   lists it again with a new log name.
3. **Start:** at most one lead a pass, never within 120 s of the last (DEC-946 item 8; an unreadable time counts as
   now): the first `ready.txt` entry whose log name is a lead log (`<W2>-A5-<run>.json`)
   that is not running, not already started for that log, has no return in its log yet, has no unread inbox item,
   whose claim reads `in_progress` on `w2/integrate` **and** in its worktree, whose worktree has no tracked change,
   whose brief exists with no `@@`, and only while the gate and the disk gate are open. Launched exactly as
   `tools/lead_chain2.sh` does: `setsid -f bash tools/launch_when_gate_opens.sh <W2> <id> <brief> <log>` (the owner's
   launch form, DEC-715), recorded in `started.txt` before the launch. Every skipped entry is named with its reason.
4. **Land:** `land.txt` is claimed by an atomic rename to `land-inflight.lines` (a `land.txt` the CTO writes from then
   on is never touched), every line in one `tools/land.py` call (one batch, warm clones), only when the queue is free,
   no close runs and the main tree is clean and on `w2/integrate`; a malformed line lands nothing and the lines are
   given back. The in-flight record is written before the launch, so a failure after it never lands twice. When `land.py` has
   exited, each line's outcome (CLOSED, not landed and why, landed but not closed) goes to `land-done.txt` and an
   inbox item (with the output's last 400 characters when a ticket did not close). A dry pass finalises nothing.
5. **Status:** `status.json` and `status.txt`, which every status block reads (`python3 dispatcher.py status`); a
   pass that failed in part starts `status.txt` with `TICK FAILED`, so a stale status never looks current.
6. **Escalation:** an inbox item unread for 30 minutes writes `inbox-stale.txt` once, with stable content (the count
   and the oldest item's name), removed when nothing is stale; the sentinel's `deadman.py --watch` (with
   `deadman_patch.py` applied) pushes it to the owner's phone once per stall. It alerts during a CTO stand-by too, on
   purpose: a return waiting for a CTO who stands by still needs the owner to know.

Each step's error is logged and the pass goes on; a step never acts on an error in its own checks (fail closed).
Two passes never overlap (`tick.lock`). It never starts what is not in `ready.txt` and never lands what is not in
`land.txt`: **the order of work and every landing approval are the CTO's**.

## Files (here)
| File | Who writes it | What |
|---|---|---|
| `ready.txt` | the CTO | the ordered ready list: `<W2> <ticket id> <brief in ../briefs/> <log in ../log/>`, `#` comments; in the WBS's order, its dependencies and RESUME HERE's priorities; each brief built and its readiness checked |
| `land.txt` | the CTO | approvals to land: `<W2>=<commit>` (the lead's verified head) |
| `started.txt`, `land-done.txt`, `land-inflight.txt` | the dispatcher | what it started, landed, and is landing |
| `inbox/` | the dispatcher | finished returns and land outcomes; the CTO moves each read item into `inbox/read/` |
| `status.json`, `status.txt`, `dispatch.log` | the dispatcher | the true state; the log of every pass |
| `inbox-stale.txt` | the dispatcher | present while an inbox item has been unread 30 min |
| `OFF` | the CTO | while present, every pass does nothing |

## Starting and stopping
- Until the owner's cron line: `setsid -f bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/dispatch/loop.sh`
  (one loop at a time; its pid in `loop.pid`).
- The owner's ACT (crontab), which also restarts it after a reboot or a WSL restart:
  ```
  * * * * * /usr/bin/bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/dispatch/run_tick.sh
  ```
  (cron runs at boot too, so no `@reboot` line is needed; when cron runs it, stop `loop.sh`.)
- Stop: `touch dispatch/OFF` (every pass stops at once); remove the file to resume. Or kill the loop's pid.
- A dry pass: `bash dispatch/run_tick.sh --dry` (logs "would start" / "would land"; marks no return seen).
- Tests: `python3 -m pytest -q dispatch/test_dispatcher.py` (33; planted repositories, every external command faked).

## How the CTO uses it
Keep `ready.txt` in the plan's order (claim committed, worktree merged, brief built with its head filled, before the
line goes in); read the inbox at every wake and move read items to `inbox/read/`; approve landings in `land.txt` after
reading a DONE return; take the lead count and the load from `status.txt`, never from memory.
