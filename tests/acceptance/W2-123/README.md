# W2-123 acceptance tests (DAEO-qzrq, STANDARD)

Written by the independent test designer (MR-3) from the ticket's KPI lines, DEC-1014 (items 4 and 6), DEC-1015
(item 2), DEC-1017, DEC-1010 item 7, ACT-OLLAMA-CAP-1 and the lead's interface spec for this run ("The outside of
W2-123", S1 to S6), without reading the implementation.

Run 2 (DEC-1026, DEC-1015 item 4) adds `test_w2_123_retry.py`, written by a fresh independent test designer from the
ticket's new first success line and the lead's run-2 interface spec ("The outside of W2-123 run 2", R1 to R3), without
reading the implementation; see "Run 2: the retry" below.

## The interface

Every name is in `gov.retrieval.ollama` (the lead's run-1 spec, S1 to S6; these are the spec's item names, not the KPI
lines' numbers, which the map below gives):

- **S1** the configuration: `<HOME>/.gov-os/machine/gate.json`, key `embedding_servers`, entries `shared` and
  `query`, each with optional `parallel`, `cpus`, `nice`, `probe_slow_s`, `probe_hung_s`; an unreadable value refuses
  the start (`state` `CONFIG_INVALID`, the warning naming the file and the key, once on standard error).
- **S2** `ensure_available` / `ensure_query_available`: every start capped (CPUs, niceness, `OLLAMA_NUM_PARALLEL`),
  inherited by every process the server starts; the result gains `settings` (`parallel`, `cpus`, `nice`, `source`).
- **S3** `probe(server, *, env=None)`: `healthy`, `slow`, `hung`, `down` (or `CONFIG_INVALID`); never starts anything.
- **S4** `safe_restart(server, *, env=None)`: never while answering; a hung `<executable> serve` stopped with its
  children and started again under its cap; another program on the port never stopped; down started; one line in
  `<HOME>/.gov-os/machine/embedding-restarts.jsonl` for every call that stops or starts.
- **S5** `check_determinism(host, references, parallel)`: one request per text, `parallel` in flight, float32
  byte-for-byte comparison; `accepted` only when every vector is equal.
- **S6** `docs/changes/W2-123-evidence.md`: the 16 measured cases and a `Chosen setting:` line.

## KPI lines and their tests

Run 2 (DEC-1026) added the ticket's first success line, so run 1's lines moved down by one: run 1's S1 to S6 are now
S2 to S7 (`gov accept` names the lines by their order in the ticket file).

| KPI line | Tests | Expected red reason on the base code |
|---|---|---|
| S1: A rebuild's embedding request that times out is retried, bounded (at most three tries, a growing wait, each try under the per-request timeout); after the last failed try the stage ends not_recreated, named; never a partial store reported as built; the tries and waits stated in the rebuild's result | `test_w2_123_retry.py::test_a_request_that_times_out_once_is_tried_again_after_the_first_wait_and_the_stage_is_built`, `::test_a_request_that_times_out_twice_is_tried_a_third_time_after_a_longer_wait_and_the_stage_is_built`, `::test_each_try_waits_no_longer_than_the_timeout_and_the_waits_between_tries_are_taken`, `::test_after_the_last_failed_try_refresh_reports_the_tries_and_the_waits_and_sends_no_later_batch`, `::test_after_the_last_failed_try_the_rebuild_states_the_tries_and_waits_and_no_partial_store_is_reported_built`, `::test_with_no_request_timed_out_the_stage_is_built_and_retries_is_an_empty_list`, `::test_a_failure_that_is_not_a_time_out_ends_the_stage_at_once_without_a_retry` (2 cases: not-json, no-vector), `::test_a_server_error_at_every_try_is_tried_within_the_bound_and_the_stage_ends_unavailable` (revised from the third, http-error, under Rewrite-Reason P-W2-123-4) | the base code sends each batch request once with no retry: a timed-out batch is tried once (the five time-out cases fail on the count of tries) and the stage ends with the bare `NO_EMBEDDING`, not R3's reason; `refresh`'s report has no `retries` (the case where nothing times out, and the two not-a-time-out cases, which otherwise already pass on the base: one try, the bare `NO_EMBEDDING`); the revised server-error case: on `w2/integrate` at W2-123's merge a 500 is sent once, not tried 3 times (P-W2-123-4) |
| S2: `ensure_available` sets parallel requests and the CPU cap from one value each (defaults from the measure), states them; an unreadable value refuses the start, named, never uncapped | `test_w2_123_start.py::test_shared_start_uses_the_configured_cap_and_parallel_requests_inherited_by_its_runner`, `::test_shared_start_without_configuration_uses_the_default_resolved_from_the_callers_cpus`, `::test_a_server_already_answering_is_used_and_the_settings_a_start_would_use_are_stated`; `test_w2_123_config_invalid.py` (all 14) | the result has no `settings` (the start cases, and the case with the server already answering); the base reads no configuration, so an unreadable value does not stop the start: the planted executable runs as `serve` (the 13 refusal cases) |
| S3: Determinism: parallel requests return the same vector, to the stored precision; a difference refuses | `test_w2_123_determinism.py::test_equal_vectors_are_accepted_with_that_many_requests_in_flight`, `::test_a_difference_below_the_stored_precision_is_not_a_difference` | `check_determinism` does not exist (`AttributeError`) |
| S4: Measured in `docs/changes/W2-123-evidence.md`, the setting chosen where the cap is not the limit | `test_w2_123_evidence.py::test_the_evidence_file_holds_the_sixteen_measured_cases_and_the_chosen_setting` (the only test of this line; no test measures) | the file does not exist |
| S5: A product feature: read from the gate's file with the measured defaults; nothing of this machine in the code | `test_w2_123_start.py::test_shared_start_without_configuration_uses_the_default_resolved_from_the_callers_cpus` (the default cap is resolved from the calling process's own CPUs, narrowed by the test, so a machine's CPU numbers in the code fail it), `::test_shared_start_uses_the_configured_cap_and_parallel_requests_inherited_by_its_runner`; `test_w2_123_config_invalid.py` | no `settings`; the configuration is not read |
| S6: Health probe (healthy, slow, hung) and safe restart (hung server stopped, started again under its cap, recorded); never a restart while answering | `test_w2_123_probe.py` (all 7); `test_w2_123_restart.py::test_a_server_that_answers_is_never_restarted`, `::test_a_hung_server_of_the_gov_os_is_stopped_with_its_runner_and_started_again_under_its_cap`, `::test_a_port_held_by_another_program_is_never_stopped`, `::test_a_down_server_is_started_under_its_cap_and_recorded`, `::test_an_unreadable_value_stops_and_starts_nothing` | `probe` and `safe_restart` do not exist (`AttributeError`, in the pytest process or in the child) |
| S7: Both servers start under their cap from the gate's file, the query server with the GPU visible (DEC-1033, replacing DEC-798); every restart keeps the cap; a planted start of each shows it | `test_w2_123_start.py::test_query_start_uses_its_own_entry_and_leaves_the_gpu_as_the_caller_set_it` (2 cases), `::test_shared_start_uses_the_configured_cap_and_parallel_requests_inherited_by_its_runner`; `test_w2_123_config_invalid.py::test_an_unreadable_query_entry_refuses_the_query_start`; `test_w2_123_restart.py::test_the_query_server_restarts_under_its_own_cap_with_the_gpu_as_the_caller_set_it` (2 cases), `::test_a_hung_server_of_the_gov_os_is_stopped_with_its_runner_and_started_again_under_its_cap`, `::test_a_down_server_is_started_under_its_cap_and_recorded` | no `settings`; the started process runs on every CPU at the caller's niceness; no `safe_restart`; once those exist, the two query-server tests fail as S8 says |
| S8: The query embedder may use the GPU (DEC-1032, DEC-1033 replacing DEC-798): `ensure_query_available` starts the query server without hiding the GPU (no `CUDA_VISIBLE_DEVICES=-1`), so a server restarted by the code comes back on the GPU | `test_w2_123_start.py::test_query_start_uses_its_own_entry_and_leaves_the_gpu_as_the_caller_set_it` (2 cases: the caller names `CUDA_VISIBLE_DEVICES=0`, the server and its runner see `0`; the caller names none, they see none); `test_w2_123_restart.py::test_the_query_server_restarts_under_its_own_cap_with_the_gpu_as_the_caller_set_it` (2 cases: the same two for the restarted server) | the code before the DEC-1033 patch starts the query server with `CUDA_VISIBLE_DEVICES=-1` added: the server (and its runner) sees `-1`, not the caller's `0` or none (every other assertion of these cases, the cap, `OLLAMA_HOST` and `settings`, passes there) |
| F1: parallel requests that change a vector; a server started uncapped; a setting chosen without its measure | `test_w2_123_determinism.py::test_vectors_changed_by_parallel_requests_refuse_the_setting`, `::test_one_differing_vector_is_named_and_refuses`, `::test_a_missing_vector_refuses`; the cap assertions of `test_w2_123_start.py` and `test_w2_123_restart.py` and every case of `test_w2_123_config_invalid.py` (no uncapped start); `test_w2_123_evidence.py` (no setting without its measure) | as the rows above |

The key edge cases of STANDARD (DEC-221): an unreadable value of each kind S1 names (12 cases: the file not JSON,
not an object, the section and the entry not objects, a key of the wrong type and out of range, a CPU list that
cannot be parsed or names no CPU the caller may run on, a probe time not positive, `probe_slow_s` not below
`probe_hung_s`; and one for the query entry); the query server's cap with the caller's GPU setting left as it is
(`CUDA_VISIBLE_DEVICES=0` in the caller's environment, and none; revised for DEC-1033, see below); the cap inherited by a child (each daemon's runner); a restart refused
while the server answers (healthy and slow) and for a foreign process on the port.

## Revision for DEC-1033: the query server on the GPU (`Rewrite-Reason: DEC-1033`)

DEC-1033 (an emergency decision) replaces DEC-798: the query embedder may run on the GPU, and the Gov OS starts the
query server with the GPU visible (the ticket's success lines S7, as amended, and S8). Run 1 asserted the query
server's hidden GPU; a fresh independent test designer revised exactly those expectations (DEC-866: a test revised
for a newer decision lowers no other expectation), without reading the implementation:

| Old test (old expectation) | New test (new expectation) |
|---|---|
| `test_w2_123_start.py::test_query_start_uses_its_own_entry_and_keeps_the_gpu_hidden`: with `CUDA_VISIBLE_DEVICES=0` in the caller's environment, the started query server and its runner see `-1` | `::test_query_start_uses_its_own_entry_and_leaves_the_gpu_as_the_caller_set_it[caller-names-gpu-0]`: they see `0`; `[caller-names-no-gpu]`: with none in the caller's environment, they see none |
| `test_w2_123_restart.py::test_the_query_server_restarts_under_its_own_cap_cpu_only`: the restarted query server sees `-1` | `::test_the_query_server_restarts_under_its_own_cap_with_the_gpu_as_the_caller_set_it[caller-names-no-gpu]`: it sees none; `[caller-names-gpu-0]`: with `0` in the caller's environment, it sees `0` |

Every other assertion of those tests is unchanged (the configured entry, `OLLAMA_HOST`, the CPU list, the niceness,
`OLLAMA_NUM_PARALLEL`, the result's `settings`, the restart record). The child's environment is built from scratch
(`Stage.environment`), so "none" means the caller's environment has no `CUDA_VISIBLE_DEVICES` at all; the planted
daemon and its runner record what they see from inside.

## How the suite runs the code under test (DEC-732)

- **Whatever `gov` the pytest process imports.** `probe` and `check_determinism` are called in the pytest process
  (`from gov.retrieval import ollama`, the `ollama` fixture). `ensure_available`, `ensure_query_available` and
  `safe_restart` are called in a child `sys.executable` whose `PYTHONPATH` is the pytest process's own (or, if unset,
  the folder the pytest process imported `gov` from), with `env=` its whole environment. Run in the ticket's
  worktree with that worktree's `PYTHONPATH`, they exercise the ticket's code:

      PYTHONPATH=<worktree>/src python3 -m pytest tests/acceptance/W2-123 -q -p no:cacheprovider -o tmp_path_retention_policy=failed

- **Nothing real is touched.** Every call gets a temporary `HOME` (with the planted `gate.json`), `OLLAMA_HOST` and
  `GOV_QUERY_OLLAMA_HOST` on free loopback ports the test picks, and `GOV_OLLAMA_BIN` naming a planted executable
  under `tmp_path`. No test sends anything to 127.0.0.1:11434 or :11435, or runs the real `ollama`. A safe restart
  only ever finds a process the test started.
- **The planted executable** (`w2_123_support.py`, `WRAPPER` and `DAEMON`) is a bash script that `exec -a`'s Python
  on a stand-in daemon, so its command line reads exactly `<executable> serve`, as S4 compares. From inside, it
  records its `Cpus_allowed_list`, its niceness and `OLLAMA_HOST`, `OLLAMA_NUM_PARALLEL` and `CUDA_VISIBLE_DEVICES`;
  starts one child (its runner, as `ollama serve` starts `llama-server`) that records the same; and answers
  `/api/version` and `/api/embed` healthy, slow or hung. A probe or determinism case uses an in-thread stand-in
  embedder instead.
- **Nothing of this machine.** CPU lists come from `os.sched_getaffinity(0)` at run time (the lower half, the upper
  half, or a CPU one above the highest allowed); niceness is the pytest process's own plus 3 or 5.
- **Teardown** ends every stand-in: the in-thread endpoints, the processes the test started, and every daemon and
  runner that recorded itself, after checking its command line names this test's folder.

## Choices the interface leaves open, and how the tests read them

- A hung server's command line: S4 says "its command line is `<executable> serve`"; the planted daemon's
  `/proc/<pid>/cmdline` is exactly that, while `/proc/<pid>/exe` is Python. An implementation that compares the
  command line (as S4 says) passes; one that compared `/proc/<pid>/exe` would not.
- `new_pid` is read as the pid of the started server process (the daemon records its own pid).
- The reason for a foreign holder "names the process": its pid or its program (`python`) in `reason`.
- A file that is not JSON or not an object has no key to name: the warning names the file (`gate.json`). With
  `probe_slow_s` not below `probe_hung_s`, either key may be named.
- Niceness: the started process's niceness is at least the configured one (S1).
- The evidence table (S6): a table with a column whose header names "parallel", one "chunks" and one "semantic",
  at least four rows for each of 1, 2, 4 and 8, numbers in each; a line beginning `Chosen setting:`.

## Run 2: the retry (`test_w2_123_retry.py`, KPI line S1)

### The interface (the lead's run-2 spec, R1 to R3; every name in `gov.retrieval.semantic`)

- **R1** Only a rebuild's chunk embedding (each `/api/embed` batch of up to `BATCH` texts sent to `OLLAMA_HOST` by
  `refresh(root)`, or by `search(..., refresh=True)`) is retried, and only when it timed out (accepted, no complete
  answer within `TIMEOUT_S`). Every other failure (an HTTP error, an answer that is not JSON or lacks a vector for each
  text, nothing listening) ends the stage at once with `NO_EMBEDDING`, no retry. *Revised by W2-126's KPI 7*
  (P-W2-123-4, DEC-1042 item 4; see "KPI 7's revision" below): an HTTP 5xx and a reset or refused connection are
  retried within the same bound too.
