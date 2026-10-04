# W1-18 — Ollama on-demand lifecycle and fallback: acceptance tests

Written by the Independent Test Designer (MR-3, DEC-069) from the KPIs of ticket `DAEO-1ve2` (W1-18), DEC-074 Q4,
ADR-0002 §3 ("Processes") and §4 (the stopping-reason list), the `ollama` row of
`governance/project/tool-registry.yaml`, DEC-221 (profile STANDARD), and the three decisions that answer the first
batch's packages: DEC-260, DEC-261 and DEC-257. Written before implementation. No earlier ticket's test was
rewritten.

Two batches: the first held one test (`71651e81`); the second adds the behavioural tests. The suite now has
**12 test functions, 15 cases**.

## Run

```sh
python3 -m pytest tests/acceptance/W1-18 -q -p no:cacheprovider
```

Standard library and `pytest` only. Nothing is installed. Ollama is not needed and is never run. The whole directory
takes about 9 seconds once the module exists.

- **The function runs in a child process.** Each test starts `python3 -c` with `src/` on `PYTHONPATH`, calls
  `gov.retrieval.ollama.ensure_available(timeout_s=...)` there, and reads the result as JSON. The child's standard
  error is captured. A child that has not ended after 30 s is killed and the test fails as a hang.
- **Stand-ins, in a temporary directory:**
  - a stand-in `ollama` executable that records how it was run (arguments, pid, any keep-alive variable). Its
    `serve` either answers `GET /api/version` with 200 on its own `OLLAMA_HOST` ("healthy") or only sleeps
    ("never");
  - a stand-in endpoint on a free loopback port, given through `OLLAMA_HOST`;
  - recording stand-ins for `systemctl`, `systemd-run` and `loginctl`.
