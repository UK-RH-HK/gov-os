# SIZING-1: a bigger machine, sized on the figures after W2-107 (DEC-1011 item 2)

Draft for the owner. Prepared 2026-11-01 about 20:50. Read-only: nothing on the machine was changed. Figures are
marked **(M)** for measured or **(E)** for estimated or modelled. The scripts are in the CTO helper's scratchpad
(`sizing/measure.py`, `waits.py`, `cpu_split.py`, `idle_while_waiting.py`, `size.py`). Window: **2026-10-31 18:47
(W2-107 merged) to 2026-11-01 20:50**, about 26 hours: 1,462 one-minute samples, 49 bench runs and 18 leads.

## Answer first

- **This PC cannot run 10 leads.** The processor is the limit. All 20 of its threads are already given to WSL, and at
  6 leads 18.8 of 20 are busy (p50). Ten leads need about **50 threads (63 with margin) and about 42 GiB (48 with
  margin)**. Twelve need about **51 threads (64 with margin) and 46 GiB (53 with margin)**.
- **Memory is not what binds today. The admission rule binds.** The rule adds every p95 as if all peaks came at
  once, so it allows about 4 leads in 24 GB. In fact 8 leads ran at once, and the most memory ever in use was
  **18.3 GiB of 23.5** (M). The rule is safe, but it is about 5 GiB more cautious than anything measured.
- **Most of today's slot waiting is not about processors.** Since 16:00 (when rebuilds started taking slots,
  DEC-1001), a lead's heavy step has waited **at least 23 minutes on average** (M, 28 steps; 4 were still waiting at
  20:50). In about half of the minutes when something was waiting, 6 or more cores were idle. The cause is cold
  rebuilds in new worktrees. Each one holds a slot for **50 to 62 minutes** while the shared embedding server, which
  answers one request at a time (`-np 1`), embeds its whole corpus. On its own, that stage takes 12 to 25 minutes.
  Before 16:00 the same day, 13 heavy steps waited **0** minutes.
- **The recommendation, in order:** (1) without spending anything, take the cold rebuilds' embedding out of the
  slots, and possibly give the embedder parallel requests (two P1 ticket proposals). (2) Optional: give WSL 28 GB
  instead of 24 GB. That is a `.wslconfig` change, an owner act, worth about +1 lead under the rule. (3) For 10 to 12
  leads, Wave 3's question: a machine with **at least 64 threads and 96 to 128 GB**, with a GPU or 8 more cores for
  the embedder. Under CAPACITY-1 §6, Wave 2 gains about a day from a bigger machine, against 1 to 2 days of setup.

## 1. Context

The owner's aim is 10 leads at once (DEC-999 to DEC-1004). The dispatcher admits a lead only when memory covers
everything at its peak (DEC-1008 item 5, the "slots" rule):
floor 3,072 MB + N leads × their p95 outside test runs + 3 slots × a slot run's rise + the shared services' p95 +
the base. CAPACITY-1 (2026-10-31) found the machine bound by its processor, with a heavy-job limit as the remedy. That
limit is now in force: 3 slots of 6 workers (`tools/heavy_slots.conf`, provisional from 2026-10-31 23:47), and the
merge queue and closes go first (DEC-1011 item 3). CAPACITY-1 also sized a bigger machine on figures from before
W2-107, and DEC-975 and DEC-1011 asked for that sizing again on figures from after W2-107. This is that sizing.

**The machine (M, read 2026-11-01):**

| | Value |
|---|---|
| Windows host | Intel i7-12700F, 12 cores (8 performance and 4 efficient), **20 threads**. 31.8 GiB visible (2 × 16 GB DDR4 at 2,133 MT/s, **2 of 4 DIMM slots used, board maximum 128 GB**). RTX 5070 Ti 16 GB (2.6 GB in use, 28 %). |
| `.wslconfig` (`C:\Users\usain`) | `memory=24GB`, `swap=8GB`, `autoMemoryReclaim=gradual`. The processor count is not set, so WSL sees all 20 threads. |
| WSL | `nproc` 20. MemTotal 24,607,384 kB (23.47 GiB). Swap 8 GB, 2.3 GB of it in use. Windows had 4.0 GiB free at the reading. |
| Slots | `SLOTS=3`, `WORKERS=6`. Cold and warm rebuilds share the slots (since 2026-11-01 15:56). |
| Embedder | one `llama-server` (ollama) with `-np 1`: **one request at a time**, about 4.4 cores busy at the reading. |

