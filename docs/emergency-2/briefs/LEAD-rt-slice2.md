# Lead brief: the run-time tool, slice 2: the machine-aware dispatcher and load balancer (W2-199, a new feature)

Read `/home/usain/Dynamic-Agentic-Engineering-OS/docs/emergency-2/briefs/NIGHT-COMMON.md` first and follow it.
Branch `e2/rt-slice2` from `w2/integrate`, worktree `/home/usain/gov-os-worktrees/E2-rt-slice2`. C2 (run-time tool
code): Sonnet helpers. `Task: DAEO-<your new ticket id>`, `Class: F`.

**Why (the owner's first priority tonight):** protect the machine and cut usage. Last night the load reached 194 on 20
CPUs (leads' pytest runs outside the slot); the CTO's full suites reached 54 today. Today the only thing holding runs
inside the resource gate is a scratch shell script, `.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh` (its
`admit` waits for a 1-minute load under 12, then takes one of `heavy_slots.conf`'s SLOTS=2 x WORKERS=4 slots, confined
with taskset), outside the product, with machine-specific constants.

**Read:** EMERGENCY-2 §6.3 (the decided scope and RT-1 to RT-8); audit 3 `docs/emergency-2/audits/03-run-time-tool.md`
(today's parts and the design); slice 1's ticket `.tickets/DAEO-5rgj.md` (W2-121c: gov msg, the watch pass, slots from
the machine detected at start) and its code `src/gov/dispatch/` (runtime.py, limits.py, heavy.py, procs.py, state.py),
`gov resources` (`src/gov/resources/`, the gate: load limit = nproc, cpu, memory, GPU); the scratch slot script above.

**Your feature (write it as a ticket first: `.tickets/` in the form of DAEO-5rgj, wbs_id W2-199, status in_progress, KPI
lines each observable with its verify):**
1. **The load admission in the product:** every heavy job the dispatcher or `gov resources --slot` starts (a test run, a
   rebuild, a measure) is admitted only while the machine has room: under a start threshold derived from the detected
   machine (default 60 % of nproc), slots and workers per slot derived from detected CPU, RAM and GPU (RT-3, no machine
   constant), and a running job never pushes the 1-minute load over the gate's limit by more than a measured margin
   (find how: fewer workers, taskset, or holding the next start). A nested run (a test that itself starts a slot run)
   is never held, so nothing deadlocks.
2. **One state file and one wake rule** for the dispatcher's watching (RT-7): what today is spread over the tick, the
   watchers and the inbox notices; the CTO's stall check stays in the tick (DEC-1214 T1).
3. **RT-1:** no ready job waits more than 10 minutes while the machine has room (from the state file's log).
4. **RT-4:** zero GPU spill: embedder and reranker jobs admitted only with their GPU memory free; never CPU (T3).
5. **A drop-in for the scratch script:** `heavy_slot.sh`'s callers (leads, the CTO, tests) can call the product's slot
   (`gov resources --slot test -- <command>` or the form that exists) with the same exit codes; keep the script working
   as a thin wrapper over the product until the CTO switches (do not edit the live scratch script in the main tree;
   put the wrapper's new text in your branch under `governance/project/orchestration/tools/` and say so).

**Flow:** test designer (Sonnet) writes the acceptance tests under `tests/acceptance/W2-199/` from your KPI lines, red
on the base; engineer (Sonnet) builds until `gov accept W2-199` is green; then the folders you touched and
`tests/unit/dispatch`, `tests/unit/resources`. Never switch the live dispatcher (the cron `run_tick.sh` runs every
minute from the main tree): the CTO switches after landing. Then, if time remains, write slice 3's ticket (RT-2, RT-5,
RT-6 across sessions) and stop.
