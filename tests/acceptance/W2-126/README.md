# W2-126 acceptance tests: a machine-wide vector cache keyed by the text (DAEO-jpr0)

Written by the independent test designer (MR-3) from the ticket's KPI lines and sources (DEC-1032;
P1-LOAD-BALANCE-1 section a, levers b.1 and b.6; DEC-1031, DEC-1015, DEC-374), before the implementation, without
reading it. Behaviour through public interfaces only (DEC-462), in proportion to a STANDARD ticket (DEC-221).

## Run

    PYTHONPATH=<this worktree>/src python3 -m pytest tests/acceptance/W2-126 -q -p no:cacheprovider \
        -o tmp_path_retention_policy=failed -rs

27 cases (one of them `local_only`): 17 for success lines 1 to 6, 10 for success line 7 (`test_w2_126_retry.py`);
about 40 s for the first 17 without the `local_only` case (about 2 minutes with it), and about 20 s more for the
retry file (measured on the base).
Each needs `gitleaks` on `PATH` and an importable `sqlite_vec` (the lexical index and the vectors need them); a case
is skipped, named, where either is missing.

## How the suite finds the code under test

- `w2_126_support.SRC` is the `src/` of the repository the test file sits in (`Path(__file__).parents[3] / "src"`),
  never a fixed path and never an installed copy. Merged into the ticket's worktree, the suite exercises that
  worktree's code.
