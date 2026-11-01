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
3. **Start:** at most one lead a pass, 120 s apart, the first `ready.txt` entry passing every check (a lead log name;
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
5. **Status:** `status.json`, `status.txt` (`TICK FAILED` first when part of a pass failed).
6. **Escalation:** `inbox-stale.txt` (stable content) while an inbox item is unread 30 minutes; the sentinel pushes it.

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
