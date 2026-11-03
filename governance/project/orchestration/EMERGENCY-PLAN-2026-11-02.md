# EMERGENCY PLAN — DEC-1033 (in force since 2026-11-02 13:01), the one file a fresh or compacted session carries on from

## THE OWNER'S PLAN (DEC-1039, 2026-11-02 ~18:20) — the fresh session works from this, in order, all in emergency mode
1. **No infrastructure fix waits for the ticket path.** Each one now, as an emergency patch, out of the ordinary,
   with the reds' rules (an acceptance test that must change is revised by a test designer; a review where needed;
   every heavy run through the gate): the shared reranker on the GPU (W2-112: resume from
   `~/gov-os-worktrees/W2-112/.gov-runtime/scratch/lead/CHECKPOINT.md`, round 2's review); W2-122's seeding and
   W2-123's bounded retry (branches `3fc448601e2d`, `3de9bcf44d91`, approved in the queue; the queue stops on W2-54's
   six CPU-only cases until a test designer revises them under DEC-1033); the vector cache (W2-126: its tests are
   ready at `75c4db0e` in its worktree); the real gitleaks fix (each gate slot confined to its CPU share with
   `taskset` in `tools/heavy_slot.sh`; `src/gov/secrets/__init__.py:599`'s pool sized by `os.sched_getaffinity`;
   `nightly.sh`'s runs included: it takes the slot locks itself, F2); the machine-derived limits and the standing
   targets (`drafts/BRIEF-MACHINE-TARGETS.md`). **Re-pin as often as needed**, each like window 1:
   `bash pin/make_repin3_commands.sh <commit>` (it builds twice, fills the sha256), `pin/repin3_checks.sh` on the
   dry install, `packages/ACT-REPIN-EMERGENCY-1.md` as the model for the ACT (the old pin's folder kept for the
   rollback; the registry script `pin/repin3_registry.py` needs its OLD_COMMIT/OLD_SHA moved to a7182f6c's entry
   first), the hold, a ping.
1b. **The Gov Load Balancer (the owner, ~18:40; DEC-1039 (1b)), with the infrastructure fixes:** for this repository
   now and for the Gov OS. Plan leads, closes, landings and rebuilds together by their **phases** and each phase's
   **measured peak on every resource** (CPU, RAM, the GPU and its memory); **pair GPU-heavy work** (leads searching,
   rebuilds embedding) **with CPU-heavy work** (test runs) so neither peaks twice at once; keep the embedders and
   rerankers on the GPU within its budget, **even if that limits leads to two or three**. **Document the rule: the
   GPU's dedicated memory never spills into shared memory, and never runs out into a CUDA crash**; test the load
   balancer and the dispatcher on it and on the phase balancing. In the CTO's tools first (the dispatcher already has:
   admission on CPU, RAM and GPU memory, the lead cap from memory, slots by device, `gpu_headroom_mib`, the rerankers'
   GPU slots, `log/capacity/kinds.jsonl` samples by kind, `lead-mem.jsonl`; missing: per-phase peaks, phase pairing,
   a forecast before admission, the spill rule's check: nvidia-smi's dedicated memory against the budget and WSL's
   shared-memory use); fold it with `drafts/BRIEF-MACHINE-TARGETS.md` into one engineer's brief, one review. For the
   Gov OS: propose to the owner whether it is its own ticket or KPI lines in W2-20 and W2-121 (DEC-1003).
2. **The tests and the code, before the full suite:** a report of the code's size (files and lines: product code,
   tests, tools), the number of tests (unit, acceptance), which are no longer needed, which repeat each other or can be
   merged, even across tickets. Then test designers refactor the tests (an independent reviewer checks them) and a
   senior engineer refactors the code. Every KPI line stays covered by at least one test; **the list of deletions and
   merges goes to the owner first.** The inventory may start in parallel with 1; the refactor waits for stable
   infrastructure.