- Every call runs in a child process (a small driver written to the test's temporary folder) whose `PYTHONPATH` is
  that `src/` (plus a folder that links this machine's `sqlite_vec`). A session fixture asserts that `gov` imported
  with that `PYTHONPATH` comes from that `src/` (DEC-732).
- The public interfaces used: `gov.retrieval.semantic.refresh(root)`, `search(root, question, refresh=False)` and
  `query_vector(root, question)`; the store's plain `semantic_vector` and `semantic_manifest` tables
  (`.gov-runtime/store.db`, read read-only); the retrieval check as its declaration runs it,
  `python3 -m gov.retrieval.retrieve_check` in a project root with `GOV_DEV_TIERS` set.

## Never the real embedders, never the user's real cache

- **A stand-in embedder** (`StandIn`) on a free loopback port answers Ollama's protocol: `/api/version` (so the
  base's `ensure_available`/`ensure_query_available` find it healthy and start nothing), `/api/tags` (the model
  with a revision the case chooses, as its `digest`, DEC-374), `/api/ps` (the model wholly on the CPU, so the
  device rule decides no case) and `/api/embed`. It records every text it is sent with the vector it returned.
  Its vectors are float32-exact and a function of (revision, text), or, with `varying`, of the request too (so a
  vector served from the cache shows it was not computed again). It can hold one request open (`hold`).
- `OLLAMA_HOST` and `GOV_QUERY_OLLAMA_HOST` both name it; `PATH` holds no folder with an `ollama` in it (gitleaks is
  linked into a folder of its own); `HOME`, `XDG_CACHE_HOME` and `TMPDIR` are temporary folders of the test;
  `GOV_VECTOR_CACHE_DIR` names a temporary folder (one case leaves it out on purpose, with `HOME` and
  `XDG_CACHE_HOME` still temporary). No network beyond the loopback stand-in. Each server is stopped by its fixture.
- Every project is a temporary git repository planted from scratch under `tmp_path` (this repository's path map
  with the namespaces replaced, and the template's gitleaks rules: single named files), cloned with `git clone`
  where a case needs a clone.

## Interface the cases need

What the cases rely on, and nothing more (no module, function or table of the code to be written is named):

1. **Location setting: `GOV_VECTOR_CACHE_DIR`**: the folder that holds the machine-wide cache, created if absent.
   Default: a folder in the user's own folder (for example under `$XDG_CACHE_HOME`, else `~/.cache`: the cases
   only check that it is under `HOME` or `XDG_CACHE_HOME`). Once every process using it has ended, the folder
   holds **one file, the cache, of mode 0600**. Every tree and clone on the machine shares it. No switch to turn
   the cache off is needed: the "built without the cache" store is built with an empty cache folder of its own.
2. **Size-limit setting: `GOV_VECTOR_CACHE_MAX_BYTES`**: a whole number of bytes, the bound on the cache, measured
   as the size on disk of what the cache folder holds once a write has ended. Default: about two corpora, from the
   measured corpus (not tested). Past it, the least recently used entries (by lookup or store) go first.
3. **The result names the cache**: the dicts `semantic.refresh(root)` and `semantic.search(root, question, ...)`
   return carry a key `vector_cache` with
   - `hits`: the number of texts whose vector came from the cache in that call;
   - `misses`: the number of texts sent to the embedder in that call (and stored);
   - `skipped`: `None` when the cache was used; otherwise a non-empty string saying why it was skipped (unreadable,
     locked); the texts are then embedded and the call succeeds.
   `query_vector` keeps its `(vector, reason)` return; the cases only count what it sends.
4. The key is the model, the revision `/api/tags` reports (its `digest`) and the sha256 of the exact text sent
   (a chunk's first characters as sent; a question's text as sent). The cases see it only through what is sent.

## KPI lines and their tests, with the red reason on the base

The base has no machine-wide cache: a second tree re-sends its texts, there is no cache file, no setting is
honoured and the results do not name a cache. Seen on the base (`2a3c998fe786`), every case fails, each as below.

The map `gov accept DAEO-jpr0` reads (DEC-1042 item 3): the KPI column names each line as `gov accept` reads it,
`S<n>` for the ticket's success line n and `F<n>` for its failure line n; the test column holds only test names in
backticks, a parameterised case once per parameter (`name[id]`); notes on a case are in the third column.

| KPI | test | notes, and the red reason on the base |
|---|---|---|
| S1 | `test_w2_126_hits.py::test_a_second_tree_and_a_clone_send_nothing` | "a tree whose texts are all cached sent texts to the embedder" |
| S1, F1 | `test_w2_126_hits.py::test_a_changed_text_is_a_miss` | one letter's case changed; "texts already cached were sent again" |
| S1 | `test_w2_126_hits.py::test_a_question_from_two_trees_is_embedded_once` | "the question was embedded once per tree" (2 == 1) |
| S1 | `test_w2_126_hits.py::test_the_cache_is_one_file_of_mode_0600` | "the cache folder must hold one file, not []" |
| S1 | `test_w2_126_hits.py::test_by_default_the_cache_sits_in_the_users_own_folder` | "without the location setting, a second tree sent its texts again" |
| S2 | `test_w2_126_same_vector.py::test_a_cached_vector_is_the_one_the_embedder_returned` | varying stand-in; also the result's hits, misses and skipped; "a tree whose texts are all cached sent texts to the embedder" |
| S2, F2 | `test_w2_126_same_vector.py::test_an_all_cached_rebuild_gives_the_store_built_without_the_cache` | "the rebuild of an all-cached tree embedded texts" |
| S3, F1, F3 | `test_w2_126_writers.py::test_concurrent_rebuilds_and_searches_serve_only_right_vectors` | 4 processes; "texts every writer stored were sent again: a write was lost" |
| S3 | `test_w2_126_writers.py::test_no_lock_is_held_across_an_embedding_request` | one request held open; "the result does not name the vector cache ('vector_cache')" |
| S3, F3 | `test_w2_126_writers.py::test_an_unusable_cache_is_skipped_and_named[unreadable]`, `test_w2_126_writers.py::test_an_unusable_cache_is_skipped_and_named[locked]`, `test_w2_126_writers.py::test_an_unusable_cache_is_skipped_and_named[garbage]` | "the cache folder must hold one file, not []" (each) |
| S4 | `test_w2_126_bound.py::test_least_recently_used_entries_go_first` | 96 KiB bound, 1 KiB vectors; "the most recently used entry was evicted" (the base caches no question for a tree without a `.gov-runtime/` folder, so every ask is sent) |
| S4, F1 | `test_w2_126_bound.py::test_a_revision_change_is_a_new_key_space` | "the first revision's entries were lost when the revision changed" |
| S5 | `test_w2_126_dev_tiers.py::test_a_later_check_embeds_nothing` | a planted GOV_DEV_TIERS folder: two small tiers, four questions; "a later check embedded 60 texts cold" |
| S5 | `test_w2_126_dev_tiers.py::test_a_later_check_on_this_machines_dev_tiers_embeds_nothing` | marked local_only: this machine's dev tiers by GOV_DEV_TIERS's name, skipped where absent; "a later check embedded … texts cold" |
| S6 | `test_w2_126_evidence.py::test_the_evidence_file_states_the_named_figures` | light: the file exists and names the figures, never their values; "docs/changes/W2-126-evidence.md does not exist" |
| S7 | `test_w2_126_retry.py::test_a_transient_failure_then_an_answer_is_tried_again_and_the_stage_is_built[500]`, `test_w2_126_retry.py::test_a_transient_failure_then_an_answer_is_tried_again_and_the_stage_is_built[503]`, `test_w2_126_retry.py::test_a_transient_failure_then_an_answer_is_tried_again_and_the_stage_is_built[reset]` | batch 0 fails once, then answered: 2 tries after the first wait, built, `retries` one entry of 2 tries, embedded; "after a 500 (503, reset), the batch was not tried again exactly once": `['500'] == ['500', 'answered']` |
| S7 | `test_w2_126_retry.py::test_a_refused_connection_then_an_answer_is_tried_again_and_the_stage_is_built` | nothing listens for 1 s after batch 0's answer, the waits lowered to 2 s and 3 s: batch 1 reaches the stand-in after the first wait, built, `retries` 2 tries, embedded; "batch 1 did not reach the stand-in once after its refused try: []" (`retries` `[]`) |
| S7 | `test_w2_126_retry.py::test_a_transient_failure_at_every_try_fails_closed_after_the_last_try_within_the_bound[500]`, `test_w2_126_retry.py::test_a_transient_failure_at_every_try_fails_closed_after_the_last_try_within_the_bound[503]`, `test_w2_126_retry.py::test_a_transient_failure_at_every_try_fails_closed_after_the_last_try_within_the_bound[reset]`, `test_w2_126_retry.py::test_a_transient_failure_at_every_try_fails_closed_after_the_last_try_within_the_bound[mixed]` | batch 1 fails at every try (`mixed`: a time-out, a 500, a reset: one bound): exactly 3 tries after their waits, no later batch, within the bound, `FACET_UNAVAILABLE` with a reason beginning `NO_EMBEDDING`, `retries` 3 tries not embedded, a search without refresh `stale`, no hit; "the batch that kept failing was not tried exactly 3 times" (one try; `mixed`: the time-out retried, then the 500 ended it, `['held', '500']`) |
| S7 | `test_w2_126_retry.py::test_a_refused_connection_at_every_try_fails_closed_after_the_last_try_within_the_bound` | nothing listens again after batch 0: the stage waits both waits, ends within the bound, `FACET_UNAVAILABLE`, `retries` 3 tries not embedded; "the stage ended 0.01 s after nothing listened: it did not wait 1.0 s to try again" |
| S7 | `test_w2_126_retry.py::test_a_device_read_that_never_answers_fails_closed_and_stores_nothing` | DEC-1065 (1) (W2-32's S10, F-2): every `/api/ps` connection reset, so the device of batch 0's vectors is never read: the read tried again, then `EMBEDDER_DEVICE_UNREAD`, no later batch, nothing stored or cached; red where no device is read (before W2-32) |
| S7 | `test_w2_126_retry.py::test_a_client_error_is_not_retried_and_the_stage_ends_at_once` | an edge, green on the base (a guard): an HTTP 400 is not a transient server error, sent once, exactly `NO_EMBEDDING`, `retries` `[]` |

Success line 7 (DEC-1042 item 4, after W2-123 landed; `Rewrite-Reason: P-W2-123-4`): see "Success line 7: the
bounded retry" below. W2-123's case that an HTTP 500 is not retried is revised in
`tests/acceptance/W2-123/test_w2_123_retry.py` (its README, "Run 2", says how).

Failure lines: **F1** (a vector for a different text, model or revision): the changed-text, concurrent-writers and
revision cases. **F2** (a store built with the cache differs): the all-cached rebuild, the cached-vector case and
the unusable-cache cases (the store equals the one built from the embedder). **F3** (a rebuild or search fails
because of the cache): the concurrent-writers, held-request and unusable-cache cases (every call must succeed).

## Notes

- **A model change** cannot be made through a public interface (the model is pinned in the code); the revision
  change stands for "a new key space" (KPI 4). The key's other parts are seen only through what is sent.
- **The bound's default** (about two corpora) and KPI 6's figures are values for the evidence and the audit, not
  tested.
- **"Locked"** is made by holding both a `flock` and a POSIX record lock over the whole cache file from the test
  process, so whatever whole-file lock the cache takes is taken already; a cache that waits on it must still end
  the call within the driver's limit (300 s).
- **"Garbage"** (the file overwritten with other bytes) must not fail a rebuild or a search, and must not give
  wrong vectors; whether it is skipped (named) or replaced is the engineer's choice and is not tested.
- **The root conftest's per-test cache folder** (W2-126's own fixture, DEC-1042 item 1) sets `GOV_VECTOR_CACHE_DIR`
  in the pytest process only. No case here reads it: every child process gets an environment built from scratch
  (`Box.env`: only `PATH` is taken from the pytest process), naming the case's own folder, or, in the
  default-location case (`use_setting=False`), no `GOV_VECTOR_CACHE_DIR` at all, so that case sees the default
  under its temporary `HOME` and `XDG_CACHE_HOME` whatever the pytest process holds.
- **The user's own folder** already holds what the base writes there besides the cache (its secrets scan, under
  `~/.cache/gov-os/`): the default-location case counts only what appears once the location setting is left out.
