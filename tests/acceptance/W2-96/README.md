# W2-96 acceptance tests — `gov accept`, the opaque acceptance runner

Ticket DAEO-ouet (W2-96), profile FULL. Written by the independent test designer (MR-3) from the ticket's KPI
lines, its sources (DEC-959 items 6 and 7, DEC-957's work order, DEC-820 (c), DEC-317, ROLES-RESEARCH-1 §2.7) and
the lead's design note for both workers, in parallel with the engineer (DEC-959 item 7). The implementation
(`src/gov/accept/`, `tests/unit/accept/test_w2_96*`) was never read.

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
own words `Traceback`, `AssertionError`, `::` or `conftest` either (the interrupt case alone checks only the
marker), the given `TMPDIR` must be empty after the run, and the project's tree must be unchanged (every path,
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
| Premises (no KPI line: counted under unmapped) | `test_w2_96_at_premises.py` | **Green before the implementation, by design**: they test the tests. The planted suites give the designed outcomes under raw pytest and raw output holds the marker; the planted collection errors and crashes end pytest as designed; the decoy discriminates; the marker is nowhere in `src/`; this README is a map in the design note's form naming success 1 to 5 and failure 1 to 4 and every test file here. |

What each file holds:

- **Success 1** — a row-form map and a heading-form map over the same six planted files (12 cases pass, 1 fails,
  1 is skipped), reported exactly: every line name form (`Success N`, `S N`, `SN`, `KPI N`, `kpi N`, `K N`, `KN`,
  `failure N`, `FAILURE N`, `F N`, `FN`), every separator (`/`, `,`, `;`, `and`), every item form (a file, a path
  ending in a file, `file::test`, a bare word equal to the function name or to it without `test_`, parametrized
  functions), lines in numeric order (`success-9` before `success-10`) then failure lines, text outside the map
  ignored, a row and a table whose KPI cell or nearest heading names no line mapping nothing; every planted case
  ran and only those; the WBS id names the same ticket; each ticket runs its own declared folder; the child runs
  in the root with the tree's own `src/` first; `--root` from another folder; text and `--json` agree.
- **Success 2 / Failure 1** — a failing run (an assertion with values, a setup error, a teardown error, a skip,
  prints, logs, warnings) shows none of it in `--json` or text; the tests' temporary folders are made under the
  given `TMPDIR` and removed; an interrupted run (SIGINT to `gov` alone while a planted test sleeps) stops its
  child and leaves nothing. Every other case also runs the leak probe.
- **Success 3 / Failure 2** — unmapped cases counted (3 passed, 1 failed) and never named, and an unmapped
  failure leaves exit code 0, in `--json` and text; `ACCEPT_NO_MAP` for no README, an empty README, prose only, a
  table whose rows name no line, a table under a heading that names no line, and a KPI table with no Test or File
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

## Outside these paths (for the lead)

Adding a `gov` command turns W1-07's, W1-26's and W1-32's command-list cases red; that revision is outside this
folder and is returned as a package (DEC-747).
