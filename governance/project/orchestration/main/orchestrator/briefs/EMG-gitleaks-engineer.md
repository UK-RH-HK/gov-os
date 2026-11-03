# Emergency task: the real gitleaks fix: each slot confined to its CPU share; the scan's pool sized by affinity; the nightly inside the budget (engineer)

Read `briefs/EMG-common.md` beside this file first; its rules hold.

**Role:** engineer. **Worktree:** `/home/usain/gov-os-worktrees/EMG-gitleaks`, branch `emg/gitleaks` (from
`w2/integrate` `3630679c`). **Tickets:** product code `Task: DAEO-r30l` (W2-20, which carries the thread-budget,
CPU-set and pool-sizing KPI lines, P-W2-20-THREAD-BUDGET (a)); the nightly's folder `Task: DAEO-sdxk` (W2-00).
`Implements: DEC-1039,DEC-1038`. TMPDIR `/tmp/gov-os-emg-gitleaks`.

## Why
Incident `.gov-runtime/scratch/orchestrator/log/incidents/2026-11-02-1620-T1-cpu.md` (read it first): load 76 on 20
CPUs during one landing. The gate admitted the run's 6 pytest workers, but the secret-scan tests each started gitleaks,
and the scan's pool is `os.cpu_count()` wide (`src/gov/secrets/__init__.py`, about line 599), each gitleaks itself on
every CPU. The thread budget now live in `tools/heavy_slot.sh` (DEC-1038) did not bound it: measured on W2-69's 352
tests, 968 s against 1,069 s, but peak runnable 179 against 165. The owner (DEC-1038 (4)): "The overload must end, not
just improve."

## The three parts
1. **Product (`src/gov/secrets/__init__.py`, its unit tests under `tests/unit/secrets/`):** the scan's pool sized by
   the CPUs the process may use (`len(os.sched_getaffinity(0))`, falling back to `os.cpu_count()`), and no wider
   than the thread budget when one is exported (`GOV_HEAVY_THREADS` or the variables `heavy_slot.sh` exports; read
   the script for which). Read W2-20's KPI lines in `.tickets/DAEO-r30l.md` and meet the pool-sizing line exactly.
   Results unchanged (same findings, same order). Unit tests for: an affinity of 4 gives at most 4; a budget of 2
   gives 2; no affinity call available falls back.
2. **The gate (CTO tooling, in scratch, NOT in your worktree):** build
   `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.candidate.sh` from
   the live `heavy_slot.sh` (never edit the live file: the CTO switches it on after the review): each slot's run
   confined with `taskset -c` to its own share of the CPUs (the logical CPUs from the process's affinity, divided
   evenly among the slots of `heavy_slots.conf`; slot i takes its own contiguous range), everything the run starts
   inheriting it; the thread budget then follows from the share. State in the script's header why the embedders'
   CPU sets (12-19 shared, 8-11 query, owner ACTs) are or are not excluded, with the measurement below as the
   reason. Tests: extend `tools/test_heavy_slot.sh` (H13 on; run with `HEAVY_SLOT_UNDER_TEST=<candidate path>`): a
   child program printing its CPU set and environment shows the slot's share; two slots get disjoint sets; a run
   with no `taskset` on the machine still runs (named). Backups before you write: `heavy_slot.sh.pre-emg-gitleaks`
   and `test_heavy_slot.sh.pre-emg-gitleaks`.
3. **The nightly (`governance/project/orchestration/nightly/nightly.sh`, in your worktree):** it takes the slot locks
   itself (DEC-984), so today it gets neither the worker cap nor the thread budget (the gate review's F2: 20 workers,
   each gitleaks on 20 CPUs). Give its runs the same budget and CPU confinement as one slot per lock it holds (it
   holds all three: so all the CPUs, at most the conf's total workers, the budget exported), by calling the same
   logic, not a copy. Its own tests (`test_nightly.sh` in that folder) must pass; add one for the budget.

## The measurement (the acceptance for the review)
Re-play the 16:20 situation: W2-69's tests (find them as the incident record's measurement did) through the candidate
gate, with this worktree's `src`, sampling the load and the runnable count each second: time no more than 20 % slower
than 968 s, and peak runnable within the slot's share (about 7, not 179). One run at a time, only through the gate.
Results in your return and in the incident record's "Fix" field (append; never rewrite what is there).

Return DONE with the branch head, the candidate's path, the tests' results and the measurement. Then one independent
review (the CTO starts it), then the CTO merges, switches the gate on and re-pins. Estimate: 2 hours.