- **Lever b.6 through public interfaces**: the retrieval check clones the tiers into a new temporary folder on
  every run, so a later run that sends nothing shows that the tiers' chunks and questions came from the machine-wide
  cache. The `local_only` case uses this machine's tiers only by `GOV_DEV_TIERS`'s name (default
  `~/gov-os-workbench/synthetic`) and checks only that a named file exists there; the check itself clones them into
  the test's temporary folder.

## Success line 7: the bounded retry (`test_w2_126_retry.py`; DEC-1042 item 4, P-W2-123-4)

Written after W2-123 landed on `w2/integrate`, from KPI 7 and W2-123's run-2 interface (R1 to R3, its README), by a
fresh independent test designer, without reading W2-126's implementation. The integrated code (W2-123's retry) was
read for the names it exposes; the cases use only those: `semantic.refresh`, `search(..., refresh=False)`,
`TIMEOUT_S`, `RETRY_WAITS_S`, `NO_EMBEDDING` and the report's `retries`.

- **The bound** is W2-123's: `len(RETRY_WAITS_S) + 1` tries of one chunk batch request, the waits of `RETRY_WAITS_S`
  before the later tries, each try under `TIMEOUT_S`. KPI 7 adds no other bound, so a time-out, a 5xx and a reset met
  by one request share it (the `mixed` case: three tries in all).
