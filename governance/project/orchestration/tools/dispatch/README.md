# The dispatcher (owner, 2026-11-01; DEC-1008 item 5, DEC-1010 items 6 and 7)

A plain program (Python 3 standard library, git, bash; no AI) that keeps the machine full and the work moving without
any Claude session remembering to watch. **Its code is here, committed; its state is in
`.gov-runtime/scratch/orchestrator/dispatch/`** (`DISPATCH_STATE` moves it, for the tests only). The owner's crontab
runs one pass a minute: `run_tick.sh` (here) → `dispatcher.py tick` (here), reading and writing the state folder.

## One pass
1. **The truth:** running leads from the processes (the launch form's identity marker
   `GOV_ROLE":"orchestrator","GOV_TICKET` and a lead worktree as the working folder), waiting launchers and starts
   under 10 minutes old (counted as leads), load, **real busy cores** (from `/proc/stat` deltas since the last pass:
   user + nice + system + irq + softirq + steal; iowait is not busy) and the embedding server's own cores, memory, the
   disk gate, the heavy-job slots held, the merge queue (its `run.lock`, or an interpreter running `land.py`), a close
   running, the main tree (clean, on `w2/integrate`), heavy steps running outside a slot. Every external command has
   a 60 s limit; a timeout is a failed check.
2. **Returns:** every finished lead log not in `log/returns-seen.txt` becomes an inbox item; a start that never ran
   (5 minutes, no process, no return) becomes one, once.
3. **Start:** nothing starts while the embedding server's last known state (`embed-health.json`, from the previous
   pass's check, 4d) is HUNG or NOT RUNNING: every ready entry waits with "embedding server hung: starts held
   (DEC-1015)". Landings and closes are not held; they fail their own rebuild check instead. Otherwise,
   at most one lead a pass, 120 s apart, the first `ready.txt` entry passing every check (a lead log name;
   not running or launching; not already started for that log; no return yet; no unread inbox item for it; the claim
   `in_progress` on `w2/integrate` and in its worktree; no tracked change there; the brief without `@@`) **and admitted**:
   - **real CPU, first and for every admission (the `gate_check` fallback included):** busy cores + the embedding
     server's CPU p95 above what it uses now < nproc − `cpu_margin` (2), over the interval since the last pass (at
     most 3 minutes); a first pass, or a sample older than 3 minutes, records the sample and refuses ("measuring"); a
     dry pass records nothing; an unreadable `/proc/stat` refuses;
   - **CPU slots:** running and launching leads < slots × `K` (3 × 2);
   - **memory** (`memory_rule: slots`, the default): free memory + the leads' current trees ≥ the floor + each running
     or launching lead at the larger of the lead p95 outside verification and its own outside maximum + the newcomer
     likewise + 3 slot runs + the shared services' headroom (the embedding server and the code-graph daemon at their
     p95 above what they hold; a reranker outside every lead tree, while a queue or close runs); `memory_rule:
     literal` counts each lead at its all-sample p95 instead;
   - never while a heavy step has run outside a slot for over 5 minutes (a finding);
   - with `peaks.json` missing, over 7 days old, or under 120 minutes of history outside verification: `gate_check`'s
     verdict (fail closed to the old rule). The status shows `gate_check`'s verdict either way, for comparison.
   It launches with `launch_now.sh` (here): the owner's launch form copied verbatim from
   `tools/launch_when_gate_opens.sh`, without its wait on `gate_check` (admission is the dispatcher's), keeping the
   disk gate.
4. **Land:** `land.txt` claimed by an atomic rename, every line in one `tools/land.py` call, only when the queue is
   free, no close runs and the main tree is clean and on `w2/integrate`; the outcome to `land-done.txt` and the inbox.
   **A close holds a landing only when it conflicts (DEC-1014 item 1):** a running `close_build.py` closing one of the
   landing's tickets (its arguments' W2 ids), or one committing its records (only `.tickets/` or `closes/` files
   modified in the main tree: one pass); any other close does not. `land.py`'s own close commit retries up to 3
   times while another commit holds `index.lock`.
   **The nightly's hold (DEC-1018 item 1):** the nightly (cron 04:00) starts only after 5 quiet minutes with a clean
   main tree and an unchanged `w2/integrate`, and gives up at its latest start; a landing run takes about 45 minutes.
   So from `nightly_hold_from` (config, "03:15", local time) no landing is claimed until the nightly has started:
   `NIGHTLY-RUNNING` in the orchestrator folder newer than today's hold start, or a line for today in
   `log/nightly/status.txt` (written only from 08:00 by `nightly_check.sh`, or after a reboot, so in practice the marker is
   what releases it; a night that gives up, or exits early and removes its marker, stays held until the end). The hold
   always ends at `nightly_hold_until` ("05:30").
   Status: `land: held for the nightly (DEC-1018) until it starts`. A landing already in flight is finalised as usual,
   never stopped; starts and the inbox are not held. The dispatcher's own writes stay in its state folder under
   `.gov-runtime/` (ignored by git), so they never make the main tree unclean.
