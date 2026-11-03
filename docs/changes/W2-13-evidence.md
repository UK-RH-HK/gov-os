# W2-13 evidence: the ranked lexical route (BM25, SQLite FTS5) and RETR-X-02's stated gap (DAEO-zqvn; DEC-995, DEC-1055)

The ticket as built at `bdc4b7956a48` (lead resume 1, PACKAGES: waiting for W2-92; code head `febe5f6403d5`),
brought up to `w2/integrate` at `5522a603dead` (W2-92, W2-91, W2-61h merged; the CTO's P2 adding
`src/gov/retrieval/retrieve.py` to the ticket's paths) by the merge `b91e78b17cdb` (D-4b, DEC-1055). The merge had no
conflict; `src/gov/retrieval/lexical.py` auto-merged with DEC-1045's change on integrate (the secrets file among the
filter's judges). The one change W2-13 waited for is `3c0320080829`: `retrieve()` fuses each route's
`answer.get("ranked", answer["hits"])`, so the lexical route hands the fusion its ranked list beside the semantic one
(S2). W2-92's record and code routes, W2-112's `rerank` field and W2-126's cache are unchanged.

**Verified on:** the merge commit `b91e78b17cdb`, with the one line at `3c0320080829` (the worktree's store rebuilt
there with `--seed` under the D-4b lock, 2026-11-03: all three stores recreated, 57 s; seed: none, no warm base
configured) and the two builder tests fixed for the merge at `06e5ae70a4a7` (no code change; `gov accept` alone:
56 of 56, 6 of 6 lines). After the review: `3d1d1b34` (R4, a fused hit whose chunk the lexical index does not
hold is skipped), `ea486253` (R3's budget cut) and its revert `80cdd7ff` (DEC-419 DP-3, below); `gov accept` alone
on `80cdd7ff`: 56 of 56, 6 of 6 lines (load near 12); unit `tests/unit/retrieval` and `tests/unit/retrieve`: 300 passed, 1 skipped.

This record holds scores only: ids, counts and figures. It quotes no question's text and no gold answer. The
acceptance tests were run (pass or fail), never read.

## The KPI lines and how each is verified

`gov accept` = `PYTHONPATH=<tree>/src bash heavy_slot.sh python3 -m gov.cli.main accept W2-13 --json`, in the
worktree. Unit = `tests/unit/retrieval/test_w2_13_ranked.py`, `test_w2_13_id_boost.py`, `test_w2_13_rerank_work.py`,
`tests/unit/retrieve/test_w2_13_stated_gap.py` (in the scoped run, below).

| KPI | How it is verified | Command | Result | Verified on |
|---|---|---|---|---|
| S1 the ranked lexical route: FTS5, BM25 with id, title and body weights; an exact id first | `gov accept` line success-1; unit `test_w2_13_ranked.py`, `test_w2_13_id_boost.py` | `gov accept`; unit | pass, 13 of 13; unit pass | `06e5ae70a4a7` |
| S2 the fusion receives the ranked lexical list; the dev queryset's lexical-only hit@5 recorded | `gov accept` line success-2 (the `gov retrieve` case that waited for W2-92 now passes); the hit@5 below; the fusion's contribution: measure: D-4b measure 1 | `gov accept`; `lexical_hit5.py` (below); measure: D-4b measure 1 | pass, 3 of 3; hit@5 87.0 at the head (45 of 52), 0.0 at the base (0 of 52); the fusion's contribution: D-4b measure 1 | `06e5ae70a4a7` (`gov accept`); `3c0320080829` (hit@5) |
| S3 "unavailable" instead of raising; latency within the retrieve budget on the dev tiers | `gov accept` line success-3; the latency file alone; unit `test_w2_13_rerank_work.py` | `gov accept`; `pytest tests/acceptance/W2-13/test_w2_13_latency.py` through `heavy_slot.sh` | pass, 25 of 25 alone (load 1.6 at its start); under load (the scoped run beside it, load near 20): 24 of 25, the one red the load-sensitive latency case; the latency file alone: 2 of 2 (load 1.1 at its start; 261 s, the real-model case's call 14.2 s after a 189 s setup, the lexical case 57.7 s) | `06e5ae70a4a7` (`gov accept`); `3c0320080829` (latency alone) |
| S4 an id that exists nowhere: the stated gap | `gov accept` line success-4; unit `tests/unit/retrieve/test_w2_13_stated_gap.py` | `gov accept`; unit | pass, 8 of 8; unit pass (one case's double fixed for the merge, below) | `06e5ae70a4a7` |
| F1 RETR-A-04's bundle unchanged | `gov accept` line failure-1 | `gov accept` | pass, 3 of 3 | `06e5ae70a4a7` |
| F2 the secrets filter on the FTS5 table: a planted canary never indexed | `gov accept` line failure-2, after DEC-1045's change to `lexical.py` on integrate (merged without conflict) | `gov accept` | pass, 4 of 4 (both runs) | `06e5ae70a4a7` |

The two builder tests changed for the merge (`06e5ae70a4a7`), each the smallest fix inside the ticket's paths:

- `tests/unit/retrieve/test_w2_13_stated_gap.py`, the no-database case: since W2-92, `retrieve()` keeps a record
  graph that cannot be read to the record and closure routes, so the semantic route is asked next; the case's double
  answered from a store that is no database, and the gathering met a chunk the lexical index did not hold
  (`KeyError`). The case now asks the real semantic route, which reads the store before any endpoint and fails as the
  real one does: `gov retrieve` exits 1 with `STORE_UNREADABLE` and no traceback, as before (also checked with the
  real CLI and no doubles on a tree whose store is no database).
- `tests/unit/retrieval/test_w2_92_routes.py`, the missing or unreadable record store case: the evidence's routes
  are now `["lexical", "code"]`, not `["code"]`: the ranked lexical route holds the question's word beside the code
  route's span (S2, the change this ticket makes).

## S2: the dev queryset's lexical-only hit@5

The lexical route alone, asked each of the dev queryset's 52 questions (`~/gov-os-workbench/synthetic/dev-queryset.yaml`,
tiers `a-dev` and `b-dev`, each cloned and adopted as `gov.retrieval.retrieve_check` does, the lexical index refreshed
only). hit@5: a `must_cite` path among the first five distinct paths of the list the route hands the fusion
(`ranked` where the code has one, else `hits`); the figure is the mean over the ten classes, as `retrieve_check`
computes it. The script is the lead's `.gov-runtime/scratch/lead/lexical_hit5.py` (in the worktree), run unchanged.

```
PYTHONPATH=<code> bash .gov-runtime/scratch/orchestrator/tools/heavy_slot.sh \
    python3 lexical_hit5.py ~/gov-os-worktrees/W2-13
```

| | Code (`PYTHONPATH`) | Questions hit | lexical-only hit@5 | Exact route (`hits`) only | Raised | p95 per question |
|---|---|---|---|---|---|---|
| base | `w2/integrate` at `5522a603dead` (`git archive 5522a603 src`) | 0 of 52 | 0.0 | 0.0 | 0 | 0.002 s |
| head | the worktree at `3c0320080829` | 45 of 52 | 87.0 | 0.0 | 0 | 0.003 s |

Head per class: decisions 100.0, failed-approaches 100.0, tests 80.0, stale-evidence 83.3, current-vs-superseded
100.0, deletable 60.0, callers-impact 100.0, where-defined 83.3, why 80.0, history 83.3. The lead's figure before the
merge was 85.0 (44 of 52, at `febe5f6403d5`). The base has no ranked list: its exact route hits no dev question in its
first five paths, as the head's `hits` alone do not either.

The fusion's contribution (lexical, semantic and the reranker each contributing, S2's other half) is not measured
here: measure: D-4b measure 1.

## The scoped run

`PYTHONPATH=<tree>/src python3 .gov-runtime/scratch/orchestrator/tools/select_tests.py <tree> W2-13 DAEO-zqvn`
(scope `scoped`, base `5522a603dead`, 90 targets), then `pytest tests <its pytest_options> -n auto -o
tmp_path_retention_policy=failed -p no:cacheprovider` through `heavy_slot.sh`, at `3c0320080829`: 5085 passed,
32 failed, 8 skipped, 20 errors in 1087 s, under load (`gov accept` beside it; load near 20).

- **Three reds were the merge's,** in two builder tests: fixed at `06e5ae70a4a7` (above); both files then pass,
  51 of 51.
- **The other 29 failed and 20 errors: 13 are W2-13's (corrected after the review, R2).** A first control re-ran
  their 18 files with `PYTHONPATH` swapped to `git archive` copies of the base's code and found the same 46. That
  control was invalid for W2-92, W2-87, W1-21, W1-19 and W1-28: their support modules start their children with
  their own tree's `src` (DEC-732), so all three runs ran the head's code there. The S2 hit@5 base figure above is
  not affected: `lexical_hit5.py` imports `gov` in its own process, with no child.
- **The control, redone against a real checkout:** the five suites (`tests/acceptance/W2-92`, `W2-87`, `W1-21`,
  `W1-19`, `W1-28`, `-n auto`, through `heavy_slot.sh`), run one after the other, in the worktree with its own
  `src`, and in a `git clone` of `w2/integrate` at `7524fa04` (its `src/` and these suites the same as at
  `5522a603dead`) with that clone's `src`:

  | tree | result | reds |
  |---|---|---|
  | `w2/integrate` `7524fa04` | 4 failed, 369 passed | integrate's own: W1-19 `embedding_policy`, `semantic_index`, the reranker-process case; W1-28's whole-tree copy case |
  | W2-13 head `80cdd7ff` | 17 failed, 356 passed | the same 4, plus the 13 below |

- **The 13 are W2-13's, by design:** S2 changes the lexical list the fusion takes. 11 pin the old lexical
  behaviour, and the test designer re-pins them next (MR-3):
  - W2-92 `test_w2_92_unchanged.py`: `test_u1_a_question_naming_no_record_or_symbol_gets_todays_bundle` `[plain]`,
    `[batched]`, `[unknown id]`, `[ticket]`; `test_u2_todays_bundle_is_the_plain_fused_order_of_todays_routes`.
  - W2-92 `test_w2_92_fail_closed.py`: `test_f4_a_question_naming_no_symbol_does_not_report_the_code_route_ok_or_fail`.
  - W2-87 `test_w2_87_authority.py`: `test_2b_a_lower_chunk_better_by_more_than_the_lift_keeps_its_place`,
    `test_3b_without_the_block_the_order_is_the_plain_fused_one`.
  - W1-21 `test_w1_21_family_check.py`: `test_the_check_is_red_when_the_dev_tiers_fail_the_baselines` (its
    premise, dev tiers below the 80 baseline, no longer holds: the ranked route lifts them over it).
  - W1-19 `test_w1_19_unavailable.py`: `test_a_reranker_that_cannot_be_loaded_leaves_the_fused_list_and_says_so`,
    `test_with_the_environment_and_no_snapshot_nothing_is_reranked_nothing_is_fetched_and_nothing_raises` (their
    reference order is built from `hits`, not `ranked`).

  The other 2 are the budget gap (review R3): W2-92
  `test_u4_a_batched_answer_with_a_new_route_continues_to_its_end_within_the_budget` and W1-21 `test_w1_21_expansion.py`
  `test_a_parent_that_does_not_fit_the_bundle_budget_is_not_expanded`. They are **not fixed on this head.** A cut of
  the gathered chunks to the budget (`ea486253`) made both pass, but it turned 11 W1-21 cases red
  (`test_w1_21_paging.py`: 8; `test_w1_21_merge.py`: 3). Those cases hold DEC-419 DP-3, W1-21's approved spec: "the
  bundle budget ... bounds parent expansion only; a child hit is never dropped for it". The cut was reverted
  (`80cdd7ff`), and the choice went to the CTO as a decision package (DEC-105).
- **Not re-run against a real checkout:** W2-108's 20 errors (its support takes `PYTHONPATH`, so the first control
  is valid for it: integrate's own), W2-55's 3 (red on clean `w2/integrate` in the review's run: integrate's own),
  W2-59's 4, W1-06's 1 and W2-54's 1 (attribution unverified).
