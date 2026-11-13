# ACT-NIGHTLY-RESTART-1: the nightly back, in the quiet hours, nothing else running, sized to memory (DEC-1132 (4))

By an ACT-preparation helper for the CTO (session b40cba91), 2026-11-11. Round 1 about 15:30-16:30 UTC, round 2 (the one fix
pass of DEC-1133 (4)) about 16:40-17:30 UTC. Class (b): the owner's one-line yes (the crontab row of `class-rules.yaml`).
Round 2, for review (the last round, DEC-1131); not yet reviewed; not rehearsed by the operator itself. Everything below marked **M**
was read or measured here (source named); **E** is an estimate. Dates and times are UTC (the machine's clock is UTC).

## 0. The short version

1. **What the owner says yes to: two crontab lines change, not one.**
   - **New, at 04:00:** `0 4 * * * /usr/bin/bash .../nightly/nightly_restart.sh` (the wrapper that starts the nightly, below).
   - **Back on, at 08:00:** `0 8 * * * bash .../nightly/nightly_check.sh` (the morning check; its DEC-1049 stop lifted).
   - The old stopped 04:00 line (`nightly_cron.sh`) stays commented, as does the `@reboot` check and the 09:30 sweep.
     Nothing else in the crontab moves. The yes line: `yes ACT-NIGHTLY-RESTART-1 <sha8>`.
2. **When:** 04:00 every night, through the wrapper. It runs the same `nightly_cron.sh` as before (which runs `nightly.sh
   night`), with the 08:00 morning check back. Estimated run: 59 min (E; M: D-10 run 2 took 45 min).
3. **Nothing else running:** the wrapper looks once a minute and starts only after 5 quiet minutes in a row. It gives up at
   06:01 (07:30 less one and a half times the estimate) and the 08:00 check then calls the night FAILED, as for any night
   that did not run. Once started, it switches the dispatcher off (`dispatch/OFF`) so no lead starts during the run.
4. **Sized to memory:** the run lives in a `systemd-run --user --scope` with `MemoryMax` = memory available now less 3 GiB,
   at most 12 GiB, never under 9 GiB, no swap, and the kernel kills the whole run if it passes it. 16 workers at 12 GiB.
   A watchdog also stops the run if the machine's free memory falls under 2 GiB. A planted 600 MB hog in a 200 MB cap was
   killed; the session and the shared servers stayed up (section 5). Since round 2 the wrapper also reads the cap back from
   a probe scope and refuses the night if the kernel does not enforce it.
5. **The user service manager** is up on its own now: the owner ran `loginctl enable-linger usain` (DEC-1134 (2); M:
   `loginctl show-user usain -p Linger` says `Linger=yes`). Without a user scope the wrapper still does not run the
   nightly (a night not run is better than a run without its cap).
6. **Class and undo:** (b); undo by the operator's `undo` line, or by hand with one `sed` (tested byte for byte). Since round 2
   `apply.sh` installs only over the crontab it was built for (F1, below).
7. **Order:** the wrapper and `quiet_check.py` are committed (`db8576bc0cdd`, the reviewed bytes). The fix pass for F8-F11
   (`wrapper-r2`, section 8) is a patch in the helper's folder: **the CTO commits it after round 2's READY and before queuing
   the ACT**. Until then the two checks that pin the committed wrapper's and quiet check's blob ids (checks 12 and 13 of 13) are red
   and the operator's G8 refuses: it fails closed.

## 1. When and what

### 1.1 The crontab after the ACT (M: `crontab -l`, 11-11 16:45; the same bytes as at round 1)
```
# DEC-1049 stopped: 0 4 * * * bash .../nightly/nightly_cron.sh                 (kept, still stopped: the exact undo)
0 4 * * * /usr/bin/bash .../nightly/nightly_restart.sh  # DEC-1132 (4), ACT-NIGHTLY-RESTART-1: ...   (NEW LINE 1)
0 8 * * * bash .../nightly/nightly_check.sh  # DEC-1132 (4), ACT-NIGHTLY-RESTART-1: ...                 (BACK ON, LINE 2)
# DEC-1049 stopped: @reboot sleep 300 && bash .../nightly/nightly_check.sh     (stays stopped)
# DEC-1050 stopped: 30 9 * * * bash .../nightly/runs_sweep.sh                   (stays stopped)
* * * * * /usr/bin/bash .../dispatch/run_tick.sh                                (unchanged)
*/10 0,8-23 * * * ... operator_launch.py ...                                    (unchanged)
```
Two lines change (F4: round 1 found that "one line" was said somewhere; it is two, and the owner's summary names both). The diff
is in `acts/ACT-NIGHTLY-RESTART-1/{before,after}/crontab/crontab`.

**Why 04:00 and not earlier.** (a) It is DEC-973's hour and inside the quiet hours (02:00 to 07:30). (b) `nightly_check.sh`
looks for a night whose run folder is stamped 03:55 to 07:59 (M: its code), so an earlier start would be called MISSED.
(c) The measured run is short enough to end well before 07:30 (below).

**Why the `@reboot` check and the 09:30 sweep stay stopped.** The `@reboot` check runs after any WSL restart, at any hour:
from 08:00 on it would write "MISSED" and ping P1 for a day on which the nightly had not yet been installed or had not yet
been due (E, from reading `nightly_check.sh`); the 08:00 check and the digest's own backstop (a night with no status line
is MISSED) cover a night when WSL was down at 08:00. The sweep is DEC-1050's and the owner did not ask for it. Either can be
added by a later ACT.

### 1.2 The measured duration (M: `log/nightly/history.jsonl`, `log/nightly/digest.txt`, `log/d10/run2/summary.txt`)
| run | head | workers | parallel | serial | setup | actual | cases (parallel + serial) |
|---|---|---|---:|---:|---:|---:|---|
| D-10 run 1 (11-10 18:10) | afad23270a30 | 16 | 1,082 s | 1,349 s | 41 s | 3,420 s | 9,449 passed + 130 passed, 168 red |
| D-10 run 2 (11-10 22:22) | 078e972d5647 | 16 | 1,113 s | 1,382 s | 43 s | 2,690 s | 9,612 + 134 passed, 2 red |

`nightly_estimate.py estimate` gives **3,554 s (59 min)** (M, round 1: run then: parallel 1,763 s at the lowest measured
effective parallelism 7.58, serial 1,427 s, setup 41 s, +10 %). The older runs (the 19,000-case suite, 1.5 to 5.4 h) are
no longer in its three-run window. With fewer workers the parallel part grows (12 workers: about +6 min, E).

**The window.** Start 04:00, end about 05:00 to 05:15 (E). The latest start is `07:30 - 1.5 x estimate` = **06:01** at that
estimate (it moves with the estimate). A run started at 06:01 ends by about 07:10 to 07:30. `nightly.sh`'s own rule that a run is
never cut short for the window (DEC-933 item 2.6) is kept: only a 3-hour hang limit stops a run (3.2).

### 1.3 The command and the groups
- Command: `nightly_restart.sh` -> `nightly_cron.sh` (its committed-code check, `rotate.sh`) -> `nightly.sh night`.
  Night mode, on a fresh clone of `w2/integrate`'s head, the clone's own code, the parallel run of `tests/` less the
  serial-only list, then the listed cases one by one, each failing case re-run alone, the verdict.
- **Groups (DEC-1061 (2), D4-LIST):** the full run is tier 2, the cut suite: about 9,700 parallel and 136 serial cases today
  (M: D-10 run 2). The opt-in suites `lifted` (`tests/optin-lifted.txt`, `optin-lifted-guard.txt`) and `breadth`
  (`optin-lifted*breadth*.txt`) are left out unless a run opts in (`--optin=...`, M: `tests/conftest.py`). **The nightly runs
  neither.** That is DEC-1061 (2) as written ("not counted in the full run").
- **An open point the owner may want to decide (SWITCHED-OFF-1 D4):** nobody runs `lifted` since D-10. It ran once, report
  only, 277 paths, 1,933 s with 16 workers, exit 1 (M: run 2). It cannot simply be added to the nightly: `nightly.sh` has no
  report-only mode, so a lifted red would turn every night red. Recommendation: leave it out now; if the owner wants it
  weekly, a separate later ACT adds a Sunday line with the form `d10_run.sh` uses (the `lifted` step alone, about 32 min,
  after the nightly). Not part of this ACT.

### 1.4 What it reports
- `log/nightly/digest.txt`: one line a night (head, parallel, serial, verdict, duration), written by `nightly.sh`
  (DEC-852 (3): the result in the next digest). `log/nightly/<stamp>/run.txt` holds the detail.
- `log/nightly/status.txt`: the 08:00 check's one final line for the night (`ran`, `running`, `FAILED` or `MISSED`); the
  dispatcher turns each new line into one inbox item (M: `watch_nightly`).
- **A red of the head** is `P1 NIGHTLY-RED` (held to 08:00 by `ping_gate.sh` in the quiet hours) and a package from the CTO
  (DEC-880 (c): a failure the scoped closes missed). A night that did not start or end is `FAILED` or `MISSED`, P1 at 08:00.
  Since round 2 a scope that fails after its probe is a NOT STARTED night that names the scope failure, not a MISSED one (F9).
- The wrapper's own log: `log/nightly/restart/<date>.log` (what it saw, the cap, the workers, what stopped the run).
- **The two warm-query latency reds** (DEC-1125 (1)) fail alone in every run (D-10 run 2: `verdict: red 2`). DEC-1134 (1)
  adds the two cases to `accepted_reds`, named, until W2-155 closes, as the owner's commit prepared by the CTO and applied by
  the owner's operator. Until that commit is in, every night says `verdict: red 2` and pings P1 (E: how `nightly_alone.py`
  then treats the named entries was not re-read here). This ACT does not touch it.