3. **The full suite on the re-pinned head**, every red fixed in emergency mode (even in the Gov OS), repeated until
   green (see "Steps (5)" below for the known reds and nightly.sh's missing budget).
3b. **Before the freeze lifts, the Wave 2 plan refactored** (WBS, tickets, the wave): done in substance by the
   emergency (formal closing only), overlapping (merge), no longer needed, to re-scope; every KPI line of a merged or
   retired ticket shown met with evidence or moved. **The list goes to the owner first, with the new estimate for
   EXAMIN's copy.**
4. Once green the owner lifts the emergency and the freeze; re-pin if needed; tickets resume; W2-112, W2-122,
   W2-123, W2-126, W2-20 and the others closed formally afterwards with their records.
- P-W2-20-THREAD-BUDGET (a): done (W2-20 `DAEO-r30l` has the four success lines and one failure line).
- **The dispatcher starts nothing**: `dispatch/ready.txt` is empty (its lines in `ready.parked-by-stop-1821.txt`, the
  freeze's in `ready.parked-by-freeze.txt`); `land.txt` absent. Restart work only under this plan.
- **The push of w2/integrate** (30 commits incl. the registry `fe01f3cb`) was refused by the CTO session's
  permissions: the owner's (`git push origin w2/integrate`).

## State at ~18:30 (AFTER THE SWITCH): window 1 DONE
- `pin-a7182f6c` live (registry `fe01f3cb`), confirmed from the CTO session: `readlink -f ~/.local/bin/gov`, no CPU
  gate in its `semantic.py`, a search 1.3 s with both facets, no old-pin process (`tree_busy.sh --cmd`). Rollback: the
  old pin `pin-5c401220` kept (ACT-REPIN-EMERGENCY-1's rollback lines; undo ACT-QUERY-GPU-2 first).
- ACT-QUERY-GPU-2 done: the query server on the GPU (29/29, pid 3877550, CPUs 8-11, nice 0, pinned), a question
  0.04-0.22 s (13.7 s before); the wrapper set to `gpu` and updated (drops a slot's thread budget);
  `dispatch/config.json` `gpu_expected.query` = true (backup `.pre-gpu-query`); the dispatcher reads both 29/29.
- The gate's thread budget live (`tools/heavy_slot.sh`, H1-H12); it does not bound the load (plan item 1's fix does).
- **Stopped:** the W2-122/123 landing (17:00, both approved); W2-112's lead (17:08, safe point, round 2's review not
  started); **W2-126**: the dispatcher had started its run 1 at 17:07 (the CTO's slip: the ready list was not emptied
  at the 17:00 stop); its `retrieve_check`/`context_check` restarted the query server at 18:14 (through the wrapper: on
  the GPU with its caps; `~/.ollama/query-autostart.log`); its verification run stopped at 18:25 (8 processes; its
  tree clean at `75c4db0e`); its lead stopped at a safe point and exited (tests ready, 17 cases, `f90b34c47fdd`; no engineer started; see the stops log).
- `tools/tree_busy.sh --cmd <path>` is the ACTs' process check (ACT-QUERY-GPU-2, the re-pin template), never `pgrep -f`.

Rewritten 2026-11-02 15:55 by session `07f25884` (W2O V3); updated 16:15 and ~17:15. Read this before anything
else in the checkpoint. The register holds the decisions; this file holds the state. Updated before the switch and
after it.

**The owner's order of ~17:00 (supersedes the earlier step list):** the re-pin no longer waits for the landing: fix
(b) is on `a7182f6c`, so window 1 re-pins from there. In order: (1) stop everything at safe points (DONE, see
`log/emergency-stops-20261102.md`); (2) the handover kept current; (3) BEFORE the re-pin, the gitleaks fix: the thread
budget in `heavy_slot.sh` with its own quick test and one review, switched on; and a KPI proposal for W2-20's gate
(DEC-1003); (4) window 1 from `a7182f6c` (fix (b) confirmed on it), commands generated, every check re-run on its dry
install, the hold written, the owner pinged for the ACT; ACT-QUERY-GPU-2 right after; (5) straight after, the full
suite on the re-pinned head, then **every red fixed as an emergency, not through the ticket path: the CTO launches
senior engineers to fix the reds directly as emergency patches, no leads, no tickets; the only rule kept is that an
acceptance test that must change is revised by a test designer, with a review where needed; every smart practice;
actions out of the ordinary permitted to fix the machine and the infrastructure; the full run repeated until green**;
(6) once green the owner lifts the freeze: then land W2-122, W2-123 and every in-flight ticket that can land, restart
the closes, carry on with the tickets with the load within its band. **Session `07f25884` stays on until window 1's
re-pin and ACT-QUERY-GPU-2 are done and checked; then it updates the handover, writes the stand-by file, says "fresh
session ready" and does nothing further; the fresh session carries on from step (5).**

## State at ~17:50 (BEFORE THE SWITCH)
- **Step 3 done in part:** the thread budget is LIVE in `tools/heavy_slot.sh` (17:46; review PASS, verdict block last;
  review F1 and F4 fixed with test H12; H1-H12 pass on the live gate; backup `heavy_slot.sh.pre-dec1038`). Measured on
  W2-69's 352 tests: 968 s against 1,069 s, but peak runnable 179 against 165: **it does not bound the load**; the
  cause is the scan's pool of `os.cpu_count()` gitleaks in `src/gov/secrets/__init__.py:599` (incident record
  updated). Proposed to the owner with the window 1 ping: each slot confined to its CPU share (`taskset`) and the pool
  sized by `os.sched_getaffinity` (an emergency patch + unit test + one review). The review's F3 (a server keeps a
  slot's budget) is in ACT-QUERY-GPU-2's step 0 (the wrapper's update, 14 tests; `1d271a30`); F2 (nightly.sh has no
  budget) is in step (5) below.
- **Step 4:** all checks PASS on a7182f6c's dry install (17:2x); `REPIN-COMMANDS-a7182f6c.sh` and
  `packages/ACT-REPIN-EMERGENCY-1.md` committed (`80ee632d`); the hold `log/act-in-progress.txt` written at the ping;
  **waiting for the owner's operator**. After "done": end the hold (`mv` to `.ended-HHMM`), confirm the pin, set
  `gpu_expected.query`, measure a question, update this file, RESUME HERE and the checkpoint, then the stand-by file
  and "fresh session ready".

## State at ~17:15
- **Stopped (owner ~17:00):** the W2-122 + W2-123 landing (the queue stopped itself at 17:00 on W2-54's six CPU-only
  cases, red on a7182f6c since fix (b); both still approved); W2-112's lead (safe point, round 2 of the review not
  started, its checkpoint in its worktree); no CTO agent running. Details and resume points: the stops log.
