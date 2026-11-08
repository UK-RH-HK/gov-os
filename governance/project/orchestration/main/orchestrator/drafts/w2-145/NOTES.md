# W2-145 draft: notes for the CTO

Draft only: nothing is filed under `.tickets/`, and nothing is committed. Before `tk` files it, replace the placeholder id
`DAEO-xxxx` and the `created` time. The frontmatter validates against `ticket.schema.json` with `common.schema.json`
(no errors). It has 7 success lines and 5 failure lines, and each success line carries a `[DEC-…]` bracket and a
`Verify:` clause.

## What the product does today (read from the code at `e66f2a696`)

- `src/gov/retrieval/rerank.py`, `default_reranker()`: the search calls `_ask` (the service). On any exception it calls
  `_started()`, which starts `rerank_worker.py` as a private process with `lru_cache`, and logs
  `FALLBACK … private|unavailable: …`. `last_outcome().by` can be `private`.
- `src/gov/retrieval/rerank_worker.py`, `main()`: the private worker. It takes a GPU slot (`take_slot`) and refuses
  the CPU unless `GOV_RERANK_ALLOW_CPU=1`, a test hatch. The service imports `take_slot`, `load`, `scores` and
  `device_of` from this file, so the file has to stay and only its `main` changes.
- `src/gov/retrieval/rerank_service.py`: takes one slot (`take_slot(allow_cpu=False)`), so one private can run beside
  it (DEC-1036 (2)).
- `.gov-runtime/scratch/orchestrator/tools/rerank_service_slot_hold.py --watch` is live (pid 8416 at the time of
  reading). It holds the other slots whenever a process named `rerank_service.py` runs, and lets them go 60 s after the
  last one ends. It loses the race to a private that took a slot first, and it is not product code. Other files depend
  on it: `RESTART-CLASSES.md` (lines 98 to 109), `DECISIONS-IN-FORCE.md:103`, and `dispatcher.py:301`, whose
  `slot_holders` counts it as holding a slot with no GPU memory. The dispatcher counts reranker slots by pid, so a
  service that holds two slots still counts as one reranker. No dispatcher change is needed.

## The design choices in the draft (for the CTO to confirm)

1. **"Unreachable" means never a private.** The CTO's brief says so, and DEC-1046 (1) ("no private reranker on the
   GPU while the shared service runs") implies it: a client cannot tell "down" from "unreachable" (EPERM, a timeout,
   a full queue), so any private fallback can end up beside a running service. With the watcher holding the slots,
   most fallbacks already go unranked today, after a wait of up to 20 s. S4 removes that wait.
2. **S3 moves the watcher's job into the service**: the service holds every slot for its life. This is a step beyond
   the minimum, and I chose it because it makes the product fail closed by construction against older trees' privates
   (and against any worker under the `.pth`) while a service runs, and lets the watcher be retired after the re-pin.
   - The narrower alternative: S3 dropped, the watcher kept indefinitely with its role stated in S5 (b).
   - What the alternative saves: about 40 lines and 4 tests.
   - What it costs: a CTO tool stays a standing dependency.
   - Recommendation: keep S3. Confidence: medium-high.
3. **The `rerank.log` kind stays `FALLBACK`** (S4), so `gov status` and old logs read alike. That keeps
   `src/gov/status/command.py` and its test out of the paths. If the CTO prefers a renamed kind (`UNRANKED`), add
   `src/gov/status/command.py` and `tests/unit/status/test_status.py`.
4. **`rerank_worker.py` run as a program ends at once, named** (S2). The `.pth` interim module is not touched
   (DEC-1048 (1)). Its unit test `test_gov_reranker_gpu_slot.py` uses stand-in workers for most cases, and only its two
   "real caller" cases go through `rerank._started`.
5. **`depends_on: []` and `needs:` = the three `rerank*.py` files**, as in W2-137. W2-112, W2-137 and W2-32 are all
   `in_progress` and hold these paths, but none has code in flight; W2-137 waits only for its S5 GPU window, on a
   clone. If `gov plan` orders by `needs:` against open holders, the CTO's ordering note has to settle it, as it did
   for W2-137.

## Existing tests that assume the private fallback

### Acceptance (revised by an independent test designer, `Rewrite-Reason: DEC-1048 (5)`, S6)

- `tests/acceptance/W2-112/test_w2_112_fallback.py`: the whole file's premise (KPI 4). The cases:
  - `test_when_the_service_cannot_start_the_search_falls_back_to_a_private_reranker`
  - `test_when_the_services_model_cannot_load_the_search_still_gets_a_private_rerankers_answer`
  - `test_a_service_that_does_not_answer_is_passed_over`
  - `test_a_service_that_answers_with_an_error_is_passed_over`
  - `test_a_service_whose_model_fails_answers_with_an_error_and_the_search_falls_back`
  - `test_a_service_killed_mid_run_leaves_every_search_answered`
  - `test_where_no_private_reranker_can_start_either_the_order_given_is_kept_unscored`
  - `test_a_session_that_cannot_make_a_unix_socket_falls_back_quickly_without_an_error`
  - `test_each_fallback_is_logged_under_the_users_cache_folder`
- `tests/acceptance/W2-112/test_w2_112_slots.py`: the file is all KPI 7. The cases:
  - `test_with_a_gpu_slot_free_the_fallback_private_reranker_loads_on_the_gpu_holding_a_slot`
  - `test_with_both_gpu_slots_held_a_fallback_waits_then_goes_on_unranked_with_no_model_on_the_cpu` (its timing)
  - `test_a_fallback_waits_for_a_gpu_slot_and_takes_the_one_that_frees`
  - `test_a_fallback_never_runs_a_reranker_on_the_cpu`
  - `test_the_service_holds_one_of_the_two_gpu_slots`: now it holds all of them (S3)
  - `test_with_the_service_up_and_the_other_slot_held_a_fallback_waits_then_goes_on_unranked`
  - `test_with_both_slots_held_before_any_service_the_search_goes_on_unranked_with_no_model_loaded`
