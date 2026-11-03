# Brief: the machine's limits from the machine, its standing targets, their incidents, and a gate that holds (DEC-1037 (4), DEC-1038 (4))

For one engineer (the CTO's tooling, not the product: `governance/project/orchestration/tools/dispatch/`,
`.gov-runtime/scratch/orchestrator/tools/`), then one independent review (DEC-1033's rule; two rounds at most,
DEC-1010). Every test run of yours goes through the gate (`bash .gov-runtime/scratch/orchestrator/tools/heavy_slot.sh
python3 -m pytest ...`, DEC-1038 (4)); keep changes out of the live path until the review passes (the dispatcher runs
from its file every minute: build in a copy, install on the CTO's word). Written 2026-11-02 16:25 by the CTO.

## Why
The owner (DEC-1038 (4)): "The overload must end, not just improve." On 2026-11-02 at 16:20 the load was 76 on 20
CPUs during one landing: the gate admitted the run's 6 pytest workers, but W2-69's secret-scan tests each started
gitleaks, which uses every CPU (31-49 gitleaks at once, about 10 cores). And the limits are numbers fixed for this
machine (DEC-1037 (4)): a bigger machine or more RAM must be used at once.

## 1. Limits derived from the machine (DEC-1037 (4))
- At the dispatcher's start and on each pass, detect: logical CPUs (`os.sched_getaffinity` / `/proc/cpuinfo`),
  physical cores, RAM (`/proc/meminfo` MemTotal), the GPU's model and memory (nvidia-smi, already read). Record them in
  `status.json` ("machine") and write an inbox item when they change.
- Derive every limit from them, with the ratios as the only settings (documented, each from today's value on 20 CPUs,
  24 GB, 16.3 GB GPU, so today's behaviour is unchanged): `cpu_band` (14-18 of 20 → 0.70-0.90 of CPUs), the heavy
  slots and workers (`heavy_slots.conf` 3 x 6 → from CPUs), `slots_gpu` / `slots_cpu`, `rerank_gpu_slots` (from the GPU's
  memory minus the embedders' measured share and the headroom, divided by one reranker's measured peak),
  `gpu_headroom_mib` (a fraction of the GPU's memory), the lead cap (already from memory). `gov_reranker_gpu_slot.py`'s
  number of lock files from the same figure (it reads it from the dispatcher's state, falling back to 2).
- An explicit number in `config.json` still wins (an owner's override), and the status line says when one does.
- The servers' CPU sets (12-19, 8-11) are owner ACTs; the derivation proposes them in the status line only.

## 2. The gate holds: a run's children stay inside its share
- `heavy_slot.sh`: each slot's run gets its own CPU set (`taskset -c`, the slot's share of the CPUs outside the
  embedders' sets) and a thread budget exported to everything it starts: `GOMAXPROCS`, `OMP_NUM_THREADS`,
  `MKL_NUM_THREADS`, `OPENBLAS_NUM_THREADS`, `RAYON_NUM_THREADS`, `NUMEXPR_NUM_THREADS` (the slot's CPUs / workers,
  at least 1). Measured: the W2-69 tests' time before and after (they must not slow by more than 20 %).
- The dispatcher's "heavy steps outside a slot" FINDING becomes an incident item when it lasts more than 15 minutes
  (part 3), naming the process, its tree and its session.
- The CTO's agents (engineers, reviewers, research, measurements) and the CTO's own runs: the briefs say "through the
  gate"; the dispatcher's finding catches the rest.

## 3. The standing targets, their history and their incidents (DEC-1038 (4))
- Each pass appends the balance record it already computes (`balance()`: busy cores and band, memory available and
  floor, the GPU used/total/headroom, the embedders' states) to `log/capacity/balance.jsonl` (one line a minute;
  rotated by `nightly/rotate.sh`'s rule).
- Targets, each judged per pass: (T1) busy cores within the band; (T2) memory available above the floor; (T3) GPU used
  at most total minus headroom; (T4) no timed-out embedding (a `[GIN]` line with a status of 499 or 5xx, or a time at or
  over the client's timeout, in either server's log since the last pass; and W2-123's retry log's give-ups); (T5) no
  cold rebuild (`tools/rebuild_counts.py`'s rule, from its log).
- A breach (T1-T3 continuously, T4-T5 each event) lasting more than 15 minutes, or any T4/T5 event, opens an incident:
  one inbox item `incident-<target>-<time>` and a record `log/incidents/<date>-<time>-<target>.md` with the readings,
  the top processes by CPU and memory grouped by tree and session (as the 16:20 trace did), and empty "Cause" and "Fix"
  fields the CTO fills, like a red. One incident per breach (no repeat while it lasts); it closes when the target holds
  again for 15 minutes, and the record says when.
- `tools/targets_report.py [--since] [--hours 07:30-02:00]`: for the morning package, per target the share of working
  hours met (T1 at least 80 %; T2, T3 100 %; T4, T5 zero events), the incidents with their causes, and the worst hour.

## Tests (unit, yours; MR-3 does not apply)
The derivation on three machines (today's; 32 CPUs, 64 GB, 24 GB GPU; 8 CPUs, 16 GB, no GPU); an override in
`config.json` winning; a machine change raising an item; the thread budget reaching a child (a test program printing
its environment and its CPU set) inside a slot; the breach timer (14 minutes: nothing; 16: one incident; still
breached: no second; recovered for 15: closed); T4 from planted log lines; the report's shares over a planted day.

## Acceptance (for the review)
Today's numbers unchanged on this machine; a run's children cannot exceed its slot's CPUs; the 16:20 situation
re-played (W2-69's tests in a slot) stays within the band; each target reported; a 16-minute breach gives one incident.