- **How they run.** One child per case (the suite's `Box` environment: its own HOME and cache folder), with
  `TIMEOUT_S` 1.0 and `RETRY_WAITS_S` (0.25, 0.75) set in the child before `refresh` (the refused-then-answered case:
  (2.0, 3.0)). The project is 80 one-section chunks (two notes of 40, each holding `w2126retryNNN`), three batch
  requests at `BATCH` 32. The stand-in (`Flaky`, in the test file) numbers chunk batches by their texts and fails a
  chosen batch's first tries: HTTP 500, 503 or 400 at once; a reset (the request read, the socket closed with RST);
  held (no answer for 10 s); or refused (after batch 0's answer the serving loop is stopped and the listening socket
  closed before the answer is sent, so the next connection is refused; opened again on the same port after 1 s, or
  never).
- **Readings of KPI 7, stated (not guessed past):** "covers" means the request is tried again after the next wait,
  as a time-out is; "failing closed" means W2-123's R3 end: no later batch, `FACET_UNAVAILABLE`, a search without
  refresh `stale` with no hit. The reason after the last failed try must begin with `NO_EMBEDDING`; its wording is
  not fixed (R3's exact text says "timed out", which a 5xx is not). `retries` states every chunk batch request tried
  more than once (R3 listed the timed-out ones; the KPI's "tries and waits stated in the rebuild's result" now covers
  every retried request): `tries` and `embedded` are asserted, `waits_s` within 0.1 s where the waits are lowered,
  and an entry may carry more keys. A 4xx, a body that is not JSON and one without a vector stay R1's "ends at once"
  (not transient); the 400 case guards it here, W2-123's `not-json` and `no-vector` cases there.
- **A refused try cannot be seen by the stand-in** (nothing listens). The refused cases read it from the time taken
  (the waits were waited) and from `retries`. The refused-then-answered case relies on the client sending batch 1
  less than 1 s after batch 0's answer, and the listener being back 1 s before the 2 s wait ends.

**Red on the base** (`w2/integrate` at `b120aad0f048`, this tree's `src/` equal to it): 9 failed, 1 passed (the 400
guard), in 14 s. Each 5xx and reset case: the batch sent once (`['500'] == ['500', 'answered']`, `['reset'] ==
['reset', 'reset', 'reset']`); `mixed`: the time-out retried, the 500 then ended the stage (`['held', '500']`); the
refused-then-answered case: batch 1 never reached the stand-in (`retries` `[]`); the refused-at-every-try case: the
stage ended 0.01 s after the refusal, no wait. **Shown green** against a throwaway copy of that `src/` outside the
tree whose `_ask` reads an HTTP 5xx, a `ConnectionError` and a refused `URLError` as a time-out (a probe, not W2-126's
code): 10 passed, four runs, about 22 s each.

## DEC-1065 (1): the device is read, never assumed (`Rewrite-Reason: DEC-1065 (1) (the device is read, never assumed)`)

W2-32's S10 (and the review's F-2): after each rebuild batch the device is read from `/api/ps`; an unreadable read
is retried as the request is, and after the last try the stage fails closed (`EMBEDDER_DEVICE_UNREAD`), never
assuming the GPU. Revised by W2-32's independent test designer:

- **The stand-in (`Flaky`)** goes down once batch 0 is answered **and the device read after it is answered** (it went
  down right after batch 0's answer, so the refusal fell on the device read, not on batch 1 as the two refused cases
  mean). What they guard is unchanged: a refused batch is tried again after its wait and the stage is built
  (`retries`: one request of 2 tries); a batch refused at every try fails closed after both waits, within the bound,
  with `NO_EMBEDDING`.
- **A row added:** `test_a_device_read_that_never_answers_fails_closed_and_stores_nothing` (every `/api/ps`
  connection reset: the read is tried again, then `EMBEDDER_DEVICE_UNREAD`, no later batch, no vector stored in the
  store or the machine-wide cache).
- On code that reads no device after a batch (before W2-32) the stand-in never goes down, so the two refused cases
  and the new row are red there; on W2-32 (`26ad7ca2`) the file's 11 cases pass.

## KPI map after D-4's cut (DEC-1061)

Regenerated in round 2 of the cut (DEC-1061; the review's F3, F4): each line of the ticket's `kpis:` is placed
by its own words (or by the designer, or by part A's row for that line), never by the README's layout; each
case named here runs in the full run, with every row of a class the line names; tier 2's cap then cut only
the rest. The rest stay built: `breadth` (`tests/optin-lifted*breadth*.txt`, `--optin=breadth`) and, for the
switched-off features, `lifted` (the other `tests/optin-lifted*.txt`, `--optin=lifted`). The placement is data
(`placement.json`, with the designer's `overrides.json`), checked by code against the default collection.

Cases: 25 in the full run, 2 in `breadth`, 0 in `lifted`.

| KPI line | case(s) in the full run (rows in the full run of the function's rows) | placed by |
|---|---|---|
| S1: Before it embeds a chunk or a question, the semantic stage and `query_vector` look up a machine-wide cache keyed by the model, its revision and... | `test_w2_126_hits.py::test_a_second_tree_and_a_clone_send_nothing`, `test_w2_126_hits.py::test_by_default_the_cache_sits_in_the_users_own_folder`, `test_w2_126_same_vector.py::test_a_cached_vector_is_the_one_the_embedder_returned` | the ticket's words |
| S2: The same vector for the same text: a cached vector is byte-for-byte what the embedder returned when it was stored; a rebuild of a tree whose ch... | `test_w2_126_same_vector.py::test_an_all_cached_rebuild_gives_the_store_built_without_the_cache` | the ticket's words |
| S3: Safe under many writers: concurrent rebuilds and searches read and write it at once without a corrupt entry, a lost write that is later read as... | `test_w2_126_writers.py::test_no_lock_is_held_across_an_embedding_request` | the ticket's words |
| S4: Bounded: a configured size limit (default from the measured corpus: about 2 corpora) with least-recently-used eviction; a model or revision cha... | `test_w2_126_bound.py::test_a_revision_change_is_a_new_key_space` | the ticket's words |
| S5: The retrieval check's dev tiers (a-dev, b-dev) and their 52 questions are embedded once on the machine and hit the cache in every later `gov ch... | `test_w2_126_dev_tiers.py::test_a_later_check_on_this_machines_dev_tiers_embeds_nothing` | the ticket's words |
| S6: Measured, in docs/changes/W2-126-evidence.md: the texts sent to the embedder per day before and after (target: under one corpus, about 54,000, ... | `test_w2_126_same_vector.py::test_a_cached_vector_is_the_one_the_embedder_returned`, `test_w2_126_hits.py::test_a_second_tree_and_a_clone_send_nothing`, `test_w2_126_hits.py::test_a_changed_text_is_a_miss` | the ticket's words |
| S7: The bounded retry (W2-123, DEC-1026) also covers a transient server error (HTTP 5xx) and a reset or refused connection, within the same bound, ... | `test_w2_126_retry.py::test_a_transient_failure_at_every_try_fails_closed_after_the_last_try_within_the_bound` (4 of 4), `test_w2_126_retry.py::test_a_refused_connection_at_every_try_fails_closed_after_the_last_try_within_the_bound`, `test_w2_126_retry.py::test_a_device_read_that_never_answers_fails_closed_and_stores_nothing` | the ticket's words |
| F1: A vector served for a different text, model or revision. | `test_w2_126_writers.py::test_concurrent_rebuilds_and_searches_serve_only_right_vectors` | the ticket's words |
| F2: A store built with the cache that differs from one built without it. | `test_w2_126_same_vector.py::test_an_all_cached_rebuild_gives_the_store_built_without_the_cache` | the ticket's words |
| F3: A rebuild or search that fails because of the cache. | `test_w2_126_same_vector.py::test_an_all_cached_rebuild_gives_the_store_built_without_the_cache`, `test_w2_126_writers.py::test_concurrent_rebuilds_and_searches_serve_only_right_vectors` | the ticket's words |
