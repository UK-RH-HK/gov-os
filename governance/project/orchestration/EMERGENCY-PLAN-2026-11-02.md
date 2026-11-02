# EMERGENCY PLAN — DEC-1033 (in force since 2026-11-02 13:01), the one file a fresh or compacted session carries on from

Written 2026-11-02 14:20 by session `07f25884`. Read this before anything else in the checkpoint. The register holds the
decisions (DEC-1032 to DEC-1036 and on); this file holds the state. Update it at every step.

## The rules in force
- **DEC-1033 EMERGENCY + DEC-1032 FREEZE:** nothing starts except the fixes; each fix gets one independent review
  before it goes live (two rounds at most, DEC-1010; then the owner once); acceptance tests a fix turns red are revised
  afterwards by a test designer. The owner lifts the emergency and the freeze after the after figures.
- **DEC-1028 item 6:** while an owner ACT is being applied, no main-tree commit by the CTO or its tools: write
  `log/act-in-progress.txt` at hand-over, `mv` it to `act-in-progress.ended-HHMM.txt` only on the owner's word. **No
  ACT is in progress at 14:20.**
- Quiet hours 02:00-07:30 (DEC-1021): no pings. Inbox: arm `bash tools/inbox_wait_quiet.sh` (background) after every
  wake. The dispatcher alerts on GPU crashes and partial or 0-layer loads (v4.6); also re-pin the shared embedder with
  `keep_alive:-1` if it ever reloads (DEC-1031 item 2).

