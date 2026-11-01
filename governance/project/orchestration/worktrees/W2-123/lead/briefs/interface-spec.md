## The outside of W2-123 (the lead's interface spec: the same text in both workers' briefs)

The ticket's KPI lines say what must be true; they do not say where the configuration lives, what the start's
result names, or how the health probe, the safe restart and the determinism check are called. So that the test
designer and the engineer, working in parallel and never reading each other's work, meet on the same behaviour, the
lead fixes these public forms for this run (a P3 reading of the lead, inside the ticket's paths, reversible; logged
for the CTO). Everything not fixed here is the implementer's choice, and the tests do not depend on it. Every name
below is in the module `gov.retrieval.ollama`, which today holds `ensure_available`, `ensure_query_available`,
`query_host`, `DEFAULT_HOST`, `QUERY_DEFAULT_HOST`, `NO_GPU` and `WARNING` (read it on `w2/integrate`).

### S1. The configuration (KPIs 1, 4 and 6)

- **The file** is the resource gate's one configuration file (W2-20): `<HOME>/.gov-os/machine/gate.json`, where
  `<HOME>` is the `HOME` of the environment the call is given (`env=`, default the process's own). A test plants it
  under a temporary `HOME`. Other keys of that file are W2-20's and are not read here.
- **The section** is the key `embedding_servers`: an object with up to two entries, `shared` (the server at
  `OLLAMA_HOST`, which `ensure_available` starts) and `query` (the CPU-only one at `GOV_QUERY_OLLAMA_HOST`, which
  `ensure_query_available` starts). Each entry is an object; every key in it is optional:
  - `parallel`: an integer of at least 1, the number of requests the server answers at once. It reaches
    `ollama serve` as Ollama's own setting `OLLAMA_NUM_PARALLEL` in the daemon's environment (the configured value
    wins over any inherited one).
  - `cpus`: the logical CPUs the server and every process it starts may run on, as a string in the CPU-list form of
    `taskset -c` and of `Cpus_allowed_list` in `/proc/<pid>/status` (for example `"2-5,8"`).
  - `nice`: an integer from 0 to 19, the lower priority the server and every process it starts run at (the started
    process's niceness is at least this value).
  - `probe_slow_s` and `probe_hung_s`: positive numbers of seconds, `probe_slow_s` below `probe_hung_s`, used by the
    health probe (S3).
- **Defaults** (no file, no section, no entry, or a key left out): the product's measured defaults, the same on
  every machine; the CPU default is a count, resolved at start to the highest-numbered that many of the CPUs the
  calling process may run on (all of them if it has fewer); nothing of this machine (its CPU numbers) is written in
  the code. The ports stay as today (`OLLAMA_HOST` / `GOV_QUERY_OLLAMA_HOST`, else Ollama's own default and DEC-798's
  product default): they are product defaults, not this machine's. The query server keeps its GPU hidden (`NO_GPU`)
  whatever the configuration says.
- **An unreadable value** (the file not JSON or not an object, `embedding_servers` or an entry not an object, a key
  of the wrong type or out of range, a `cpus` list that cannot be parsed or names no CPU the calling process may run
  on, `probe_slow_s` not below `probe_hung_s`): **the server is not started**. The start's result is
  `available: False`, `started: False`, `state: "CONFIG_INVALID"`, and its `warning` names the file and the key
  (for example `embedding_servers.shared.parallel`); the warning is written once to standard error. Never an
  uncapped start. If the server already answers, it is used as today (`available: True`, `started: False`), and the
  `warning` still names the unreadable value.

### S2. The start and its result (KPIs 1 and 6)

- `ensure_available(*, timeout_s=20.0, env=None)` and `ensure_query_available(*, timeout_s=20.0, env=None)` keep
  their signatures and their present behaviour (the daemon is started as `<executable> serve` with the executable
  found as today, `GOV_OLLAMA_BIN` first, detached, never stopped by them), and **every start of either server is
  capped**: the started process runs on the configured (or default) CPUs at the configured (or default) niceness,
  with its configured (or default) `OLLAMA_NUM_PARALLEL`, and every process it starts inherits the cap. A planted
  executable (`GOV_OLLAMA_BIN` pointing to a script) sees this from inside: its `Cpus_allowed_list`, its niceness,
  its environment, and those of a child it starts.
- **The result** keeps its keys (`available`, `started`, `facet`, `state`, `warning`) and gains `settings`: an object
  with `parallel` (integer), `cpus` (the CPU list applied or to be applied, in the CPU-list form, concrete, e.g.
  `"12-19"`), `nice` (integer) and `source` (the configuration file's path when the values came from it, else
  `"default"`). When the server was already answering, `settings` states the values a start would use. With an
  unreadable value, `settings` is `None`.

### S3. The health probe (KPI 5)

- `probe(server, *, env=None)`, `server` either `"shared"` or `"query"`, sends one fixed text to the server's
  `/api/embed` (the semantic store's model) and returns an object with at least `server`, `host`, `state` and
  `seconds` (the time to the answer, or `None`):
  - `state` `"healthy"`: a vector came back within `probe_slow_s`;
  - `"slow"`: a vector came back after `probe_slow_s` but within `probe_hung_s`;
  - `"hung"`: no vector within `probe_hung_s` (no answer in time, or an answer without a vector);
  - `"down"`: nothing listens at the server's address.
  A probe never starts, stops or restarts anything. An unreadable configuration value: `state` `"CONFIG_INVALID"`,
  naming it, and nothing is sent.

### S4. The safe restart (KPIs 5 and 6)

- `safe_restart(server, *, env=None)`, `server` either `"shared"` or `"query"`, returns an object with at least
  `server`, `host`, `restarted` (bool), `reason` (a string), `probe` (the probe's result it acted on), `settings`
  (as S2), `old_pid` and `new_pid` (integers or `None`):
  - **answering** (`healthy` or `slow`, re-checked immediately before any stop): nothing is stopped or started;
    `restarted` false, `reason` names that it is answering. **A restart never happens while the server answers.**
  - **hung:** the process that listens on the server's port is stopped, together with the processes it started,
    only when its command line is `<executable> serve` for the executable the Gov OS would start (resolved paths
    compared); then the server is started again exactly as S2 starts it (its configured cap and parallel requests),
    and its health is awaited. `restarted` true, `old_pid` and `new_pid` named. A port held by any other process is
    never stopped: `restarted` false, `reason` names the process that holds it.
  - **down:** the server is started as S2 starts it; `restarted` true, `reason` names `down`, `old_pid` `None`.
  - **an unreadable configuration value:** nothing is stopped or started; `restarted` false, `reason` names it.
- **The record:** every call that stops or starts a server appends one JSON line to
  `<HOME>/.gov-os/machine/embedding-restarts.jsonl` (the same `HOME` as S1), with at least `time`, `server`, `host`,
  `probe_state`, `old_pid`, `new_pid`, `restarted` and `settings`. A call that finds the server answering records
  nothing.

### S5. The determinism check (KPI 2 and the failure line)

- `check_determinism(host, references, parallel)`: `host` an endpoint in `OLLAMA_HOST`'s form; `references` a list of
  pairs `(text, expected)`, `expected` the text's vector as the semantic store keeps it (float32, native byte order,
  `struct.pack(f"{n}f", *vector)`); `parallel` an integer of at least 1. It embeds every text in a request of its own
  (the semantic store's model, `{"model": …, "input": [text]}` to `/api/embed`), with `parallel` requests in flight at
  once, packs each answer to float32 the same way, and compares it with `expected` byte for byte (the stored
  precision). It returns an object with `parallel`, `checked` (how many texts), `differing` (the indices whose vector
  differed or was not returned) and `verdict`: `"accepted"` only when every vector came back equal, otherwise
  `"refused"` (a missing answer refuses too).
- A parallel setting is only chosen, or made a default, when this check accepted it on the real embedder against
  vectors made at one request at a time; the evidence file records the check.

### S6. The evidence file (KPI 3)

- `docs/changes/W2-123-evidence.md` holds a table of the 16 measured cases (parallel requests 1, 2, 4 and 8; under
  the configured CPU cap and without it; alone and with three rebuilds' embedding at once), each row with its chunks
  per second and its semantic stage in seconds, and a line beginning `Chosen setting:` that names the parallel
  requests and the CPU cap chosen and why. The lead measures; a later engineer batch writes the file from the lead's
  figures. No test runs the measurement.
