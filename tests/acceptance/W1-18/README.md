# W1-18 — Ollama on-demand lifecycle and fallback: acceptance tests

Written by the Independent Test Designer (MR-3, DEC-069) from the KPIs of ticket `DAEO-1ve2` (W1-18), DEC-074 Q4,
ADR-0002 §3 ("Processes") and §4 (the stopping-reason list), the `ollama` row of
`governance/project/tool-registry.yaml`, and DEC-221 (profile STANDARD). Written before implementation. No earlier
ticket's test was rewritten.

**This is a first batch: one test.** The sources do not fix the public interface of the module, so the behavioural
tests wait for the three decision packages below. Nothing was guessed.

## Run

```sh
python3 -m pytest tests/acceptance/W1-18 -q -p no:cacheprovider
```

Standard library and `pytest` only. No network. Nothing is installed. Ollama is not needed.

## KPI → tests → red reason today

Red run on `w1/W1-18` at `5203ab3c`: **1 error, 0 passed, 0 failed**. The case errors in the `module` fixture:
**`the Ollama lifecycle module does not exist: nothing matches src/gov/retrieval/ollama*`**.

| KPI line | Test file | Test functions | Red reason today |
|---|---|---|---|
| **Success 1a.** gov starts `ollama serve` on demand and relies on the 5-min idle unload | — | none yet: waits for DP-1 and DP-2 | — |
| **Success 1b.** No always-on unit | `test_w1_18_no_always_on_unit.py` | `test_the_repository_ships_no_always_on_unit_for_ollama` | The module does not exist |
| **Success 2.** When Ollama is unavailable retrieval degrades to FTS-only with a warning and the facet state recorded | — | none yet: waits for DP-1 and DP-3 | — |
| **Failure 1.** A query hangs > 30 s waiting for Ollama | — | none yet: waits for DP-1 | — |
| **Failure 2.** Semantic results are silently omitted without a warning | — | none yet: waits for DP-1 and DP-3 | — |

**Count.** KPI lines with a test: 1 of 4, and that one only in part (2 success, 2 failure lines). Covers ids: the
ticket names none.

## How the test decides

