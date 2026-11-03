# The emergency's stops (DEC-1033), 2026-11-02 13:01, each at a safe point
- **The landing of six** (W2-11 c9f99b28b88b, W2-105 fa653609cc93, W2-90b 73c18fea1e1f, W2-81 e78e6af7530d,
  W2-91 55b47e075b3b, W2-92 448a835a9dca): `land.py` and its queue run stopped (17 processes) while testing in the
  queue's warm clone (merged 2f669de8842e onto 01f5d8be36ae at 11:19); w2/integrate unmoved, no merge in the main tree;
  the six stay approved in `merge-queue/approved/` and listed in `dispatch/land.pending.txt` (with W2-61h). Resume:
  relist them after the emergency (one queue run).
- **The re-close of W2-05 and W2-96** (DEC-1027 B): `close_build.py` stopped (4 processes) in its scoped run on its
  clone (selection made 12:59); no close record, no commit. Resume: run it again after the emergency, against the
  nightly baseline of 11-02.
- **W2-04's repair round** (DEC-1025): its lead stopped (14 processes) after the repair commit `de81824b` and the
  test designer's merge `a0c79a6c`; its tree clean. Next: `gov accept`, the scoped run, review 2 (the brief's steps 3
  and on). Resume: a fresh lead in its worktree from its `.gov-runtime/scratch/lead/CHECKPOINT.md`.
- **Left running (the fixes):** W2-122 (seeded rebuilds), W2-123 (the bounded retry; returning run 2 as DONE),
  W2-112 (the shared reranker, started 13:01 past the gate). Parked: the ready list in `dispatch/ready.parked-by-freeze.txt`.

- **2026-11-02 14:31, the landing of W2-122 + W2-123 stopped** (DEC-1033 + DEC-1028 item 6): it had batched the six above (their
  approvals left in the queue since 11:19); stopped in testing in the warm clone (merged 0c84e0119952 onto 1eaca451);
  w2/integrate unmoved. The six approvals are in `merge-queue/parked-by-emergency/` (relist after the emergency).
  Resume: when the owner ends the ACT-QUERY-CPUS-1 hold, write `dispatch/land.txt` with W2-123=3de9bcf44d91 and
  W2-122=3fc448601e2d (still approved) for one run of the two alone.

