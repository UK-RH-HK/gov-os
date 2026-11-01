# W2-123 acceptance tests (DAEO-qzrq, STANDARD)

Written by the independent test designer (MR-3) from the ticket's KPI lines, DEC-1014 (items 4 and 6), DEC-1015
(item 2), DEC-1017, DEC-1010 item 7, ACT-OLLAMA-CAP-1 and the lead's interface spec for this run ("The outside of
W2-123", S1 to S6), without reading the implementation.

## The interface

Every name is in `gov.retrieval.ollama` (the lead's spec, S1 to S6):

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

| KPI line | Tests | Expected red reason on the base code |
|---|---|---|
| S1: `ensure_available` sets parallel requests and the CPU cap from one value each (defaults from the measure), states them; an unreadable value refuses the start, named, never uncapped | `test_w2_123_start.py::test_shared_start_uses_the_configured_cap_and_parallel_requests_inherited_by_its_runner`, `::test_shared_start_without_configuration_uses_the_default_resolved_from_the_callers_cpus`, `::test_a_server_already_answering_is_used_and_the_settings_a_start_would_use_are_stated`; `test_w2_123_config_invalid.py` (all 14) | the result has no `settings` (the start cases, and the case with the server already answering); the base reads no configuration, so an unreadable value does not stop the start: the planted executable runs as `serve` (the 13 refusal cases) |
| S2: Determinism: parallel requests return the same vector, to the stored precision; a difference refuses | `test_w2_123_determinism.py::test_equal_vectors_are_accepted_with_that_many_requests_in_flight[1,4]`, `::test_a_difference_below_the_stored_precision_is_not_a_difference` | `check_determinism` does not exist (`AttributeError`) |
| S3: Measured in `docs/changes/W2-123-evidence.md`, the setting chosen where the cap is not the limit | `test_w2_123_evidence.py::test_the_evidence_file_holds_the_sixteen_measured_cases_and_the_chosen_setting` (the only test of KPI 3; no test measures) | the file does not exist |
| S4: A product feature: read from the gate's file with the measured defaults; nothing of this machine in the code | `test_w2_123_start.py::test_shared_start_without_configuration_uses_the_default_resolved_from_the_callers_cpus` (the default cap is resolved from the calling process's own CPUs, narrowed by the test, so a machine's CPU numbers in the code fail it), `::test_shared_start_uses_the_configured_cap_and_parallel_requests_inherited_by_its_runner`; `test_w2_123_config_invalid.py` | no `settings`; the configuration is not read |
| S5: Health probe (healthy, slow, hung) and safe restart (hung server stopped, started again under its cap, recorded); never a restart while answering | `test_w2_123_probe.py` (all 7); `test_w2_123_restart.py::test_a_server_that_answers_is_never_restarted[healthy,slow]`, `::test_a_hung_server_of_the_gov_os_is_stopped_with_its_runner_and_started_again_under_its_cap`, `::test_a_port_held_by_another_program_is_never_stopped`, `::test_a_down_server_is_started_under_its_cap_and_recorded`, `::test_an_unreadable_value_stops_and_starts_nothing` | `probe` and `safe_restart` do not exist (`AttributeError`, in the pytest process or in the child) |
| S6: Both servers start under their cap from the gate's file, the query server CPU-only; every restart keeps the cap; a planted start of each shows it | `test_w2_123_start.py::test_query_start_uses_its_own_entry_and_keeps_the_gpu_hidden`, `::test_shared_start_uses_the_configured_cap_and_parallel_requests_inherited_by_its_runner`; `test_w2_123_config_invalid.py::test_an_unreadable_query_entry_refuses_the_query_start`; `test_w2_123_restart.py::test_the_query_server_restarts_under_its_own_cap_cpu_only`, `::test_a_hung_server_of_the_gov_os_is_stopped_with_its_runner_and_started_again_under_its_cap`, `::test_a_down_server_is_started_under_its_cap_and_recorded` | no `settings`; the started process runs on every CPU at the caller's niceness; no `safe_restart` |
| F1: parallel requests that change a vector; a server started uncapped; a setting chosen without its measure | `test_w2_123_determinism.py::test_vectors_changed_by_parallel_requests_refuse_the_setting`, `::test_one_differing_vector_is_named_and_refuses`, `::test_a_missing_vector_refuses`; the cap assertions of `test_w2_123_start.py` and `test_w2_123_restart.py` and every case of `test_w2_123_config_invalid.py` (no uncapped start); `test_w2_123_evidence.py` (no setting without its measure) | as the rows above |

The key edge cases of STANDARD (DEC-221): an unreadable value of each kind S1 names (12 cases: the file not JSON,
not an object, the section and the entry not objects, a key of the wrong type and out of range, a CPU list that
cannot be parsed or names no CPU the caller may run on, a probe time not positive, `probe_slow_s` not below
`probe_hung_s`; and one for the query entry); the query server's cap and hidden GPU (even with
`CUDA_VISIBLE_DEVICES=0` in the environment); the cap inherited by a child (each daemon's runner); a restart refused
while the server answers (healthy and slow) and for a foreign process on the port.

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
