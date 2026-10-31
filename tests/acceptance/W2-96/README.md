# W2-96 acceptance tests — `gov accept`, the opaque acceptance runner

Ticket DAEO-ouet (W2-96), profile FULL. Written by the independent test designer (MR-3) from the ticket's KPI
lines, its sources (DEC-959 items 6 and 7, DEC-957's work order, DEC-820 (c), DEC-317, ROLES-RESEARCH-1 §2.7) and
the lead's design note for both workers, in parallel with the engineer (DEC-959 item 7). Review 1's cases
(`test_w2_96_at_review_1.py`) were added by a second independent test designer from the reviewer's findings, given
as described behaviours (DEC-136) in an addendum that overrides the design note where they differ. Run 2's cases
(`test_w2_96_at_run_2.py`) were added by a third, from DEC-970's decisions (PKG-1 (a); review 2's N2, N5, N7 and
N8), given the same way as R8 to R12; they override both earlier texts where they differ. The implementation
(`src/gov/accept/`, `tests/unit/accept/test_w2_96*`) was read by none of them.

## How the tests run the merged tree's code (DEC-732)

- `gov` is always run as `python3 -m gov.cli.main accept …`, with `PYTHONPATH` starting with the `src/` of the
  repository that holds the test file (`w2_96_support.SRC`, found from the file's own location), never a `gov`
  from `PATH`. Merged into `/home/usain/gov-os-worktrees/W2-96` and run there, the tests exercise that tree's
  code. Run the suite as
  `PYTHONPATH=<tree>/src python3 -m pytest tests/acceptance/W2-96 -q -p no:cacheprovider -o tmp_path_retention_policy=failed`.
- No repository is copied. Each case builds a **planted project** from scratch under pytest's `tmp_path`
  (`git init`, one commit): the ticket `.tickets/TDPL-a961.md` (WBS id `W9-61`, `acceptance_tests.path`
  `tests/acceptance/W9-61/`); a second ticket `TDPL-b962` (`W9-62`) whose own folder holds a failing test; a
  `src/` holding `qzv96leak_lib.py`, which the planted tests import; a `pyproject.toml`; and a `.gitignore`
  (`__pycache__/`, `.pytest_cache/`) as the real repository has. Planted test files are written at test time
  from strings in `w2_96_support.py`; no planted `test_*.py` is committed, and this folder has no `conftest.py`.
- **The tree's own `src/` first:** the run's `PYTHONPATH` is the tree's `src/` and then a decoy folder holding
  another `qzv96leak_lib`. A planted passing test asserts the planted tree's value, so it passes only when the
  child put the planted project's `src/` before what it was given (the premises show the decoy discriminates).
- **The environment** is built from scratch: `PATH`, an empty `HOME` (its `.local` linked to the user base where
  pytest and its plugins are installed, and `PYTHONUSERBASE` naming it), an empty `TMPDIR` of the run's own,
  `USER`, `LOGNAME`, a UTF-8 locale, `PYTHONPATH`. No `PYTHONDONTWRITEBYTECODE`, `PYTHONPYCACHEPREFIX` or
  `PYTEST_ADDOPTS` reaches the run: keeping the project free of caches is the runner's own work.

## The marker

Every planted test name, file name, docstring, assertion message, compared value, print to stdout and stderr, log
line, warning, exception message, skip reason, fixture, parameter value and parameter id, and the planted READMEs'
own text, carries **`qzv96leak`**. The ticket ids, WBS ids and declared paths do not (a refusal may name them).
After every run, `w2_96_support.Run.problems` searches stdout and stderr (the envelope and the error message are in
them), every file created or changed in the planted project (ignored files included), everything under the
`TMPDIR` the run was given, and the run's `HOME`: none may hold the marker. stdout and stderr may not hold pytest's
own words `Traceback`, `AssertionError`, `::` or `conftest` either (the interrupt case, review 1's signal cases and
run 2's R9 and R12 cases check only the marker), the given `TMPDIR` must be empty after the run, and the project's tree must be unchanged (every path,
size, digest and mtime, folders included; `.git` aside). Each planted test that runs also writes a small probe
record (process id, working folder, `tmp_path`, a grandchild's process id) into a folder outside the project and
outside the given `TMPDIR`; the cases read it to check what ran, where, and that it stopped.

## The map

| KPI line | Tests | Red now because |
|---|---|---|
| Success 1 | `test_w2_96_at_report.py` | `gov accept` does not exist: `python3 -m gov.cli.main accept …` ends with argparse's usage error (exit 2, `invalid choice: 'accept'`), so each case fails at its first check, "gov accept gave no API-0002 envelope on stdout" (the text case: "exit code 2, expected 0"). |
| Success 2 / Failure 1 | `test_w2_96_at_no_leak.py` | The same: no envelope (exit 2); the text case: "exit code 2, expected 3"; the interrupt case: "gov accept ended (exit code 2) before a planted test recorded 'sleeping'". |
| Success 3 / Failure 2 | `test_w2_96_at_unmapped_and_no_map.py` | The same: no envelope, or exit code 2 for the text cases. |
| Success 4 / Failure 3 | `test_w2_96_at_run_errors.py` | The same: no envelope, or exit code 2 for the text case. |
| Success 5 / Failure 4 | `test_w2_96_at_exit_codes.py` | The same: no envelope (exit 2). |
| Success 1 / Success 2 (review 1, R1) | `test_r1_a_project_whose_conftest_refuses_a_per_run_base_folder_is_run_and_reported_per_line` | The same: no envelope (exit 2). |
| Success 2 / Failure 1 (review 1, R2 and R3) | `test_r2_a_sigterm_or_sighup_to_gov_alone_stops_the_run_leaves_nothing_and_exits_128_plus_the_signal`, `test_r3_folders_without_permissions_left_by_a_failing_test_are_removed`, `test_r3_folders_without_permissions_held_at_a_timeout_are_removed` | R2: "gov accept ended (exit code 2) before a planted test recorded 'sleeping'"; R3: no envelope (exit 2). |
| Success 3 / Failure 2 (review 1, R4) | `test_r4_a_row_whose_kpi_cell_names_no_line_the_reader_takes_refuses_the_run`, `test_r4_a_tests_table_under_a_success_failure_or_kpi_heading_naming_no_line_refuses_the_run`, `test_r4_the_text_form_of_accept_map_unreadable_gives_its_code_and_runs_nothing` | No envelope (exit 2); the text case: "exit code 2, expected 1". |
| Success 1 (review 1, R5) | `test_r5_items_holding_a_double_colon_with_no_py_file_before_it_map_by_function_name`, `test_r5_an_item_naming_a_test_that_matches_no_case_fails_its_line` | No envelope (exit 2). |
| Success 2 / Success 5 / Failure 1 / Failure 4 (review 1, R6) | `test_r6_no_log_file_is_written_whatever_the_projects_pytest_configuration_says` | No envelope (exit 2). |
| Success 4 / Failure 3 (review 1, R7) | `test_r7_a_tests_failed_exit_with_no_failed_case_in_the_report_is_a_crash` | No envelope (exit 2). |
| Success 3 / Success 5 / Failure 2 / Failure 4 (run 2, R8) | `test_r8_a_failed_case_the_readme_never_names_fails_the_run_while_every_mapped_line_passes`, `test_r8_a_skipped_case_the_readme_never_names_leaves_a_passing_run_passing`, `test_r8_a_failing_case_outside_the_readable_map_in_w1_30s_form_fails_the_run` | Against run 1's code (the design note: unmapped cases never change the exit code): the unmapped failure leaves `outcome: pass`, exit 0: "the result is not the expected one" (`"outcome": "pass"`), and for W1-30's form "exit code 0, expected 3". The skipped case **passes already** (a guard: R8 must not make skips fail the run). |
| Success 2 / Failure 1 (run 2, R9) | `test_r9_a_ctrl_c_during_the_clean_up_is_held_back_until_the_clean_up_ends` | Seen on run 1's code: the spaced and mixed presses interrupt the removal, "the given TMPDIR holds N entries after the run" (18,913 and 9,862 in one run, 16,191 and 7,691 in the next), files left holding the marker, and "gov was killed by signal 2 (1)"; the two presses 0.2 s apart: "gov was killed by signal 2" (that second press fell while `gov` waited for its child, and the removal finished). |
| Success 2 / Success 4 / Failure 3 (run 2, R10) | `test_r10_a_chain_of_nested_folders_deeper_than_a_recursive_removal_leaves_the_result_as_the_tests_gave_it` | Seen on run 1's code: "the given TMPDIR holds 1218 entries after the run" (the chain and the run's report, holding the marker) and "the result is not the expected one" (`error`, kind `crash`), passing and failing alike. |
| Success 1 / Success 5 (run 2, R11) | `test_r11_a_signal_gov_was_started_ignoring_stays_ignored_and_the_run_completes` | Seen on run 1's code: "gov accept ended (exit code 129) on signal 1, which it was started ignoring" (SIGHUP to `gov` and to its group), "(exit code 143) on signal 15" (SIGTERM), the child stopped. The SIGINT variant **passes already** (run 1 leaves SIGINT to Python, which keeps an inherited ignore); it stays as R11's guard. |
| Success 5 / Failure 4 (run 2, R12) | `test_r12_a_signal_that_ends_the_run_ends_gov_by_an_ordinary_exit_with_128_plus_the_signal` | Seen on run 1's code: "gov was killed by signal 15" (SIGTERM twice), "signal 1" (SIGHUP twice), "signal 2" (one SIGINT), each "expected an ordinary exit with code 143 (129, 130)". |
| Premises (no KPI line: counted under unmapped) | test_w2_96_at_premises.py, and the test_premise_ cases of the review 1 and run 2 files, named without backticks (a row holding an item whose KPI cell names no line would refuse the run, R4) | **Green before the implementation, by design**: they test the tests. The planted suites give the designed outcomes under raw pytest and raw output holds the marker; the planted collection errors and crashes end pytest as designed; the decoy discriminates; the marker is nowhere in `src/`; this README is a map in the design note's form naming success 1 to 5 and failure 1 to 4 and every test here (a file whole, or a review 1 or run 2 case by its function name), and every row holding an item begins with a line name. Review 1's premises: the planted conftest refuses `--basetemp` (exit 4) and only that; a plain `shutil.rmtree` leaves the planted locked folders; the unreadable READMEs each hold a readable line beside the unreadable one; the items files give their designed outcomes; raw pytest writes the configured log file, holding the marker; the planted `pytest.exit` ends pytest with code 1 and a report without failures. Run 2's premises: W1-30's two forms map the passing cases in one Test table and hold the failing case in no Test or File table under a header row; raw pytest leaves the planted chain, 1,200 folders deep (more than 1,100 and than Python's recursion limit), with its deepest three folders at 0500, 0300 and 0000, and the cases' own removal without recursion takes it away; a process started as the R11 case starts `gov` begins with the signal ignored. |

What each file holds:

- **Success 1** — a row-form map and a heading-form map over the same six planted files (12 cases pass, 1 fails,
  1 is skipped), reported exactly: every line name form (`Success N`, `S N`, `SN`, `KPI N`, `kpi N`, `K N`, `KN`,
  `failure N`, `FAILURE N`, `F N`, `FN`), every separator (`/`, `,`, `;`, `and`), every item form (a file, a path
  ending in a file, `file::test`, a bare word equal to the function name or to it without `test_`, parametrized
  functions), lines in numeric order (`success-9` before `success-10`) then failure lines, text outside the map
  ignored, a row whose KPI cell names no line and that holds no item, and a table under a heading that names no
  line (and does not begin with success, failure or KPI), mapping nothing; every planted case
  ran and only those; the WBS id names the same ticket; each ticket runs its own declared folder; the child runs
  in the root with the tree's own `src/` first; `--root` from another folder; text and `--json` agree. Every line
  passes, and (since run 2, R8) the one unmapped failure makes the run's outcome `fail`, exit code 3.
- **Success 2 / Failure 1** — a failing run (an assertion with values, a setup error, a teardown error, a skip,
  prints, logs, warnings) shows none of it in `--json` or text; the tests' temporary folders are made under the
  given `TMPDIR` and removed; an interrupted run (SIGINT to `gov` alone while a planted test sleeps) stops its
  child and leaves nothing. Every other case also runs the leak probe.
- **Success 3 / Failure 2** — unmapped cases counted (3 passed, 1 failed) and never named, and (since run 2, R8)
  the unmapped failure fails the run with exit code 3, in `--json` and text; `ACCEPT_NO_MAP` for no README, an empty README, prose only, a
  table whose rows name no line and hold no item, a table under a heading that names no line, and a KPI table with no Test or File
  column; never raw output (`collected`, `PASSED`, `FAILED`, `=====`); the text form gives the code on stderr.
- **Success 4 / Failure 3** — `collection` for an import error, a syntax error and nothing collected; `timeout`
  for a planted test that sleeps past `--timeout 8`, with the child and its grandchild (same process group) gone;
  `crash` for a test that kills its own process (SIGKILL) and for pytest's internal-error code 3 with no report;
  each `error` with its kind only, `lines` empty, every count 0, exit code 4, `ok: true`; the text form agrees.
- **Success 5 / Failure 4** — exit code and `ok` of a pass (0, true), a fail (3, true), an error (4, true) and a
  refusal (1, false); one failing mapped line fails the run with 3 (an assertion, a setup error, a teardown error,
  only skipped cases, no matching case); `ACCEPT_UNKNOWN_TICKET` for an unknown ticket id and WBS id;
  `ACCEPT_NO_TESTS` for no `acceptance_tests`, no `path`, a missing folder, a file, and a folder outside the
  root (which is not run); nothing written in the project, ignored files included (`git status --ignored` empty,
  no `__pycache__`, `.pytest_cache` or report).

## Review 1's cases (`test_w2_96_at_review_1.py`)

Each point of the addendum (R1 to R7), what its case checks beyond the leak probe every case runs, and the case's
red reason against an implementation that keeps the design note and lacks the addendum. Now, on a branch without
`gov accept`, each is red as the map says.

- **R1** — the planted project's `tests/conftest.py` refuses a run given `--basetemp` (an xdist worker aside), as
  this repository's does, and records that it ran. Checks: the result per line (a passing line passes, a failing
  line fails, exit 3); the conftest ran and saw no base folder; each test's `tmp_path` is in pytest's own default
  base folder (`pytest-of-<user>`) under the child's TMPDIR, which is below the given `TMPDIR`. *Red without R1:*
  given `--basetemp`, pytest ends with its usage error (4) before any test, so the result is a `crash`
  (exit 4): "the result is not the expected one".
- **R2** — SIGTERM, and separately SIGHUP, to `gov`'s own process (not its group) once the planted test has
  recorded `sleeping`. Checks, all reported together: what `gov` left when it exited (the given `TMPDIR` empty, no
  marker in its output); exit code 128 plus the signal's number; the child pytest and the grandchild it started gone.
  *Red without R2:* Python's default action ends `gov` by the signal (exit code -15 or -1) and nothing stops the
  child: "exit code -15, expected 143", the child and grandchild still running, the private folder left in the
  given `TMPDIR`.
- **R3** — the planted test locks up, in its `tmp_path` and in a new folder of its temporary folder, a folder
  without read (0300), one without write (0500), one without execute (0600) and one without any permission (each
  holding a locked folder and a file), and a file without any permission; one case then fails, the other sleeps
  past `--timeout 8`. Checks: the given `TMPDIR` empty (first), the result (fail with exit 3, or `timeout` with
  exit 4), the child gone after the timeout, the locked folders made under the given `TMPDIR`. *Red without R3:* a
  plain removal leaves the locked folders (the premise shows it): "the given TMPDIR holds N entries after the
  run"; a removal that raises instead gives a result other than the expected one.
- **R4** — a row-form map with a readable row (`Success 1`) and a row naming the failing file, case or function
  under an unreadable KPI cell (`Failure:` with no number, `Success 3a`, `S8b`, `Edge …` naming no line); a
  heading-form map with a readable table and a Tests table under `### Failure: …` with no number, `## SUCCESS …`
  or `#### kpi …`. Checks: `ACCEPT_MAP_UNREADABLE`, `ok: false`, exit code 1; no planted test ran; no raw output;
  the text form gives the code on stderr. *Red without R4:* the unreadable row or table maps nothing (or
  `Success 3a` is read as `success-3`), the run goes ahead: "a refusal must answer ok: false".
- **R5** — two files share the function name `test_qzv96leak_items_twin`. Case one: `::name`, `stem::name` (a
  failing case) and `any_word::name` (both twins) map by function name. Case two: a `test_` word, a
  `file.py::test` item, a `test_….py` file and a `::test` item that match nothing each fail their line, counted by
  the cases that did match; a line whose items all match and pass (a `::` item among them) passes, and so does a
  line beside whose matching case a word naming no test (no `::`, no `test_`) matches nothing. *Red without R5:*
  the `::` items map nothing and the unmatched test items fail no line: "the result is not the expected one".
- **R6** — the planted `pyproject.toml` names a `log_file` in the project, relative to the root or absolute.
  Checks: no log file in the project (first), the result, the marker logged by the tests nowhere. *Red without
  R6:* pytest writes the log file: "pytest's log file was written in the project".
- **R7** — three cases pass, then a test calls `pytest.exit(returncode=1)`, and the failing test after it never
  runs (the premise shows pytest ends with 1 and a report holding no failure). Checks: `error` with kind `crash`,
  exit 4. *Red without R7:* the report alone gives a pass or a fail: "the result is not the expected one".

### Cases of the first batch that review 1 changed

- `ROWS_README`'s row `Edge qzv96leak (names no line)` named `test_qzv96leak_zeta.py` in backticks: under R4 that
  row now refuses the whole run. Its file is named without backticks, so the row holds no item and still maps
  nothing; the expected result is unchanged (the unreadable form moved to R4's `a-cell-naming-no-line`).
- `ACCEPT_NO_MAP`'s `rows-naming-no-line` README held rows with items and no line name: under R4 those rows refuse
  with `ACCEPT_MAP_UNREADABLE`, while the README, having no map, also answers the design note's `ACCEPT_NO_MAP`;
  which code wins is open (returned to the lead as a package). Its rows now hold no item, so only `ACCEPT_NO_MAP`
  applies.
- This README's premises row named `test_w2_96_at_premises.py` in backticks under a KPI cell naming no line: under
  R4 `gov accept DAEO-ouet` would refuse this folder. It is named without backticks; the map names review 1's cases
  by function name, and the README premise checks the new form.
- The support module's line-name reader (for the README premise) no longer takes a number followed by a letter or
  digit (`Success 3a`, `S8b`), and `Started.interrupt` became `Started.send(SIGINT)` (no change of behaviour).

## Run 2's cases (`test_w2_96_at_run_2.py`, DEC-970)

Each point of run 2's addendum (R8 to R12), what its case checks beyond the leak probe, and its expected red
reason against this branch's run-1 implementation (which keeps the design note and review 1's addendum, and lacks
run 2's). R13 (`accept` recorded among the `gov` commands) has no case here: it is W1-07's and W1-32's command
lists, revised in their own folders (see "Outside these paths").

- **R8** — (a) the README maps ALPHA's three passing cases (`Success 1`); the second file's one case, named by no
  item, fails its assertion, errors in setup or errors in teardown: the result exactly (`outcome: fail`, success 1
  passing with 3, `unmapped` failed 1, totals 3 passed 1 failed), exit 3. (b) The same with the unmapped case
  skipped: `outcome: pass`, `unmapped` skipped 1, exit 0. (c) W1-30's form, as review 2 planted it: a heading-form
  Test table under `### S1: …` maps the passing cases, while the failing case sits in a one-row table with no
  header row under `### F1: …`, or in a `Case | Clause` table under `### Failure 1: …`: `ok: true`, `outcome:
  fail`, exit 3, success 1 first and passing with 3, totals 3 and 1, the failing case counted as failed once.
  *Red without R8:* (a) and (c) answer `outcome: pass`, exit 0. (b) **passes already**; it stays as R8's guard
  that a skip never fails the run.
- **R9** — a planted test leaves 20,000 files (20 folders of 1,000) in its temporary folder, then sleeps; SIGINT to
  `gov` alone ends the run, and more presses follow during the clean-up: one SIGINT 0.2 s later (review 2's form),
  fifteen SIGINTs 0.1 s apart, or SIGTERM, SIGHUP and SIGINT in turn 0.1 s apart (a press is sent only while
  `gov` still runs; at least a second press must be sent, or the case's premise failed). Checks, all reported
  together: the given `TMPDIR` empty and no marker when `gov` ends (first); exit code 130; the child gone; the
  planted files made under the given `TMPDIR`. *Red without R9:* a later press raises `KeyboardInterrupt`
  inside the removal: "the given TMPDIR holds N entries after the run", and an exit code other than 130 (on run
  1's code the two-press variant is red on the exit code alone: its second press fell before the removal).
- **R10** — a planted test leaves in its temporary folder a chain of 1,200 nested folders, the deepest three at
  0500, 0300 and 0000 (each holding a file), then passes or fails. Checks: the given `TMPDIR` empty (first), the
  result as the tests gave it (both lines passing, exit 0; or success 2 failing, exit 3), the chain made under the
  given `TMPDIR`. *Red without R10:* a recursive removal raises `RecursionError` (Python 3.12's `shutil.rmtree`
  does, on this chain): the run is reported as an error, or the chain stays (on run 1's code, both).
- **R11** — `gov accept` is started with the signal set to "ignore" in the starting process (as `nohup` does):
  SIGHUP, SIGTERM or SIGINT to `gov` alone, or SIGHUP to `gov`'s process group, while a planted test waits; 1.5 s
  later `gov` and the child must still run; the planted test is then let go (a file it waits for). Checks: the
  result (both lines passing, exit 0), the planted test went on, the leak probe. *Red without R11:* review 1's R2
  handlers replace the inherited "ignore" for SIGHUP and SIGTERM, so `gov` stops the run: "gov accept ended (exit
  code 129 or 143) on signal N, which it was started ignoring". The SIGINT variant **passes already** on run 1's
  code (SIGINT is left to Python, which keeps an inherited ignore); it stays as R11's guard.
- **R12** — SIGTERM twice 5 ms apart, SIGHUP twice 5 ms apart, or one SIGINT, to `gov` alone while the planted test
  and its grandchild sleep. Checks: the exit code is 143, 129 or 130, an ordinary exit (never `-15`, `-1`, `-2`);
  the given `TMPDIR` empty, no marker; the child and the grandchild gone. *Red without R12:* a signal ending `gov`
  by the default action: "gov was killed by signal N" (on run 1's code, all three).

### Cases of the run-1 suite that run 2 changed (`Rewrite-Reason: DEC-970 (PKG-1 (a); review 2's N2, N5, N7, N8)`)

R8 replaces "unmapped cases never change the exit code". Both common maps leave the failing
`test_qzv96leak_epsilon_other` unmapped, so `ROWS_EXPECTED` and `HEADINGS_EXPECTED` now answer `outcome: fail`, and
these cases expect exit code 3 instead of 0; every line's result and every count is unchanged, and each case keeps
its purpose and its leak checks:

- `test_w2_96_at_report.py`: `test_a_row_form_map_is_reported_per_kpi_line_with_its_counts`,
  `test_a_heading_form_map_is_reported_per_kpi_line_with_its_counts`, `test_the_wbs_id_names_the_same_ticket`,
  `test_the_root_option_runs_the_named_project_from_another_folder`, `test_the_text_output_gives_the_same_result_as_json`.
- `test_w2_96_at_unmapped_and_no_map.py`: `test_unmapped_cases_are_counted_never_named`, and
  `test_an_unmapped_failure_never_changes_the_exit_code_in_text_either`, renamed
  `test_an_unmapped_failure_fails_the_run_in_text_too_and_is_never_named` (it still requires the unmapped counts
  in the text and no unmapped case named).

On run 1's code each of the seven is red for R8 alone: "the result is not the expected one" (`"outcome": "pass"`,
every line as expected) or "exit code 0, expected 3 (R8)".

No case of the run-1 suite expected a negative return code after a signal (R12): review 1's R2 case already
requires 128 plus the signal, and the interrupt case judges no exit code (R12's SIGINT variant does). The support
module gained, without changing what the earlier cases do: the planted kinds `many_sleep`, `deep_pass`,
`deep_fail` and `wait_for_go`; `Project.start(..., ignore=…)`, `Project.go`, `Started.send_all`, `Started.finish`
(which `Started.send` now uses); `pid_running`; and `remove_tree`, an iterative removal the R9 and R10 cases use
in their own clean-up, since pytest's own removal of a kept temporary folder recurses.

## The brief change has no test

The ticket's sixth success line (the common lead brief and the engineer's brief template name `gov accept` as the
engineer's only way to run the acceptance tests) is the orchestrator's change, recorded with this ticket's merge.
No test here judges it, and the map above names no line for it.

## Choices this suite makes where the design note leaves the form open

- **The result's keys:** the six keys of the design note's §6 (and the five of each line, the three of each count)
  are compared exactly; a key of the runner's own is not judged, but it is searched for the marker like all output.
- **The text output:** the command line prints a dict `result` as JSON (`src/gov/cli/main.py`); that JSON must equal
  `--json`'s `result`. A text form of the runner's own is accepted when each KPI line stands on a line of its own,
  in order, with its outcome and its passed and failed counts, and the outcome (and an error's kind) appear.
- **A teardown error** makes its case failed and not passed (`passed` 0, `failed` 1), as "a case passes when it
  neither failed nor errored" reads.
- **Totals and lines:** `totals` counts each case once; a case mapped to several lines (or by several items)
  counts once in each of those lines; `lines` are the lines the map names, never the ticket's own KPI list.
- **Refusals run nothing:** `ACCEPT_UNKNOWN_TICKET` and `ACCEPT_NO_TESTS` cases check that no planted test ran
  (the folder outside the root included). The `ACCEPT_NO_MAP` cases do not check it.
- **An interrupt** stops the child: "removed in every path (… an interrupt)" cannot hold while the child still runs
  and writes in the private folder. The grandchild is required gone only for the timeout ("its whole process group
  is killed").
- **The child's environment:** pytest is found through the environment the run is given (`PYTHONUSERBASE`, and
  `HOME/.local`); a runner that drops both cannot start pytest in these planted projects.
- **The tests' temporary folders** are required under the given `TMPDIR` ("one private temporary folder (under
  `TMPDIR`) for the run's report and the tests' temporary folders").
- **Timing:** the timeout case gives `--timeout 8` and checks the run lasted at least 7.5 s and ended within its
  150 s wait; the interrupt case waits up to 120 s for its planted test to start. Neither asserts a time the
  ticket promises beyond its own `--timeout`.
- **Review 1, R2's exit code** is the process's own exit status, 128 plus the signal's number, as `exit(143)`
  gives it; a `gov` that ends killed by the signal (a status of -15 to the caller, which a shell prints as 143) fails
  the case, since it has no exit code of its own.
- **Review 1, R1's base folder:** the case requires each `tmp_path` in `pytest-of-<user>` directly under the child's
  own temporary folder, which is below the given `TMPDIR`; it does not judge how deep (the private folder itself or
  a folder in it).
- **Review 1, R1's conftest** must run in the child (the case reads its probe record): a runner that skips the
  project's conftest files would not be running the project "normally".
- **Review 1, R5:** an item that names no test (no `::`, not beginning with `test_`, not a `test_….py` file) and
  matches nothing leaves its line as the design note's §4 says (it passes when its other cases do); only test
  items that match nothing fail their line.
- **Run 2, R8 in W1-30's form:** the suite does not judge whether a row with no header row, or a `Case | Clause`
  table, maps its item to its heading's line: a `failure-1` line, failing, may be reported or not, and the failing
  case may be counted there or under `unmapped`, once. It requires the run to fail (exit 3, `ok: true`), never
  pass; a refusal fails the case too.
- **Run 2, R9:** the presses go to `gov`'s own process, as review 1's R2 does; the exit code is the first press's
  (130), since later signals "change nothing". The case does not judge how long the clean-up takes.
- **Run 2, R10:** the chain is 1,200 folders deep, more than R10's 1,100 and than Python's default recursion
  limit (1,000), with short names so every path stays under the system's path length limit.
- **Run 2, R11:** "stops neither the run nor its child" is read as: after the signal, `gov` and the child pytest
  both still run, and the run reports as if no signal had come. The process-group variant sends SIGHUP as a
  hang-up reaches the foreground job; a child in `gov`'s group that does not keep the ignore fails it.
- **Run 2, R12:** as for review 1's R2, the exit code is the process's own exit status; the second signal comes
  5 ms after the first, wherever that falls (before or during the clean-up).

## Outside these paths (for the lead)

Adding a `gov` command turns W1-07's, W1-26's and W1-32's command-list cases red. DEC-970 gave the revision to
this suite's run-2 designer (R13, P-W2-96-CMDLIST (a), DEC-747): `accept` is added to W1-07's support list
(`RECORDED_GOV_COMMANDS`), to W1-07's pinned sorted list and to W1-32's pinned set, and to the line of W1-07's
README naming the list, in a commit of its own (`Rewrite-Reason: DEC-959 item 6`). W1-26's
`test_w1_26_recorded_commands.py` reads W1-07's list, so its parametrized cases gain an `accept` variant, which
holds the product's own list (`src/gov/check/commands.py`): it is red until the engineer adds `accept` there.