## 2. What was measured (all after 2026-10-31 18:47)

### 2.1 Memory, GiB (M; `kinds.jsonl` and `lead-mem.jsonl` joined by minute)

| Item | p50 | p95 | max | Note |
|---|---|---|---|---|
| A lead, outside test runs | 0.39 | **2.39** | 5.46 | 1,258 lead-minutes with no test run on the machine. The dispatcher's 7-day `peaks.json` gives 2.40, so W2-107 changed nothing here. |
| A lead, while test runs ran | 0.58 | 3.81 | 7.49 | 3,409 lead-minutes. "Inside" means any run on the machine, not necessarily the lead's own. |
| A lead's own maximum (18 leads) | 5.01 | 7.20 | 7.49 | |
| A slot run's rise (lead p95 inside minus outside) | | **1.43** | | Same as `peaks.json` (1,468 MB). A run's own share, counted as test-run processes divided by 7, is p95 0.70 and max 1.22. |
| Embedding server | 1.38 | **3.05** | 5.26 | |
| Code graph | 0.03 | 0.21 | 0.81 | |
| Rerankers (mostly inside leads' trees) | 2.16 | 6.23 | 9.76 | Covered by the leads' figures, so not added again |
| Base (in use − leads − services) | **2.78** | 7.11 | 10.15 | The CTO, closes, the queue, the nightly, helpers |
| **All memory in use** | 8.18 | 15.13 | **18.56** | Of 23.47. No OOM trip since the watch started on 10-29. |

**Memory in use by number of leads (M):** 4 leads: p95 15.8, max 17.6. 6 leads: p95 16.0, max 17.3. 7 leads: p95
16.4, max 18.3. 8 leads (93 minutes): p95 13.5, max 14.9. For 6 leads the rule asks **27.7 GiB**. The most ever
seen with 6 to 8 leads is 18.3.

### 2.2 Processor, cores (M)

| Item | Figure |
|---|---|
| Machine busy (`/proc/stat`) | p50 13.0, p95 19.3 of 20. **At 6 leads: p50 18.8.** At 5: 18.2. At 8: 17.5 (runs were waiting). |
| Load (1 min) | p50 18.7, p95 80.9, max 116, even with the slots, because of the embedder, the leads' subprocesses and the nightly |
| Embedding server | p50 3.9, p95 **8.4**, max 16.2. With leads running, p50 about 5. While a rebuild runs, p50 5.0, p95 11.6. |
| All test runs together | p50 9.3, p95 **17.5**, max 55 (minutes with a run active) |
| A slot run | design 6 (`WORKERS`). Measured as test-run processes ÷ 7: p50 1.6, p95 4.7 (rough). |
| A lead outside slots (busy − runs − rebuilds − services, ÷ leads) | p50 **0.20**, p75 0.50, p95 1.48. A lead mostly waits on the model. |
| Rebuild stages | cold, alone: the semantic stage takes **708 to 1,513 s** (W2-81, W2-92, W2-13, W2-55, W2-11). **Cold, three at once (16:00 to 18:51): 3,008 to 3,751 s** (W2-91, W2-105, W2-90b, W2-61h). Warm: 29 to 288 s in total. |

### 2.3 Contention: the bench (M; the fixed `tests/unit` run, 2,976 tests, every 30 minutes, 49 runs)

**wall = 36.9 s + 3.58 s × load (R² 0.84).**

| Load at start | Runs | Wall p50 (min to max) | × the quiet time |
|---|---|---|---|
| 0 to 10 | 18 | 56 s (51 to 81) | 1.0 |
| 10 to 20 | 7 | 74 s (60 to 115) | 1.3 |
| 20 to 30 | 7 | 106 s (97 to 144) | 1.9 |
| 30 to 50 | 11 | 179 s (89 to 236) | 3.2 |
| above 50 | 6 | 368 s (177 to 415) | 6.6 |

Up to a load of about 20 (one per thread), a run costs about 1.3 times its quiet time. Past that, the cost rises
steeply.

### 2.4 Slot waits (M; the leads' logs: the `heavy_slot: … waiting (time)` line, the run's own duration and the exit file's time)

| Period (11-01) | Heavy steps | Waited | Mean wait | Max |
|---|---|---|---|---|
| 00:00 to 16:00: test runs only in slots, rebuilds under their own lock | 13 | 0 | **0 min** | 0 |
| 16:00 to 20:50: rebuilds in slots too | 28 (plus 1 queue run) | 18 | **at least 23 min** (4 still waiting: 65, 35, 17 and 12 min) | about 110 min (W2-91's head rebuild) |

- **While a step waited** (227 minutes, 530 step-minutes of waiting): busy p50 14.2 and p10 7.7 of 20. **In 109 of
  the 227 minutes, 6 or more cores were idle.** The embedder used 5.6 cores on average.
- **At 20:51** (dispatcher `status.json`): all 3 slots were held by rebuilds, the load was 6.7, busy was about 8 of
  20, and 4 heavy steps were waiting. This is the "8.5 busy cores at load 7" in the brief.
- Durations of the steps that held slots: a test run took a mean of 31 minutes (n 12). A rebuild took a mean of 20
  minutes (n 20), split between 1 to 5 minutes for a warm rebuild and 12 to 62 minutes for a cold one. On 11-01, 9
  rebuilds ended with exit 143 (stopped). Two of them logged nothing after their wait line.
- **The slot model checks against what was measured.** Section 4's model, as measured (scenario A), predicts a mean
  wait of 25 minutes for 6 leads on 3 slots. The measured figure was at least 23 minutes, with about 6.7 leads.

## 3. Why it matters

- **The 10-lead aim cannot be met on this PC by memory alone.** At 6 leads the processor is already full (busy p50
  18.8 of 20). Past a load of about 20, every run stretches (×1.9 to ×6.6, section 2.3), and the stretch brings false
  reds, runs that hit the two-hour limit, and longer waits (CAPACITY-1 §2).
- **Buying hardware would not cure today's waits.** Cold rebuilds queue on an embedder that answers one request at a
  time. A machine with more threads but the same embedder would hold its slots just as long.
- **On Wave 2, more leads gain little.** CAPACITY-1 §6's model found about 20 ready tickets at most, and one chain
  (W2-108 → W2-13 → W2-15a → W2-32 → ACT 2 → the layers → W2-27 …) that takes about 3 days on any machine. This new
  sizing does not change that. The 10-lead question belongs to Wave 3.

## 4. Sizing for 6, 8, 10 and 12 leads (E, from the figures in section 2)

**Method.**

- **Slots.** Each slot is a server, and the slots are modelled as one queue (M/M/c, Erlang C).
  - Arrivals: 0.9 heavy steps per lead-hour (M: 29 steps in 32.5 lead-hours, 16:00 to 20:50; 52 in 69.5
    lead-hours over the whole of 11-01 is 0.75), plus 0.23 Erlang of closes and queue runs (M: about 8 runs a day,
    about 36 minutes each).
  - Service time: **A**, 24 minutes, as measured, under load and with cold rebuilds in the slots. **B**, 16 minutes
    (E, two-thirds of A): runs that are not stretched, and cold rebuilds seeded or kept out of the slots.
  - The target is a mean wait of 10 minutes or less. The model treats closes' priority as an ordinary arrival, so
    leads' real waits run a little higher.
- **Threads:** 6 × slots + 0.5 × leads (p75) + 8.4 for the embedder (p95) + 1 for the base, then ÷ 0.8 so that the
  load stays below the thread count (section 2.3).
- **Memory, the owner's formula:** 3,072 MB + N × 2,447 MB + slots × 1,464 MB + 3,123 MB (embedding) + 215 MB (code
  graph) + 2,847 MB (base p50). Margin +15 %. The figure with the base at p95 is shown as well.

| Leads | Slots for ≤ 10 min (A / B) | Threads needed (A / B), with 25 % margin | WSL or VM memory (A), GiB: formula / base p95 / +15 % | Fits on |
|---|---|---|---|---|
| 4 (today's rule) | 3 / 3 | 29 / 29, **37** | 22.9 / 27.2 / 26.3 | today's 23.47 GiB fits the formula only. The threads are overcommitted (20). |
| **6** | 4 / 3 | 36 / 30, **38 to 46** | 29.1 / 33.4 / **33.5** | 32 to 48 threads, 48 to 64 GB |
| **8** | 5 / 3 | 43 / 31, **39 to 54** | 35.3 / 39.6 / **40.6** | 48 threads, 64 GB |
| **10** | 6 / 4 | 50 / 38, **48 to 63** | 41.5 / 45.8 / **47.7** | **64 threads, 64 to 96 GB** |
| **12** | 6 / 5 | 51 / 45, **57 to 64** | 46.3 / 50.6 / **53.2** | **64 threads, 96 to 128 GB** |

Waits on today's 3 slots (A / B): 6 leads 25 / 4 min; 8 leads unbounded / 10 min; 10 leads unbounded / 34 min. With
the rebuild fix (B), 3 slots serve up to about 8 leads, but only if the runs are not stretched. On 20 threads they
are stretched, because 3 slots × 6 workers + the embedder + the leads come to about 31 threads. Measured memory with 6
to 8 leads (max 18.3 GiB) runs 9 to 17 GiB under the formula. The formula's memory figures are the safe ceiling.

## 5. Options, with cost and risk

| Option | What it gives | Cost | Risk |
|---|---|---|---|
| **0. Take cold rebuilds' embedding out of the slots** (seed a new worktree's store from the main store and rebuild warm in 1 to 5 min; or rebuild cold outside a slot; and test the embedder with parallel requests, `OLLAMA_NUM_PARALLEL` / `-np`, and fuller GPU use) | slot waits back toward the morning's 0 (M: 0 of 13 before 16:00). Each lead's rebuild takes minutes, not an hour. | Two P1 ticket proposals (DEC-974). No hardware. | Seeding must keep the store's digest and the semantic index correct (DEC-719: never empty it). Parallel requests use more GPU and CPU memory and must stay deterministic (W2-15b's embedder KPI). |
| **1a. More of this PC for WSL**: `memory=28GB` in `.wslconfig` (owner act; `wsl --shutdown` to apply) | about 27.4 GiB in WSL. The rule allows **5 leads** (5 needs 25.3; 6 needs 27.7, so 6 does not fit). | Nothing. A WSL restart stops every lead and service. | Windows keeps about 4 GB (it had 4.0 GiB free at 24 GB). The processor is unchanged, so a 5th lead adds waiting. **No more threads are available: WSL already has all 20.** |
| **1b. Fill this PC's two free DIMM slots** (2 × 16 GB DDR4 → 64 GB; or 4 × 32 GB → 128 GB), then `memory=56GB` | Memory for 12 leads under the formula. **The processor still allows about 4 to 6** (A), or 6 to 8 with option 0 if runs stay unstretched (B, doubtful on 20 threads). | Price to be checked (DDR4, matched to 2,133 MT/s or better). About 1 hour of work. | Mixing kits can lower the memory speed. Brings little without more threads. |
| **1c. A faster processor in this PC** (the same socket; a 32-thread part) | 1.6 times the threads (32) → **about 6 to 8 leads** together with 1b and option 0 | Price to be checked. The board's BIOS, power and cooling to be checked. | Downtime. Still short of 10. |
| **2. A bigger machine** (workstation, dedicated server or cloud VM) | **10 leads: 64 threads, 64 to 96 GB. 12 leads: 64 threads, 96 to 128 GB.** A GPU for the embedder, or about 8 more threads for it. | Price to be checked. Setup 1 to 2 days (CAPACITY-1 §6: the repository, secrets, pinned gov, ollama and models, a remote runner). | Held-out material must not be copied (a filtered clone). Secrets stay on the PC. Cost runs on if the machine is left up. A second place where runs can fail. A cloud VM without a GPU runs the embedder on its processor (cold embedding is slower, unmeasured). |

