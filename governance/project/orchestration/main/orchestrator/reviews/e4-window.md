# Review: E4's scoring window and replays (drafts/score-once, uncommitted)

Reviewer: a fresh, read-only independent reviewer, 2026-11-07 (~21:50-22:10). The only file written is this one; stand-in
experiments ran in the session's scratchpad only. Nothing stopped, started or touched the live reranker, a trial
service or the GPU. Nothing under `~/gov-os-eval/` was opened.

**Reviewed:** `e4_prepare.py`, `e4_count.py`, `e4_prep.sh`, `e4_window.sh`, `e4_replays.sh`, `test_e4.py`,
`E4-READINESS.md`, `run_harness_tests.sh` and `README.md`. **Read against:** `E3-E5-DESIGN.md` (E4 row),
`E0B-RESULT.md`, `D4B-SCORE-ONCE.md` (§2 L3, the M cells), `RESTART-CLASSES.md` class 3, the reviewed frames
`live_window.sh` and `score_once_window.sh`, and also `rx.py`, `so_measure.sh`, `tools/proc.sh`, `tools/gpu_backstop.sh`,
`tools/heavy_slot.sh`, `tools/rerank_service_slot_hold.py`, and the clone's `gov/retrieval/measure.py` (`_ask`).

**Judgement:** `governance/project/briefs/JUDGEMENT.md`, applied as written. ADR-0001's threat model covers honest
mistakes and plausible accidents in ordinary work. Each finding answers "Can an honest agent hit this in ordinary
work?" and "Does it fail open or lose work?". A finding that is in scope, reachable in ordinary work, and fails open or
loses work blocks. Everything else is a row. The brief adds one standing rule: a defect that could leave the live
service down or the GPU over budget in ordinary use is in scope and blocks.

## Result
**Not READY: one blocking finding (F1).** `cleanup` restores on every exit path *as long as the script survives to run
it*. The output frame (`exec > >(tee …)`) lets two ordinary events kill the script before it restores anything:

- a TERM or INT sent to the window's process group;
- the caller's output pipe closing.

Each leaves the live service down and a trial service loaded on the GPU. The fix is three lines plus one test. The
frame is inherited unchanged from `live_window.sh` and `score_once_window.sh`, so they carry the same defect. The rest
holds:

- one trial service at a time;
- the backstop, armed from the first load;
- the headroom check;
- the caches;
- the count;
- the strict replays exactly as D4B-SCORE-ONCE's cells.

## Evidence gathered
- **Tests:** `test_e4.py`, run with `TMPDIR` set to the scratchpad and `PYTHONDONTWRITEBYTECODE=1`, passed **52 of 52**.
  Every write stayed in the temp folder: 28 `e4*-…` folders. A `find -newer` over the orchestrator folder,
  `~/gov-os-runs/D4B/e4`, the clone's `src`, `~/.cache/gov-os` and the trial folder found nothing new.
  `gpu-backstop.log` and `restarts.jsonl` are untouched.
- **`DRY=1 bash e4_window.sh`:** `DRY: 1 condition(s) not met; nothing stopped or started`. The one condition not met
  is `E4-REVIEWED.sha256`, the pin that comes after this review. Met:
  - the worker copy, the trial service and venv, and both snapshots;
  - both window caches: 5,486 scores, 875 route answers, the clone's store;
  - both counts: `5488 distinct texts needed; 5128 held …; 360 lacking`;
  - the clone at `c00d525fd420`, quiet, no ACT, the trial lock free, the tools.

  It also printed: slots 0 of 2 free; `GPU now 7461 of 16303 MiB`; the plan as §2-§3 state it; `the E4 window ends
  (exit 0)`.
- **`DRY=1 bash e4_replays.sh`:** `DRY: 3 condition(s) not met; nothing written`. The three: the pin, zer lacking 360,
  gte lacking 360. The 0.6B: 5,488 held, 0 lacking. The plans show `"rule":{"kind":"merge","a":"zer","b":"gte"}` and
  `{"kind":"merge","a":"q06","b":"gte"}` on the window caches and on E0b's seed, the variant with `lift_norm` 0.0766,
  and `GOV_RX_POOL_OFF=1`.