## 2. Nothing else running

### 2.1 What exists (all M, from the code named)
| Thing | Where | What it does for the night |
|---|---|---|
| The dispatcher's status | `dispatch/status.json`, one pass a minute | Counts leads (`lead_count`), jobs by phase, landing, close, queue, heavy slots held, heavy steps outside a slot, launches pending. |
| `CLOSE-RUNNING`, `NIGHTLY-RUNNING` | `ORCH/` | `nightly.sh` refuses to start while a close runs or another nightly's marker is under 6 h old. |
| Clean main tree, no merge, head 5 min old | `nightly.sh` night loop | Waits for them until its latest start. |
| The three heavy-job slots | `/tmp/gov-os-heavy-slot-N.lock` | `nightly.sh` takes all three itself (DEC-984); other test runs wait. Only runs that use `heavy_slot.sh`. |
| The rebuild lock | `/tmp/gov-os-rebuild.lock` | The clone's rebuild waits for any other rebuild. |
| `log/act-in-progress.txt`, the operator's `install/act-in-progress.txt` | CTO's and operator's commit freezes | Landings and ACTs read them. |
| The operator's G9 | `OPERATOR-AGENT-1` | An ACT is not applied in the quiet hours or during the nightly's window; the operator's launcher cron is `*/10 0,8-23`, so it does not run 01:00 to 07:59 anyway. |
| `dispatch/OFF` | `run_tick.sh` | "The CTO's off switch": while the file exists no pass does anything. |