**Cloud sizes, for comparison only (price to be checked):**

| Leads | Size |
|---|---|
| 6 | 32 vCPU / 64 GiB (AWS c7i.8xlarge class) |
| 8 | 48 vCPU / 96 GiB (c7i.12xlarge class) |
| 10 to 12 | 64 vCPU / 128 GiB (c7i.16xlarge class) |
| 12 with room | 64 vCPU / 256 GiB (m7i.16xlarge class) |

Dedicated or workstation equivalents: 16 cores / 32 threads with 128 GB, for 6 to 8 leads; 32 cores / 64 threads or
more with 128 to 256 GB, for 10 to 12. CAPACITY-1 §6 records prices read on 2026-10-31; check them again before
ordering.

## 6. Recommendation and confidence

1. **Option 0 first,** as two P1 ticket proposals to the owner (DEC-974). Seeding or slot exclusion for cold
   rebuilds is expected to remove most of today's at-least-23-minute waits. The embedder's parallel requests go to
   a determinism test. Neither needs hardware. **Confidence: medium-high** that cold rebuilds caused the afternoon's
   waits (idle cores while waiting; semantic stage 3,000 to 3,750 s when three ran at once against 700 to 1,500 s
   alone).
2. **Option 1a is optional and small:** about +1 lead under the rule, and no processor gain. Take it only if Windows
   can spare the memory, since about 4 GB would be left to it. **1b on its own is not recommended:** it buys memory
   when the processor is the limit.
