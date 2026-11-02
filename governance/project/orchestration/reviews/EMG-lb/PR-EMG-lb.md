# Review record: EMG-lb, the Gov Load Balancer in the dispatcher (emg/lb at c5d2ad004b99)

Reviewer: independent, fresh, read-only (the CTO's emergency reviewer; session debdb3f7), 2026-11-02 evening.
Scope: `git diff w2/integrate...emg/lb` (dispatcher.py, the new balancer.py, README, gov_reranker_gpu_slot.py,
nightly/rotate.sh's one line, their unit tests) and the scratch `tools/targets_report.py` + `test_targets_report.py`.
Briefs: EMG-common.md, JUDGEMENT.md (word for word), EMG-lb-engineer.md, BRIEF-MACHINE-TARGETS.md (parts 1 and 3).

## Evidence run

- Unit tests through the gate (`heavy_slot.sh`, TMPDIR `/tmp/gov-os-emg-lb-review`): test_dispatcher.py,
  test_balancer.py, test_gov_reranker_gpu_slot.py: **215 passed, 6 skipped in 85.6 s**. test_targets_report.py:
  **6 passed**.
- Two small reproductions of the branch's own functions with planted data (state under my TMPDIR, never the live
  state, `python3 -B`): the outputs are quoted under F1 and F2.
- Live figures read only (no pass run): `dispatch/gpu-health.json` (RTX 5070 Ti, total 16,303 MiB, used 10,455 MiB,
  one holder `reranker`), `status.txt` 20:37 (1 of 2 GPU reranker slots held), `config.json` (sets none of the derived
  keys), `heavy_slots.conf` (3 x 6), 20 CPUs, MemTotal 24,607,384 kB. `/proc/<lead pid>/stat` of the running lead's
  `claude` process: own CPU 53 s, reaped children's CPU 4,497 s.

## What holds (checked, no finding)

- **Today's limits on this machine:** at the floors derive_limits gives band 14-18, margin 2, 3 x 6, slots_gpu/cpu
  3/2, headroom 2,048 MiB (16,303 x 0.1256 = 2,047.7), rerank_gpu_slots 2, spill floor 1,019. config.json sets none
  of them, so these apply. (But see F2: the reranker count does not stay at 2 once measured.)
- **A pass cannot hang on the counter read:** `gpu_shared_read` runs through `sh()`, which has `timeout=` and turns
  `TimeoutExpired` into exit 124 (POSIX `subprocess.run` kills, then waits; no wait on grandchildren's pipes).
  powershell.exe absent or interop off is an `OSError`, caught; a non-zero exit or unparsable output is
  `{"ok": False}`. The status line says "unread", no failure. The whole rule is in its own `try` in `tick()`, after
  the start and land decisions.
- **No corrupt state stops a pass:** targets.json, phase-peaks.json, jobs-prev.json and gpu-health.json are written
  tmp+rename. machine.json, limits.json and forecast.json are not (F8), but each is read through `load_json`, which
  falls back to its default, and limits.json is rewritten on the next pass when it differs. A forecast exception sets
  `forecast_error`, and a lead's admission then refuses (fails closed). A balancer status or record exception is a
  "TICK FAILED in part" line; the status is still written, and starts and landings happen earlier in the pass.
  `__pycache__/` is git-ignored, so `import balancer` from the main tree's copy does not dirty the main tree.
- **Missing samples:** below `phase_min_samples` each phase takes the larger of today's floor and its samples, so a
  missing sample never means "plenty of room". No RAM floor: memory_room refuses. CPU unreadable or measuring:
  admission() refuses before the forecast.
- **The GPU rule:** budget = this pass's nvidia-smi `used` + the running jobs' current-phase GPU peaks above what
  they hold, compared with total minus headroom. A spill is a reading above `gpu_shared_floor_mib`. Each is one
  gpu-alert at once, once per incident (`budget_since` / `spill_since`; cleared only by a reading that holds; an
  unread reading changes nothing).
- **Incidents:** `breach_step` opens a continuous target after more than 900 s breached, an event target at its
  first event, never twice while open, and closes after 900 s held. A breach back inside the quarter hour is the
  same incident. "Not measured" changes nothing. Tests cover 14 min → nothing, 16 → one, still → no second,
  15 held → closed.
- **gov_reranker_gpu_slot.py:** `_slots()` uses the env var, else limits.json's `rerank_gpu_slots` when it is an int
  from 1 to 64, else 2. Missing, unreadable, torn, non-dict, 0, bool or out of range all give 2. The README states
  the install is the owner's ACT.
- **rotate.sh:** `keep "$ORCH/log/capacity" "balance-*.jsonl" 30 204800` matches the dispatcher's rename past 20 MB.
- **targets_report.py:** read-only; working hours across midnight; T1 ≥ 80 %, T2/T3/outside-slot 100 %, T4/T5 zero
  events; causes from the records; worst hour. No finding.

## Findings

### F1: a job's CPU counts its reaped children's whole lifetime again, so phase peaks blow up and the forecast refuses leads

`proc_facts` now records `cpu_ticks_all` = utime+stime+cutime+cstime, and `job_cores` takes its delta per process.
When a process reaps a child that the previous pass already counted, the parent's cutime jumps by the child's
**entire** CPU time in one interval. Examples: pytest reaping its xdist workers; a lead's `claude` reaping the Bash
shell of a gated test run; land.py reaping its pytest. The job's cores for that pass come out at many times the
machine. Reproduced with planted processes: a heavy-slot run with 6 workers at 1 core for 6 minutes, reaped:

```
jobs after the reap: [{'kind': 'slot', 'name': 'pid 10', 'pid': 10, 'phase': 'test', 'cpu': 36.0, ...}]
slot.test peak cpu: 36.0 floor (1 of 30 samples)
forecast refuses (CPU binding): CPU 40.0 of 18 cores (busy 8 + running jobs' peaks 30.0 + the newcomer's 2.0)
```

Live, the running lead's `claude` process carries 4,497 s of reaped CPU against 53 s of its own. Every gated test
run it ends lands as one spike sample of roughly (the run's core-seconds / 60) cores in the lead's next phase,
usually `lead.build`. Below 30 samples a phase's peak is the **max** of its samples, so one spike sets
`lead.build` (or `landing.other`, `nightly.other`, `lead.review`) at 20-40 cores for the 72-hour window. Each
running job in that phase then adds about that much to the forecast's CPU need, and every newcomer is refused while
one runs. Above 30 samples the p95 still sits at spike level whenever spikes are more than 5 % of a phase's samples.
That is likely for `lead.build` (one spike per test run) and certain for `landing.other` (one per landing among
few samples). The README says the cores are "utime + stime since the last pass", which does not match the code.

- Fix proposed (one function): in `job_cores`, take from each tree's delta the last-seen `cpu_ticks_all` of the
  processes that vanished since the last pass (clamp at 0), and cap a job at nproc. Optionally use the p95, not the
  max, below `phase_min_samples` (bounded by the floor). Immediate mitigation if merged as is:
  `"forecast_admission": false` in config.json (the forecast is then shown, not applied).
- Ordinary work: yes, because every lead's gated test run, every landing's test run and every slot run ends this
  way. It is reproduced with the branch's own functions and seen in the live lead's /proc figures.
- Consequence: loses work, as the CTO's question defines it ("the dispatcher stops starting"). Ready leads are not
  started while any lead builds or a landing finishes. Nothing written is lost; on a strict reading this is "other".
  The moderator may reclassify it.

### F2: the dispatcher prices GPU memory with the derived reranker count while the installed hook still allows 2, so the forecast and gpu_room fail open

`config()` now replaces `rerank_gpu_slots` with `derive_limits`' figure: (total − the embedders' measured share −
headroom) // one reranker's measured share, from phase-peaks.json's `_shares`. Below 30 samples each share is the
**max** of its samples. Today's live reading (one reranker on the GPU, 10,455 MiB used) gives a reranker share of
about 4.6-4.7 GiB, so the derived count drops from 2 to **1** within about one phase refresh (10 min) of the merge.
The installed `gov_reranker_gpu_slot.py` (the old copy, until the owner's ACT) still hands out **2** lock files. With
`rr_slots` = 1 and 1 held, `free` = 0: the forecast prices the newcomer's reranker at 0, and `gpu_room` drops its
share too. A newcomer's reranker then takes the real second lock and pushes the card over its budget. That is last
night's failure (DEC-1029). Reproduced:

```
shares {'embedders_gpu_mib': 5800, 'reranker_gpu_mib': 4655, ...}
derived rerank_gpu_slots 1
slots=derived: forecast admits (binding GPU: GPU memory 10.2 of 13.9 GB (... the newcomer's 0.0; 0 GPU reranker slot(s) free))
slots=2 (the installed hook): forecast refuses (GPU binding): GPU memory 14.8 of 13.9 GB (... the newcomer's 4.5; 1 GPU reranker slot(s) free)
```

The same lower figure also shrinks `reranker_reserve`'s RAM reserve (`allowed x max_kb`) once its era has a day of
samples. A spuriously large share (a private embedder, desktop GPU use, a row during a model load), below 30
samples, can drive the derived count to 0: the dispatcher then never prices a reranker, while the new hook copy
falls back to 2. So "today's behaviour unchanged: 2 reranker GPU slots" does not hold past the first measured rows.
The GPU budget rule and T3 catch the overrun only after it happens.

- Fix proposed: price free slots with the count the hook really enforces. Until the ACT, keep `rerank_gpu_slots` at
  the installed count (2) and show the derived figure as the proposal. After it, use min(derived, installed), and
  never a derived 0 on a machine with a GPU. Immediate mitigation if merged as is: `"rerank_gpu_slots": 2` in
  config.json (an explicit number wins; the Limits line says so).
- Ordinary work: yes, because it follows from today's live GPU reading with no unusual step: one reranker holding a
  slot while the embedders are resident.
- Consequence: fails open (GPU memory admitted past total minus headroom; a CUDA out-of-memory risk).

### F3: a GPU not read in the last 5 minutes is not judged by the forecast, as by gpu_room

When gpu-health.json is stale or unreadable, the forecast's GPU part is skipped, so it can neither bind nor refuse.
This matches DEC-1032's accepted rule in `gpu_room` ("its absence is not a shortage"; the GPU watch alerts apart).
It is pre-existing behaviour reproduced, not introduced.

- Ordinary work: yes, because nvidia-smi can time out or fail when the driver is in trouble.
- Consequence: fails open (bounded: the GPU watch's alert; an accepted decision). Scope: out (DEC-1032's rule, not
  this ticket's change). It belongs to the Wave 3 row list, or to the owner if the rule should change.

### F4: T4 repeats stale events when a server's log becomes unreadable

`judge_progress` returns early when its log cannot be stat'ed and leaves the last read's `sv["t4_new"]` in place.
`judge_targets` then counts those lines again every pass. The T4 incident never closes, and a "More" note is
appended to its record every minute. The same happens for one pass if `watch_embedding` raises.

- Fix: clear `t4_new` / `t4_n` before the early return, or stamp them with the read time.
- Ordinary work: yes, because a configured server's log can be moved or removed (a restart writing elsewhere, a
  clean-up), though rarely.
- Consequence: other (a noisy incident; nothing admitted, nothing lost).

### F5: the forecast gates only a lead's admission; slot grants and rebuilds are not gated

Brief item 2 asks to "admit a start (a lead, a slot grant, a rebuild)". The forecast's verdicts for slot and
rebuild are only written to forecast.json, and heavy_slot.sh and rebuild_slot.sh do not read them. The README states
this honestly: heavy_slot.sh belongs to another engineer.

- Ordinary work: yes, because every gated test run and rebuild starts without it.
- Consequence: other (no regression against today; the gate's own slot count still limits them; it is a gap
  against the brief, for the heavy_slot.sh engineer or a follow-up).

### F6: the "heavy step outside a slot" incident opens after about 20 minutes, not 15

The FINDING appears only after `outside_slot_limit_s` (300 s), and the target's breach clock starts then. So the
incident opens about 5 + 15 minutes after the step starts.

- Ordinary work: yes, because any ungated heavy step takes this path.
- Consequence: other (5 minutes later than the brief; it still opens once and closes).

### F7: reaped CPU documented as own CPU

Folded into F1: README "A process's cores: its utime + stime since the last pass" versus the code's
utime+stime+cutime+cstime. To fix with F1.

- Ordinary work: yes, because every reader of the README is misled about the measure.
- Consequence: other.

### F8: limits.json, machine.json and forecast.json are written in place, not tmp+rename

limits.json is read by every reranker start once the new hook copy is installed. A torn read falls back to 2, which
is safe today but above a derived 1 (see F2) for that one worker.

- Ordinary work: no, because the window is a few microseconds once per change of the limits.
- Consequence: other (worst case one worker at today's count).

### F9: a hung Get-Counter, and powershell from cron, are unverified

On timeout the Linux side of powershell.exe is killed. Whether the Windows process ends with it is not verified; a
Get-Counter that hangs every pass could leave one powershell.exe a minute on Windows. Interop from cron is likely
fine (`/run/WSL/1_interop` exists for callers without `WSL_INTEROP`) but was not tried from cron. If it fails, the
spill rule says "unread" in the status and never alerts (no inbox item). Check after the merge: the `GPU rule:`
status line should show a numeric shared reading.

- Ordinary work: no, because Get-Counter rarely hangs, and the cron-interop failure is a hypothesis, not observed.
- Consequence: other.

### Note (not a finding): the brief's planted GPU case

5.6 + 3.5 + 3.5 GiB = 12.6 against 13.9 GiB, so the forecast admits it. The engineer reported this and tests a
refusal with an extra 2.5 GiB private server. The arithmetic is right. With the live measured reranker share (about
4.6 GiB) the same case is refused once F2 is fixed.

## Classification (DEC-809)

F1 in scope, ordinary yes, loses work (stops starts; the CTO's definition). F2 in scope, ordinary yes, fails open.
Both block under DEC-1010 item 1. F3 out of scope (DEC-1032's rule). F4, F5, F6, F7 in scope, other. F8, F9
ordinary no: rows.

Recommendation: one round (the second at most), confined to `job_cores` (F1, with F7's README line) and the
reranker slot pricing (F2), with F4's two-line clear riding along. If the CTO must merge now: merge with
config.json `"forecast_admission": false` and `"rerank_gpu_slots": 2`. That leaves today's admission exactly as it
is, with the forecast shown but not applied.

```verdict
{"kpis": [
 {"kpi": "1-phases-and-measured-peaks", "verdict": "fail", "findings": [
   {"id": "F1", "scope": "in", "ordinary_work": "yes", "consequence": "loses work"},
   {"id": "F7", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "2-forecast-before-admission", "verdict": "fail", "findings": [
   {"id": "F1", "scope": "in", "ordinary_work": "yes", "consequence": "loses work"},
   {"id": "F2", "scope": "in", "ordinary_work": "yes", "consequence": "fails open"},
   {"id": "F3", "scope": "out", "ordinary_work": "yes", "consequence": "fails open"},
   {"id": "F5", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "3-pairing", "verdict": "pass", "findings": []},
 {"kpi": "4-gpu-rule-budget-and-spill", "verdict": "pass", "findings": [
   {"id": "F9", "scope": "in", "ordinary_work": "no", "consequence": "other"}]},
 {"kpi": "5-machine-derived-limits", "verdict": "fail", "findings": [
   {"id": "F2", "scope": "in", "ordinary_work": "yes", "consequence": "fails open"},
   {"id": "F8", "scope": "in", "ordinary_work": "no", "consequence": "other"}]},
 {"kpi": "6-standing-targets-and-incidents", "verdict": "pass", "findings": [
   {"id": "F4", "scope": "in", "ordinary_work": "yes", "consequence": "other"},
   {"id": "F6", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "robustness-no-crash-hang-or-corrupt-state", "verdict": "pass", "findings": []}
]}
```

## Round 2

Reviewer: independent, fresh, read-only (round 2, the last, DEC-1010), 2026-11-02 night. Scope: `git diff
c5d2ad004b99 22b99617443f` (dispatcher.py, balancer.py, README, test_dispatcher.py, test_balancer.py), against F1, F2,
F4 and F7 of round 1. Round 1's F3, F5, F6, F8, F9 are rows by the moderator's triage and were not reviewed again.

Evidence: test_dispatcher.py, test_balancer.py, test_gov_reranker_gpu_slot.py through the gate (TMPDIR
`/tmp/gov-os-emg-lb-review2`): **224 passed, 6 skipped in 125.4 s**. The installed hook
(`~/.local/share/gov-os/reranker-venv/lib/python3.12/site-packages/gov_reranker_gpu_slot.py`, read only) has line
`int(os.environ.get("GOV_RERANK_GPU_SLOTS", "2"))`, which `hook_slots`' regex matches (2). The repo's new copy reads the
same `limits.json` path and the same 1 to 64 rule as `hook_slots`.

### What the fix does, checked

- **F1 (reaped CPU):** `job_cores` now keeps each process's parent in `jobs-prev.json`; a process in the last sample and
  gone now has its last-seen CPU taken off its nearest running ancestor's delta (clamped at 0, walk bounded at 64 hops);
  every process and every job is capped at `nproc()`. An old record without `ppid` is read (no subtraction; the cap
  holds). A pid that was orphaned rather than reaped only makes the count lower (fail-safe). The spike test
  (`test_lbr_f1_a_reaped_childs_lifetime_is_not_counted_again`) rebuilds the reviewer's 6 workers x 6 minutes case plus a
  grandchild: 7.0 cores, not 37. The cap test gives 20.0 for 50 cores. `pick` takes the larger of the floor and the
  second-largest sample below 30 samples; a test shows one 36-core sample leaves the floor 1.0 and two give 30.0. No new
  crash path: all keys are strings, `None` ancestors end the walk, `ppid` is always in the facts.
- **F2 (reranker slots):** `config()` prices `rerank_gpu_slots` with the larger of the proposal and `hook_slots` (the
  installed copy's count: its default 2; or limits.json's number for the new copy; 64 if no hook is installed; 2 if it
  is unreadable); the proposal alone goes to `limits.json`, so the new hook copy and the dispatcher agree. `derive_limits`
  gives at least 1 with a GPU. Held slots count as used (`free = slots - held`); a tool's slot holds no GPU memory
  (`rr_gpu`, so the reranker share is not divided by it). `forecast` caps the running jobs' part, then the newcomer's, at
  the free slots' share. The test reproduces the reviewer's case exactly (shares 5,800/4,655, one held: refuses with
  "GPU memory 14.8 of 13.9 GB ... 1 GPU reranker slot(s) free"), then the new-copy and no-hook forms.
- **F4:** `judge_progress` clears `t4_new` and stamps `t4_at` before its early return; `judge_targets` counts only
  events stamped this pass. The test moves the log away, ticks 15 times, and sees no "More" note and then the closure.
- **F7:** the README now states the reaped-children measure and the priced slot count.
- **Fail-open check of the "no hook installed" case (64):** `gpu_room` then always prices a reranker share (as with a
  free slot today); `reranker_reserve` keeps `min(p95, 64 x peak)`, so it stays bounded by the p95. No new refusal
  loop; the price is conservative. The `rerank_gpu_slots` rule that ends extra rerankers was not found to use the count
  anywhere else.

### R2-F1: a proposal larger than the hook's count is priced as larger (max), not as the count the hook enforces

`max(hook, proposed)` prices more free slots than an old-copy hook hands out when the derived or explicit number exceeds
2 (a larger GPU, or measured shares that fall). The newcomer's reranker is then priced when the hook would give it no GPU
slot: pricing too high, never too low.

- Ordinary work: no, because on this machine the derived figure is 1 to 2 (16,303 MiB, embedders about 5.8 GB, reranker
  about 4.6 GB); it needs another GPU or a much smaller measured share, and the effect is a refusal that errs safe.
- Consequence: other (the price errs high; it could delay a start only while the GPU is nearly full).

### R2-F2: `hook_slots` does not see a caller's `GOV_RERANK_GPU_SLOTS`, and a rising proposal is priced one pass late

The hook honours the environment variable of the process that starts the worker; the dispatcher cannot see it (the
docstring says so). With the new copy installed, limits.json is rewritten after `config()` read it, so a rise of the
proposal is enforced by the hook up to one pass (a minute) before it is priced.

- Ordinary work: no, because the variable is set by no tool found in the tree, the new copy is not installed yet (the
  owner's ACT), and the derived number rises rarely.
- Consequence: other (one minute of a possible under-price, and only after the ACT).

### R2-F3: two spike samples below 30 still set a phase's peak

`pick` ignores only the single largest sample. After the F1 fix a reaped run no longer produces a spike, so the
remaining source is a real burst seen twice.

- Ordinary work: no, because it needs two bursts above the machine's real use inside a phase's first 30 samples, and
  each job is capped at the CPU count.
- Consequence: other (a refusal that clears when the samples pass 30 or leave the 72-hour window).

### Classification

F1 and F2 of round 1: fixed, each with a test reproducing the reviewer's case. F4 and F7: fixed. No new way found for a
pass to crash, hang, write corrupt state, stop starting or landing, or admit more than the machine allows. R2-F1 to R2-F3
are ordinary no, consequence other: Wave 3 rows.

```verdict
{"kpis": [
 {"kpi": "1-phases-and-measured-peaks", "verdict": "pass", "findings": [
   {"id": "R2-F3", "scope": "in", "ordinary_work": "no", "consequence": "other"}]},
 {"kpi": "2-forecast-before-admission", "verdict": "pass", "findings": [
   {"id": "R2-F1", "scope": "in", "ordinary_work": "no", "consequence": "other"},
   {"id": "R2-F2", "scope": "in", "ordinary_work": "no", "consequence": "other"}]},
 {"kpi": "3-pairing", "verdict": "pass", "findings": []},
 {"kpi": "4-gpu-rule-budget-and-spill", "verdict": "pass", "findings": []},
 {"kpi": "5-machine-derived-limits", "verdict": "pass", "findings": [
   {"id": "R2-F1", "scope": "in", "ordinary_work": "no", "consequence": "other"},
   {"id": "R2-F2", "scope": "in", "ordinary_work": "no", "consequence": "other"}]},
 {"kpi": "6-standing-targets-and-incidents", "verdict": "pass", "findings": []},
 {"kpi": "robustness-no-crash-hang-or-corrupt-state", "verdict": "pass", "findings": []}
]}
```
