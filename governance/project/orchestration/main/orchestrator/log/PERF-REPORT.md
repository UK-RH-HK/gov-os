# Test run time: profile of `gov close` and a trial of parallel runs

Measured 2026-10-08, 17:18 to 22:10 BST, by a sandboxed session (role `independent-auditor`, ticket `DAEO-6mk8`).
Figures and causes only; no recommendation. (This file holds no apostrophe and no angle bracket: the guard hook of
the session refused a write whose text held either.)

## What was measured, and where

| | |
|---|---|
| Commit | `01a9997f14f310b6656c0d5f537a5bf34052c0f0`, branch `w1/perf`, worktree `/home/usain/gov-os-worktrees/perf` |
| Machine | WSL2, Linux 6.18.33.2; 12th Gen Intel Core i7-12700F; 20 logical CPUs (psutil reports 10 physical cores); 23 GB memory |
| Versions | Python 3.12.3, pytest 9.0.3, pytest-xdist 3.8.0 |
| `-n auto` | **10 workers** (`created: 10/10 workers`) |
| Load from other sessions | 1-minute load average between 2.5 and 39 over the session; given beside every time below |

All times are wall-clock seconds of one run each (two for the serial unit tests and W1-02). The raw line of every run
(label, seconds, exit code, load before, load after, command) is in `times.tsv`; the output of each run is `out/LABEL.out`.

**The load varied by a factor of ten between runs, and it moved the serial times**: the unit tests took 58.8 s at load 3,
80.2 s at load 10 and 115.5 s at load 27, the same command each time. Read every ratio with its two load figures.

## Part (a): profile of `gov close` as it is today

### The one run of `gov close DAEO-2lwj`

`PYTHONPATH=src python3 -m cProfile -o out/close.prof -m gov.cli.main close DAEO-2lwj --json --role orchestrator --timeout 7200`:
**0.111 s**, load 7.19 before and after. It refused before any gate and before any test run:

    {"ok": false, "command": "close", ..., "error": {"code": "STALE_EVIDENCE", "message": "ticket DAEO-2lwj is already closed", ...}}

`run()` in `src/gov/close/command.py` raises this at line 132, before the tree check, the store check and every gate.
It is a `GovError`, not a finding: nothing was counted, no repair ticket was made. The shell showed exit code 0 for
this call because it ran under `cProfile`; the code of the command itself is 3 by the source. It was not run a second
time. The phases below therefore come from separate timed runs.

### What `gov close` does, in order (read from `src/gov/close/command.py`)

1. Ticket file read; refusal if closed; iteration count read.
2. `_check_tree` (`git status`), `_check_store` (the store holds `HEAD` and as many commits as its history).
3. The commits of the ticket, the other commits of its range, the tickets of the project.
4. Gates, all asked whatever an earlier one found: probe (FULL only), trailers, work without a task, containment
   (`judge_commits`), **acceptance run** (`pytest tests/acceptance/WBS`), **regression run** (`pytest tests`
   with `--ignore tests/acceptance/WBS`), governance checks (`run_checks`, only when a commit of the range changes a
   governance file), checkpoint watchdog, context packet.
5. Refusal with every finding, or checkpoint + close record + the ticket tool.

Both test runs are one child process each: `python3 -m pytest PATH -q -p no:cacheprovider --tb=line --no-header`,
with `PYTHONPATH=ROOT/src` set **for the acceptance suites too** (the project runs acceptance suites without
`PYTHONPATH`; part (b) uses that form). `gov close` runs no store rebuild itself: it refuses with `STORE_STALE` when
the store is not of `HEAD`.

### Phases

