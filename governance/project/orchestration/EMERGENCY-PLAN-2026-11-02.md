# EMERGENCY PLAN — DEC-1033 (in force since 2026-11-02 13:01), the one file a fresh or compacted session carries on from

Rewritten 2026-11-02 15:55 by session `07f25884` (W2O V3); updated 16:15. **The owner's change of plan (16:00):
session `07f25884` stays on until window 1's re-pin and ACT-QUERY-GPU-2 are done and checked; then it updates the
handover, writes the stand-by file, says "fresh session ready" and does nothing further.** Read this before anything
else in the checkpoint. The register holds the decisions; this file holds the state. Update it before the switch and
after it.

## Window 1: what is READY (16:15)
- `pin/repin3_dry.sh` (the wheel twice + a scratch install), `pin/repin3_checks.sh <pin dir>` (every check before
  the switch: commands, no CPU gate, dependencies, a search with both facets, context, the three hooks by their exact
  lines under a scratch HOME, and the guard: `guard4_check.py`, `test_guard_fix_3.py`, `hook_timing.py`, which now
  take `GOV_PIN_PY`), `pin/REPIN-COMMANDS.template.sh` + `pin/make_repin3_commands.sh <commit>` (writes
  `REPIN-COMMANDS-<C>.sh` with the dry run's sha256; parts 0, A install beside, B checks, C quiet point, D atomic
  switch + smoke + a search, rolling back by itself on a failure, E registry by `pin/repin3_registry.py`, Role: owner).
- **Dry run on the landing's merged commit 816db78d (in the warm clone): two builds agree (sha256 ff8827cc…); ALL
  CHECKS PASS** (guard: 54 cases PASS, 269 passed 1 skipped, the same as the old pin; hook 0.14-0.94 s; a search 1.05 s
  warm against 0.92 s on the old pin; the first search after the switch is a cache miss: the cache key now carries the
  device). Note: a pin under a path over 127 characters gets a `/bin/sh` launcher line that the hooks cannot use: dry
  installs live under `~/.cache/gov-os-repin3-dry/`.
- `drafts/ACT-QUERY-GPU-2.md`, revision 2 (replaces the package at the commit): step 0 checks the new pin and waits
  for the old to drain; **the wrapper is not removed but set to the GPU** (`echo gpu > ~/.ollama/query-server-device`;
  the wrapper reads it, 11 tests), so a restart in the gap also comes back on the GPU with caps and log; undo = `cpu`.
- To do once the landing ends: commit (step 2 below), then `bash pin/make_repin3_commands.sh w2/integrate`, run
  `repin3_checks.sh` on its dry install, write `packages/ACT-REPIN-EMERGENCY-1.md` (the cover: the script, then
  ACT-QUERY-GPU-2), write `log/act-in-progress.txt` (DEC-1028 item 6), ping the owner.

## NEXT STEP (in this order)
1. **Watch the landing of W2-122 + W2-123** (started 15:48 by the dispatcher, `log/land-dispatch-20261102-1548*.out`;
   merged 816db78d2d87 onto a7182f6c in the warm clone; testing). It ends with `CLOSED W2-122` / `CLOSED W2-123`
   and a `land` inbox item. Do NOT commit to w2/integrate while it runs: a moved head makes the queue re-merge and
   re-test (HEAD_TRIES 3, ~30-45 min each).