- **Records committed `8c817af2`** (DEC-1037, DEC-1038, the P1 approved, ACT-QUERY-GPU-2 revision 2, the plan, the
  prompt's DEC-1038 line). Uncommitted: `.tickets/DAEO-1vka.md` (W2-127 gains F3's KPI line, the CTO as moderator),
  `packages/P-W2-20-THREAD-BUDGET.md` (the KPI proposal): commit with the next records commit (not during the ACT hold).
- **Step 3, the gate's thread budget:** `tools/heavy_slot.candidate.sh` (max(1, CPUs/slots/workers) threads exported
  as GOMAXPROCS, OMP_NUM_THREADS, MKL, OPENBLAS, RAYON, NUMEXPR (both), VECLIB; inherited values overridden;
  `GOV_HEAVY_THREADS` overrides); `tools/test_heavy_slot.sh` H1-H11 PASS on the candidate (H9-H11 fail on the live gate,
  as they should; run with `HEAVY_SLOT_UNDER_TEST=<path>`); backups `heavy_slot.sh.pre-dec1038`,
  `test_heavy_slot.sh.pre-dec1038`. Measurement (W2-69's tests through each gate, time and peak runnable) running; one
  independent review (independent-auditor) running. **Switch on** = `cp heavy_slot.candidate.sh heavy_slot.sh` once the
  review passes (verdict.py) and the measurement holds (no more than 20 % slower). Then incident
  `log/incidents/2026-11-02-1620-T1-cpu.md` gets its fix line.
- **Step 4, window 1 from a7182f6c:** fix (b) confirmed (6ed6a5ae is an ancestor; semantic.py has no CPU gate);
  `pin/REPIN-COMMANDS-a7182f6c.sh` generated (sha256 9ed615a8…, two builds agree, reproducible across runs); checks on
  its dry install (`~/.cache/gov-os-repin3-dry/a7182f6c/venv`) running (8c817af2, byte-identical code, passed ALL
  CHECKS at 17:0x). Then: write `packages/ACT-REPIN-EMERGENCY-1.md` (the cover: `bash pin/REPIN-COMMANDS-a7182f6c.sh
  2>&1 | tee ~/repin-a7182f6c.log` in a plain terminal, then ACT-QUERY-GPU-2), write `log/act-in-progress.txt`, ping.
- **After the switch (the CTO):** confirm `readlink -f ~/.local/bin/gov` → `pin-a7182f6c`, a live tool call through the
  hook, a search; after ACT-QUERY-GPU-2: `dispatch/config.json` `gpu_expected.query = true`, a question's time.

## Window 1's tools (ready)
- `pin/repin3_dry.sh` (the wheel twice + a scratch install), `pin/repin3_checks.sh <pin dir>` (every check before
  the switch: commands, no CPU gate, dependencies, a search with both facets, context, the three hooks by their exact
  lines under a scratch HOME, and the guard: `guard4_check.py`, `test_guard_fix_3.py` (through the gate),
  `hook_timing.py`, which take `GOV_PIN_PY`), `pin/REPIN-COMMANDS.template.sh` + `pin/make_repin3_commands.sh <commit>`
  (parts 0 preconditions incl. the hold file, A install beside, B checks, C quiet point, D atomic switch + smoke + a
  search, rolling back by itself on a failure, E registry by `pin/repin3_registry.py`, Role: owner).
- Dry installs live under `~/.cache/gov-os-repin3-dry/` (a path over 127 characters gets a `/bin/sh` launcher line
  the hooks cannot use). The first search after the switch is a cache miss (the cache key now carries the device).
- `packages/ACT-QUERY-GPU-2.md` revision 2: step 0 checks the new pin and waits for the old to drain; the wrapper set
  to the GPU (`echo gpu > ~/.ollama/query-server-device`), so a restart in the gap also comes back on the GPU.

## Steps (5) and (6) for the fresh session, in short
- (5) The full suite on the re-pinned head, started by hand like the nightly (`nightly.sh` against the head),
  detached, through the gate: expected about 1.5-2 h on the frozen machine. **The gate review's F2: `nightly.sh`
  takes the slot locks itself, so it gets neither the worker cap nor the thread budget (20 workers, each gitleaks on
  20 CPUs): export the budget for the run (`GOMAXPROCS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
  RAYON_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 NUMEXPR_MAX_THREADS=1`) or give `nightly.sh` the same budget as an
  emergency patch (one review); and watch W2-54's context-check time limit (F7: gitleaks' fan-out is
  `os.cpu_count()` at once, each with a 60 s + size limit).** Then the reds: known so far: W2-54's six
  CPU-only cases (a test designer revises them under DEC-1033, `Rewrite-Reason: DEC-1033`), W2-59 hook_lines (4, red
  at the baseline), W1-19 default_reranker (revised under DEC-1033 item 3), W1-19 warm p95 (load-sensitive), the
  baseline nightly's 32 reds (`log/nightly/20261102-0400/run.txt`); W2-90b and W2-105 among the parked six; W2-90c,
  W2-66b, W2-55, W1-01b. Senior engineers fix them directly as emergency patches (owner ~17:00): each with its tests,
  a review where needed, through the gate; repeat the full run until green.