### 2.2 What is missing, and what this ACT does about it
1. **Nothing keeps leads off during the run.** The dispatcher admits leads by forecast while a nightly runs (DEC-961, M:
   `README`, `dispatcher.py`); its `nightly_hold` only holds landings before the start (and is set to an empty window now).
   -> The wrapper writes `dispatch/OFF` after the quiet minutes (a second look follows) and removes it afterwards, only if
   the file still holds its own token. Cost: for the length of the run (about an hour) the dispatcher does no pass: no start,
   no landing, no inbox item, no status refresh. A CTO-made `OFF` is respected (the wrapper waits, never removes it).
   **A switch the wrapper itself left behind** (a SIGKILL, or WSL ended mid-run, so its EXIT trap never ran) is stale: its
   token names a pid. At the next start, if that pid is not alive (`kill -0`), the wrapper removes it and logs that (F8, in
   wrapper-r2).
   **A lead started by hand during the run is not held (F7, review round 1, out of this ACT's scope):** only `run_tick.sh`
   reads `dispatch/OFF`; `launch_worker.sh` and `launch_now.sh` do not. A row for the CTO, not part of this ACT (those
   scripts are other ACTs' paths; ACT A of DEC-1133 (3) already changes `launch_now.sh`): make both refuse while
   `NIGHTLY-RUNNING` exists. Meanwhile the cap, the watchdog and `mem_guard` bound the effect, and a stopped run is FAILED,
   never green.
2. **No marker for a memory measure.** Nothing records "a measure is running". -> The wrapper honours a file
   `ORCH/MEASURE-RUNNING` (a refusal while it exists). **Nothing writes it today.** Needed: whoever builds the memory audit
   (W2-170, first run Monday 11-23 21:00) or runs a D-4b measure writes it for the length of the measure. Until then: no
   measure by hand between 03:00 and 07:30, and the Monday audit (21:00) is far from 04:00.
3. **No single "is anything running" call.** -> `quiet_check.py` (200 lines, standard library): the dispatcher's status
   (fresh within 3 minutes, else it cannot count leads, a refusal), then the same without the dispatcher (a process working
   in a ticket worktree, the runs, evaluation or walled-session folders; `close_build.py`, `land.py`, `merge_queue.py`,
   `heavy_slot.sh`, `rebuild_slot.sh`, launchers, `operator_run.py`, `gov rebuild`, any pytest), the slot, rebuild and queue
   locks (probed without waiting, then let go), the marker files above, the main tree, load 3 or more, more than 100 `rg`.
   The integration store's worktree and the nightly's own clone are not counted. It prints each reason. Since round 2 its `git`
   calls run with `GIT_OPTIONAL_LOCKS=0`, so `git status` never refreshes (writes) the main tree's index (F11, in wrapper-r2).

### 2.3 How it waits and refuses
Every minute: `quiet_check.py`. Five quiet looks in a row -> the `OFF` switch -> a second look (no load test) -> go. At 06:01
(the latest start) still busy -> **refuse**: the night's `run.txt` is written with first line `nightly night: NOT STARTED by
nightly_restart.sh: <what was running>`, so the 08:00 check writes `FAILED | ...` and pings P1 (the wrapper does not ping
itself: no double ping). Also refused, the same way: code in `nightly/` that is not its commit at HEAD (the same rule as
`nightly_cron.sh`'s, for the new files), past the latest start, no user scope, a scope whose memory cap is not enforced
(F10), not enough memory.

### 2.4 A reading for the owner: process names in the quiet check (F6; not decided here)
DEC-1073 (4) (L-0075) says every wait and stop uses process ids or process groups, never a name match. `quiet_check.py`
does match process names, in **detection only** (it can only add a reason to refuse a night):
- the basenames of eight job scripts in a process's first arguments (`close_build.py`, `land.py`, `merge_queue.py`,
  `heavy_slot.sh`, `rebuild_slot.sh`, `launch_worker.sh`, `launch_now.sh`, `operator_run.py`), `pytest`, and `gov rebuild`
  (M: `quiet_check.py`, `process_reasons`);
- a count of processes whose command name is `rg`, above 100 (M: `rg_count`); and the watchdog's `ps -eo comm= | grep -cx rg`,
  which only writes an inbox item above 200.

No wait is on a named process and no stop is by name: the wrapper waits on its own two children by pid (`$SPID`, `$WPID`), and
stops only the exact unit it created (`systemctl --user stop gov-nightly-<stamp>.scope`, else `kill -TERM $SPID`).
**The reading the CTO puts to the owner in the digest:** a detection-only match that can only refuse a night is outside
DEC-1073 (4), in the spirit of DEC-1133 (5) D1 (the exception for `rg`, there for a stop by program name; this one stops
nothing). If the owner reads it otherwise, the alternative is a pid-only quiet check (the dispatcher's status and the lock
probes only), which would stop seeing a hand-started job script or test run. The CTO decides nothing here; the owner's answer
goes to the decision register.

## 3. Sized to memory

### 3.1 The measurements (M unless E)
- The machine: 24,607,392 kB (23.5 GiB), 8 GB swap, 20 CPUs (`.wslconfig`: `memory=24GB`, `swap=8GB`). Memory available at a quiet
  moment: 17 to 19.7 GB (`status.json`, D-10 run 2's gate line `have=19723792 kB`).
- D-10 `vmstat` at 30 s (my script `vmstat_peaks.py`, MemTotal less free, buffers and cache = in use): the nightly's own
  phase raised memory in use by **6.58 GB (run 1, 16 workers, from 6.87 to 13.45 GB)** and **8.08 GB (run 2, from 4.44 to 12.51
  GB)**; no swap activity in run 2 (max 7 KB/s), 3.3 MB/s in run 1. About **0.41 to 0.51 GB a worker** (the rise over 16).
  Peak runnable processes 102 to 107. (The `lifted` step after run 2 reached 15.09 GB in use, 7.17 GB above its start.)
- `peaks.json`/`phase-peaks.json` (11-11 15:19): `nightly.test` p95 5.27 GB (72 samples); `nightly.rebuild.lexical` 7.28 GB
  (29 samples); `gate.json` `rebuild_peak_bytes` 7.58 GB. The per-worker figure is not recorded as such: it is the rise over
  16 workers, above.
- The floors: 3 GiB (`memory_floor_bytes`, DEC-942), the out-of-memory trip-wire at 2 GiB (`oom_floor_bytes`, DEC-947 (5)).
- The 11-11 14:19 stop: 2,161 `rg` processes, 19.3 GB (about 9 MB each); nothing the nightly started.

### 3.2 The rule and what it gives
- **Cap** = MemAvailable at the start less 3 GiB, at most **12 GiB** (1.5 times the largest measured rise), refuse under
  **9 GiB** (the clone's rebuild peaks at 7.3 GB). **Workers** = (cap - 2 GiB) / 0.6 GB (0.6 = the 0.51 measured plus 18 %),
  between 4 and 16.
- MemAvailable 20 GB -> cap 12 GiB, **16 workers** (what D-10 ran). 13 GB -> cap 9.4 GiB, **12 workers**. Under about 12.3 GB
  available (11.4 GiB gives 8.4 GiB) -> refused, a night not run, FAILED at 08:00 with the figure.
- The scope also has `MemorySwapMax=0` (a run past its cap is killed, never pushed into the machine's swap), `OOMPolicy=kill`
  (when one process is killed for memory, the whole run is; a lone killed pytest worker would give a half-red verdict),
  `RuntimeMaxSec=10800` (3 h, a hang limit; flagged for the owner: DEC-933 item 2.6 says a run is never cut short for the
  window, this is only for a hang, set well past any measured run).
- The run's processes get `oom_score_adj` 500 (a process may raise its own), so if the machine itself ever runs short the
  kernel picks them before the sessions and the servers.

### 3.3 Exactly how the limit is applied (nightly_restart.sh)
```
systemd-run --user --scope --quiet --unit=gov-nightly-<stamp> \
  -p MemoryMax=<cap>M -p MemorySwapMax=0 -p OOMPolicy=kill -p RuntimeMaxSec=10800 \
  env PYTEST_XDIST_AUTO_NUM_WORKERS=<w> NIGHTLY_RESTART=1 \
  bash -c 'echo 500 > /proc/self/oom_score_adj; exec bash "$@"' _ .../nightly_cron.sh
```
**Before it, the probe (F10, in wrapper-r2):** a scope with `MemoryMax=64M` runs `cat` on its own `memory.max`; the wrapper
requires the answer `67108864` and refuses the night with "the memory cap is not enforced" otherwise (the memory controller
is delegated to the user manager by `user@.service`'s defaults here; the probe makes a machine where it is not a refused night,
never an uncapped one). The whole nightly (the clone, the rebuild, both test phases, the re-runs) is inside the scope, so the cap
covers the rebuild too. `nightly.sh` already passes `PYTEST_XDIST_AUTO_NUM_WORKERS` through (`heavy_slot.sh --held` takes it as
given). Page cache inside the cap is reclaimed before any kill. A scope killed for memory ends with exit 137 (a SIGKILL of the
run's own command; `nightly.sh` never exits 137). The wrapper now waits up to 5 s for the unit to settle before it reads the
unit's `Result` and resets its failed state (a rehearsal of the old wrapper once left the unit listed as failed after a kill, probably because the reset came before the
unit had settled, E; the exit code still decides). It removes the `NIGHTLY-RUNNING` marker (a kill skips `nightly.sh`'s own trap, and
`close_queue.sh` would wait on the marker forever), appends a line to the night's `run.txt`, and leaves the clone for the diagnosis.
**A scope that fails after the probe** (the command never runs; exit 1) leaves no run folder, which the 08:00 check would read as
MISSED ("cron, WSL or the PC was not up"). In wrapper-r2 the wrapper then writes a `NOT STARTED` run.txt that names the scope
failure, so the morning line says FAILED, with the reason (F9).

### 3.4 The watchdog, the tripwire and the prerequisite
- **Watchdog** (every 10 s, inside the wrapper, outside the scope): MemAvailable under the 2 GiB trip-wire -> `systemctl --user
  stop gov-nightly-<stamp>.scope` (the exact unit it created; never a name match over processes, L-0075, DEC-1073), recorded.
  This covers a hog that is not the nightly's: the cap bounds the nightly, not the machine, so the watchdog gives the memory
  back by ending the one thing the wrapper is allowed to end.
- **`rg` tripwire** (DEC-1132 (3) (a)): `tools/oom_watch.sh` already writes an inbox item above 200 `rg` processes. The wrapper
  repeats it during the run (the same item text, at most one in 10 minutes) so the tripwire holds even if `oom_watch.sh` is
  not running that night; it stops nothing. Before the start, more than 100 `rg` is "something else running".
- **The user service manager.** `systemd-run --user` needs it; cron has no session of its own. The owner ran
  `loginctl enable-linger usain` (DEC-1134 (2); M: `Linger=yes`), so the manager runs without a login. The wrapper sets
  `XDG_RUNTIME_DIR` and the bus address itself, as cron has neither (tested with `env -i`). If it is ever down at 04:00 the
  wrapper refuses ("no systemd user scope", FAILED at 08:00).
- Not used: `ulimit -v` (a per-process address-space limit: 16 workers with their children sum to no bound, and numpy or
  torch reserve far more address space than they use, so it kills the wrong runs). A cgroup `MemoryMax` is the brief's first
  choice, and it works here.

## 4. Class, commands, rollback

### 4.1 Class (M: `governance/project/operator/class-rules.yaml`, `OPERATOR-AGENT-1.md` section 2)
- The ACT touches **one file, the crontab**: root `crontab`, row `crontab` -> **(b)**, a control path; claimed class (b).
  Needs the owner's yes in the chat, `yes ACT-NIGHTLY-RESTART-1 <sha8>`, after the review (G6). `act_class.classify` on the
  bundle is run in `build_act.py gates` (result in section 6). Review round 1 agreed: class (b), no script hits.
- **The wrapper files are not touched files of the ACT.** `governance/project/orchestration/nightly/` has no row of its own,
  so `nightly_restart.sh` and `quiet_check.py` fall to the catch-all row (O, `control: false`: "not an ACT's business"; the
  landing check flags only `control: true` paths). The CTO committed the two in the ordinary way (`db8576bc0cdd`, blobs
  `5e08e24764f0` and `1b887c11b491`, the copies round 1 read; `test_nightly.sh` passes). The manifest's checks hold the ACT back
  until the committed bytes are the reviewed ones: `git ls-files --error-unmatch`, `git diff --quiet HEAD -- nightly/`, `bash
  -n`, and, since round 2, **two pins on the blob ids (F3)**: `git rev-parse HEAD:.../nightly_restart.sh` and `.../quiet_check.py`
  must be the blob ids of wrapper-r2's files. `nightly.sh`, `nightly_cron.sh`, `nightly_check.sh`, `nightly_estimate.py` are not changed.
- **Which blob ids are pinned (the choice F7-F10 asked for):** drafting F8, F9, F10 and F11 each came out small (the diff,
  `wrapper-r2.diff`, is 78 added and 10 removed lines in all: the wrapper 28 and 6, `quiet_check.py` 3 and 1, the test 47 and 3; section 8), so the
  checks pin the **patched** blobs: `nightly_restart.sh` `dd5129a25715b3bc00685e6104eba79f195563e2` and `quiet_check.py`
  `3225297532f2dcdbb849c21e758cd4529b300dc2` (`git hash-object` of `files/nightly-r2/`). **The CTO commits wrapper-r2 after
  round 2's READY and before queuing the ACT.** At today's head (the round-1 bytes) the two pins are red, so the dry run in the
  operator's clone refuses the ACT: fails closed, never applied on bytes nobody reviewed. If round 2 asks for a change to
  wrapper-r2, the blob ids change and the bundle is rebuilt (the manifest sha with it).
- No script hit raises the class: apply.sh has no `sudo`, push, tag, install, network or `rm` outside the project.

### 4.2 The owner's commands
1. The prerequisite is done (linger, DEC-1134 (2)).
2. The chat line after the review: `yes ACT-NIGHTLY-RESTART-1 <sha8>`, meaning **yes to these two crontab changes: the new 04:00
   `nightly_restart.sh` line, and the 08:00 `nightly_check.sh` line back on** (nothing else moves). The operator's gates do the
   rest (frozen copy, decision, rehearsal log, review READY, hashes, class, live state as stated, dry run with undo, no quiet
   hours). By hand, if the owner prefers the terminal: `bash acts/ACT-NIGHTLY-RESTART-1/apply.sh check`, then `apply`, then the
   checks in the manifest, then `verify`.
3. `apply.sh` (F1, rebuilt for round 2): `apply` installs the after crontab only over the before (or does nothing when it is
   already the after); over a crontab that moved since the build it exits 3 and touches nothing. `undo` puts the before back
   only over the after (or does nothing when it is already the before), else exit 3 and nothing touched. `check` and `verify`
   decide by the crontab's sha256 as before.

### 4.3 Rollback (the line commented again)
- The operator's: `undo ACT-NIGHTLY-RESTART-1 <sha8>` (its tested undo, byte for byte, for 7 days; it needs the crontab to be
  the after: a crontab changed since is left as it is, exit 3).
- By hand, exact (tested in round 1: the output equals the `before` crontab, `cmp` silent):
```bash
crontab -l > ~/crontab.pre-nightly-restart-undo-$(date +%Y%m%d-%H%M).txt
crontab -l | sed -e '/ACT-NIGHTLY-RESTART-1: the nightly back/d' \
  -e 's|^\(0 8 \* \* \* bash .*nightly_check\.sh\)  # DEC-1132 (4), ACT-NIGHTLY-RESTART-1:.*$|# DEC-1049 stopped: \1|' | crontab -
```
- A run in progress is not stopped by the undo. To stop it: `bash tools/proc.sh stop <pid of the scope's command>` (its pid
  is in the wrapper's log) or `systemctl --user stop gov-nightly-<stamp>.scope`. A leftover `dispatch/OFF` whose text begins
  `nightly_restart pid` is the wrapper's: the next start removes it when its pid is dead (F8); by hand, remove it.

### 4.4 Order of work and the first night
1. Round 2's review of the rebuilt bundle (the last round, DEC-1131). 2. After READY, the CTO commits wrapper-r2 (the patch
`wrapper-r2.diff`; the patched copies are in `files/nightly-r2/`; `git apply` on the repository root) in the ordinary way; the
blob ids must be the pinned ones. 3. The CTO rebuilds the bundle at the moment of queuing if the crontab or the pins moved
(`python3 build_act.py all`): with the same crontab and the same bytes the manifest sha is the same (F2, section 6), so the
READY still holds. 4. Owner's yes; the operator applies outside the quiet hours. 5. **The first night is watched**: the CTO reads
`log/nightly/restart/<date>.log` and the 08:00 check; the first real run is the proof of `nightly_cron.sh` inside the scope
(the full suite was not run here: DEC-968).
The wrapper runs only if the machine is up at 04:00; whether the Windows wake task of ACT-NIGHTLY-0400 is installed is not
known to me (a Windows-side step, class (O); not read).

## 5. The rehearsal (M: `acts/ACT-NIGHTLY-RESTART-1/rehearsal.log`, built by `build_act.py rehearse`)
Everything is planted: the wrapper's cases (`test_nightly_restart.sh`) use a fixture repository (its head dated 2020), a scratch
orchestrator folder, a process list, slot and rebuild locks, a fake meminfo. They touch no live file, no server and no crontab,
and use no `/tmp` folder outside the scratch folder (`TMPDIR` set). The rehearsal log holds nothing that depends on the live head,
the date or a process id (F2).
- **Part 1, apply.sh on a stub crontab** (a file seeded with the live bytes): check, verify (red before), apply, byte-equal to the
  after, the manifest's crontab checks, **F1's cases** (apply over a crontab that moved: exit 3, the added line stays; undo over a
  moved after: exit 3, untouched; apply when already the after, undo when already the before: exit 0, untouched), undo byte for
  byte, a moved crontab refused by `check`, a tampered frozen copy refused (4). Then the five "committed code" checks in a
  fixture repository holding wrapper-r2 (green), and negatives: a changed uncommitted file, a file not committed, and **F3's**:
  a wrapper committed with other bytes fails its pin while the other pin holds.
- **Part 2, the operator's own form** (as `operator_run.py`'s dry run builds it): a **clone of the live head**
  (`git clone --no-checkout`, `checkout --detach`), a planted HOME in this folder's `tmp/`, the crontab stubbed by a file seeded
  with `crontab -l`, a clean environment with only `HOME`, `PATH`, `LANG` and the stub's variables; `apply.sh check`, `apply`,
  every manifest check run in the clone, `verify`, `undo`, the crontab byte for byte, the clone's and the HOME's trees
  unchanged, the clone clean. The one addition: when the live head does not hold wrapper-r2 yet, the CTO's commit of it is simulated
  in the clone alone (so the pins can be green); at a head that holds it, nothing is simulated and nothing differs. No untracked
  tool is needed by `apply.sh` or any check, so none was copied in. Never the real crontab, never a real nightly, never a full suite.