- **R2** `RETRY_WAITS_S` (default `(10.0, 30.0)`): the growing waits before the 2nd, 3rd … try; `len(RETRY_WAITS_S) + 1`
  tries; each try under `TIMEOUT_S`; both read at the time of each request. A request that answers on a later try is
  used, and the build goes on with the next batch.
- **R3** `refresh`'s report gains `retries`: one `{"tries", "waits_s", "embedded"}` per batch request that timed out at
  least once, in request order; `[]` when none did. After the last failed try the stage stops (no later batch),
  `FACET_UNAVAILABLE`, reason exactly `f"{NO_EMBEDDING}: the request timed out at all {tries} tries (each under
  {TIMEOUT_S:g} s; waits {', '.join(f'{w:g} s' for w in RETRY_WAITS_S)})"`; `gov rebuild --json` shows the semantic
  stage `not_recreated` with that reason; a search without refresh reports `FACET_UNAVAILABLE`, `stale`, no hit.

### How the cases run

- **The code under test (DEC-732).** `refresh` and `search` are called in the pytest process, on the `gov` it imports,
  with `TIMEOUT_S` lowered to 1.0 and `RETRY_WAITS_S` to `(0.25, 0.75)` by `monkeypatch`. `gov rebuild --json --root
  <project>` runs in a child `sys.executable` whose `PYTHONPATH` is the pytest process's own (`code_path()`, with a
  link to `sqlite_vec`, which the scratch `HOME` cannot find), through a launcher that sets the same two attributes and
  calls `gov.cli.main.main`. Run in the ticket's worktree with that worktree's `PYTHONPATH`, every case runs the
  ticket's code.
