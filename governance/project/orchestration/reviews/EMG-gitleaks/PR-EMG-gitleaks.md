# Independent review: EMG-gitleaks (branch emg/gitleaks; the candidate gate)

Reviewer: a fresh, read-only independent reviewer (session debdb3f7), 2026-11-02 evening. Not committed (the
reviewer's record place).

## What was reviewed
- Branch `emg/gitleaks` in `/home/usain/gov-os-worktrees/EMG-gitleaks`, `git diff w2/integrate...emg/gitleaks`:
  `c1257869b963` (`gov.secrets._workers`; both pools; `tests/unit/secrets_check/test_w2_20_pool.py`,
  `test_scan_scale.py`) and `b7428f793836` (`nightly.sh` through `heavy_slot.sh --held`; `test_nightly.sh` N18-N19).
- `tools/heavy_slot.candidate.sh` against the live `tools/heavy_slot.sh` (diffed), and `tools/test_heavy_slot.sh`
  H13-H19 (diffed against `test_heavy_slot.sh.pre-emg-gitleaks`).
- The CTO's design (P-EMG-GITLEAKS-1 (a): contiguous shares 0-5, 6-12, 13-19; the time bound in CPU-seconds) was not
  re-judged.

## Tests run
- `HEAVY_SLOT_UNDER_TEST=<candidate> bash tools/test_heavy_slot.sh`: `PASS: heavy_slot.sh H1-H19`, exit 0.
- `tests/unit/secrets_check` with this tree's `src`, through the live gate, `-p no:cacheprovider`: 79 passed in 130 s.
- Not run (outside what the brief allowed): `test_nightly.sh`; the engineer's measurement.

## The answers to the questions
- **Lose a run's work, hang, deadlock, leak a lock (gate):** no. The lock is the same file, the same
  `flock -n -o -E 213` call; the only change is `taskset -c <share>` placed between `flock` and the command, and
  taskset execs the command (no extra process stays, the lock fd is still closed before the run, `-o`). The priority
  path's `bash -c 'rm -f "$0"; exec "$@"'` now execs taskset, then the command: the same. The added work before each
  try (`share`, `budget`) opens no fd and cannot block. Lock names unchanged, so the old and the new gate share the
  slots while the switch-on is in progress. The command's exit code goes through (taskset execs it); the one changed
  code is a command that cannot be started (F3).
- **`--held`:** takes no lock and checks nothing about who holds the named slots, so a caller can use it to run past
  the slot limit (F1). Only the nightly calls it; no brief or tool tells an agent to use it.
- **Fail open (a run outside any slot, or an unconfined run that is not said):** none found. Every ordinary run still
  starts under a slot's lock. Every case that runs unconfined says so on standard error: no taskset (H19); taskset
  refusing the whole CPU set; `--held ""` (H17); an `EXCLUDE_CPUS` that leaves none. A share taskset refuses at run
  time (not reachable in practice: shares are subsets of the set already checked) ends red (taskset exit 1). It never
  runs the command unconfined.
- **Secrets change:** findings and their order are unchanged. `indexable` keeps `pool.map` order over
  `dict.fromkeys(paths)`; `stores_with_secrets` builds its result from the sorted `files`, and `reused` is printed
  sorted. The `large` semaphore (2) and the per-gitleaks timeout do not depend on the width. A timeout or a gitleaks
  error still raises, and `_workers()` is at least 1. With width 1 nothing is skipped, and nothing submits nested work
  to the same pool, so width 1 cannot deadlock. A budget that is not digits is ignored (tested), so it cannot widen
  past the CPU set. No fail-open path. The test for "the result does not depend on the width" (widths 1 and 3, planted
  secrets in both pools) passes.
- **nightly.sh:** both suites still run (`( noslot env` twice, each now `"${HEAVY_RUN[@]}" $WITH_LOCK python3 -m
  pytest`). The three slot locks are taken by the same unchanged loop and closed in the children by `noslot`; the held
  list is only recorded. With the old gate (no `# heavy-slot: --held` line, as the live `heavy_slot.sh` today) or no
  file: `HEAVY_RUN=()`, the suites run exactly as before, and run.txt says so. The gate's one stderr line comes before
  pytest's output, so `tail -1` of parallel.txt/serial.txt (run.txt's summary) still reads pytest's last line. Exit
  codes `p_exit`/`s_exit` come through `exec`. Held 0 slots: 6 workers, unconfined, said (safer than the old `-n auto`).

## Findings