- (6) On the owner's lift: `tools/queue_park.py unpark`, land W2-122/123 and the rest, `dispatch/ready.parked-by-freeze.txt`
  back, closes restarted, W2-112 resumed from its checkpoint, the machine-targets engineer (`drafts/BRIEF-MACHINE-TARGETS.md`).

## Work the owner ordered that waits for an engineer (DEC-1037 (4) and follow-ups)
- **Limits derived from the machine** (DEC-1037 (4)): no number fixed for this machine; the CTO's tools detect
  cores, RAM, the GPU's model and memory at start and when they change, and derive every limit. Hard-coded today:
  the dispatcher's `cpu_band` [14,18], `slots_gpu` 3, `slots_cpu` 2, `rerank_gpu_slots` 2, `gpu_headroom_mib` 2048
  (`dispatcher.py` defaults ~line 327; `nproc()` and the lead cap from memory are already measured);
  `gov_reranker_gpu_slot.py`'s two lock files; the servers' CPU sets (12-19, 8-11; owner ACTs). An engineer, its
  tests, one review (DEC-1033's rule). Then KPI proposals for W2-20 and W2-121 (the product), under DEC-1003, to the owner.
- **A dispatcher alert when the query server loads on the GPU** (today only its status line shows it): small, with
  the machine-limits change or alone; one review. Interim: the wrapper below.

## The rules in force
- **DEC-1033 EMERGENCY + DEC-1032 FREEZE:** nothing starts except the fixes and DEC-1037's steps; each fix gets one
  independent review before it goes live (two rounds at most, DEC-1010; then the owner once); acceptance tests a fix
  turns red are revised afterwards by a test designer. The owner lifts the emergency and the freeze after the clean
  restart (DEC-1037 (3)) and the after figures.
- **DEC-1028 item 6:** while an owner ACT is being applied, no main-tree commit: write `log/act-in-progress.txt` at
  hand-over, `mv` it to `act-in-progress.ended-HHMM.txt` only on the owner's word. **No ACT in progress at 15:55**
  (ACT-QUERY-CPUS-1 ended 15:47).
- **Emergency stops park the queue's approvals** (DEC-1037 (5)): `python3 tools/queue_park.py park [--keep W2-x]`
  with the dispatcher's lists; `unpark` on the lift. `land.py` now refuses a landing while the queue holds an
  approval it was not given (`strays()`, 4 tests in `tools/test_queue_park.py`).
- **DEC-1038 (owner ~16:20, draft `drafts/register-DEC-1038.md`, commit with DEC-1037):** (1) anything outside the
  repository that changes how the machine runs comes to the owner as an ACT (never placed by the CTO or its agents);
  (2) checkpoints only by `bash tools/cto_checkpoint.sh "<next>" [inputs]` (straight to scratch; never `gov checkpoint`
  in the main tree, never a checkpoint moved by hand); (3) `.wslconfig`: no change before the RAM upgrade's restart;
  (4) the standing targets (band >= 80 % of working hours, memory above the floor, GPU within budget, no timed-out
  embedding, no cold rebuild) in every morning package; a breach over 15 min is an incident traced like a red
  (`log/incidents/`; the first: `2026-11-02-1620-T1-cpu.md`, gitleaks threads past the gate); **every heavy job through
  the gate, the CTO's own agents and runs included** (`tools/heavy_slot.sh`), none past it without the owner's order.
  The mechanism is briefed for one engineer + one review: `drafts/BRIEF-MACHINE-TARGETS.md` (with DEC-1037 (4) and
  the gate's thread budget): **the fresh session launches it** (not this session: nothing may outlive it).
- Quiet hours 02:00-07:30: no pings. Pings: `tools/ping_log.sh "<text>"`, PushNotification, `ping_log.sh --result`.
  `rm` needs the owner's approval (by day: ping first). Never touch the shared Ollama servers except through owner ACTs.

## The query server (127.0.0.1:11435): state and the interim guard
- Since ACT-QUERY-CPUS-1 (15:44): pid 2221804, CPU-only, CPUs 8-11, nice 0, model pinned.
- **Incident 15:29-15:44:** in the ACT's 3-second restart gap, W2-112's lead's serial-only acceptance run (its
  worktree's code since `6ed6a5ae`, whose `ensure_query_available` no longer hides the GPU) started the query server
  with the GPU visible; pinned searches got no semantic results until the operator restored it. The lead was told
  (SendMessage, 15:53) to check its 4 serial failures against that window.
- **Interim guard until ACT-QUERY-GPU-2:** `~/.local/bin/ollama` = `tools/ollama_query_cpu_wrapper.sh` (7 tests:
  `tools/test_ollama_query_cpu_wrapper.sh`). Every automatic start finds it first on PATH (the old pin, the new code,
  the cron jobs' PATH too; nothing outside tests sets `GOV_OLLAMA_BIN`); `serve` for 11435 runs with the GPU hidden
  on CPUs 8-11, logged with its caller in `~/.ollama/query-autostart.log`; everything else passes through.
  ACT-QUERY-GPU-2 (revision 2) sets it to the GPU through `~/.ollama/query-server-device`; it stays until the
  product's automatic start carries the caps.
- **Why a question takes ~13.7 s whatever the load:** the runner computes with 10 threads (one per physical core of
  the i7-12700F) on the 4 CPUs it is given (8 before), and ggml's threads wait for each other at every step: about
  6.3 s per text whatever its length (the server's log: two texts 12.6 s; one text 6.3-7.0 s). The same question on
  the GPU (the shared server, 15:50): 0.07-0.5 s. The GPU move after the re-pin removes it.

## The fixes: state
| Fix | State at ~17:15 | Next |
|---|---|---|
| (a) W2-112 shared reranker on the GPU (`DAEO-clon`, FULL; `~/gov-os-worktrees/W2-112`) | STOPPED ~17:08 at a safe point: review round 2 not started (repairs committed f59c9ba5560e + tests ed0891667f46) | after green: resume from its checkpoint; land; window 2 |
| (b) a question's vector from any device (merged `6ed6a5ae`) + the query server on the GPU | on a7182f6c, NOT in the pin; query server CPU-only (ACT-QUERY-CPUS-1) | window 1 from a7182f6c, then ACT-QUERY-GPU-2 |
| Reranker interim rule (GPU slots; wait 20 s or unranked) | LIVE (`81b7a739`) | retired by W2-112's ACT |
| (c) dispatcher v4.6 | LIVE (`b06ee350`) | machine-derived limits (above) |
| (d) no cold rebuild (seeding) | LIVE (`648e5067`) | integration store refresh after the landing |
| W2-122 seeded rebuilds, W2-123 bounded retry | landing STOPPED 17:00 by the queue (W2-54's CPU-only reds on the head, not theirs); both approved | land after green (owner's step 6) |
| W2-126 vector cache (`DAEO-jpr0`) | run 1 (tests only) on the ready list | engineer after W2-123 lands |
| W2-127 the reranker's socket in the sandbox | filed | after W2-112 lands |

## What was stopped, and where it resumes (details: `log/emergency-stops-20261102.md`)
- Six landings (W2-11 c9f99b28b88b, W2-105 fa653609cc93, W2-90b 73c18fea1e1f, W2-81 e78e6af7530d, W2-91
  55b47e075b3b, W2-92 448a835a9dca): approvals in `merge-queue/parked-by-emergency/`, lines in
  `dispatch/land.pending.txt` (with W2-61h ac7dfa1790c7, and W2-104 waiting for its run 3). Those that fix a red of
  the full run land first (step 6); the rest on the lift.
- The re-close of W2-05 + W2-96: the measured SEEDED close (`close_build.py`, detached) for the after figures.
- W2-04's repair round: a fresh lead from its checkpoint after the freeze.
- Parked ready list: `dispatch/ready.parked-by-freeze.txt`; restore it on the lift.

## The decisions since DEC-1033
- DEC-1034 (delegated): W2-112's engineer unsandboxed; extended at 14:20 to its reviewer (recorded in DEC-1037).
- DEC-1035 (owner): v4.6's G1 fix without a third review; P-W2-112-T2 (c) now and (a) as W2-127.
- DEC-1036 (delegated): W2-112 KPI 6, three unit files, the answer-form ruling, a Wave 3 row for W2-96's runner.
- DEC-1037 (owner, ~15:50; to commit, step 2): the re-pin (a) in two windows; the full run after window 1; the clean
  restart; machine-derived limits; stops park the queue's approvals. Next free id after it: DEC-1038.

## The ACTs
- Done: ACT-RERANK-GPU-SLOTS-1, ACT-RERANK-WAIT-1, ACT-W1-01-EXEMPT-1, ACT-STOP-WAITER-1, ACT-GUARD-FIX-3,
  ACT-QUERY-CPUS-1 (15:47).
- Never apply: ACT-RERANK-CPU-1, ACT-QUERY-GPU-1.
- Next: the window 1 re-pin ACT (to write, step 4); ACT-QUERY-GPU-2 (gets step 0, step 2) right after it.

## Slips logged today (log/drift-2026-w44.txt)
- The 13:01 stop left six approvals in the queue (fixed by DEC-1037 (5)); an `rm -f` of the killed run's empty
  `run.lock` without the owner's approval (reported); merge `6ed6a5ae` without trailers.

## The after figures due (DEC-1033 item 4)
- After (a)-(d) have run for an hour: load, memory, the GPU, rebuild counts and times (`tools/rebuild_counts.py`),
  a seeded close's time beside today's cold median of 30 min (confirm no close runs cold), a question's time
  (13.7 s on the CPU now; expected under 0.5 s after ACT-QUERY-GPU-2).
- Before snapshot: `log/emergency-before-20261102.txt` (load 36, 10.8 GB free, GPU 6.8/16.3 GB with 6 rerankers;
  shared p95 60 s, query p50 15 s, p95 53 s).
- Then DEC-1032 step (v): the assessment and redesign of the ticket's path (launch, verify, land, close).

## Background tasks (the owner asked, 15:50)
- Stopped at 15:52 as not needed: the embedder log watch (v4.6's GPU alerts cover it), the CPU reranker wait (its
  benchmark long done; its `pgrep -f` matched itself). The experiments subagent finished hours ago.
- The inbox waiter: session-bound by nature; re-armed by `07f25884` at 16:01 when the owner kept it on; the fresh
  session arms its own (`bash tools/inbox_wait_quiet.sh` in the background, re-armed after every wake). The sentinel
  watches the inbox on its own. The stand-by file was ended at 16:01 (`log/cto-standby.ended-1601.txt`).
- Nothing needed belongs to the old session alone: the dispatcher (cron), the nightly (cron), the landing (the
  dispatcher's, detached), the W2-112 lead (its own session), the wrapper (a file) all run without it.