- **The project** is a temporary git repository under `tmp_path`: a path map with `notes/**` embedded, the kernel's
  gitleaks rules, and two notes of 40 Markdown sections each: 80 chunks, so three batch requests at `BATCH` 32. Each
  chunk holds its own marker (`w2123chunkNNN`), so the stand-in tells a chunk batch from any other embed request and
  sees which chunks were sent and embedded.
- **The stand-in shared runner** (`Runner`) listens on a free loopback port the test picks (`OLLAMA_HOST`); it answers
  `/api/version`, `/api/tags` (the model with a digest), `/api/ps` and `/api/embed`. It numbers chunk batches by the
  order their texts are first seen (a retry is the same texts), and holds back the chosen batch's first one, two or
  three tries: it reads the request, then answers nothing for 10 s, ten times the lowered timeout. Or it fails every
  chunk batch at once (HTTP 500, a body that is not JSON, an answer with no vector; the 500 is now retried, KPI 7). Any other embed request (a probe's
  fixed text) is answered at once and never held.
- **Nothing real is touched.** `HOME` is the test's own, `GOV_QUERY_OLLAMA_HOST` a second free port with nothing on it
  (no case reaches the query embedder), `GOV_OLLAMA_BIN` a planted script that starts nothing. Nothing is sent to
  127.0.0.1:11434 or :11435; the real `ollama` is never run. The file runs in about 15 to 25 s.