2. **Then commit what is waiting** (all written in scratch, nothing half-written):
   - `docs/DECISION_REGISTER.md`: append `drafts/register-DEC-1037.md` after DEC-1036's version table, then its own
     version table `| 0.419 | 2026-11-02 | Owner (recorded by the orchestrator, DEC-861): DEC-1037. Next free id: DEC-1038. |`;
     then `drafts/register-DEC-1038.md` and `| 0.420 | ... DEC-1038. Next free id: DEC-1039. |`.
   - `governance/project/prompts/w2-orchestrator.md`: one standing line for DEC-1038 (ACT for machine changes; the
     checkpoint tool; the targets; every heavy job through the gate).
   - `governance/project/orchestration/packages/P1-REPIN-EMERGENCY.md` from `drafts/P1-REPIN-EMERGENCY.md`, its
     header marked "APPROVED (a), DEC-1037, 2026-11-02 ~15:50".
   - `packages/ACT-QUERY-GPU-2.md` replaced by `drafts/ACT-QUERY-GPU-2.md` (revision 2: the wrapper set to the GPU,
     not removed).
   - The scratch tools stay in scratch (land.py's strays, queue_park.py, the wrapper and the pin scripts).
   - This file into `governance/project/orchestration/EMERGENCY-PLAN-2026-11-02.md` (the committed copy).
   - One commit, trailers `Task: DAEO-sdxk`, `Implements: DEC-1037`, `Role: orchestrator`.
3. **Refresh the integration store once by hand** (`tools/refresh_integration_store.sh`; it is at `6ebd7b56`).
4. **Window 1's preparation** (DEC-1037 (1); the P1's section 4 (a), "window 1" steps, is the checklist): on the
   landed head, the GOV_PIN_PY override in the guard-check tools; the wheel built twice, sha256 equal;
   `REPIN-COMMANDS-<head12>.sh` and the registry script; every check before the switch, the guard's included (W2-84's
   stricter reads, `smoke_repin2.sh`); then ping the owner for the plain-terminal ACT (re-pin by `mv -T`, old pin
   kept), then ACT-QUERY-GPU-2 once `pgrep -f pin-5c401220` finds nothing (the new pin's own processes excepted).
   **Any failed check, or a broken search after the switch: switch straight back to the old pin and tell the owner.**
5. **The full suite on the re-pinned head** as soon as window 1 is done (DEC-1037 (2)): expected about 1.5-2 h on
   the frozen machine (29-30 Oct quiet runs: 5,300-5,600 s with a 1,000-1,500 s cold setup; seeding cuts the setup;
   today's contended nightly took 5.4 h). Started by hand like the nightly (`nightly.sh` against the head), detached.
6. **The clean restart** (DEC-1037 (3)): every red of that run listed with the ticket that fixes it (W2-90b, W2-105
   among the parked six; W2-90c, W2-66b, W2-55, W1-01b; any other: file it); those landed and run first, at top
   priority (unpark their approvals with `tools/queue_park.py unpark` only for the ones landing, or name them); the
   full run repeated until green, or every remaining red has its fix landing. Acceptance tests by test designers only.
   Then the owner lifts the freeze.
7. **Window 2** after W2-112 lands (its lead `w2-112-2b` is in its serial-only run; then the FULL review, reviewer
   unsandboxed under DEC-1034's extension; then DONE; land through the queue); then W2-127.
8. **The after figures** (DEC-1033 item 4), with ACT-QUERY-GPU-2's question time in them.

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
| Fix | State at 15:55 | Next |
|---|---|---|
| (a) W2-112 shared reranker on the GPU (`DAEO-clon`, FULL; lead `w2-112-2b`, `~/gov-os-worktrees/W2-112`) | lead's serial-only run (4 F, maybe the incident) | FULL review, DONE, land; window 2 |
| (b) a question's vector from any device (merged `6ed6a5ae`) + the query server on the GPU | code in the repository, NOT in the pin; query server CPU-only (ACT-QUERY-CPUS-1) | window 1 re-pin, then ACT-QUERY-GPU-2 |
| Reranker interim rule (GPU slots; wait 20 s or unranked) | LIVE (`81b7a739`) | retired by W2-112's ACT |
| (c) dispatcher v4.6 | LIVE (`b06ee350`) | machine-derived limits (above) |
| (d) no cold rebuild (seeding) | LIVE (`648e5067`) | integration store refresh after the landing |
| W2-122 seeded rebuilds, W2-123 bounded retry | LANDING since 15:48 (the two alone) | close records come from land.py |
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
