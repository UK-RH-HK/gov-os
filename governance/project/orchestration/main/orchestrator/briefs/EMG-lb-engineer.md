# Emergency task: the Gov Load Balancer in the dispatcher, with the machine-derived limits and the standing targets (engineer)

Read `briefs/EMG-common.md` beside this file first; its rules hold.

**Role:** engineer. **Worktree:** `/home/usain/gov-os-worktrees/EMG-lb`, branch `emg/lb` (from `w2/integrate`
`3630679c`). The dispatcher that cron runs every minute is the main tree's
`governance/project/orchestration/tools/dispatch/` (`run_tick.sh`); you build in your worktree's copy of that folder,
and it goes live only when the CTO merges your branch after the review. `Task: DAEO-sdxk` (W2-00, the CTO's tools
lane, DEC-979 item 2), `Implements: DEC-1039,DEC-1038,DEC-1037`. TMPDIR `/tmp/gov-os-emg-lb`.

## Why
The owner (DEC-1039 (1b), 2026-11-02 ~18:40): "the Gov Load Balancer: plan leads, closes, landings and rebuilds
together by their phases and each phase's measured peak on every resource (CPU, RAM, the GPU and its memory); pair
GPU-heavy work (leads searching, rebuilds embedding) with CPU-heavy work (test runs) so neither peaks twice at once;
keep the embedders and rerankers on the GPU within its budget, even if that limits leads to two or three. Document
the rule: the GPU's dedicated memory never spills into shared memory, and never runs out into a CUDA crash; test the
load balancer and the dispatcher on it and on the phase balancing." Last night the GPU ran out (8 to 11 rerankers),
CUDA crashed three times and the shared embedder fell to the CPU for seven hours (DEC-1029). And DEC-1037 (4): no
number fixed for this machine.

## Read first
`governance/project/orchestration/tools/dispatch/` (the dispatcher, its README and tests), the CTO's brief
`.gov-runtime/scratch/orchestrator/drafts/BRIEF-MACHINE-TARGETS.md` (parts 1 and 3 are yours; part 2's `taskset`
in `heavy_slot.sh` belongs to another engineer working now: never edit `heavy_slot.sh`), the plan
`governance/project/orchestration/packages/P1-LOAD-BALANCE-1.md` (or `drafts/` if not there) and its GPU section
`drafts/LB-PLAN-gpu.md`, and today's samples: `log/capacity/kinds.jsonl`, `log/lead-mem.jsonl`, the dispatcher's
`status.txt`. What exists: admission on CPU, RAM and GPU memory, the lead cap from memory, slots by device,
`gpu_headroom_mib`, the rerankers' GPU slots, samples by kind.

## What is missing, and is your work
1. **Phases and their measured peaks:** name the phases of each kind of work (a lead: start and retrieval, building,
   its test run, its review; a rebuild: lexical, embedding; a landing or close: rebuild, test run; the nightly) and
   derive each phase's peak per resource (CPU cores busy, RAM, GPU memory, GPU use) from the samples, kept current
   from new samples (a p95 over a rolling window, with a floor from today's figures when samples are few). Detect
   a running job's phase from what it runs (its processes, its slot, its rebuild lock), stated in the README.
2. **A forecast before admission:** admit a start (a lead, a slot grant, a rebuild) only if, for every resource, the
   running jobs' current-phase peaks plus the newcomer's worst-phase peak stay within capacity: CPU within the band,
   RAM above the floor, GPU memory at most total minus headroom. Name the binding resource in the status line.
3. **Pairing:** when several starts are possible, prefer the one whose heavy resource is the idle one (a GPU-heavy
   start while test runs fill the CPU; a CPU-heavy one while the GPU is busy embedding), so neither peaks twice.
4. **The GPU rule, documented and checked each pass:** dedicated memory used (nvidia-smi, `/usr/lib/wsl/lib/nvidia-smi`)
   plus the forecast never above total minus headroom; and no spill into shared memory: find a read-only way to read
   WSL's shared GPU memory use (for example the Windows counter `\GPU Adapter Memory(*)\Shared Usage` through
   `powershell.exe -NoProfile Get-Counter`, if it answers within a few seconds; or what nvidia-smi reports); a
   reading above a small floor is a `gpu-alert` inbox item at once (the quiet waiter wakes on those). If no reading
   is possible without a machine change, say so and write the owner's ACT.
5. **Machine-derived limits (BRIEF part 1):** every limit derived from the detected machine by ratios that reproduce
   today's numbers on this machine exactly (20 CPUs, 24 GB, the RTX 5070 Ti's 16 GB); an explicit number in
   `config.json` still wins and the status says so; a machine change is an inbox item. The number of reranker GPU
   slots derived too (the installed `gov_reranker_gpu_slot.py`'s lock count is the owner's ACT: write it, never apply it).
6. **The standing targets and incidents (BRIEF part 3):** `log/capacity/balance.jsonl`, T1 to T5, the 15-minute
   breach rule, one incident per breach, `tools/targets_report.py` (in `.gov-runtime/scratch/orchestrator/tools/`,
   the one file outside your worktree you may write, with its own unit tests beside it), and the "heavy steps
   outside a slot" finding becoming an incident after 15 minutes.

## Tests (unit, yours) and the live check
The BRIEF's list, plus: the forecast refusing a start that would put GPU memory over its budget (planted samples:
the embedders at 5.6 GB, a reranker service at 3.5 GB, a newcomer whose retrieval phase takes 3.5 GB on 16 GB with
2 GB headroom: refused, GPU named); pairing choosing a GPU-heavy start beside two running test slots; a phase
detected from planted processes; today's numbers unchanged on this machine's figures; the spill check raising one
item. Then one live dry pass on the real machine with your copy writing only to your TMPDIR (a status written there,
no start, no inbox item in the live inbox), and show its status line.

Return DONE with the branch head, the README section that states the rule, the tests' results and the dry pass's
status line. One independent review follows (the CTO starts it), then the CTO merges (live) and writes the DEC-1003
proposal for the product. Estimate: 3 to 4 hours.
