# W2-137 evidence: the shared reranker's request cap raised (DAEO-5emz; DEC-1090 (2), PAT-1 G1)

**The cause.** Each request to a reranker carried at most 16 texts (`rerank.MAX_REQUEST_TEXTS`, DEC-1067 (f)), set
when the shared reranker's memory climbed with large requests. With the pool's 40 candidates a search sent 3
requests, and 20 searches at once took 13.4 s each (p50), against W2-112's 2.32 s with no cap (PAT-1 §4). W2-112's
release (DEC-1068) now empties the GPU cache after every request, which removes the reason for the small cap.

## The change

- **`src/gov/retrieval/rerank.py`:** `MAX_REQUEST_TEXTS` raised from 16 to **64**.
  - **Why 64:** it holds the pool's `rerank_depth` (40) in one request, and a pool as deep as the routes
    (`route_depth` 60), with room; it stays far under the service's own bound (`rerank_service.MAX_TEXTS`, 512).
  - **What bounds memory now:** a request's GPU memory is set by its padded size (its count times its longest pair),
    and `MAX_REQUEST_CHARS` (24,000 padded characters) bounds that whatever the count. It stays, and still splits a
    request whose texts are long: 64 texts fit one request only when each pair is at most 375 characters; 40 when
    each is at most 600. So a request's padded size is no larger than under the cap of 16.
  - `requests()` is unchanged: the longest text first, as many as fit both bounds; a text whose pair alone is over
    the bound is read up to it.
- **`src/gov/retrieval/rerank_service.py`:** `MAX_TEXTS` stays 512, at least the client's cap. A request over it is
  refused whole, never cut, with its own reason naming the bound and the count (`ValueError: a request is a question
  and at most 512 texts: this one has 513, none scored`). A malformed request keeps its own reason.
- **What stays as it was:** the service's release after every request and its `MEMORY` line (`serve`, `released`);
  `rerank()`'s mapping of each score back to its candidate, so the order is the unbatched one.
- **The unit tests that pinned 16 (D-1)**, each change commented `DEC-1090 (2)`:
  - `test_w2_112_shared_reranker.py`: `test_the_release_leaves_the_client_s_bounds_as_they_were` (now `(64, 24_000,
    512)`), `test_a_search_s_requests_never_reach_the_service_s_cap` (now `== 64 <`), and one comment;
  - `test_w2_32_whole_chunk.py`: the count test's cap and rows (63, 64, 65, 129 added), the service test (100 texts as
    `[64, 36]`), the padded-bound test's count (read from `MAX_REQUEST_TEXTS`), the shape test (`[100] * 40` is now one
    request of 40; `[100] * 100` is `[64, 36]`);
  - `test_w2_32_pool.py`: three comments only (its assertions read `MAX_REQUEST_TEXTS`).

## The KPI lines and how each is met

| KPI | How it is met | Tests |
|---|---|---|
| S1: 40 candidates in one request when they fit the padded bound; the padded bound stays and splits long texts | `MAX_REQUEST_TEXTS = 64`; `MAX_REQUEST_CHARS` and `requests()` unchanged | unit `tests/unit/retrieval/test_w2_137_request_cap.py`: `test_s1_the_cap_holds_the_pool_s_40_and_the_routes_60`, `test_s1_short_texts_at_the_pool_s_depth_go_in_one_request[40]` and `[60]`, `test_s1_40_long_texts_are_split_by_characters_never_by_count_alone` (40 x 2,000 characters: 11, 11, 11, 7), `test_s1_one_long_text_with_short_ones_goes_alone_and_the_short_ones_together`, `test_s1_one_text_over_the_bound_is_read_up_to_it`, `test_s1_a_pool_over_the_cap_still_goes_in_requests_of_at_most_the_cap` (100 as 64, 36), `test_s1_a_rerank_of_40_short_candidates_asks_the_shared_service_once` |
| S2: the service's bound at least the new cap; a request over it refused with a named reason, never truncated | `MAX_TEXTS` 512 >= 64; over the bound, its own `ValueError` naming the bound and the count, the encoder never called | unit `test_s2_the_service_s_bound_is_at_least_the_client_s_cap`, `test_s2_the_service_scores_a_request_at_the_cap_and_at_its_bound[64]` and `[512]`, `test_s2_a_request_over_the_service_s_bound_is_refused_with_its_count_named_never_truncated`, `test_s2_a_malformed_request_keeps_its_own_reason`, `test_s2_the_client_names_the_service_s_refusal` |
| S3: the order under the new cap equals the order under 16, the largest score difference within 1e-3 | `rerank()` puts each score back at its candidate's index, so the split does not reach the order | unit `test_s3_the_order_and_scores_under_the_new_cap_equal_those_under_16` (40 short, 60 short, 100 short, 10 long with 30 short, one huge with 39 short: same order, difference 0 with the stub encoder, fewer or equal requests), `test_s3_the_service_scores_a_text_the_same_in_one_request_or_in_pieces_of_16` |
| S4: the release and its MEMORY line after every request, whatever its size; W2-112's tests pass but the two that pinned 16, revised | `serve()` unchanged | unit `test_s4_every_request_is_released_once_after_its_answer_with_its_memory_line` (1, 16, 40, 64, 512 and 513 texts: one release after the answer, one `MEMORY` line; 513 refused unscored and still released); W2-112's two revised tests (D-1) and its in-process release tests pass; see the results below for the cases the sandbox cannot run |
| S5: 20 and 10 searches at once on the GPU, the peak under 14,255 MiB; hit@5 and MRR unchanged within 1 | | S5: the CTO's measure, after the merge |