- **Environment, built from scratch:** `PATH` (only the stage's own directory), an empty temporary `HOME`,
  `TMPDIR`, locale, `PYTHONPATH`, `PYTHONDONTWRITEBYTECODE`, `OLLAMA_HOST`, and `GOV_OLLAMA_BIN` when the test sets
  it. So the "no executable" case really has none, and no proxy variable is passed on.
- **No outside network.** Only loopback, to a stand-in the test or the module started.
- **Teardown** ends every stand-in, including a `serve` the module started (by the pid it recorded). A stand-in
  daemon also ends by itself after a minute.

## KPI → tests → red reason today

Red run on `w1/W1-18` at `71651e81` plus this batch: **15 errors, 0 passed, 0 failed**. Every case errors in the
`module` fixture with the same reason:
**`the Ollama lifecycle module does not exist: nothing matches src/gov/retrieval/ollama*`**.

| KPI line | Test file | Test functions | Red reason today |
|---|---|---|---|
| **Success 1a.** gov starts `ollama serve` on demand and relies on the 5-min idle unload (DEC-260, DEC-261) | `test_w1_18_on_demand_start.py` | `test_a_healthy_endpoint_is_used_and_nothing_is_started` · `test_with_the_endpoint_down_ollama_serve_is_started_on_demand[3]` · `test_starting_sets_up_no_unit_and_no_keep_alive_override` · `test_the_started_daemon_is_left_running_and_used_again` | The module does not exist |
| **Success 1b.** No always-on unit | `test_w1_18_no_always_on_unit.py` · `test_w1_18_on_demand_start.py` | `test_the_repository_ships_no_always_on_unit_for_ollama` · `test_starting_sets_up_no_unit_and_no_keep_alive_override` | The module does not exist |
| **Success 2.** When Ollama is unavailable retrieval degrades to FTS-only with a warning and the facet state recorded (DEC-257) | `test_w1_18_fallback.py` | `test_without_an_executable_the_result_is_fts_only_with_the_facet_state` · `test_a_daemon_that_never_becomes_healthy_gives_the_same_degraded_result` · `test_degrading_writes_no_file` | The module does not exist |
| **Failure 1.** A query hangs > 30 s waiting for Ollama (DEC-260) | `test_w1_18_deadline.py` | `test_a_daemon_that_never_becomes_healthy_is_given_up_at_the_deadline` · `test_an_endpoint_that_accepts_and_never_answers_does_not_hang_the_call` · `test_the_default_deadline_is_20_seconds` · every call in the suite (killed and failed after 30 s) | The module does not exist |
| **Failure 2.** Semantic results are silently omitted without a warning (DEC-257) | `test_w1_18_fallback.py` | `test_a_degraded_result_is_never_silent[2]` · the two Success 2 result tests | The module does not exist |

**Count.** KPI lines with tests: 4 of 4 (2 success, 2 failure). Covers ids: the ticket names none.

## How the tests decide

- **The `module` fixture** fails until something matches `src/gov/retrieval/ollama*` (the ticket's `allowed_paths`).
- **The result** is the mapping the function returns. Every call checks it has `available`, `started`, `facet`,
  `state` and `warning`, and that the child ended with exit code 0 (the function never raises for an unavailable
  daemon).
- **Started on demand.** The stand-in executable's record shows one `serve` run when the endpoint was down, and none
  when it was already healthy. The executable is found in each of the three places of DEC-260 (one case each); the
  order between them is not tested.
- **No unit, no keep-alive override.** No stand-in unit command was called, nothing was written under `HOME`, the
  daemon's environment has no variable whose name contains `KEEP_ALIVE`, no argument contains `keep`, and no request
  to the endpoint carries `keep_alive`.
- **Never stopped.** After the child has ended, the test itself asks the endpoint and gets 200. A second call is
  available with `started` false, still one `serve` run, and no `stop` argument.
- **Degraded.** `available` is false, `facet` is `semantic`, `state` is `FACET_UNAVAILABLE`, and `warning` is a
  non-empty string that names Ollama and says FTS-only. The exact warning text appears once in the child's standard
  error. `HOME`, the working directory and `TMPDIR` hold the same files before and after.
- **The deadline.** With `timeout_s=2`, the call itself (timed inside the child) returns within 4 s: when the daemon
  never becomes healthy, and when the endpoint accepts the connection and never answers. The default of `timeout_s`
  is read from the function's signature and is 20.
- **The static test** asks git for `*.service`, `*.socket` and `*.timer` files in the working tree and fails when
  one names Ollama in its file name or its text.

## Readings the decisions do not spell out

1. **"Within the deadline"** allows 2 s on top of `timeout_s` for scheduling. The hard bound is the KPI's 30 s.
2. **"Says results are FTS-only"** is matched as `FTS-only` or `FTS only`, in any letter case. **"Names Ollama"** is
   matched in any letter case.
3. **"Once on standard error"** means the result's `warning` string occurs exactly once in the standard error of the
   call. Other text on standard error is allowed.
4. **"No file is written"** is checked where a module would plausibly write: `HOME`, the working directory and
   `TMPDIR` of the child. The repository's `src/` is protected by `PYTHONDONTWRITEBYTECODE`.
5. **`OLLAMA_HOST`** is given as `127.0.0.1:<port>`, the form of the default. No test gives it with a scheme.
6. **The default deadline** is tested through the signature, not by waiting 20 s.

## Left unasserted, because no decision states it

- The values of `facet`, `state` and `warning` when the daemon is available.
- The value of `started` in a degraded result.
- What `env` means when it is given (the tests leave it `None` and set the child's process environment).
- The order of the three executable locations, and a `GOV_OLLAMA_BIN` that names a missing file.
- Whether a `serve` that never became healthy is left running (teardown ends it either way).
- What the function does with the daemon's output streams.

No KPI line needs any of these, so no package is returned for them.

## Decision packages: all three answered

The full text of the packages is in this file at `71651e81`.

| Package | Question | Decision | Tested as |
|---|---|---|---|
| **DP-1** | The public interface of the lifecycle module | **DEC-260** (owner): `gov.retrieval.ollama.ensure_available(*, timeout_s, env=None)` returns a mapping with `available`, `started`, `facet`, `state` and `warning`, and never raises for an unavailable daemon. Executable: `GOV_OLLAMA_BIN`, then `ollama` on `PATH`, then `~/.local/ollama/bin/ollama`. Endpoint: `OLLAMA_HOST` (default `127.0.0.1:11434`); healthy means `GET /api/version` answers 200. The default total deadline is 20 s and covers the probe, the start and the wait. `src/gov/retrieval/__init__.py` joins the ticket's `allowed_paths`. | Every behavioural test |
| **DP-2** | Does `gov` stop the daemon | **DEC-261** (owner): start on demand, never stop. No keep-alive override, no unit, no `stop`. Ollama's 5-minute idle unload frees the model's memory. | `test_w1_18_on_demand_start.py` |
| **DP-3** | What "the facet state recorded" means | **DEC-257** (delegated): the result names facet `semantic`, state `FACET_UNAVAILABLE` and a non-empty warning that names Ollama and says results are FTS-only. The warning is also written once to standard error. No file is written. The module does not set a bundle's stopping reason. | `test_w1_18_fallback.py` |

The three decisions are recorded on the integration branch. This branch does not contain them yet; their content
reached this batch through the ticket lead's request.

## Not written

- The `local_only` case against the real daemon, planned in the first batch. Ollama is not on this machine's `PATH`,
  nothing is installed in this ticket, and no KPI line needs it.
- "Endpoint answers with an error", planned in the first batch. It is the same path as an endpoint that is down
  (healthy means 200), so it would add a case without a KPI behind it (DEC-221).

## Observations for the ticket lead (no test depends on them)

1. The registry note says "The embedding model enters the registry with W1-18" (DEC-195).
   `governance/project/tool-registry.yaml` is not in the implementer's `allowed_paths`, and nothing is installed in
   this ticket. No KPI line asks for the row, so no test asserts it.
2. G-22 is cited by the ticket but exists in the repository only as one line of `docs/spec/gov-os/READINESS.md`
   ("Ollama health check, FTS-only fallback"). Its text is in the archived sources, which this role does not read
   (DEC-222 is for product-spec workers).
3. ADR-0002 §3 still says the daemon is "started and stopped by `gov`", and the ticket body says "start and stop".
   DEC-261 decides there is no stop; the two texts were not changed by this role.
4. A daemon the function starts may inherit the caller's output streams. A caller that reads them through a pipe
   would then wait for the daemon. The tests avoid this by sending the child's streams to files, so they do not
   assert it either way.