| Phase | Seconds | Load before / after | How measured |
|---|---|---|---|
| `gov rebuild --json` (step 1, as ordered) | **not measured: did not finish.** Stopped by the harness after about 44 min (started 17:19:08, killed about 18:03) | 8.50 / not read | one run; foreground limit of 600 s, then the 30 min background limit of the harness |
| `gov rebuild --json` with the embedding endpoint unreachable (`OLLAMA_HOST=127.0.0.1:9 GOV_OLLAMA_BIN=/bin/false`) | 161.0 (holds up to 20 s of waiting for the endpoint) | 10.75 / 39.35 | one separate run; the semantic store `not_recreated`, the code index `not_recreated` (sandbox, below) |
| `gov close` as a whole on the closed ticket | 0.111 | 7.19 / 7.19 | the one run of step 2 |
| `_check_tree` | 0.046 | 37.40 / 15.87 | in-process, `gates.py` (calls the gate functions of `gov.close.command` for DAEO-2lwj in the order of `run()`; nothing recorded) |
| `_check_store` | 0.012 | same run | same |
| ticket commits + range + tickets | 0.076 | same run | same (55 commits of the ticket, 212 others in its range) |
| probe gate | 0.036 | same run | same |
| trailers gate | under 0.001 | same run | same |
| work-without-task gate | 0.001 | same run | same |
| containment (`judge_commits`, 55 commits) | 0.912 (0.947 in the first run) | same run | same |
| governance checks (`run_checks`, what `gov check` runs) | **66.3** at load 37; **18.0** at load 11 | 37.40 / 15.87; 10.65 / 9.70 | same; the 18.0 s run was made while the store was unreadable (below), so some checks may have ended early |
| checkpoint watchdog | 0.004 | same run | same |
| context packet | 0.004 | same run | same; it ended at its first finding (`BLOCKED: mandatory input S0a-G-12 not found`), so a packet that builds is not measured |
| **acceptance run**, `tests/acceptance/W1-30`, 290 passed | **576.4** | 13.66 / 2.92 | separate run of the command the close uses, plus `--durations=40 --durations-min=1.0` |
| **regression run**, everything else under `tests/` | **3137.8 + two suites that did not finish** | per suite, below | separate run per suite in the form the close uses (one call would have passed the 40 min limit of the harness); the sum holds one interpreter start per suite that the single call does not have |