**A note for S5 (not a change here).** The real cross-encoder (`CrossEncoder.predict`) splits its input into its own
batches (32 pairs by default), each padded to its own longest. So a 40-text request is two forward passes on the GPU,
neither larger than the request's padded size. A text's score can then differ by floating-point rounding with the
padding of the batch it lands in; S3's tolerance of 1e-3 and S5's live check cover that.

## Test results (through the heavy slot; HOME a scratch folder with only the user site linked)

- **Unit, the new file and the revised whole-chunk file** (every row, `--optin=lifted,breadth`):
  `test_w2_137_request_cap.py` and `test_w2_32_whole_chunk.py`: 71 passed (26 of them W2-137's).
- **Unit, the three D-1 files** (every row): 117 passed, 21 failed before the last fix. One was
  `test_w2_32_whole_chunk.py::test_one_batch_that_fails_leaves_every_candidate_unscored`, whose 20 texts went in two
  requests under 16 and go in one under 64; it now sends 100 (64 and 36) and passes. The 20 others are all in
  `test_w2_112_shared_reranker.py`: the launch sandbox refuses the shared reranker's Unix socket (`PermissionError:
  [Errno 1] Operation not permitted`), so the stand-in service never listens and each search falls back. They are the
  sandbox's, as in W2-131, W2-133 and W2-135 (18 there with the opt-in rows left out; 20 here with every row). Among them
  are W2-112's two revised tests (`test_a_search_s_requests_never_reach_the_service_s_cap`,
  `test_a_request_over_the_cap_is_refused_and_the_search_falls_back`), which need the socket; the CTO runs them outside
  the sandbox. `test_the_release_leaves_the_client_s_bounds_as_they_were` and the in-process release tests pass.
- **`gov accept W2-137`:** pass, 37/37. success-1 18/18, success-2 9/9, success-3 5/5, success-4 5/5; 0 unmapped,
  0 skipped.
- **`tests/unit/retrieval`, `tests/acceptance/W2-32`, `W2-112`, `W1-19` and `W1-21`** (`-n auto -m "not local_only"
  -k "not real and not green_here and not time_limit"`, the opt-in rows left out as by default): 853 passed, 52 failed,
  3 skipped, 1 xfailed, in 8 min 16 s. Every red, by cause:
  - **The sandbox refuses Unix sockets (41):** 19 in `tests/unit/retrieval/test_w2_112_shared_reranker.py` and 22 in
    `tests/acceptance/W2-112/` (`test_w2_112_answers.py` 3, `test_w2_112_service.py` 6, `test_w2_112_concurrency.py` 4,
    `test_w2_112_gpu.py` 2, `test_w2_112_slots.py` 2, `test_w2_112_fallback.py` 5). No stand-in service can listen, so
    each search falls back; W2-112's own support names the refusal in most of them. The CTO runs them outside the
    sandbox.
  - **They pin the old cap of 16 (D-2, an independent test designer's, not this ticket's paths) (9):**
    `tests/acceptance/W2-32/test_w2_32_s11_pool.py::test_every_rerank_request_keeps_the_padded_bound[v456]` (22 texts),
    `test_w2_32_s11_pool.py::test_v456_rerank_depth_reranks_the_first_40_once_and_cuts_the_pages_with_the_others_on`,
    `test_w2_32_s7_dec1067.py::test_no_reranker_request_carries_more_than_16_texts_and_the_order_is_the_unbatched_one[fusion_search]`
    (30) and `[retrieve]` (20),
    `test_w2_32_s7_size_bound.py::test_a_pool_of_long_chunks_goes_in_the_fewest_requests_within_16_texts_and_24000_characters[fusion_search]`
    (18), `test_w2_32_s8_phrasings.py::test_the_merged_pool_is_reranked_once_within_16_texts_and_24000_characters[content]`
    (24) and `[record]` (31), `test_w2_32_s8_routing.py::test_the_16_text_cap_holds_with_routing_on` (20), and
    `tests/acceptance/W1-19/test_w1_19_semantic_index.py::test_both_routes_are_fused_into_one_list_and_reranked_in_one_pass`
    (`RERANK_CAP`, 19 and 10).
  - **A unit test that pins 16 outside D-1's list (1):**
    `tests/unit/retrieval/test_w2_32_routing.py::test_routing_on_keeps_one_rerank_of_the_merged_set_in_full_requests_of_16`
    (`[16] * (pool // 16) + ...`); its sibling `test_phrasings_on_rerank_the_merged_pool_once_within_the_bounds` also
    reads `n <= 16` and passed here only because its pool is small. Neither is in `allowed_paths`; not changed.
  - **Not this change (1):**
    `tests/acceptance/W1-19/test_w1_19_embedding_policy.py::test_only_the_namespace_that_says_embedded_reaches_the_vectors`
    (nothing sent to the embedding stand-in) passes alone (1 passed); it touches no rerank code.
  - W1-21's cases all pass (its `RERANK_CAP` cases stay within the new cap).
  - The skips: two W2-32 record cases with no baseline measure record under the scratch HOME, one W2-32 fusion case
    whose limit above the cap does not arise.