- `tests/acceptance/W2-112/test_w2_112_gpu.py`:
  - `test_below_its_share_or_without_a_gpu_the_service_does_not_start_and_nothing_loads_on_the_cpu`, which accepts a
    private's answer
  - `test_below_its_share_the_fallback_and_its_reason_are_logged_under_the_users_cache_folder`
- `tests/acceptance/W2-112/test_w2_112_bundle.py`:
  - `test_the_bundle_names_a_private_reranker_and_its_gpu_when_the_service_is_down`
  - `test_gov_status_counts_the_searches_that_fell_back`, which expects `reranked` true from a private
  - `test_below_its_share_the_bundle_never_names_the_cpu_and_gives_its_reason`
  - `test_with_both_gpu_slots_held_the_bundle_is_unranked_named_with_its_reason` (its wait)
- `tests/acceptance/W2-112/test_w2_112_concurrency.py`: `test_a_request_past_its_time_limit_does_not_hold_the_search`
  (it expects a private to score).
- Helpers: `tests/acceptance/W2-112/w2_112_support.py` (`FALLBACK_S`, which includes a private's start;
  `check_scored_or_unranked`; `SETTLE_S`) and `w2_112_session.py`.
- `tests/acceptance/W2-32/test_w2_32_s4_reranker_dies.py`: `test_the_default_reranker_that_dies_after_loading_is_reported_not_raised`
  and `test_retrieve_with_a_dying_reranker_cites_its_evidence_and_reports_the_rerank_unavailable[None]`. Their fake
  `rerank_worker.py` is never started any more, so they would pass without testing anything. They need a new premise:
  a service that dies after accepting.
- **Check only, likely unchanged:** `W2-112/test_w2_112_answers.py` and `test_w2_112_memory_release.py`. They use an
  in-process reference reranker, which is a reference, not a fallback. Also `W1-19/test_w1_19_real_models.py::test_the_default_reranker_is_a_process_of_its_own_started_from_the_reranker_environment`,
  which needs the real model and, after the change, sees the service as that process.
- **Not affected:** `W2-112/test_w2_112_retirement_act.py` (the `.pth` stays) and `W2-137/w2_137_support.py` (a
  comment only).

### Unit (revised by the engineer, all in `allowed_paths`)

- `tests/unit/retrieval/test_w2_112_shared_reranker.py`: about 12 cases, at lines 217, 260, 269, 281, 369, 381, 391,
  559, 570, 579, 589, 612, 649 and 659. Among them:
  - `_ties_keep_the_given_order_and_the_answers_match_a_private_reranker`, which uses `rerank._started` as its
    reference
  - `_below_its_gpu_share…falls_back`
  - `_with_the_gpu_hidden…` (`GOV_RERANK_ALLOW_CPU`)
  - `_killed_mid_request…private`
  - `_a_service_that_cannot_start_leaves_the_search_to_the_private_reranker`
  - `_a_session_that_cannot_make_a_socket_falls_back_at_once`
  - `_the_private_worker_holds_a_slot_or_waits_then_ends_named`
- `tests/unit/semantic/test_rerank_process.py`: its 3 private-process cases (the fixture clears `_started`).
- `tests/unit/retrieval/test_w2_32_rerank_fusion.py::test_a_private_reranker_that_dies_is_reported_and_started_again_next_time`.
- `tests/unit/retrieval/test_w2_32_whole_chunk.py::test_the_shared_service_and_a_private_reranker_are_each_asked_within_both_bounds`.
- `tests/unit/orchestration/test_gov_reranker_gpu_slot.py`: `test_the_search_reranks_on_a_free_slot` and
  `test_the_search_goes_on_unranked_when_no_slot_frees`, through the `caller` fixture and `rerank._started`.

## Risk

- **Quality when the service is down.** Every such search is now unranked, where today one might be reranked by a
  private on a free slot. This is named in the bundle and counted by `gov status`, but a measurement run on a tree with
  this ticket must count unranked searches as faults. The 80 is not affected: it runs at `c00d525f`, before this
  ticket.
- **Old trees.** Window 4's commit and the pins keep the private fallback until the re-pin, so the watcher and the
  `.pth` must stay until then (S5). Retiring the watcher early reopens DEC-1043 (2)'s overrun.
- **A service that cannot start** (an older private holds both slots, or the GPU is below its share) leaves every
  search unranked until it can. This is fail-closed and named, and it is the same outcome as today with the watcher.
- **S3's slot polling** adds a thread to the service. Its own tests must show it never delays an answer and that its
  locks go with the process on SIGTERM or a crash. flock locks are released by the kernel when the process ends.
- **A large revision round.** About 25 acceptance cases across 6 W2-112 files plus 2 W2-32 cases, and they land
  together with the engineer's change (G-1). The W2-112 socket cases pass only outside the sandbox, as W2-137 found.

## Estimate

- **Code:** product about 80 lines. That is `rerank.py` about −40/+15, `rerank_worker.py` `main` about −15/+10 and
  `rerank_service.py` S3 about +40. New and revised unit tests add about 150 lines, so `est_loc` is 230.
- **Time:**
  - Test designer: about half a day (about 15 new cases plus about 27 revised).
  - Engineer: about half a day.
  - Review: about half a day, one round expected.
  - S7: the CTO, by observation after the re-pin, with no GPU window.
- **Calendar:** about a day, all on the CPU, merged before the lift's re-pin and not during the 80's run.