Every gate of `gates.py` on DAEO-2lwj gave a finding or an error (probe, trailers, work without task, containment,
checks, checkpoint, context; `_check_tree` gave `TREE_NOT_COMMITTED` for the placeholders of the sandbox, see "left
behind"). The times are of gates that found something.

Measured total of what a close of this ticket would run, without the rebuild: gates 67 s (at load 37) + acceptance
576 s + regression 3138 s = **about 3780 s (63 min)**, plus W1-19 and W1-21 (each over 36 min here, not finished) and
the real-session cases the sandbox cannot run.

### The regression run, suite by suite (the form the close uses, `PYTHONPATH=src`)

| Suite | Seconds | Load before / after | Result |
|---|---|---|---|
| tests/unit | 58.8 | 2.77 / 2.86 | 1512 passed |
| W1-01 | 5.2 | 2.71 / 2.49 | 46 passed, 28 skipped |
| W1-02 | 120.1 | 2.49 / 2.71 | 529 passed |
| W1-03 | 103.8 | 2.71 / 3.51 | 364 passed |
| W1-04 | 113.1 | 3.51 / 3.36 | 336 passed |
| W1-05 | 366.5 | 3.17 / 3.60 | 99 passed (338 s of it is one case that runs W1-02, W1-03 and W1-04 again) |
| W1-06 | 0.9 | 3.60 / 3.60 | 96 passed |
| W1-07 | 146.5 | 3.60 / 2.93 | 218 passed |
| W1-08 | 63.7 | 2.93 / 3.33 | 209 passed |
| W1-09 | 32.8 | 3.33 / 3.06 | 76 passed, 1 failed (sandbox) |
| W1-10 | 11.9 | 3.21 / 3.24 | 76 passed |
| W1-11 | 16.9 | 3.24 / 3.19 | 142 passed |
| W1-12 | 4.8 | 3.19 / 3.25 | 21 passed |
| W1-13 | 34.7 | 3.25 / 3.43 | 110 passed |
| W1-14 | 9.3 | 3.43 / 3.36 | 63 passed |
| W1-15 | 62.0 | 3.36 / 6.77 | 92 passed |
| W1-16 | 0.9 | 6.39 / 6.39 | 8 passed, **158 errors (sandbox): time not representative** |
| W1-17 | 66.9 | 6.39 / 13.92 | 65 passed |
| W1-18 | 8.9 | 13.92 / 12.97 | 15 passed |
| W1-19 | **not measured: did not finish** | | 11 cases passed, then no output for over 36 min; killed by the harness with its batch |
| W1-20 | 19.3 | 23.45 / 26.25 | 42 passed, 9 errors (sandbox) |
| W1-21 | **not measured: did not finish** in 520 s, nor in 2200 s | 10.73 / 29.04 | 72 of 126 cases passed in about 9 min, then no output until the 2200 s bound |
| W1-22 | 11.7 | 31.96 / 32.16 | 25 passed |
| W1-23 | 1.3 | 32.16 / 32.16 | 10 passed |
| W1-24 | 9.0 | 31.67 / 29.29 | 54 passed |
| W1-25 | 224.6 | 29.29 / 28.06 | 49 passed, 3 errors (real session, sandbox); 172.5 s of it is the set-up of the failed session |
| W1-26 | 282.7 | 19.53 / 16.54 | 294 passed, 1 skipped |
| W1-27 | 282.0 | 28.06 / 19.21 | 123 passed, 1 failed (sandbox) |
| W1-28 | 70.3 | 19.21 / 19.74 | 149 passed |
| W1-29 | 3.6 | 19.74 / 19.74 | 45 passed |
| W1-33 | 5.0 | 16.54 / 15.45 | 113 passed |
| W1-34 | 0.6 | 15.45 / 15.45 | 8 passed |
| W1-35 | 44.4 | 15.45 / 19.42 | 112 passed |
| W1-36 | 5.5 | 19.42 / 18.35 | 84 passed |
| W1-37 | 0.3 | 18.35 / 18.35 | 4 passed |
| W1-38 | 98.0 | 18.35 / 7.00 | 87 passed |
| W1-39 | 117.4 | 7.00 / 4.69 | 67 passed |
| W1-40 | 58.3 | 4.69 / 3.99 | 74 passed |
| W1-44 | 1.8 | 3.99 / 3.99 | 5 passed |
| W1-45 | 23.1 | 3.99 / 3.77 | 105 passed |
| W1-46 | 128.6 | 3.50 / 13.23 | 457 passed; `test_w1_46_live_sessions.py` (36 cases, real sessions) left out |
| W1-47 | 279.7 | 13.23 / 22.56 | 970 passed |
| W1-48 | 1.1 | 22.56 / 22.56 | 172 passed |
| W1-49 | 15.2 | 22.56 / 20.32 | 96 passed; `test_w1_49_live_session.py` (9 cases, real sessions) left out |
| W1-50 | 226.8 | 19.01 / 11.49 | 664 passed; its 2 real-session cases left out |
| **Sum of the suites that finished** | **3137.8** | | |

The ten slowest suites that finished: W1-30 576, W1-05 367, W1-26 283, W1-27 282, W1-47 280, W1-50 227, W1-25 225,
W1-07 147, W1-46 129, W1-02 120.

### The 20 slowest cases

From `--durations=40 --durations-min=1.0` of the run of each suite above (the form the close uses). W1-19 and W1-21
gave no durations (they did not finish); the cases they stopped in are slower than everything from rank 3 down.

| # | Seconds | Suite | Case |
|---|---|---|---|
| 1 | 337.94 | W1-05 | `test_w1_05_switch_over_record.py::test_the_dependencies_pass_their_acceptance_tests_at_the_switch_over` |
| 2 | 172.49 (set-up, failed) | W1-25 | `test_w1_25_live_session.py::test_the_session_states_the_ticket` (the start of the real session, refused by the sandbox; not its time outside it) |
| 3 | 15.55 | W1-04 | `test_w1_04_only_escalates.py::test_the_hook_never_gives_an_explicit_allow` |
| 4 | 11.50 | W1-27 | `test_w1_27_doctor.py::test_doctor_real_registry_every_entry_reported` |
| 5 | 10.05 | W1-38 | `test_w1_38_rulesync.py::TestToolAbsentOrHanging::test_timeout_handling` |
| 6 | 7.95 (set-up) | W1-17 | `test_w1_17_dev_tier.py::test_the_whole_tier_is_indexed_and_no_canary_reaches_the_store` |
| 7 | 7.95 | W1-30 | `test_w1_30_iteration.py::test_mixed_causes_reach_escalation` |
| 8 | 7.80 | W1-17 | `test_w1_17_dev_tier.py::test_a_rebuild_of_the_tier_gives_the_same_digest` |
| 9 | 7.77 | W1-27 | `test_w1_27_adoption.py::test_doctor_report_mentions_adoption_level` |
| 10 | 7.77 | W1-15 | `test_w1_15_filter.py::test_no_dev_canary_is_in_a_file_an_indexer_may_read[a-dev]` |
| 11 | 7.72 | W1-15 | `test_w1_15_filter.py::test_no_dev_canary_is_in_a_file_an_indexer_may_read[b-dev]` |
| 12 | 7.50 | W1-30 | `test_w1_30_iteration.py::test_iteration_count_hidden_across_multiple_failures` |
| 13 | 7.49 | W1-30 | `test_w1_30_iteration.py::test_owner_decision_checker_failing_refuses` |
| 14 | 7.40 (set-up) | W1-26 | `test_w1_26_authority.py::test_research_cited_as_decision_is_red` |
| 15 | 7.32 | W1-27 | `test_w1_27_doctor_r5.py::test_stale_path_in_historical_record_is_not_reported[bootstrap]` |
| 16 | 7.02 | W1-09 | `test_w1_09_review.py::test_releases_and_claims_raced_from_separate_processes_never_remove_another_holders_claim` |
| 17 | 6.96 | W1-27 | `test_w1_27_rebuild_r4.py::test_rebuild_stores_hold_no_secret` |
| 18 | 6.85 | W1-27 | `test_w1_27_path_compliance.py::test_full_coverage_is_healthy` |
| 19 | 6.85 | W1-27 | `test_w1_27_isolation_r2.py::test_doctor_isolation_is_measured_not_constant` |
| 20 | 6.36 | W1-09 | `test_w1_09_claims.py::test_claims_raced_from_separate_processes_give_exactly_one_holder` |

The 576 s of W1-30 are spread over 290 cases of 2 to 8 s each (its 40 slowest end at 2.9 s); it has no single slow case.

## Part (b): trial of parallel runs

Form: acceptance suites `env -u PYTHONPATH python3 -m pytest tests/acceptance/SUITE -q -p no:cacheprovider --tb=short`,
unit tests `PYTHONPATH=src python3 -m pytest tests/unit -q -p no:cacheprovider --tb=short`; the parallel arm adds
`-n auto` (10 workers). Driver: `arms.py`.

### Cases set apart (found by reading)

In the selections timed:

| Node id | Reason | Run |
|---|---|---|
| `tests/acceptance/W1-02/test_w1_02_guard_hook.py::test_decision_p95_is_under_100_ms` (5 parameter sets) | asserts p95 under 100 ms over 40 hook processes | serial, apart |
| `tests/acceptance/W1-05/test_w1_05_live_hooks.py::test_a_call_waits_under_100_ms_p95_for_the_hook` (9 parameter sets) | asserts p95 under 100 ms | serial, apart |
| `tests/acceptance/W1-05/test_w1_05_switch_over_record.py::test_the_dependencies_pass_their_acceptance_tests_at_the_switch_over` | runs W1-02, W1-03 and W1-04 in a child `pytest -x`, so it holds the five p95 cases of W1-02. Found by the profile and by its first serial run, where it failed on the inner `p95 decision time per round (ms): 152.4, 179.7, 135.1` | serial, apart |
| `tests/acceptance/W1-50/test_w1_50_review_of_the_symmetric_rule.py::test_read_merge_answers_for_a_merge_commit_with_very_many_parents_in_time_and_never_calls_the_undone_test_brought` | asserts an answer within `HOOK_TIMEOUT_S / 3`, by `SIGALRM` | serial, apart |
| `tests/acceptance/W1-50/test_w1_50_freeze_live_pause.py::test_a_flag_put_over_the_placeholder_during_a_command_stays` | launches a real worker session | **not run: the sandbox cannot** |
| `tests/acceptance/W1-50/test_w1_50_freeze_launcher.py::test_a_launched_session_leaves_no_placeholder_at_the_flag_s_path` | launches a real worker session | **not run: the sandbox cannot** |

Why the two real-session cases were not started: the one real session a suite did start here (W1-25, in part (a)) ended
after 172 s with an `API Error` line naming `ERR_PROXY_TUNNEL` ("the proxy refused the tunnel"), the sandbox reporting
`deny network-outbound api.anthropic.com:443`. After that, no case that launches a session was started.

W1-47, W1-26, W1-27, W1-30 and `tests/unit`: no case that asserts a time bound or starts a real session or daemon was
found by reading ("live" in W1-47 is the hook wiring driven as processes, not a session).

In suites not timed in part (b), for whoever runs them in parallel later:

- Real sessions: `W1-25/test_w1_25_live_session.py` (3 cases), `W1-46/test_w1_46_live_sessions.py` (36), `W1-49/test_w1_49_live_session.py` (9).
- Time bounds: `W1-19/test_w1_19_real_models.py::test_a_warm_query_answers_within_half_a_second_at_p95`;
  `W1-18/test_w1_18_deadline.py` (two cases on `elapsed_s` against `BOUND_S`); `W1-07/test_w1_07_help.py` (median under
  `HELP_BUDGET_S`); `W1-10/test_w1_10_dev_tier.py` (`FULL_LOAD_LIMIT_S`); `W1-17/test_w1_17_dev_tier.py` (`REINDEX_LIMIT_S`).
- A real daemon or real models: W1-16 (codebase-memory daemon; all its `local_only` cases), `W1-20/test_w1_20_code.py`,
  `W1-19/test_w1_19_real_models.py`, `W1-21/test_w1_21_dev_tier.py` (Ollama models; the cases W1-19 and W1-21 stopped in).
- Races between processes by design: `W1-09/test_w1_09_review.py` and `test_w1_09_claims.py` (claims raced from separate processes).

### Serial against parallel, per selection

| Selection (without the cases set apart) | Cases | Serial s | Load before / after | Parallel s | Load before / after | Ratio | Failing only in parallel |
|---|---|---|---|---|---|---|---|
| tests/unit | 1512 | 80.2 (first sample 115.5 at load 27) | 9.69 / 9.77 | 18.9 | 11.34 / 19.94 | 4.2 (6.1 with the first sample) | 1 |
| W1-02 | 524 | 210.6 (first sample 219.4 at load 28) | 9.77 / 15.21 | 22.7 | 19.94 / 18.21 | 9.3 | 0 |
| W1-47 | 970 | 281.7 | 21.66 / 10.42 | 36.4 | 18.21 / 19.91 | 7.7 | 0 |
| W1-50 | 663 | 206.2 | 19.91 / 6.54 | 41.1 | 6.54 / 9.45 | 5.0 | 24 (one file) |
| W1-30 | 290 | 703.8 | 11.87 / 6.64 | 99.7 | 10.50 / 12.64 | 7.1 | 0 |
| W1-26 | 294 + 1 skipped | 235.8 | 7.29 / 12.26 | 37.8 | 10.09 / 12.24 | 6.2 | 0 |
| W1-27 | 124 | 253.4 | 14.39 / 8.04 | 68.6 | 6.71 / 27.53 | 3.7 | 0 (1 fails in both arms) |
| W1-05 | 89 | 15.6 | 12.16 / 10.28 | 4.6 | 10.28 / 10.50 | 3.4 | 0 |
| **Sum** | | **1987.3** | | **329.8** | | **6.0** | 25 |

W1-30, W1-26 and W1-27 are the three slowest suites that finished besides the named ones; W1-05 is kept because the
profile put it second, though without its nested case it is 16 s. W1-19 and W1-21 were not taken: neither finished serially.

One more figure, from before the nested case of W1-05 was set apart: W1-05 with that case took **444.8 s under `-n auto`**
(90 passed) against 366.5 s serially in part (a): the inner serial run of three suites competes with the nine other workers.

### The combined calls

| Call | Seconds | Load before / after | Result |
|---|---|---|---|
| Acceptance: W1-02, W1-05, W1-26, W1-27, W1-30, W1-47, W1-50 in one `pytest -n auto` | **432.0** | 27.53 / 9.69 | 2929 passed, 1 skipped, 25 failed (the same 24 of W1-50 and the 1 of W1-27) |
| Unit: `tests/unit` in one `pytest -n auto` | 18.9 | 11.34 / 19.94 | the unit row above (it is the same call; not run a second time) |

The seven acceptance suites took 310.8 s as seven parallel calls one after another and 432.0 s as one call; the one call
began at load 27.5. Against their serial sum of 1907.2 s that is 6.1 times and 4.4 times.

### The cases set apart, serial, on their own

| Cases | Seconds | Load before / after | Result |
|---|---|---|---|
| W1-02, 5 p95 cases | 10.6 | 7.72 / 7.45 | 5 passed |
| W1-50, the read-merge time bound | 8.3 | 7.45 / 7.47 | 1 passed |
| W1-05, 9 p95 cases and the nested-suites case | 554.9 | 7.47 / 15.59 | 5 passed, **5 failed** (below) |
| **Sum** | **573.7** | | |

### Overall, everything timed in both arms, with the set-apart time added to both sides

| | Serial | Parallel | Ratio |
|---|---|---|---|
| Selections only | 1987.3 | 329.8 (separate calls) | 6.0 |
| + set-apart cases (573.7 on both sides) | **2561.0** | **903.5** | **2.8** |
| the same with the combined calls (432.0 + 18.9 + 573.7) | 2561.0 | 1024.6 | 2.5 |

With the first serial samples of the unit tests and W1-02 the serial side is 2605.2 and the ratios are 2.9 and 2.5.

### Cases that fail only in parallel

**1. `tests/unit/pause/test_pause.py::test_the_chain_read_from_proc_is_this_process_first_and_each_next_one_its_parent`**

    E   AssertionError: assert (/usr/bin/python3.12 == /usr/bin/python3.12
    E     and "pytest" in "/usr/bin/python3 -u -c import sys;exec(eval(sys.stdin.readline()))")

(quotation marks changed for this file; the lines as printed are in `out/b_par_unit.out`.)

Cause: the case asserts that the word `pytest` is in the command line of its own process (line 199). An xdist worker
is started by execnet as `python3 -u -c import sys;exec(eval(sys.stdin.readline()))`, so the word is not there. No
shared path, port or state. Alone, serially: passed (0.24 s). The fix lies in the test (what it expects of its own
command line); the product code reads the chain correctly.

**2. All 24 cases of `tests/acceptance/W1-50/test_w1_50_judge_commits.py`** (17 functions; one with 8 parameter sets)

    tests/acceptance/W1-50/test_w1_50_judge_commits.py:50: in _judge
        from gov.guard.containment import judge_commits
    E   ModuleNotFoundError: No module named gov

Cause: the order of cases within one process. The file imports `gov` inside its helper without putting `src` on the
import path, and the acceptance form has no `PYTHONPATH`. Other W1-50 files put `src` there for the length of one case
(`monkeypatch.syspath_prepend(str(SOURCES))` in `test_w1_50_read_merge_helper.py`, `test_w1_50_read_merge_every_parent.py`,
`test_w1_50_review_of_the_symmetric_rule.py`, `w1_50_own_change_support.py`); once one of them has imported `gov`, the
package stays in `sys.modules` and the import of this file succeeds. In the serial run of the suite such a case runs
first; in a worker that has not run one, the import fails. **The file alone, serially, fails as well: 24 failed in
6.5 s** (it does not pass alone, so this is an order dependence the serial suite hides, not a clash between workers).
No shared path, port or state. The fix lies in the tests (the import path of the file itself); no change of the
product code. In the form the close uses (`PYTHONPATH=src`) the import does not depend on the order; that form was not
run in parallel here.

No case failed in parallel for a shared path, a port, a file in the tree, a daemon or the state under `.gov-runtime/`
in the eight selections: W1-02, W1-05, W1-26, W1-30 and W1-47 had no parallel failure at all.

### Cases that fail in the serial arm too

| Case | First lines | Cause |
|---|---|---|
| `tests/acceptance/W1-27/test_w1_27_rebuild_r4.py::test_rebuild_codeintel_is_recreated_when_tool_answers` (both arms, part (a) and the combined call) | `AssertionError: with codebase-memory-mcp on PATH, the code index should be recreated but is not_recreated` | **sandbox**: `[Errno 30] Read-only file system` on a folder under `/tmp/gov-cbm-1000`, the reason `gov rebuild` gave here for the same store |
| W1-05, 5 of the 9 p95 cases in the set-apart serial run: `test_a_call_waits_under_100_ms_p95_for_the_hook[Edit-engineer]`, `[Glob-engineer]`, `[NotebookEdit-engineer]`, `[Read-engineer]`, `[Write-engineer]` | `p95 wait of a Edit call for its PreToolUse hooks, per round (ms): 112.2, 112.3, 114.3; the bound is 100 ms` (Glob: 234.9, 219.6, 211.2) | **the load of the machine from other sessions** (7.5 rising to 15.6 during the run), not the sandbox as such: all 9 passed in part (a) at load 3.2 to 3.6, in the same sandbox |
| W1-05, the nested-suites case, in its first serial run (before it was set apart) | inner `p95 decision time per round (ms): 152.4, 179.7, 135.1; the bound is 100 ms` | the same: load 12 to 16; it passed in part (a) at load 3 and in the set-apart run |

Failures of part (a) outside the selections, all caused by the sandbox:

- W1-09 `test_w1_09_vendoring.py::test_the_vendored_script_is_executable`: `warning: unable to access /home/usain/gov-os-worktrees/perf/.gitconfig: Permission denied` then `fatal: unknown error occurred while reading the configuration files` (the placeholder of the sandbox at `.gitconfig` in the worktree).
- W1-16, 158 errors: `OSError: [Errno 30] Read-only file system: /tmp/w16-nrl6cmln` (its fixtures make folders directly under `/tmp`).
- W1-20, 9 errors: `AssertionError: gov.codeintel.index failed (exit code 1)` at `CBM_RUNTIME_DIR` (`/tmp/gov-cbm-1000` read-only).
- W1-25, 3 errors: the real session, `ERR_PROXY_TUNNEL`.

## Not measured, and why

| What | Command | Why |
|---|---|---|
| `gov rebuild` to its end | `PYTHONPATH=src python3 -m gov.cli.main rebuild --json` | Not finished after about 44 min; killed by the harness (600 s foreground, then 30 min background). It was embedding the corpus through the local Ollama endpoint inside one write transaction (`store.db` grew from 30 MB to 75 MB, about 1.1 MB a minute). The sandbox also reported `deny network-outbound ollama.com:443` three times during it |
| The gates and test runs inside one `gov close` | the close of step 2 | `STALE_EVIDENCE` in 0.111 s: the ticket is closed |
| The regression run as the one call `gov close` makes | `pytest tests -q ... --ignore tests/acceptance/W1-30` | It would pass the 40 min limit of the harness for one command; measured per suite |
| W1-19 | `PYTHONPATH=src python3 -m pytest tests/acceptance/W1-19 -q ...` | 11 cases passed, then none for over 36 min, in `test_w1_19_real_models.py::test_the_pinned_embedder_reaches_a_section_from_a_paraphrase_and_the_manifest_names_it`; killed by the limit of the harness. `deny network-outbound ollama.com:443` reported |
| W1-21 | the same form | 72 cases passed, then none until the 2200 s bound (`timeout`, exit 124), in `test_w1_21_dev_tier.py::test_the_dev_query_set_meets_the_hit_at_5_pass_line`. `deny network-outbound ollama.com:443` reported |
| Real-session cases: W1-50 (2), W1-46 (36), W1-49 (9); W1-25 (3) ran and errored | `claude` started by the tests | `deny network-outbound api.anthropic.com:443`; `ERR_PROXY_TUNNEL` |
| W1-16 as a whole, 9 cases of W1-20, 1 of W1-27, the code index of `gov rebuild` | | `/tmp` outside the folder of the session and `/tmp/gov-cbm-1000` are read-only here |
| The context gate with a packet that builds; the gates on a ticket without findings | | the context of DAEO-2lwj ends at `mandatory input S0a-G-12 not found` |
| `gov check` at a steady load | | two runs, 18.0 s and 66.3 s, at loads 11 and 37 and with the store in two states |
| The parallel arm in the form the close uses (`PYTHONPATH=src` for acceptance suites) | | not in the brief; named because the 24 W1-50 failures depend on it |
| Each time at a quiet machine | | other sessions held the load between 2.5 and 39; no run was repeated for the load except the serial unit tests and W1-02 |
| The exit code of the close run | | it ran under `cProfile`, which showed 0 |

## Left behind in the worktree

Tracked files: none changed; no commit; `git status` shows no tracked path. `HEAD` is still `01a9997f`.

- `.gov-runtime/store.db` (30 MB): as the second rebuild left it, of this commit, **without the semantic vectors**
  (the unfinished transaction of the first rebuild was rolled back when the second opened the store; between the two
  the store answered `STORE_UNREADABLE ... attempt to write a readonly database` to readers).
- `.gov-runtime/last_head.json`, `.gov-runtime/findings.jsonl` (18 lines) and `.gov-runtime/snapshots/`: written by the
  hooks of this session, not by the commands measured. `.gov-runtime/codeintel/` (folders `files`, `home`): made by `gov rebuild`.
- `.gov-runtime/scratch/perf/`: this report, `run.py`, `gates.py`, `arms.py`, `times.tsv`, `out/` (one output per run,
  and `close.prof`). About 600 KB.
- No untracked ticket file: the close refused before `_refuse`, so no repair ticket and no count.
- `__pycache__` folders under `src/` and `tests/` (ignored by git).
- Seen from inside the sandbox, and reported by the containment hook after each command as "left in place":
  `.bash_profile`, `.bashrc`, `.gitconfig`, `.gitmodules`, `.idea`, `.mcp.json`, `.profile`, `.ripgreprc`, `.vscode`,
  `.zprofile`, `.zshrc`, `docs/source`, and `.gov-runtime/s`, `sc`, `scr`, `scra`, `scrat`, `scratc`. They are the
  placeholders of the sandbox (empty, or the null device), not written by a command of mine. They are what made
  `_check_tree` answer `TREE_NOT_COMMITTED` and the vendoring case of W1-09 fail. Whether they remain once the session
  ends was not measured.
- Outside the worktree: the temporary folders of pytest under the `TMPDIR` of this session
  (`/tmp/gov-launch-independent-auditor-ms8r77u9/claude-1000/pytest-of-usain`). `gov rebuild`, W1-19 and W1-21 start
  `ollama serve` by the code of the product when the endpoint is down and never stop it; whether one was started, and
  whether it still runs, cannot be seen from the sandbox (each command has its own process table). I sent no signal to
  any process but my own runs (`timeout` on the suites W1-20 to W1-50 and on W1-21).