- **DRY changed nothing.** The live service's READY line is the same before and after, `2026-11-07T14:21:51 READY pid
  1657369 device cuda:0`, and pid 1657369 kept running (etime 07:10:03, then 07:10:51). Also unchanged: `rerank.log`
  at 3,497 lines, `restarts.jsonl` at 8, no `act-in-progress.txt`, no new folder under `~/gov-os-runs/D4B/`.
- **Caches, read-only:**
  - `e4/caches/gte` and `e4/caches/zer` each hold 5,486 scores and 875 route answers. Their meta is the model alone,
    `memo_keys store`, and the store `["…/w4-e0/repo", "c00d525fd420…"]`.
  - Their memo key sets equal E0b `a`'s and `b`'s.
  - E0b `a` and `b` hold the same 314 scores (equal keys and values).
  - The seeds hold scores only.
  - `need-*.txt`: 5,488 distinct each. `lack-gte` and `lack-zer`: 360 distinct each.
- **Stand-ins for F1**, in `…/scratchpad/pipe/`, each a 10-line script with the window's output frame, traps and
  cleanup:
  - **`t.sh`:** `kill -TERM -- -<pgid>` killed the `tee`, and the cleanup died at its first `echo`: `restored? NO`,
    the log ends at `started`. The same by pid: restored.
  - **`t3.sh`:** the caller's pipe closed (`| head -1`). The script died at its next `echo`, mid-run, with no cleanup.
  - **The fix variant**, `exec > >(trap "" INT TERM; exec tee -p -a LOG) 2>&1` (`t2.sh`, `t4.sh`, `t5.sh`): restored
    in both cases, and the log is complete.

## Findings

### F1 (R1, blocking): a group TERM/INT, or a closed caller pipe, kills the window before its trap restores anything
`e4_window.sh` line 237 is `exec > >(tee -a "$OUT/window.log") 2>&1`. The `tee` runs in the script's own process group
and writes to the caller's stdout.

- **(a) A TERM or INT to the window's group.** This is `proc.sh stop -<pgid>`, the standing L-0075 form, and the way
  the frame stops its own children. Ctrl-C on a foreground run does the same. The signal kills `tee` with the script.
  `trap 'exit 143' TERM` runs `cleanup`. `stop_sampler` prints nothing, so `stop_services`' first `echo "stopping the
  measure's group …"` writes to the dead pipe. bash takes SIGPIPE and dies. The measure's and the trial service's
  groups are never stopped, `restore` never runs, and the hold is not released.
- **(b) The caller's output closes.** For example, a foreground tool call outlives its limit (the window takes 15-20
  min, and a foreground call is capped at 10), or a pipe is closed. `tee` dies at its next write, and the script dies
  at its next `echo`, mid-window, with no trap at all.
- **(c) `proc.sh stop` without `--grace`** sends SIGKILL after 30 s. The cleanup takes up to 10 s for the measure, up
  to 30 s for the service, and then the restore's two `gov retrieve` calls. It can be killed partway through, by pid
  too.

Both (a) and (b) were reproduced on stand-ins (evidence above). Test E6b sends TERM to `$$` only, so it does not cover
this. `live_window.sh` and `score_once_window.sh` share the frame and the defect. They are already done, and the fix
rides with this resume.

**Fix (small):**
1. `exec > >(trap '' INT TERM; exec tee -p -a "$OUT/window.log") 2>&1`. `tee` then ignores the group signal and
   keeps writing the log when stdout goes away.
2. Make `cleanup`'s first line `trap '' INT TERM PIPE` instead of `trap - EXIT INT TERM` (keeping `EXIT` reset). A
   second signal or a dead stdout then cannot cut the restore short.
3. Add a test case that TERMs the copy's whole group (`os.killpg`) during a measure, and one whose stdout is closed.
   Each expects `EVENT restore` in the log file.
4. In `E4-READINESS.md` §2: run the window in the background with its output to a file, and stop it early by TERM to
   the script's pid with a grace longer than the cleanup (`proc.sh stop --grace 300 <pid>`), never by its group.

Ordinary work: yes, because the operator stopping a setsid job by its group with proc.sh is the standing rule (L-0075),
and a 15-20 minute foreground run outlives the tool's 10-minute limit.
Consequence: fails open (the "restored on every exit path" guarantee silently does not hold: the live service is left
down, a trial service stays loaded on the GPU, and the hold is left).