- The `module` fixture fails until something matches `src/gov/retrieval/ollama*` (the ticket's `allowed_paths`). It
  assumes nothing else about the module.
- The test asks git for `*.service`, `*.socket` and `*.timer` files in the working tree (tracked, or untracked and not
  ignored) and fails when one names Ollama in its file name or its text. No other file is listed or read.
- This is the static half of "no always-on unit". The behavioural half (starting the daemon calls no `systemctl`,
  observed through a recording stand-in on `PATH`) needs the entry point of DP-1.

## Planned second batch (after the packages are answered)

All through a stand-in `ollama` executable and a stand-in loopback endpoint in a temporary directory:

- Endpoint down and executable present: `serve` is started once, and the caller gets an available result.
- Endpoint already up: nothing is started.
- Starting sets up no unit (no `systemctl` call) and passes no setting that keeps the model loaded beyond 5 minutes.
- Executable absent: FTS-only, with a warning and the facet state.
- Executable present but the endpoint never answers: the call returns within the bound, FTS-only, with a warning.
- Endpoint answers with an error: FTS-only, with a warning.
- Every degraded result carries the warning; none is silent.
- One `local_only` case against the real daemon, skipped when it is absent.

## Decision packages

### DP-1 — The public interface of the lifecycle module

- **Question.** Through what do callers, and these tests, use the module?
  - (i) the entry point: its module path, its name and its arguments;
  - (ii) how the `ollama` executable is found;
  - (iii) how the endpoint is found, and which request counts as "healthy";
  - (iv) how the wait bound is set, so a test need not wait 30 s;
  - (v) how the outcome is returned.
- **Why now.** Three and a half of the four KPI lines are behavioural. There is no `gov` command for this module
  (W1-19 and W1-21 consume it later), and no source names any of (i) to (v).
  - The `allowed_paths` give only `src/gov/retrieval/ollama*`.
  - The registry note gives one location, `~/.local/ollama/bin/ollama`.
  - Without an answer, every behavioural test would fix the interface by guessing.
- **Options.**
  - (a) **One function in `gov.retrieval.ollama`.**
    - `ensure_available(*, timeout_s=30.0, env=None)` returns a mapping: `available` (boolean), `started` (boolean),
      `facet` (`"semantic"`), `state`, and `warning` (a string, or `None` when available).
    - Executable: `GOV_OLLAMA_BIN` if set, otherwise `ollama` on `PATH`, otherwise `~/.local/ollama/bin/ollama`.
    - Endpoint: Ollama's own `OLLAMA_HOST`, default `127.0.0.1:11434`. Healthy means `GET /api/version` answers 200.
    - It never raises for an unavailable daemon.
  - (b) **A module command line.** `python3 -m gov.retrieval.ollama --json` prints the same mapping as one JSON
    object. The tests run it as a child process, as the W1-07 suite runs `gov`. The same environment variables
    apply, plus `--timeout`.
  - (c) **Both.** The function of (a), with (b) as a thin wrapper.
  - (d) **Wait.** Give W1-18 no behavioural acceptance tests, and test it through `gov retrieve` in W1-21.
- **Impact.**
  - (a) is the smallest and fits the 40 LOC estimate. The tests import the module in-process, so a stalled start
    needs a watchdog in the tests.
  - (b) adds about 15 LOC. It gives process isolation and a hard kill on a hang, which makes the 30 s line easy to
    test honestly.
  - (c) costs the most code.
  - (d) leaves W1-18 with one static test, and moves its four KPI lines to a FULL ticket two steps later.
- **Reversibility.** High for all four. Only W1-19 and W1-21 will call it and neither is written. Renaming later means
  rewriting this suite's support module, reported as a rewrite.
- **Cost.** (a) about 40 LOC and about 10 tests. (b) about 55 LOC and the same tests. (c) about 60 LOC. (d) none
  now.
- **Recommendation.** (a), with the environment variables and the `timeout_s` argument exactly as listed. The tests
  call it in a child `python3` process they start themselves, so a hang is still killed.
- **Confidence.** Medium. The shape is conventional. The names are my proposal, not a source's.

### DP-2 — Does `gov` stop the daemon, and what does "5-min idle unload" bind?

- **Question.** The sources disagree on stopping.
  - ADR-0002 §3: "started and stopped by `gov`".
  - The ticket body: "On-demand start and stop".
  - The KPI: "starts ollama serve on demand and relies on the 5-min idle unload".
  - Ollama's 5-minute idle behaviour (`keep_alive`) unloads the model from memory. It does not end the `serve`
    process.
- **Why now.** It decides what Success 1a asserts after a query:
  - that the `serve` process is still running;
  - that it has been stopped;
  - or only that nothing overrides the 5-minute default.
- **Options.**
  - (a) **Start only.** `gov` starts `serve` when needed and never stops it. The model unloads after 5 idle minutes
    by Ollama's default, and the idle process stays. The tests assert that no `OLLAMA_KEEP_ALIVE` or `keep_alive`
    longer than 5 minutes is set, and that no unit is set up.
  - (b) **Start, plus an explicit stop function.** A `stop()` ends a `serve` that `gov` itself started. A later
    ticket calls it (`gov doctor`, or the session end). The tests assert that `stop()` ends only a daemon the module
    started.
  - (c) **Start and stop on every query.** The process is ended after each call.
- **Impact.**
  - (a) matches the KPI wording and the estimate. It leaves an idle process (small, with no model loaded), against
    the ADR's "stopped by gov".
  - (b) satisfies both texts and adds about 15 LOC and 2 tests.
  - (c) defeats the warm p95 of 0.5 s that W1-19 needs.
- **Reversibility.** High. Adding `stop()` later is additive.
- **Cost.** (a) none extra. (b) about 15 LOC. (c) a cold start on every query.
- **Recommendation.** (a) for W1-18, with the ADR's "stopped" read as "not kept alive by a unit". If the owner wants
  a real stop, (b).
- **Confidence.** Medium-high that (c) is wrong. Medium between (a) and (b).

### DP-3 — What "the facet state recorded" means

- **Question.** Which value is recorded, for which facet, and where?
- **Why now.** Success 2 and Failure 2 assert it.
  - ADR-0002 §4 and DEC-034 give `FACET_UNAVAILABLE` only as a bundle stopping reason ("index stale/down").
  - The facets the sources name are decisions, code, tests, history, why, and lessons/failures. None is called
    "semantic".
  - No source gives a place for the record: the returned value, standard error, or a file under `.gov-runtime/`.
- **Options.**
  - (a) **In the result.** The outcome carries `facet: "semantic"`, `state: "FACET_UNAVAILABLE"` and a non-empty
    `warning`. The same warning is written once to standard error. No file is written. W1-21 copies the state into
    the bundle.
  - (b) **Also in a file.** As (a), plus a line appended to a file under `.gov-runtime/`, for `gov doctor` and
    `gov status`.
  - (c) **Warning only.** A boolean `available` and a warning. The bundle's facet state is left to W1-21.
- **Impact.**
  - (a) makes "recorded" testable here, without a write path outside the ticket's `allowed_paths` story.
  - (b) needs a file name and format that no source gives, and a reader that does not exist yet.
  - (c) makes half of Success 2 untestable in W1-18.
- **Reversibility.** High for (a) and (c). Medium for (b), because a file format gains readers.
- **Cost.** (a) inside the estimate. (b) about 10 LOC more and a format decision. (c) the least.
- **Recommendation.** (a). The warning text must name Ollama and say that results are FTS-only.
- **Confidence.** Medium. `FACET_UNAVAILABLE` is the only state word the sources offer. "semantic" as the facet name
  is my reading of DEC-033 ("the semantic facet").

## Observations for the ticket lead (no test depends on them)

1. `src/gov/retrieval/` does not exist, and `src/gov/retrieval/__init__.py` is not matched by the implementer's
   `allowed_paths` (`src/gov/retrieval/ollama*`). The module still imports from `src/` as a namespace package, but
   `[tool.setuptools.packages.find]` would not package it.
2. The registry note says "The embedding model enters the registry with W1-18" (DEC-195).
   `governance/project/tool-registry.yaml` is not in the implementer's `allowed_paths`, and nothing is installed in
   this ticket. No KPI line asks for the row, so no test asserts it.
3. G-22 is cited by the ticket but exists in the repository only as one line of `docs/spec/gov-os/READINESS.md`
   ("Ollama health check, FTS-only fallback"). Its text is in the archived sources, which this role does not read
   (DEC-222 is for product-spec workers).
