# W2-137 acceptance tests: the shared reranker's request cap raised

Ticket DAEO-5emz (W2-137), profile STANDARD (DEC-1090 (2), PAT-1 G1). Written by the independent test designer (MR-3)
from the ticket's KPI lines S1 to S4, before any implementation, reading only the integrated code (`w2/integrate`
`f50fb0025995`, DEC-963). S5 is the CTO's live measure in a GPU window, not a test here.

## How they run

    env HOME=<an empty folder> PYTHONUSERBASE=$HOME_REAL/.local PYTHONPATH=<worktree>/src TMPDIR=<scratch> \
      python3 -m pytest tests/acceptance/W2-137 -q -p no:cacheprovider -o tmp_path_retention_policy=failed

Under 1 s, in process. The tests use the tree `PYTHONPATH` names; without one, the worktree's own `src`.

- **No model, no GPU, no socket, no process.** The encoder is a stand-in (`w2_137_support.Encoder`); the service is
  driven in this process through `rerank_service.answer` and `rerank_service.serve` with W2-112's seam (a stand-in
  listener, connection and `torch` in `sys.modules`); the client's side of a refusal through `rerank._ask` with
  `rerank._connect` replaced by a stand-in connection.
- **The oracle** (`w2_137_support`): a request's padded size is its count times its longest pair,
  `len(query) + len(text)` (the ticket's rule and `rerank.py`'s docstring); how many texts of one length fit a request
  is `24_000 // (len(query) + length)`. The question is 48 characters. The pool's depth is read from this repository's
  `governance/project/retrieval.yaml` (`pool.rerank_depth`, 40).
- **The bounds assumed.** S1: `MAX_REQUEST_CHARS` stays 24,000 (the ticket: "the bound ... stays"); the count cap
  `MAX_REQUEST_TEXTS` is at least the pool's 40. No value of the new cap is fixed: the cases pass at 40, 64 or any
  cap of at least 40. S2: the service's bound `MAX_TEXTS` is at least the client's cap (and so at least 40), whatever
  either number is.
- **S3's stand-in** scores each pair from its digest (steps of 0.001, the 40 scores of each pool apart by more than
  1e-3, checked as a premise) and moves each score by under 1e-5 with the batch it is padded into, as a padded model
  does. So the two batchings give different scores, and the cases check the ticket's tolerance, not equality.

## KPI lines, tests, and the outcome on `w2/integrate` `f50fb0025995`

Run in the launch sandbox through the heavy slot, with `-m "not local_only" -k "not real and not green_here and not
time_limit"` (it leaves none of these out): **37 tests, 8 failed, 29 passed** (0.21 s). Every red is S1's and fails
on the count cap of 16 splitting a pool that fits the padded bound; none fails on a premise.