### F2 (R2, row): the headroom check reads the base from the window's start, not the GPU now
`headroom()` uses `BASE`, read once after the live stop. Before zerank it does not re-read the GPU, and nothing checks
that no other `rerank_service.py` started in the gap after gte's stop.

**The scenario:**
1. The return to the base takes over 60 s, so the slot watcher has released its slot.
2. An agent's search then starts the live 0.6B in the seconds after the base check.
3. zerank's check passes on the old base and zerank loads beside the 0.6B.
4. zerank's expected peak is about base + 2,735 + 6,220, over 14,255. rx's limit applies before each request, and the
   backstop sits at 15,872.

In the usual gap, about 10-15 s, the watcher still holds the other slot, so zerank is REFUSED and the window stops and
restores: it fails closed.

A related point: an empty `nvidia-smi` reading gives `BASE=""`, which bash's arithmetic counts as 0, so the headroom
check passes. rx then stops on the unreadable GPU.

**Fix:** run the headroom check on `$(gpu)` read just before each load, and refuse an empty or non-numeric reading.
Check `slots_free` ≥ 1 again before each start.

Ordinary work: no, because it needs an agent's search to land in a seconds-wide gap after a return-to-base wait of
more than 60 s (or an empty nvidia-smi read).
Consequence: other (a transient GPU excursion over the budget, under the backstop; rx's limit stops the next request).

### F3 (R1, row): the restore runs even if a trial service survived SIGKILL
`stop_services` ignores `proc.sh stop`'s exit 1 ("survived SIGKILL"), and `cleanup` restores anyway. The live service
then starts beside a stuck trial process.

**Fix:** remember the failure, and skip the restore with a loud line, or restore and say so in `restarts.jsonl`.

Ordinary work: no, because a process surviving SIGKILL (stuck in a driver call) is not ordinary.
Consequence: other.

### F4 (R6, row): E4-READINESS's risks and §5 are incomplete
- **§2** does not say how to run the window: in the background, with output to a file. It also does not say how to
  stop it early: by its pid with a long grace (F1).
- **§5** says the trap "runs once, on every path". This is not true for F1's paths. It is also not true for a backstop
  trip, which pauses the script's own group (`$MG`) with SIGSTOP, along with the service and the measure, so the trap
  does not run and the live service stays down until the CTO acts on the inbox item. That pause is the owner's design,
  but it is the one designed path where the live service stays down, and it should be named.
- **Risk 4:** `heavy_slot.sh`'s wait has no bound. It waits for a free slot, and also yields to a landing or close
  priority waiter (`a landing or close waits first`). The live service is down, and a trial service loaded, for the
  whole wait.

What the document states correctly:
- the commands and the pin's form (relative names, all nine files);
- the 11-06 rises: gte 7,659 − 6,096 = 1,563, zerank 12,316 − 6,096 = 6,220;
- the headroom limits: 12,391 and 7,734;
- the durations. E0b B ran 164 + 116 s fully cached. On 11-06, gte took 227 + 143 s and zerank 250 + 177 s for all
  5,486 texts. So 4-7 min per model and 15-20 min for the window are fair; 10-12 min for the replays is fair.
- the 52 of 52 test count.

Ordinary work: yes, because the CTO runs and stops the window from this document.
Consequence: other (documentation; its correction rides with F1's fix).

### F5 (R4, row): the M1 condition checks run A's own cache, while the replay reads a copy of run B's
`e4_replays.sh` checks `held q06 "$E/seed" "$E/a"`, but `copy_own` copies `$E/b`, which is what the replay reads after
the seed. The two hold the same 314 scores today (equal keys and values, verified), so the check is right in effect.

**Fix:** name `$E/b`, so the check tests what the replay reads.

Ordinary work: no, because a and b differ only if something writes into one of E0b's kept caches.
Consequence: other.

### F6 (R5, row): test_e4.py leaves its temp folders behind
The test leaves 28 `mkdtemp` folders, never removed. Under `run_harness_tests.sh` they go to `/tmp/gov-os-emg-e0b`.
Without `PYTHONDONTWRITEBYTECODE`, its imports may also refresh `__pycache__` beside the harness and in the clone's
`src`. That is Python's default, the folders already exist, and it is harmless.

Ordinary work: yes, because every run of the test does this.
Consequence: other (clutter only; nothing outside temp folders is changed in substance).

### F7 (R5, row, cosmetic): the DRY output prints each window cache's line twice
Inside `need`, `cache_ok` prints its count line to stdout before the `ok:` line, which repeats it.

Ordinary work: yes, because every DRY run prints it.
Consequence: other.

## Per check
- **R1, the restore: fail (F1).**
  - **Paths that do restore** (stand-in tests E1-E7b, read in the code): success, a failed measure, a load refused or
    late, the headroom check failing, a missing text after scoring, new route answers, the GPU not back at the base,
    the backstop failing to stay up, and a TERM to the script's pid.
  - **What each of those paths does:**
    - the measure's group is stopped (10 s), then the service's group (30 s), then the backstop, all through `proc.sh`
      by pid or group;
    - `LIVE_STOPPED=1` is set before the stop is tried;
    - the class 3 start line runs, with `rerank.by` checked and the result logged;
    - the hold is released.
  - **The failure:** a group TERM/INT or a closed stdout ends the script before the trap (F1).
- **R2, GPU safety: pass (F2 a row).**
  - `arm "$MG" "$SP"` runs right after the service starts, before READY, and `arm "$MG" "$SP" "$MP"` covers each
    measure. Each new backstop is checked alive before the old one stops (E7b).
  - The headroom check runs before each load.
  - gte's group is stopped and the GPU must be back at the base + 300 before zerank (E1d, E4).
  - One service at a time, on the default 2 slots.
  - `GOV_RX_GPU_LIMIT_MIB=14255`.
- **R3, the caches: pass.**
  - Scores go only into `e4/caches/<m>` (`GOV_RX_CACHE`). The seeds and kept caches are read, never written; E0b's
    caches are untouched.
  - The key is `rx._key("rr", "<id>@<rev>", query, text)`, the same strings in the window and the replays.
  - rx enforces the store key (meta `store`, `memo_keys store`).
  - The 875 route answers are compared before and after each model, and the window stops on any change.
  - `e4_count.py --check` must show 0 lacking after each model.
  - The set of texts does not depend on the scorer. The depth-40 head comes from the cached fusion, and a continuation
    call reranks the same head (`_kept`'s note, `measure._ask`). The strict replays stop loudly if that ever fails.
- **R4, the replays: pass (F5 a row).**
  - The rules are `merge` zer/gte and q06/gte, w = 0.5 by default, min-max over the pass (`combine`). This is grid.txt's
    `g-M3`/`g-M1`.
  - The variant is v456 + rq + `lift_norm` 0.0766, with `GOV_RX_POOL_OFF=1`.
  - Strict: `GOV_RX*` is unset and `GOV_RX_LIVE_MISSING` is never set. The run stops on `unscored`, a nonzero live
    count, or a replay that failed.
  - No GPU: COMBINE builds no client.
  - Each cell gets a fresh own cache from E0b B.
  - Every search's output is kept under `~/gov-os-eval/runs/e4/<cell>-<set>/`, and each question's first call comes
    from `first_calls()`.
  - `e0_figures.py` gives the figures, and `score138.py --same` compares each cell with E0b B.
- **R5, the tests: pass (F6, F7 rows).** 52 of 52, with writes in temp folders only. Both DRY runs printed the above
  and changed nothing (the live pid is unchanged). The other test files in the folder are unchanged and were not
  re-run here.
- **R6, E4-READINESS: fail (F4, a row).** The commands and durations are right. The risks and §5 are incomplete as F4
  states. The corrections ride with F1's fix.

```verdict
{"kpis": [
  {"kpi": "R1", "verdict": "fail", "findings": [
    {"id": "F1", "scope": "in", "ordinary_work": "yes", "consequence": "fails open"},
    {"id": "F3", "scope": "in", "ordinary_work": "no", "consequence": "other"}]},
  {"kpi": "R2", "verdict": "pass", "findings": [
    {"id": "F2", "scope": "in", "ordinary_work": "no", "consequence": "other"}]},
  {"kpi": "R3", "verdict": "pass", "findings": []},
  {"kpi": "R4", "verdict": "pass", "findings": [
    {"id": "F5", "scope": "in", "ordinary_work": "no", "consequence": "other"}]},
  {"kpi": "R5", "verdict": "pass", "findings": [
    {"id": "F6", "scope": "in", "ordinary_work": "yes", "consequence": "other"},
    {"id": "F7", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
  {"kpi": "R6", "verdict": "fail", "findings": [
    {"id": "F4", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}
]}
```

## Round 2 (the last allowed, DEC-1010), 2026-11-07 ~22:10-22:15

The same reviewer re-checked the delta under the same rules: read-only, DRY only, no live service, trial service or GPU
touched. The changed files are `e4_window.sh`, `e4_replays.sh`, `test_e4.py` and `E4-READINESS.md`.

### Result
**READY: no blocking finding.** F1 is fixed and tested on the real paths, and F2, F3, F5, F6 and F7 are fixed. F4 is
fixed apart from one new row (F8): §2's pid line is wrong when the window is started from an interactive terminal.

### What was checked
- **F1, the output frame:** line 266 is now `exec > >(trap '' INT TERM; exec tee -p -a "$OUT/window.log") 2>&1`.
  This is the form round 1's stand-ins proved for both a group TERM and a closed output.
- **F1, the cleanup:** its first line is `trap '' INT TERM PIPE; trap - EXIT`, so a second signal cannot cut it short,
  and a write to a dead output fails without killing the script.
- **F1, the restore:** both of its `gov retrieve` calls run under `setsid -w env --default-signal=INT,TERM,PIPE`. I
  checked this on this machine (scratch `sig.sh`, `sig2.sh`; coreutils env 9.4, util-linux setsid 2.39.3):
  - From a shell ignoring INT, TERM and PIPE (SigIgn `…5002`), a plain child inherits the ignores.
  - The process that `env --default-signal=INT,TERM,PIPE` execs ignores nothing (SigIgn `0`), so the live service the
    call starts stays stoppable by TERM.
  - `setsid -w` gives it its own session, waits for it and passes its exit code back (7 in, 7 out).
  - In a command substitution feeding `python3`, restore's `rerank.by` parse still reads `service`.
- **The G tests reach the real paths:**
  - `window_group` starts the copy with `start_new_session=True`, so the copy leads its own group, as under `setsid`.
  - The trial service and the measure are real `setsid sleep` processes, and `stop_group` really kills them.
  - G1 and G2 send `os.killpg(p.pid, SIGTERM/SIGINT)` to the whole group.
  - G3 closes the parent's read end (`p.stdout.close()`).
  - G3b does both.
  - Each case reads the window's log file, not its stdout, and checks that no stand-in pid is left alive.
  - `restore` is still a stub in these cases. E5f checks the real call by its text, and `sig.sh` above checks its
    behaviour.
- **F3:** `stop_services` sets `STUCK` when `proc.sh` reports that the service's group survived SIGKILL. `run_model`
  then stops, and `cleanup` does not restore. It prints `NOT RESTORED: …` and rewrites the hold to say why (E5e). This
  is right: never two models on the GPU.
- **F2:** the headroom check runs on `now=$(gpu)` just before each load, through `numeric` (so an empty or garbled
  reading stops the window). The base reading is also checked by `numeric`, and `slots_free` is checked again before
  each load (E5-E5d).
- **F5:** M1's condition reads `$E/seed` + `$E/b`, which the DRY run confirms (5,488 held, 0 lacking).
- **F6:** every temp folder sits under one root, removed when all cases pass, and no bytecode is written. After the
  run, my TMPDIR was empty.
- **F7:** `quietly` wraps the checks, and each cache's line now prints once.
- **F4:** the readiness now covers:
  - §2: run in the background, output to a file, stop with `proc.sh stop --grace 300 <pid>`;
  - §5: the frame, the cleanup's order, the backstop pause named as the one designed path that does not restore, and
    what is not covered (SIGKILL to the script, a grace shorter than the cleanup);
  - §6: risk 4 (the heavy-slot wait has no bound, and yields to a landing or close), 5b and 5c;
  - §9: the fix list.

  Commands, durations and the GPU plan are unchanged and still right.
- **Tests:** `test_e4.py` passed **61 of 61** (E0-E7, E5-E5f, G1-G3b, R0-R5, PIN1-4 ×2, P1-P9, C1-C5b), exit 0. Its
  temp root was removed. After the run:
  - no stand-in `sleep 300` is left;
  - nothing new was written under the orchestrator folder (other than the dispatcher's and the samplers' own logs),
    under `~/gov-os-runs/D4B/e4`, in the clone's `src`, or in the trial folder.

  The one `gpu_backstop.sh` process running (on group 2873049) was started 13 minutes earlier from another session.
  It is not from these tests.
- **`DRY=1 e4_window.sh`:** `DRY: 1 condition(s) not met; nothing stopped or started`. The one is the pin. All other
  conditions are met, including quiet and both caches (5,486 scores, 875 route answers, 360 lacking each), and each
  cache line prints once. GPU 7,433 MiB with the live service up. The plan shows the new headroom line.
- **`DRY=1 e4_replays.sh`:** `DRY: 3 condition(s) not met; nothing written`. The three: the pin, zer lacking 360, gte
  lacking 360. The 0.6B: 5,488 held by seed + **b**.
- **DRY changed nothing:**
  - the READY line is the same before and after, `2026-11-07T14:21:51 READY pid 1657369 device cuda:0`, and pid
    1657369 kept running (etime 07:24:36, then 07:25:17);
  - `rerank.log` grew from 3,547 to 3,559 lines, all 12 of them `MEMORY` lines from the live service serving searches
    (no READY, END or stop);
  - `restarts.jsonl` still has 8 lines;
  - there is no `act-in-progress.txt`, and no `e4/window` or `e4-window` folder.

### New finding

#### F8 (R6, row): with job control on, §2's `echo $! > window.pid` records a dead pid, and the stop line then stops nothing
§2 starts the window with `setsid bash … &` and keeps `$!`.

- **Job control off** (the CTO's tool calls): the background job is not a group leader, so `setsid` execs in place and
  `$!` is the script's pid.
- **Job control on** (an interactive terminal; `set -m` in scratch `bang.sh`): the job leads its own group, so
  `setsid` forks. `$!` is then the parent, which exits at once: `$! = 2914124`, while the script's own pid was
  2914126, and `$!` was not alive.

`proc.sh stop --grace 300 $(cat window.pid)` then prints `stopped` for the dead pid, while the window runs on to its
own end. That end still restores.

**Fix:** have the window write its own `$$` (for example to `$Q/window.pid`, or beside `window.log`), and point §2's
stop line at that file.

Ordinary work: yes, because the owner or CTO may start the window from an interactive terminal.
Consequence: other (an early stop does not happen; the window still ends normally and restores; nothing fails open
and no work is lost).

### Per check (round 2)
- **R1, the restore: pass.** Every exit path now restores, and both G cases signal or close the whole group.
  - Success, a failed measure, a refused or late load, headroom, an empty reading, no slot, texts lacking, new route
    answers, no return to the base, the backstop not staying up: E1-E7.
  - TERM or INT to the pid (E6b) or to the whole group (G1, G2); the output closed (G3); both (G3b).
  - A service that survives SIGKILL is deliberately not restored over (F3, E5e).
  - The restore's `gov` runs with default signals in its own session (verified).
  - What stays unrestored is named in §5: the backstop's SIGSTOP (the owner's design), and SIGKILL to the script.
- **R2, GPU safety: pass.** Headroom on a fresh numeric reading and a free slot before each load. The backstop,
  return-to-base and one-service-at-a-time checks are as in round 1.
- **R3, the caches: pass.** Unchanged since round 1.
- **R4, the replays: pass.** F5 is fixed; the rest is as in round 1.
- **R5, the tests: pass.** 61 of 61, nothing left behind, and both DRY runs changed nothing.
- **R6, E4-READINESS: pass (F8 a row).** F4 is fixed. F8 is a one-line correction that can ride along with any
  resume, or be applied before the window runs.

```verdict
{"kpis": [
  {"kpi": "R1", "verdict": "pass", "findings": []},
  {"kpi": "R2", "verdict": "pass", "findings": []},
  {"kpi": "R3", "verdict": "pass", "findings": []},
  {"kpi": "R4", "verdict": "pass", "findings": []},
  {"kpi": "R5", "verdict": "pass", "findings": []},
  {"kpi": "R6", "verdict": "pass", "findings": [
    {"id": "F8", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}
]}
```