- **Part 3, the wrapper's 62 cases (F5), re-run for the rebuild on the wrapper as committed in that clone** (`nightly/`, with the
  test beside the ACT in `packages/`), not a copied log. **Every case ran for real**, including the real
  `systemd-run --user --scope` ones, each with a stub run command: the sizing and scope-limit cases (a stub that exits at once;
  the caps are limits, not reservations), the 600 MB hog in a **200 MB** cap, the watchdog (stops in seconds), the 3 s time limit
  and the 4 s tripwire case. The whole part takes about 55 seconds (M). Two stand-ins only, by design: a `systemd-run` that drops
  its limits (F10's refusal case) and an unparseable `RuntimeMaxSec` (a real scope that fails, F9). Cases not run: none.
  - **The cap kills the hog:** the run ended non-zero, the wrapper said "KILLED by its memory cap" (exit 137), the sibling died
    with it (whole run), `NIGHTLY-RUNNING` and `dispatch/OFF` were gone, the test's own session stayed alive, every shared-server
    process seen before was alive after, and no gov-nightly unit is left loaded or failed.
  - **The scope's real limits** read from inside it: `memory.max` 12,884,901,888 (12 GiB), `memory.swap.max` 0,
    `memory.oom.group` 1, `oom_score_adj` 500; `dispatch/OFF` present during the run and gone after; the same under `env -i`.
  - **Refusals:** a planted lead (status and process), a held heavy slot, a held rebuild lock, an ACT in progress,
    `MEASURE-RUNNING`, `CLOSE-RUNNING`, `NIGHTLY-RUNNING`, the operator's freeze, a stale status, the CTO's `OFF`, 150 `rg`,
    load 3.4, an untracked file in the main tree: each busy and named; the wrapper refuses at the latest start with the right
    `run.txt` first line and starts nothing; past the latest start; no user scope; changed uncommitted code; 11.4 GiB available.
  - **Round 2's cases (F8-F11):** a stale `dispatch/OFF` (dead pid) removed and logged, the night runs; one whose token names a
    live pid kept, the night refused; a scope that fails after the probe leaves a NOT STARTED run.txt naming the scope; a run that
    ran and exited 1 keeps its own run.txt (no NOT STARTED line added); a probe whose `memory.max` is not 64M is refused with the
    nightly never started; `quiet_check.py` leaves the index alone (and the control: a plain `git status` does rewrite it). Run
    against the round-1 copies, five of the nine fail (the stale-OFF run and its clean-up, the scope failure, the uncapped probe,
    the index), so they show something.

## 6. Counts, the manifest and the operator's gates
- **Rehearsal: 114 cases, 0 failures** (`rehearsal.log` ends `failures: 0`): 52 for the ACT (parts 1 and 2), 62 for the wrapper and
  the quiet check (part 3).
- **F2, the same inputs give the same sha (M):** the bundle was built twice (`build_act.py all`, from scratch each time: build,
  rehearse with the 62 real cases, finalize, gates): **both runs gave the manifest sha256 `0e308cde3aecb0347a0aad634a8bf248a3df881cad500c23c8044611cec8ed88`**. The rehearsal log holds no
  live-head line, no pid, no date; the manifest changes only when the crontab, `apply.sh`, the checks (so the pinned blob ids) or
  the log's own text change.
- **The operator's own code on the bundle** (`build_act.py gates`, read-only): `validate_manifest` pass; 5 files hash as the
  manifest says; the path rule passes on `apply.sh` and every check; `act_class.classify`: **class b**, no script hits, why
  `crontab:crontab`. **Manifest sha256 `0e308cde3aecb0347a0aad634a8bf248a3df881cad500c23c8044611cec8ed88`; the yes line `yes ACT-NIGHTLY-RESTART-1 0e308cde`.**
- At the live head when built (`483a5a2bee12`) wrapper-r2 is not committed, so 2 of the 5 git checks (the pins) are red there, as designed; they are
  green in the rehearsal's clone once the CTO's commit is simulated. `test_nightly.sh` (nightly/'s own tests) passes with the
  patched copies in place (M: a scratch copy of the folder; not wrapped in `heavy_slot.sh`, whose own test N19 would fail nested).
- Not done here, as the brief says: no crontab change, no commit or stage, no change to a committed tool; wrapper-r2 and the bundle
  are in the helper's folder only.

## 7. Open points for the CTO and the owner
1. **The reading on process names (F6)**, section 2.4: put to the owner in the digest; not decided here.
2. **A lead started by hand during the run is not held (F7):** a row for the CTO (`launch_worker.sh`, `launch_now.sh` refuse while
   `NIGHTLY-RUNNING` exists; other ACTs' paths).
3. **MEASURE-RUNNING** (2.2 (2)): W2-170 and any hand measure must write it; today nothing does.
4. **The two named latency reds**: DEC-1134 (1), the owner's commit, until it is in every night says `red 2` and pings P1.
5. **`lifted`** (1.3): not in the nightly; the owner decides whether a weekly report-only run is wanted.
6. **The 3 h hang limit** (3.2) and **the `@reboot` and sweep lines left stopped** (1.1): the owner may change either.
7. **A stale `dispatch/OFF` is removed only when its token's pid is dead.** After a WSL restart the pid may belong to some other
   process; then the OFF stays, the next night is refused (FAILED, P1), nothing is lost, and one `rm` fixes it (E: pids restart
   low after a boot, and the wrapper's was one of many).
8. **Not tested:** `nightly_cron.sh` and `nightly.sh` inside the scope end to end (no full suite, DEC-968; the first night is
   the proof), the Windows wake, a real cron firing.

## 8. Round 2: what changed since round 1 (review r1: READY, class (b), F1-F11)
Round 1's bundle is kept in `acts/ACT-NIGHTLY-RESTART-1.round1/` (manifest `2ec8ae17c698`). The rebuild is round 2's, the last.

| Finding | What changed |
|---|---|
| F1 | `apply.sh`: `apply` needs the live crontab to be the before (or already the after); `undo` the after (or already the before); else exit 3, nothing touched. Rehearsal cases 3, 7, 16, 21, 22. |
| F2 | The rehearsal log has no live-head line (the old "at the live head today: red, green, red" is gone, printed to the console only); part 3 has no pid or count that varies. The manifest sha is the same on a rebuild: shown twice (section 6). |
| F3 | Two new checks pin the blob ids of `nightly_restart.sh` and `quiet_check.py` at HEAD, to the patched ones of wrapper-r2 (`git hash-object`); red at any other head. |
| F4 | Sections 0, 1.1 and 4.2 name both crontab lines (the 04:00 wrapper and the 08:00 `nightly_check.sh` back on) in the owner's yes. |
| F5 | The rebuild re-runs `test_nightly_restart.sh` on the wrapper as committed in the operator-form clone, with real `systemd-run --user --scope` for the memory cases (stub run commands, 200 MB hog cap; about 55 s). Not run: none. |
| F6 | Section 2.4: the reading the CTO puts to the owner in the digest; not decided. |
| F7 | Stays a row (section 2.2, 7 (2)): `launch_worker.sh` and `launch_now.sh` are other ACTs' paths. |
| F8 | wrapper-r2: at start a `dispatch/OFF` whose token's pid is not alive (`kill -0`) is removed and logged. |
| F9 | wrapper-r2: a non-zero exit with no run folder today writes a NOT STARTED run.txt naming the scope failure. |
| F10 | wrapper-r2: the probe reads the scope's own `memory.max` and refuses the night unless it is 67108864. A hook `NR_SYSTEMD_RUN` for the tests. |
| F11 | wrapper-r2: `GIT_OPTIONAL_LOCKS=0` in `quiet_check.py`'s `git()`. |
| (new) | wrapper-r2 also lets the unit settle (up to 5 s) before the wrapper reads its `Result` and resets its failed state: found by this round's rehearsal (a failed gov-nightly unit left after a memory kill, in 1 of 2 runs of the old wrapper; the likely cause, E, is a reset that comes before the unit has settled), not in review r1's list; 1 line. |

`wrapper-r2.diff` (the patch, applies with `git apply` at the repository root) and `files/nightly-r2/` (the three patched
files: `nightly_restart.sh`, `quiet_check.py`, and `test_nightly_restart.sh` with 9 new cases and the pid and count texts taken out so
the log is stable). The wrapper's own committed copy in `packages/ACT-NIGHTLY-RESTART-1/` is the old test: the patch
replaces it.