4b. **The CTO's watchers, as passes (DEC-1014 item 3), each finding one inbox item, once:** a lead's new commit not on
   `w2/integrate` whose subject marks a key result (baseline, measure, figures, hit@5, findings report, probe record,
   research record, PACKAGE; `interim-seen.txt`, keyed by the commit's patch-id, else its subject and tree, so a
   rebased commit is not reported again; a worktree seen the first time is marked silently); a new line of
   `log/guard-refusals.jsonl` with no `verdict` or `judgement` yet (`guard-offset.txt`, written only when the file
   grows; a file shorter than the offset is re-baselined to its end with no items); the nightly's status line for
   today (`nightly-seen.txt`). Their items carry their own label (`Interim:`, `Guard:`, `Nightly:`), never `W2:`, so
   they hold no lead's start. No inbox item overwrites another.
4c. **The guard harvest** (`tools/guard_refusals.py`, at most every 10 minutes): after the start and land decisions,
   detached (`dispatcher.py harvest` in its own session), one at a time under `guard-harvest.lock`, limited to
   `guard_harvest_timeout_s` (300). Its result is `guard-harvest.json`, shown in the status; a non-zero exit or a
   timeout is one of the pass's failures until a harvest succeeds.
4d. **The embedding server's health (DEC-1015 item 2):** every `embed_check_every` passes (1), after the decisions,
   one test request (`POST /api/embed`, `embed_model` `qwen3-embedding:0.6b`, a fixed short text, limit
   `embed_timeout_s` 30, never through a proxy, the server's own keep-alive left alone). `embed_hung_after` (3)
   failures, timeouts or refused connections in a row make an incident: HUNG, or NOT RUNNING when the last check was
   refused. Either writes one `Server:` item and a `server:` line in `inbox-stale.txt`, once per incident, and holds
   starts (step 3); both clear when it answers. A restart runs only when
   `embed_restart_cmd` is set in `config.json` (default none: alert only), the incident has lasted `embed_restart_after_s`
   (900) with no answer in that window, and no restart ran in the last `embed_restart_min_gap_s` (1800); each restart
   is logged and itemised. State: `embed-health.json`. Status: `embedding server: healthy (0.05 s) | HUNG since ... |
   NOT RUNNING since ... | failing (n in a row)`.
4e. **The heavy-slot holders' progress (DEC-1015 item 2):** each holder of `/tmp/gov-os-heavy-slot-*.lock` (from
   `/proc/locks`; a waiter is not a holder) has its process tree's CPU time (utime + stime) compared with the last
   sample (`slot-progress.json`, keyed by pid and start time). Not grown for `slot_idle_s` (900): IDLE, one `Slot:`
   item naming the slot, the pid, the command, the tree (cwd) and the idle time, and a `slot N pid P:` line, once per
   holder; it clears when the CPU grows or the holder ends. A holder is never killed; while the server is HUNG the item
   says the holder is likely waiting on it. Status: `heavy slot holders: slot N pid P (command) idle M min`.
5. **Status:** `status.json`, `status.txt` (`TICK FAILED` first when part of a pass failed).
6. **Escalation:** `inbox-stale.txt`, one line per cause, each written once per stall: `sentinel: ...` (first) while
   the sentinel is expected (`sentinel-expected` in the state folder) and its watch has written nothing parseable to
   `log/deadman.log` for 2 hours (DEC-1014 item 2: also one inbox item per silence; a malformed line falls back to
   the newest parseable one, none reads "unreadable"); `server: ...` while the embedding server is HUNG or NOT RUNNING (4d);
   `slot N pid P: ...` while a slot holder is IDLE (4e); `inbox: ...` while an inbox item is unread 30 minutes. The
   sentinel pushes it, keyed on its first 150 characters, so the short lines come first.

`peaks.json` (state folder) is refreshed at most hourly from `log/capacity/kinds.jsonl` and `log/lead-mem.jsonl`
(7 days). `config.json` (state folder) holds `K`, `cpu_margin`, `memory_rule`, `min_outside_samples` and the rest.

## The state folder
`ready.txt` and `land.txt` (the CTO's), `started.txt`, `land-done.txt`, `land-inflight.*`, `never-ran.txt`, `inbox/`
(the CTO moves read items to `inbox/read/`), `status.*`, `peaks.json`, `config.json`, `cpu_prev.json`,
`dispatch.log`, `tick.lock`, `loop.lock`, `loop.pid`, `OFF` (while present, every pass does nothing).

## Running it
- The owner's crontab line (ACT): `* * * * * /usr/bin/bash /home/usain/Dynamic-Agentic-Engineering-OS/governance/project/orchestration/tools/dispatch/run_tick.sh`
- Without cron: `setsid -f bash /home/usain/Dynamic-Agentic-Engineering-OS/governance/project/orchestration/tools/dispatch/loop.sh`.
- Stop: `touch .gov-runtime/scratch/orchestrator/dispatch/OFF`. A dry pass: `bash run_tick.sh --dry`.
- Tests: `python3 -m pytest -q tests/unit/orchestration/test_dispatcher.py`.