| KPI line | Test (node id) | On integrate | Why |
|---|---|---|---|
| S1 | `test_w2_137_s1_requests.py::test_s1_premise_the_pool_reranks_forty_and_the_padded_bound_stays` | green (premise) | `rerank_depth` is 40 and `MAX_REQUEST_CHARS` 24,000 |
| S1 | `test_w2_137_s1_requests.py::test_s1_the_count_cap_carries_the_pool_s_depth` | red | `MAX_REQUEST_TEXTS` is 16, under the pool's 40 |
| S1 | `test_w2_137_s1_requests.py::test_s1_the_pool_s_short_texts_go_in_one_request[one-char]` | red | 40 texts of 1 character (padded 1,960) go in [16, 16, 8] |
| S1 | `test_w2_137_s1_requests.py::test_s1_the_pool_s_short_texts_go_in_one_request[100-chars]` | red | 40 texts of 100 (padded 5,920) go in [16, 16, 8] |
| S1 | `test_w2_137_s1_requests.py::test_s1_the_pool_s_short_texts_go_in_one_request[at-the-padded-bound]` | red | 40 texts of 552 (padded exactly 24,000) go in [16, 16, 8] |
| S1 | `test_w2_137_s1_requests.py::test_s1_rerank_asks_the_reranker_once_for_the_pool` | red | `rerank.rerank` on 40 candidates of 120 asks the reranker 3 times, not once; the order is the scores' |
| S1 | `test_w2_137_s1_requests.py::test_s1_long_texts_split_by_the_padded_bound_never_by_count_alone[1000-chars-22-a-request]` | red | 22 texts of 1,000 fit a request, so 2 requests [22, 18]; the count cap gives 3 [16, 16, 8] |
| S1 | `test_w2_137_s1_requests.py::test_s1_long_texts_split_by_the_padded_bound_never_by_count_alone[2000-chars-11-a-request]` | green (guard) | the padded bound splits 40 texts of 2,000 into 11, 11, 11, 7 |
| S1 | `test_w2_137_s1_requests.py::test_s1_long_texts_split_by_the_padded_bound_never_by_count_alone[5000-chars-4-a-request]` | green (guard) | 10 requests of 4 |
| S1 | `test_w2_137_s1_requests.py::test_s1_long_texts_split_by_the_padded_bound_never_by_count_alone[12000-chars-1-a-request]` | green (guard) | 40 requests of 1 |
| S1 | `test_w2_137_s1_requests.py::test_s1_a_long_text_goes_alone_and_the_short_ones_together` | red | one 23,000-character text with 39 of 200: [1, 7, 16, 16], not the long one alone and 39 together |
| S1 | `test_w2_137_s1_requests.py::test_s1_one_text_over_the_bound_alone_is_read_up_to_it` | green (guard) | one text of 30,000 is sent read up to 23,952 (padded 24,000) |
| S1 | `test_w2_137_s1_requests.py::test_s1_one_text_over_the_bound_among_the_pool_is_read_up_to_it` | red | the over-long text alone and read up to the bound, but the 39 short ones go in [16, 16, 7] |
| S1 | `test_w2_137_s1_requests.py::test_s1_guard_every_request_keeps_both_bounds_on_mixed_pools[1]` | green (guard) | pools of 1 to 200 mixed lengths (1 to 26,000): each text once, at most the cap, padded at most 24,000 |
| S1 | `test_w2_137_s1_requests.py::test_s1_guard_every_request_keeps_both_bounds_on_mixed_pools[2]` | green (guard) | as above, another seed |
| S1 | `test_w2_137_s1_requests.py::test_s1_guard_every_request_keeps_both_bounds_on_mixed_pools[3]` | green (guard) | as above |
| S1 | `test_w2_137_s1_requests.py::test_s1_guard_every_request_keeps_both_bounds_on_mixed_pools[4]` | green (guard) | as above |
| S1 | `test_w2_137_s1_requests.py::test_s1_guard_every_request_keeps_both_bounds_on_mixed_pools[5]` | green (guard) | as above |
| S2 | `test_w2_137_s2_service_bound.py::test_s2_the_service_bound_is_at_least_the_client_cap` | green (guard) | `MAX_TEXTS` 512 is at least the cap (16) and the pool's 40; fails a fix that raises the cap past the service |
| S2 | `test_w2_137_s2_service_bound.py::test_s2_the_service_answers_a_request_at_the_cap_whole[the-client-cap]` | green (guard) | `answer` scores every text of a request of the cap, in one batch |
| S2 | `test_w2_137_s2_service_bound.py::test_s2_the_service_answers_a_request_at_the_cap_whole[the-pool-depth]` | green (guard) | the same for 40 |
| S2 | `test_w2_137_s2_service_bound.py::test_s2_the_service_answers_a_request_at_the_cap_whole[the-service-bound]` | green (guard) | the same for `MAX_TEXTS` itself |
| S2 | `test_w2_137_s2_service_bound.py::test_s2_a_request_over_the_service_bound_is_refused_with_a_named_reason` | green (guard) | `MAX_TEXTS + 1`: an error naming the bound, no scores, nothing reaches the encoder |
| S2 | `test_w2_137_s2_service_bound.py::test_s2_every_request_a_search_makes_is_within_the_service_bound` | green (guard) | `requests()` on 40, 513 and 120 texts: no request above `MAX_TEXTS` |
| S2 | `test_w2_137_s2_service_bound.py::test_s2_the_client_names_the_service_s_refusal` | green (guard) | `_ask` raises "refused the request" carrying the service's reason; the request was sent whole |
| S2 | `test_w2_137_s2_service_bound.py::test_s2_an_answer_short_of_scores_is_an_error_never_a_truncation` | green (guard) | an answer one score short raises in `_ask` |
| S2 | `test_w2_137_s2_service_bound.py::test_s2_a_reranker_that_drops_texts_leaves_the_pool_unscored_and_named` | green (guard) | `rerank.rerank` keeps the order given, no scores, `unavailable` naming the count |
| S3 | `test_w2_137_s3_same_scores.py::test_s3_the_order_and_scores_under_the_cap_equal_those_under_16[short]` | green (guard) | `rerank.rerank` through the service's `answer` under the module's cap and under 16: same order, scores within 1e-3. On integrate both are 16; after the fix, 1 request against 3 |
| S3 | `test_w2_137_s3_same_scores.py::test_s3_the_order_and_scores_under_the_cap_equal_those_under_16[at-the-padded-bound]` | green (guard) | as above, 40 texts of 552 |
| S3 | `test_w2_137_s3_same_scores.py::test_s3_the_order_and_scores_under_the_cap_equal_those_under_16[mixed]` | green (guard) | as above, four long texts (4,000 to 26,000) among 36 of 300, split by the padded bound under either cap |
| S3 | `test_w2_137_s3_same_scores.py::test_s3_the_service_scores_the_pool_in_one_request_as_in_requests_of_16[short]` | green (guard) | the service asked for the 40 in one request and in requests of 16: same order, within 1e-3 (meaningful on integrate too) |
| S3 | `test_w2_137_s3_same_scores.py::test_s3_the_service_scores_the_pool_in_one_request_as_in_requests_of_16[at-the-padded-bound]` | green (guard) | as above, 40 texts of 552 |
| S4 | `test_w2_137_s4_memory.py::test_s4_a_request_at_the_new_cap_still_releases_and_logs_memory[the-client-cap]` | green (guard) | `serve` with a request of the cap: predict, the answer sent, closed, one release; one `MEMORY` line with allocated and reserved MiB |
| S4 | `test_w2_137_s4_memory.py::test_s4_a_request_at_the_new_cap_still_releases_and_logs_memory[the-pool-depth]` | green (guard) | the same for 40 |
| S4 | `test_w2_137_s4_memory.py::test_s4_a_request_at_the_new_cap_still_releases_and_logs_memory[the-cap-at-the-padded-bound]` | green (guard) | the same for the cap's texts, padded to the bound |
| S4 | `test_w2_137_s4_memory.py::test_s4_a_request_at_the_new_cap_still_releases_and_logs_memory[over-the-service-bound]` | green (guard) | refused, still released once after the error is sent |
| S4 | `test_w2_137_s4_memory.py::test_s4_a_search_s_requests_each_release_once` | green (guard) | a pool of 40 with one long text, served request by request: one release and one `MEMORY` line each |