### The cases

| Case | Stand-in | What must hold |
|---|---|---|
| no time-out | every batch answers | built; every chunk embedded; each batch sent once; `retries == []` |
| once | batch 0 held once | 2 tries of batch 0, the second answered; every later batch sent; built; `retries == [{"tries": 2, "waits_s": [0.25], "embedded": true}]` |
| twice | batch 0 held twice | 3 tries; built; `waits_s` both waits, growing |
| timing | batch 0 held twice | the gap between tries k and k+1 is at least `TIMEOUT_S` + wait k (less 0.05 s) and at most that plus 1.5 s; from the first try to the end at most 2 × `TIMEOUT_S` + both waits + 3 s |
| last failed try (`refresh`) | batch 1 held three times | 3 tries, then no later batch; `FACET_UNAVAILABLE`, R3's reason; `retries` names 3 tries, both waits, not embedded |
| last failed try (`gov rebuild --json`) | batch 1 held three times | 3 tries, no later batch, not every chunk sent; `stores.semantic` `not_recreated` with R3's reason; then `search(refresh=False)`: `FACET_UNAVAILABLE`, `stale`, no hit (batch 0's vectors may stay) |
| not a time-out (2 cases) | not JSON / no vector | one try, no later batch; the reason exactly `NO_EMBEDDING`; `retries == []` (passes on the base but for `retries`) |
| a server error at every try (revised, P-W2-123-4) | HTTP 500 at every chunk batch | batch 0 tried exactly 3 times, each after its wait (within 0.05 s early, 1.5 s late), no later batch; `FACET_UNAVAILABLE`, the reason beginning `NO_EMBEDDING`; `retries` one entry: 3 tries, both waits, not embedded |