## The owner's stop of ~17:00 (re-pin from a7182f6c without waiting for the landing)
- **The landing of W2-122 + W2-123:** the queue had already stopped itself at 17:00 (exit 4: W2-54's six CPU-only
  cases red on a7182f6c without the batch, since fix (b); not the batch's). Both stay approved in
  `merge-queue/approved/`; `dispatch/land.txt` absent; nothing landed. Resume: after the repository is green (the
  W2-54 cases revised by a test designer), write `dispatch/land.txt` with W2-123=3de9bcf44d91 and W2-122=3fc448601e2d.
- **W2-112's lead (`w2-112-2b`):** stopped at a safe point ~17:08, session ended. Review round 2 of 2: both repairs
  committed (engineer's §5 fix `f59c9ba5560e` = head of w2/W2-112; designer's F1 test `ed0891667f46` on
  w2/W2-112-tests, not merged); the second review NOT started; tree clean; no workers; its reranker service stopped
  (socket removed). Its checkpoint: `~/gov-os-worktrees/W2-112/.gov-runtime/scratch/lead/CHECKPOINT.md`. Resume (its
  step 4): merge w2/integrate, then the tests branch; §5 worded "a re-pin that carries W2-112's worker, and no tree
  running an older worker"; acceptance + scoped verification through heavy_slot.sh; the second and last review; on a
  pass, the probe record. Leftovers to clear with the owner's approval (rm): `/tmp/gov-os-lead-W2-112` (200 MB), its
  tests worktree.
- **The CTO's agents:** none was running but the pre-switch check of 8c817af2 (finished at 17:0x: ALL CHECKS PASS).

## W2-126, stopped ~18:25 (the owner's order of ~18:20)
- Started by the dispatcher at 17:07 from the ready list after the 17:00 stop (the CTO's slip: the list was not
  emptied; now empty, its lines in `dispatch/ready.parked-by-stop-1821.txt`). Its verification run stopped by the CTO
  at 18:25 (8 processes); the lead stopped at a safe point and exited.
- State: the tests done (designer's `8c3ea9964218`, 17 cases, merged `f90b34c47fdd`; checkpoint record `75c4db0e08f7`);
  no engineer started; tree clean. Scoped run: 4,119 passed, 17 failed (exactly the 17 new W2-126 cases), 7 skipped;
  gov check exit 3 (retrieval-regression red: its base predates fix (b) and refuses the GPU vector; context
  reproducibility timed out at 600 s; core-mutation flags DAEO-a3u2, already on the base).
- Its rebuilds and gov check restarted the query server at 18:14 through the wrapper (on the GPU, capped:
  `~/.ollama/query-autostart.log`); the live server pid 3877550 has that tree as its working folder: never stop it
  with the tree.
- Resume (DEC-1039 item 1, an emergency patch): merge w2/integrate into it first; the engineer builds to the tests'
  README interface (`GOV_VECTOR_CACHE_DIR`, `GOV_VECTOR_CACHE_MAX_BYTES`, `vector_cache` {hits, misses, skipped});
  its checkpoint `~/gov-os-worktrees/W2-126/.gov-runtime/scratch/lead/CHECKPOINT.md`. Leftovers for the owner's rm
  approval: `/tmp/gov-os-lead-W2-126`, `/tmp/gov-launch-independent-test-designer-*`.

## 20:27-20:29, the load at 54 on 20 CPUs (the owner's order of ~20:25: investigate and bring it into its band)
- Cause (sampled 10 times a second, `/proc`): 99 % busy; on average 27 runnable, 17 to 22 of them gitleaks, every one
  with affinity 0-19 and no thread budget in its environment (W2-69's tests build their children's environment from
  scratch), started by two test runs inside heavy slots: the gitleaks engineer's scoped set (live gate, slot 2) and
  the W2-123 + W2-122 landing's scoped run (merge queue warm clone, slot 1). Nothing heavy outside the gate; nothing on
  the CPU that should be on the GPU (both embedders 29/29 on the GPU; 10.4 of 16.3 GB).
- 20:27:38 the engineer's scoped run paused (SIGSTOP, 29 processes), then ended 20:29 (TERM; a run on the unfixed gate
  is not the evidence the fix needs). The engineer returned PACKAGES (built; re-run its scoped set through the
  confined gate).
- 20:29:23 the landing ended at its test phase (TERM to 67 processes from land.py 244805): nothing merged into
  w2/integrate (head a58ba344), both approvals kept in merge-queue/approved/, dispatcher recorded "no outcome".
  Resume: relist `land.txt` W2-123=3de9bcf44d91, W2-122=3fc448601e2d once the confined gate is live.
- Staggered: W2-126's engineer and both W2-42a agents told to start no heavy run until the confined gate is live.
  Kept: W2-112's lead (slot 3), the gitleaks and load-balancer reviews.
- After: 20:31, 7 % busy (1.3 cores), 1-minute load 18.9 and falling.

## 2026-11-02 23:09 — EVERYTHING STOPPED (the owner's order, DEC-1051): resume after the refactoring and the re-pins, from here
- **The W2-123 + W2-122 landing** (land.py pid 2851683, since 22:25): stopped in its attribution step (re-running reds
  alone against the 11-02 nightly, warm clone "alt" just reused at 23:07:13; candidate merge 35a851b36c6d of W2-123
  3de9bcf44d91 and W2-122 3fc448601e2d onto b60ff1120424). Nothing landed; w2/integrate unmoved (8562ae79). Both
  approvals parked (`merge-queue/parked-by-emergency/`, with the six earlier). Resume: `queue_park.py unpark`, then
  `dispatch/land.txt` with both (and W2-126 once its conflict is resolved).
- **W2-126** (vector cache): ejected from the 22:25 batch on a conflict (with W2-123 in semantic.py); branch
  w2/W2-126 at 2785b2e47432, clean, review READY, gov accept 17/17. Resume: after W2-123 lands, merge w2/integrate,
  resolve the conflict, KPI 7 (DEC-1042 (4)), gov accept + the W2-54 cache cases, land.
- **W2-112's lead** (claude -p pid 2781778, run r3-land, started 22:17:55 on the owner's order): stopped in its
  verification (the scoped serial phase: W1-02/W1-05/W1-20 cases in heavy slot 2); its designer's retirement-act test
  and the engineer's §5 rewrite were done (interim results 22:23 and 22:32); branch w2/W2-112 at d5216599e6fd, clean.
  Its shared reranker service (pid 3361765) stopped. Resume: a lead from its checkpoint for the verification step
  only, then land.
- **The CTO's agents (all stopped):** E1 (queue Q-1 + G-1; owner-stopped earlier: EMG-queue dirty, 3 uncommitted
  files; tools/land.candidate.py empty); E2 (T-4: emg/select 194e3289 clean, its scoped run killed unread); E3
  (rules 1/5 + rm: drafts/act-guard-fix-4/ partial, the replay script unwritten); the DEC-1045 product switch
  (emg/noscan ddcec657 clean, waiting on its re-runs); the LB fix (EMG-lb2, 3 uncommitted files); earlier stops:
  W2-42a (w2/W2-42a ce03bb8b clean), the W1-19 helper (emg/w1-19-helper a0d1d3a0). Reports done: R1, R2, R3, P1.
- **Kept on:** the dispatcher (cron, its ready list empty, no land.txt; GPU alerts work), the slot watcher
  (tools/rerank_service_slot_hold.py --watch, pid 3518237; holds nothing once no service runs), the embedders.
- After: heavy slots free; GPU 5979 of 16303 MiB; load 10.1 and falling.
- **2026-11-02 23:39:43: the CAPACITY-1 benchmark stopped** (`tools/bench_loop.sh`, pid 1188718, running since 2026-10-31 18:15: `tests/unit` with 4 workers every 30 min on a frozen clone, results in `log/capacity/bench.jsonl`). Missed in the 23:08 stop (asleep between runs); its 23:30:41 run was the CPU spike the owner saw (52 s; load 0.3 to 4.6). Resume: `setsid -f bash tools/bench_loop.sh` from this folder, on the owner's word only.