3. **10 leads means option 2:** at least 64 threads and 96 to 128 GB (WSL or VM memory of at least 64 GB), with a
   GPU or extra threads for the embedder. This is for **Wave 3**. For Wave 2 it gains about a day against 1 to 2
   days of setup (CAPACITY-1 §6, unchanged). **Confidence: medium on memory** (26 hours, 18 leads; the formula is
   conservative by about 9 to 17 GiB against what was measured). **Medium-low on the slot and thread counts**: the
   M/M/c assumptions, a service time from 32 steps on one day, and B's 16 minutes estimated. They are re-measured once
   option 0 is in, and the counts would most likely fall.
4. **The dispatcher's `peaks.json` needs no change.** Its 7-day figures match the window after W2-107 (lead p95
   outside: 2.40 against 2.39 GiB; slot rise: 1.43 in both).

## 7. What it blocks

- **Nothing in Wave 2.** The chain and the ready-ticket count set its pace (CAPACITY-1 §6).
- **The 10-lead aim** (DEC-999 to DEC-1004). On this PC it stops at about 4 to 6 leads (5 with 1a) until option 2.
  Option 0 decides whether 6 to 8 work well here.
- **Wave 3's plan size.** If it keeps this plan's breadth, its machine is decided before it starts.
- **Re-sizing `heavy_slots.conf`** (DEC-979 D1 "re-sized from the re-measure after W2-107"). Today's data says not
  to add slots on 20 threads: a 4th slot adds 6 threads of demand to a machine already full. Revisit after option 0.