### F1: `--held` takes no lock and does not check that the named slots are held
`heavy_slot.candidate.sh` lines 118-137: `bash heavy_slot.sh --held 1,2,3 <cmd>` runs at once, with 18 xdist workers
and every CPU, whatever holds the slots. A run started this way while leads hold slots doubles the load in those
shares and bypasses the slot limit (DEC-979 D1).
Ordinary work: no, because only the nightly calls the form, and the briefs (EMG-common, every lead's) name
`heavy_slot.sh <command>` only. Using `--held` while waiting would be a deliberate choice of a form the header reserves
for "a caller that holds slots itself", not an honest slip.
Consequence: fails open (the slot limit; the CPU set still holds the run to the named shares).
Recommendation (Wave 3 row, or a cheap ride-along at the switch-on): in `--held`, for each named slot, a
`flock -n -E 0 "$DIR/gov-os-heavy-slot-$i.lock" true` that succeeds means no process holds it: drop that slot, with a
stderr line (the nightly's `NIGHTLY_SLOT_DIR` and the gate's `GOV_HEAVY_DIR` both default to `/tmp`; a test would set
both).

### F2: codeintel's secret-check pool is still sized to the machine
`src/gov/codeintel/__init__.py:189` `ThreadPoolExecutor()`: on Python 3.12.3 that is `min(32, os.cpu_count() + 4)` =
24 wide, each `path_holds_secret` a gitleaks. W2-20's KPI line 45 says "the product's own parallel work sizes its pools
to the CPUs the process may use … the secret scan's pool (`gov.secrets`) included". The brief's part 1 named only
`gov.secrets`, which is now met.
Ordinary work: yes, because every code-index rebuild runs it.
Consequence: other (load only; inside a slot the CPU set holds it to the share; the findings are unchanged).
Recommendation: `max_workers=secrets._workers()` there when W2-20 resumes (DEC-802), or as a W2-20 row.

### F3: a command that cannot be started now exits 127, not 69
`flock … cmd` exits 69 when it cannot execute `cmd`; `flock … taskset -c … cmd` exits 127 (checked by hand). Both are
non-zero, and no caller found keys on 69.
Ordinary work: yes, because a mistyped command reaches it.
Consequence: other (still red; only the code changes).

### F4: the shares come from each caller's own CPU set
The candidate divides the gate process's own affinity (H15). Two callers with different CPU sets would get overlapping
slot shares; a nested call (a gate inside a slot's run) gets a subset of the outer share, which is safe.
Ordinary work: no, because every session and tool on this machine runs with the full CPU set today (the embedders,
the only pinned processes, never call the gate).
Consequence: other (the shares overlap; the locks still bound the slot count).

### F5: KPI line 44's "outside any CPU set the configuration gives the embedding servers"
The candidate does not exclude the embedders by default (`EXCLUDE_CPUS` empty, as the CTO decided, (a)). The header
gives the reason and the measurement, as the brief asked. Read with "the configuration" as `heavy_slots.conf`, which
gives the embedders no set today, the line is met; read literally against the owner ACTs' sets (12-19, 8-11), it is
not.
Ordinary work: yes, because the close reads the KPI line as written.
Consequence: other (wording; no run is affected).
Recommendation: the close's evidence names the reading, and P-EMG-GITLEAKS-1 (a) as its source, so the line is not
counted as a miss.

## Risks noted (not findings)
- The brief's two measured numbers are not met (the engineer's Fix entry: a third of the CPUs, CPU-bound; and
  `w2_69_support.base_environment` drops the budget, so each child's pool is the share wide: about 4 runnable per
  CPU, still inside the share). Under the CTO's (a) the time bound is in CPU-seconds; the CPU confinement holds.
- The nightly's serial phase gets the whole held set as its budget (GOMAXPROCS = 20, scan pool 20), as before the
  change, and by design (one process).

```verdict
{"kpis": [{"kpi": "W2-20 pool-sizing line (KPI line 45; brief part 1, gov.secrets)", "verdict": "pass", "findings": [{"id": "F2", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "W2-20 CPU-set line (KPI line 44; brief part 2, heavy_slot.candidate.sh)", "verdict": "pass", "findings": [{"id": "F1", "scope": "in", "ordinary_work": "no", "consequence": "fails open"}, {"id": "F3", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F4", "scope": "in", "ordinary_work": "no", "consequence": "other"}, {"id": "F5", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "W2-20 thread-budget line (KPI line 42; brief part 3, nightly.sh --held)", "verdict": "pass", "findings": []}]}
```
