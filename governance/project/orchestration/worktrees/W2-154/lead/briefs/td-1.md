# Brief td-1: W2-154 (DAEO-l4gf), independent test designer, tests first (run 2)

You are the independent-test-designer (MR-3) for ticket DAEO-l4gf (W2-154), profile STANDARD, class C2.
Use your test-design skill: write the acceptance tests from the KPIs and the ticket's Interface (I1-I4), before any
implementation exists. They must be RED on the current code for the right reason (the behaviour is missing), never
for a typo, an import of a name the Interface does not state, or a harness fault.

## Where you work
- Your worktree / branch: /home/usain/gov-os-worktrees/W2-154-tests  /  w2/W2-154-tests (write here only).
- Write ONLY new files matching `tests/unit/close/test_serial*` (e.g. `tests/unit/close/test_serial_w2_154_plugin.py`,
  `tests/unit/close/test_serial_w2_154_nightly.py`, and a support module `tests/unit/close/test_serial_w2_154_support.py`
  if you need one — the support file's name must also match `test_serial*`). Do not edit the existing
  `tests/unit/close/test_serial.py`. Do not touch `tests/unit/close/test_nightly.py`, `conftest.py`, any `src/` file,
  `nightly.sh`, or `tests/acceptance/serial-only.txt` (S4 is out of this batch: it happens after S1 is green).
- The ticket (read-only): /home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-l4gf.md — read it whole, especially
  its "## Interface" section (I1-I4). The Interface is the contract your tests hold the code to; cite I1-I4 by name in
  each test's docstring along with the KPI id (S1, S2, S3, F1, F2).
- Sources (read by id in /home/usain/Dynamic-Agentic-Engineering-OS/docs/DECISION_REGISTER.md, grep by id only):
  DEC-1112 (item 3), DEC-1061, DEC-889 (item 5), DEC-549, DEC-1109.

## What your tests must check (one or more cases per line)
- **S1 / I1 / I2**: a planted project (under tmp_path) with its own `tests/acceptance/serial-only.txt` and its own
  `tests/conftest.py` whose opt-in mechanism deselects (reports via `config.hook.pytest_deselected`) the cases named
  by a planted `tests/optin-lifted-<x>.txt` unless opted in. Model the planted conftest on the project's real opt-in
  mechanism (read `tests/conftest.py`, lines ~30-60 and ~200-260, for its behaviour: `--optin=<name>` /
  `GOV_TESTS_OPTIN`, deselected not skipped). The planted list holds: entry A, every case of which the opt-in list
  leaves out; entry B, which names no case and no opt-in list explains. Checks:
  - with only A given to the serial-afterwards run: the run does not stop (exit 0), stdout/stderr has
    `gov_close_serial_only: not in this run: <A>`, the file named by `GOV_CLOSE_SERIAL_ONLY_OUT` holds `<A>` (one per
    line), and A's cases ran nowhere;
  - the close's stated record for the serial-afterwards run carries `"not_in_this_run": [<A>]` and its `"cases"` does
    not list A; with every given entry out, the close counts a serial run of 0 cases with no finding (I2).
  - **F1**: with B given (alone, and together with A): exit 4 (`pytest.UsageError`) with "no case is named by the
    entry"; a pass there is the failure.
- **S2 / I1**: the same planted project with the opt-in list switched on (`--optin` / `GOV_TESTS_OPTIN`): A's cases are
  in the serial phase (the serial-afterwards run's record / JUnit) and none in the parallel phase; A is not in
  `not_in_this_run`.
- **S3 / I3 / I4**: nightly.sh run ONLY through its stub seam, `NIGHTLY_SERIAL_STUB=<file>` (the stub sets `ENTRIES`,
  `s_exit` and writes `$JUNIT/serial.xml`). Never run the real nightly; any case that would run nightly.sh without the
  stub is a defect in your test. Read nightly.sh (`governance/project/orchestration/nightly/nightly.sh`) for where
  `$OUT`, `$JUNIT`, `run.txt` and the verdict line live, and what environment a stubbed run needs (keep every
  output path under tmp_path; never write the real log/ or digest). Cases:
  - stub runs 5 cases (serial.xml with 5 `<testcase>`, s_exit 0): `serial: 5 cases run`, not red from the serial step;
  - stub runs none (0 `<testcase>`, green JUnit, s_exit 0): final line reads red with `verdict: red serial: 0 cases run`
    (**F2**: green there is the failure);
  - stub ends with a collection error (s_exit 4 or 2, JUnit green): red with `verdict: red serial: collection error, exit E`;
  - nothing declared (`ENTRIES` empty): `serial: 0 declared`, not red, and not today's exit 2 "no serial-only entry read".
- **F3** (the branch changes only the allowed paths) is checked by the lead from `git diff`; if you write a case for it,
  it judges only branch w2/W2-154 (skip elsewhere, naming the branch found) and compares paths with
  `Path.is_relative_to` / pattern match, never a text search of a temporary path (DEC-1155).

You may read anything in the repository for harness patterns: existing tests in `tests/unit/close/test_parallel_runs.py`,
`tests/unit/close/test_serial.py`, `tests/unit/close/test_nightly.py`, `tests/acceptance/W1-30/w1_30_support.py`,
`tests/acceptance/W2-57/w2_57_list_support.py` show how planted projects drive the close's runs and how its stated record
is read. Use only names the Interface states or that exist today (e.g. `GOV_CLOSE_SERIAL_ONLY_GIVEN`,
`GOV_CLOSE_SERIAL_ONLY_OF`, `GOV_CLOSE_SERIAL_ONLY_OUT`, `NIGHTLY_SERIAL_STUB`); do not rely on any private helper the
engineer would have to invent. Driving the plugin through a real `python3 -m pytest` subprocess on the planted project
is preferred (the plugin's folder on PYTHONPATH, `-p gov_close_serial_only`).

## How you run tests (every pytest, no exception)
```
env TMPDIR=/tmp/w2-154-td PYTHONUSERBASE=/home/usain/.local HOME=/home/usain/gov-os-worktrees/W2-154-tests/.gov-runtime/scratch/empty-home PYTHONPATH=/home/usain/gov-os-worktrees/W2-154-tests/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest tests/unit/close/test_serial_w2_154_*.py -q -p no:cacheprovider -o tmp_path_retention_policy=failed
```
(make /tmp/w2-154-td and the empty-home folder first; TMPDIR stays outside the repository and outside ~/gov-os-runs).
A resource gate's refusal is a wait: retry when it opens. Show red: every S1/S2/S3/F1/F2 case fails on today's code for
the missing behaviour (the F1 exit-4 case may already pass today — say so; it is the guard against regression). Also
run the existing `tests/unit/close/test_serial.py` to show you broke nothing.

## Commit (your paths only, in your worktree)
```
git commit -m "W2-154: acceptance tests for S1-S3 (serial entry not in this run; nightly serial count)" --trailer "Task: DAEO-l4gf" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-1112, DEC-1061, DEC-889, DEC-549, DEC-1109" -- <your new test files>
```
`Task:` is DAEO-l4gf; `Implements:` only these ids. No `Role: owner`, no `Decided-by:`.

## Rules
- Reads are open, except secrets, held-out qualification material's contents, the hidden half of any evaluation set, and
  the engineer's work on this ticket. No `gov retrieve` and no `gov context` in the sandbox: search with Read and Grep,
  then search once more in different words.
- Anything longer than one line goes in a script file under /home/usain/gov-os-worktrees/W2-154-tests/.gov-runtime/scratch/,
  run with `bash <file>` or `python3 <file>`. Write files with Write/Edit and absolute paths.
- Refused twice for the same call by the guard, the sandbox or a hook: stop and say so; never work around a refusal.
- No new ticket and no widening: a gap in the Interface comes back in `unresolved` as a question, not a guess.

## Return (your last message; the twelve fields, each a labelled line, "none" where nothing)
task: / status: / work_completed: / files_changed: / evidence: / tests: / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:
In `tests:` give each file's case count and the red/green per case on today's code with the one-line reason each red
fails; in `evidence:` quote the pytest summary line; in `files_changed:` the commit hash12 and paths.