## The owner's decision (six parts, DEC-818)

1. **Context:** the aim is 10 leads. The rule allows about 4, and the processor is full at about 6.
2. **What was measured:** sections 2.1 to 2.4. Memory in use reached at most 18.3 GiB with 6 to 8 leads. Busy p50 was
   18.8 of 20 at 6 leads. Waits were at least 23 minutes since rebuilds joined the slots, with idle cores in half of
   the waiting minutes.
3. **Why it matters:** section 3.
4. **Options:** 0, 1a, 1b, 1c and 2 (section 5).
5. **Recommendation:** 0 now (P1 proposals). 1a optional. 2 for Wave 3, at 64 threads and 96 to 128 GB. Confidence as
   in section 6.
6. **Blocks:** section 7.

## Sources

`log/capacity/kinds.jsonl`, `log/lead-mem.jsonl`, `log/capacity/bench.jsonl` (from 2026-10-31T18:47);
`dispatch/peaks.json` (computed 2026-11-01 20:22); `dispatch/status.json` (20:51); `dispatch/dispatcher.py`
(`compute_peaks`, `admission`); `tools/heavy_slots.conf`, `tools/heavy_slot.sh`, `tools/rebuild_slot.sh`,
`tools/gate-config.json`; the leads' logs `~/gov-os-worktrees/*/.gov-runtime/scratch/lead/log/` (rebuild records'
`timing`, pytest summaries, wait lines, exit files); `merge-queue/log/`, `log/close-build/`; `log/oom-watch.txt`;
`C:\Users\usain\.wslconfig`; Win32_ComputerSystem, Win32_Processor, Win32_PhysicalMemory(Array) and
Win32_OperatingSystem (read-only); `governance/project/orchestration/packages/CAPACITY-1.md`,
`log/capacity/bigger-machine.md`; DEC-975, DEC-979, DEC-1001, DEC-1008, DEC-1011.