## The fixes: state, and expected time to live
| Fix | State at 14:20 | Next | Expected live |
|---|---|---|---|
| (a) W2-112 shared reranker on the GPU (`DAEO-clon`, FULL; lead session `w2-112-2b`, worktree `~/gov-os-worktrees/W2-112`) | 51 acceptance cases; engineer batch 3 running (the no-GPU fallback fault; 3 unit files; the measure written up); real-GPU measure done: embedder 3.17 + service 3.26 = 6.43 GB peak, warm p95 3.8 s, same answers 20/20 | the lead's scoped run, then the FULL review (reviewer unsandboxed, allowed 14:20), then DONE; land through the queue (emergency) | 17:30-18:30 (merged); reaches agents' searches only after the re-pin |
| (b) a question's vector from any device (merged `6ed6a5ae`, reviewed) + the query server on the GPU | code live in the repository; **NOT in the pin** (pin-5c401220 still has `_on_cpu`); ACT-QUERY-GPU-2 stopped at its pre-check, nothing changed | interim: ACT-QUERY-CPUS-1 (the query server on CPUs of its own; being written); the move: after the emergency re-pin, in the same window | after the re-pin (tonight, if the owner approves the re-pin P1) |
| Reranker interim rule (no CPU reranker; without a GPU slot it waits up to 20 s or the search goes unranked) | LIVE (ACT-RERANK-WAIT-1, `81b7a739`; module in the reranker venv; backup `.dec1031`) | retired by W2-112's ACT when it lands | done |
| (c) dispatcher v4.6 (whole machine: progress-based health, FAILING on 5xx, admission on CPU/RAM/GPU, lead cap from memory, slots by device, partial-load alerts) | LIVE, committed `b06ee350` (2 review rounds; G1/G2 installed on the owner's word, DEC-1035) | lead cap reads 0 until a day of reranker samples (harmless in the freeze; shorten `reranker_min_span_s` in config if it blocks after) | done |
| (d) no cold rebuild: seeding everywhere (`seed_store.py`, `new_worktree.sh`, merge_queue promotion, throwaway head trees, nightly vectors-only seed) | LIVE, committed `648e5067` (2 review rounds, READY true) | refresh the integration store once by hand (it is at `6ebd7b56`, 11-01); use `tools/new_worktree.sh <W2>` for every new worktree | done (the first seeded landing is W2-122 + W2-123, claimed ~14:15) |
| W2-122 seeded rebuilds (product `gov rebuild --seed`) | DONE: branch `3fc448601e2d`, verified `b9398da0b934` | landing now with W2-123 (`dispatch/land.txt`) | ~15:00 |
| W2-123 bounded embed retry (+ the DEC-1033 merge; caps kept on the automatic start) | DONE: branch `3de9bcf44d91`, verified `2a4455be0785` | landing now with W2-122 | ~15:00 |
| W2-126 vector cache (`DAEO-jpr0`; + P-W2-123-4: retry 5xx/resets) | run 1 (tests only) queued on the ready list | engineer after W2-123 lands | 20:00-21:00 (rebuilds use it at once; searches only after a re-pin) |
| W2-127 the reranker's socket in the sandbox (`DAEO-1vka`, FULL) | filed | right after W2-112 lands | tomorrow |

## What was stopped, and where it resumes (details: `log/emergency-stops-20261102.md`)
- The landing of six (W2-11 c9f99b28b88b, W2-105 fa653609cc93, W2-90b 73c18fea1e1f, W2-81 e78e6af7530d, W2-91
  55b47e075b3b, W2-92 448a835a9dca) + W2-61h ac7dfa1790c7 and W2-104 (run 3 for gitleaks fixtures queued): all in
  `dispatch/land.pending.txt`; relist when the owner lifts the emergency.
- The re-close of W2-05 + W2-96 (DEC-1027 B): rerun as the measured SEEDED close (~15:30, the owner did not object)
  against the 11-02 nightly; it gives the seeded close time for the after figures.
- W2-04's repair round: resume a fresh lead from its checkpoint (accept, scoped run, review 2) after the emergency.
- Parked ready list: `dispatch/ready.parked-by-freeze.txt` (W2-66b, W1-01b, W2-104, W2-55 run 2, W2-81, W2-92, W2-61h,
  W2-91); restore it when the freeze lifts.

## The decisions since DEC-1033 (all in the register)
- DEC-1034 (delegated): W2-112's engineer unsandboxed (DEC-799 reading; extended to its reviewer at 14:20); retrieve.py
  and status/command.py in its paths; P3s.
- DEC-1035 (owner): v4.6's G1 fix without a third review; P-W2-112-T2 (c) now and (a) as W2-127.
- DEC-1036 (delegated): W2-112 KPI 6 (no service on the CPU; the service holds one GPU slot), three unit files, the
  moderator's answer-form ruling, a Wave 3 row for W2-96's runner.
- To record next: the 14:20 extension of DEC-1034 to the reviewer; the owner's re-pin instruction (below).

## The ACTs
- Done: ACT-RERANK-GPU-SLOTS-1, ACT-RERANK-WAIT-1, ACT-W1-01-EXEMPT-1 (`2acc8a31`), ACT-STOP-WAITER-1,
  ACT-GUARD-FIX-3 (`e662684a`).
- Never apply: ACT-RERANK-CPU-1, ACT-QUERY-GPU-1 (both marked superseded).
- Waiting: ACT-QUERY-CPUS-1 (being written, now); ACT-QUERY-GPU-2 (after the re-pin, same window, once no old-pin
  process runs).

## The re-pin question (the owner, 14:15)
- The pinned gov (`~/.local/bin/gov` → `pin-5c401220`, 28 Oct) is what every session's `gov retrieve`, `gov context`
  and hooks run; the emergency's query-side fixes reach agents only through it.
- A research agent is drafting `drafts/P1-REPIN-EMERGENCY.md`: which fixes need the pin; if most, an emergency re-pin
  P1 (from which head and when, the checks, the old pin kept for rollback, running leads and stores, the gains), modelled
  on `packages/ACT-REPIN-1.md` and `ACT-REPIN-2.md`. Then: the package to the owner (ping); the re-pin in a maintenance
  window after W2-122, W2-123, W2-112 land; ACT-QUERY-GPU-2 right after.

## The after figures due (DEC-1033 item 4)
- About 19:30, after (a)-(d) have run for an hour (the vector cache's addendum later): load, memory, the GPU, rebuild
  counts and times per ticket and per batch (`tools/rebuild_counts.py`), a seeded close's time beside today's cold median
  of 30 min (confirm no close runs cold), a question's time.
- Before snapshot: `log/emergency-before-20261102.txt`: load 36, 10.8 GB free, GPU 6.8/16.3 GB with 6 rerankers;
  shared p95 60 s, query p50 15 s and p95 53 s (09:00-13:00); a question measured 8.8-10.1 s at 14:16.
- The owner then lifts the emergency and the freeze; then step (v) of DEC-1032: the assessment and redesign of the
  ticket's path (launch, verify, land, close) for the owner's decision.