**A check of the tests themselves** (a scratch copy of `src`, never committed): `MAX_REQUEST_TEXTS = 64` and nothing
else passes all 37. The same copy with `rerank_service.MAX_TEXTS = 32` and `MAX_REQUEST_CHARS = 10 ** 9` fails 21:
S1's premise, long-text and over-the-bound cases, S2's bound and answer cases, and S3 and S4 where the service now
refuses a request of 40.

## Notes and limits

- **N-1. S4's other half.** S4 says "the existing W2-112 tests pass unchanged". They are not repeated here. Two of
  them pin the cap at 16 and cannot pass unchanged once it is raised (see N-3).
- **N-2. S3 on integrate.** The `rerank.rerank` comparison has the same cap on both sides on integrate (16), so it is
  only meaningful after the fix (1 request against 3 for the short pool). The service-level case compares one request
  of 40 against requests of 16 directly, so it bites on integrate too.
- **N-3. Tests elsewhere that pin 16** (not this folder; for the CTO). Raising the cap turns red, or leaves stale,
  tests that assert the count cap is 16 or that a pool of 40 goes in three requests:
  `tests/unit/retrieval/test_w2_112_shared_reranker.py` (`test_the_release_leaves_the_client_s_bounds_as_they_were`,
  `test_a_search_s_requests_never_reach_the_service_s_cap`), `tests/unit/retrieval/test_w2_32_whole_chunk.py:241`,
  `tests/unit/retrieval/test_w2_32_pool.py` (around 449), and the acceptance tests of W2-32 (`CAP_TEXTS`/`CAP = 16`
  in `test_w2_32_s7_size_bound.py`, `test_w2_32_s7_dec1067.py`, `test_w2_32_s8_routing.py`, `w2_32_pool.py`),
  W1-19 (`RERANK_CAP = 16`) and W1-21 (`RERANK_CAP = 16`). None is in the ticket's `allowed_paths`, and acceptance
  tests are a test designer's to revise.

## Files

- `w2_137_support.py`: the oracle, the stand-in encoder and recorders, W2-112's seam for `serve`.
- `conftest.py`: the tree and the support module on the path.
- `test_w2_137_s1_requests.py` (S1), `test_w2_137_s2_service_bound.py` (S2), `test_w2_137_s3_same_scores.py` (S3),
  `test_w2_137_s4_memory.py` (S4).