### Choices the run-2 interface leaves open, and how the tests read them

- `waits_s` may hold the configured waits or the measured ones: each is compared within 0.1 s.
- A dropped connection (accepted, closed with no answer) is neither a time-out nor one of R1's listed other failures:
  no case uses it.
- The rebuild's other stages (record store, lexical, code index, compaction) are not asserted; the envelope must be
  `ok`.

## KPI 7's revision (`Rewrite-Reason: P-W2-123-4`; W2-126, DAEO-jpr0; DEC-1042 item 4)

W2-126's seventh success line: "The bounded retry (W2-123, DEC-1026) also covers a transient server error (HTTP 5xx)
and a reset or refused connection, within the same bound, still failing closed after its last try; W2-123's
acceptance case that a 500 is not retried is revised by the test designer with `Rewrite-Reason: P-W2-123-4`"
(evidence: W2-123's rebuild of 2026-11-02 10:39-11:12 ended `not_recreated` after a transient error; the same batch
answered 200 in 2.6 s at 11:16).

- **Revised:** `test_a_failure_that_is_not_a_time_out_ends_the_stage_at_once_without_a_retry[http-error]` (an HTTP 500
  sent once, never retried) left that function's parameters and is now
  `test_a_server_error_at_every_try_is_tried_within_the_bound_and_the_stage_ends_unavailable`: every chunk batch
  answers 500; the first is tried exactly `TRIES` times after each wait in turn, no later batch is sent, the stage
  is `FACET_UNAVAILABLE` with a reason that begins with `NO_EMBEDDING` (R3's exact text says "timed out", which a 500
  is not, and KPI 7 fixes no wording), and `retries` names the request: 3 tries, both waits, not embedded. The
  file's case count is unchanged (9).
- **Kept:** `not-json` and `no-vector` (a malformed answer is not a transient server error) and every time-out case.
- **The rest of KPI 7** (a 5xx or a reset then an answer; a refused connection, once or at every try; a mix of a
  time-out, a 500 and a reset sharing the one bound; an HTTP 400 still not retried) is in W2-126's own suite,
  `tests/acceptance/W2-126/test_w2_126_retry.py`.
- **Red and green.** On `w2/integrate` at `b120aad0f048`: the revised case fails ("the batch that answered HTTP 500
  was not tried 3 times": one try), the other 8 pass. Against a throwaway copy of that `src/` outside the tree whose
  `_ask` reads a 5xx, a `ConnectionError` and a refused `URLError` as a time-out: 9 passed.

