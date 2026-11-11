"""Review 1's cases for ``gov accept``: the independent reviewer's findings, given to this suite as described
behaviours (DEC-136); where they differ from the design note, they override it.

- **R1** The runner never gives pytest a base folder of its own; the child's TMPDIR is a folder inside the private
  folder, so pytest's own default base folder and every test's temporary folder fall inside it. A project whose
  conftest refuses a per-run base folder (as this repository's ``tests/conftest.py`` does) is run and reported.
- **R2** SIGTERM or SIGHUP to ``gov`` alone ends the run as an interrupt does: the child and all it started are
  stopped and the private folder removed before ``gov`` exits, with exit code 128 plus the signal's number.
- **R3** The private folder is removed even when a test left folders or files in it without read, write or execute
  permission, after a failure and after a timeout's kill alike.
- **R4** A map row whose Tests cell holds an item while its KPI cell begins with no line name the reader takes, or
  a Tests table with no KPI column under a heading that begins with the word success, failure or KPI but names no
  line, refuses the whole run before any test runs: ``ACCEPT_MAP_UNREADABLE``, exit code 1, ``ok: false``.
- **R5** ``::test_x`` and ``stem::test_x`` (no ``.py`` before the ``::``) map every test of the folder of that
  function name; an item naming a test (it holds ``::`` or begins with ``test_``) that matches no case fails its line.
- **R6** No log file is written, whatever the project's pytest configuration says.
- **R7** pytest's "tests failed" exit code with no failed or errored case in its report is a ``crash``.

Every case runs the suite's leak probe (``assert_clean``: the marker in stdout, stderr, the project, the given
``TMPDIR`` and ``HOME``; the given ``TMPDIR`` empty; the project unchanged). The ``test_premise_*`` cases test the
planted projects themselves, and are green before the implementation by design.
"""

from __future__ import annotations

import re
import shutil
import signal
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_96_support as support  # noqa: E402

SECOND_FAILS_RAW = {
    "test_qzv96leak_alpha::test_qzv96leak_alpha_one": "passed",
    "test_qzv96leak_alpha::test_qzv96leak_alpha_param[qzv96leak-id-a]": "passed",
    "test_qzv96leak_alpha::test_qzv96leak_alpha_param[qzv96leak-id-b]": "passed",
    "test_qzv96leak_second::test_qzv96leak_second_fails": "failed",
}


def _locked(name, kind):
    """``ALPHA`` and a second file whose one case (``locked_fail`` or ``locked_sleep``) locks folders up (R3)."""
    return support.second_file(kind, name, extra=support.LOCK_UP)


def _tops_outside(project, run, kind):
    """The planted locked folders made outside the given TMPDIR (removing them must have been the run's work)."""
    records = project.records(kind)
    if not records:
        return [f"the planted test never locked its folders (no {kind!r} record)"]
    given = run.tmpdir.resolve()
    return [f"a planted locked folder {top} was made outside the given TMPDIR {given}"
            for record in records for top in record.get("tops", ()) if given not in Path(top).resolve().parents]


def _unlock_all(project):
    """Give back the permissions a planted test took, wherever it locked, so pytest's own clean-up can remove it."""
    for record in project.records():
        for top in record.get("tops", ()):
            support.unlock(top)
    support.unlock(project.base)


# R1 -----------------------------------------------------------------------------------------------------------

def test_r1_a_project_whose_conftest_refuses_a_per_run_base_folder_is_run_and_reported_per_line(tmp_path):
    """The planted ``tests/conftest.py`` refuses a run given ``--basetemp``; a passing line passes, a failing one
    fails, the tests' temporary folders are in pytest's own base folder under the child's TMPDIR."""
    project = support.Project(tmp_path, support.SECOND_FAILS, support.SECOND_README,
                              root_files=support.REFUSING_CONFTEST)
    run = project.run(support.TICKET_ID)
    support.assert_outcome(run, support.SECOND_FAILS_EXPECTED, support.EXIT_FAIL)
    conftest = project.records("conftest")
    assert conftest, "the project's tests/conftest.py never ran in the child: its refusal was not in force"
    assert all(record["basetemp"] is None for record in conftest), f"pytest was given a base folder: {conftest}"
    given = run.tmpdir.resolve()
    ran = project.records("ran")
    assert ran, "the planted tests left no probe record"
    for record in ran:
        tempdir, folder = Path(record["tempdir"]).resolve(), Path(record["tmp_path"]).resolve()
        assert given in tempdir.parents, f"the child's TMPDIR {tempdir} is not a folder under the given {given}"
        assert tempdir in folder.parents and folder.relative_to(tempdir).parts[0].startswith("pytest-of-"), \
            f"a test's temporary folder {folder} is not in pytest's own default base folder under {tempdir}"
    support.assert_clean(run)


# R2 -----------------------------------------------------------------------------------------------------------

@pytest.mark.parametrize("signum", [signal.SIGTERM, signal.SIGHUP], ids=["SIGTERM", "SIGHUP"])
def test_r2_a_sigterm_or_sighup_to_gov_alone_stops_the_run_leaves_nothing_and_exits_128_plus_the_signal(
        tmp_path, signum):
    """The signal to gov's own process only, while a planted test (and the grandchild it started) sleeps."""
    project = support.Project(tmp_path, support.second_file("sleep", "test_qzv96leak_sleeper"),
                              support.SECOND_README)
    started = project.start(support.TICKET_ID)
    try:
        sleeping = started.wait_for("sleeping", support.START_WAIT_S)
        run = started.send(signum)
        problems = run.problems(generic=False)   # first, so it is what gov left when it exited
        expected = 128 + int(signum)
        if run.returncode != expected:
            problems.append(f"exit code {run.returncode}, expected {expected} (128 plus signal {int(signum)})")
        if not support.pid_gone(sleeping["pid"]):
            problems.append("the child pytest still runs after gov accept ended")
        if not support.pid_gone(sleeping["grandchild"]):
            problems.append("a process the child started still runs after gov accept ended")
        assert not problems, "\n".join(problems) + "\n" + run.describe()
    finally:
        started.stop()


# R3 -----------------------------------------------------------------------------------------------------------

def test_r3_folders_without_permissions_left_by_a_failing_test_are_removed(tmp_path):
    """A failing test leaves, in its tmp_path and in a folder of its temporary folder, folders without read,
    write, execute or any permission (each holding a locked folder and a file) and a file without any."""
    project = support.Project(tmp_path, _locked("test_qzv96leak_locked_fails", "locked_fail"),
                              support.SECOND_README)
    try:
        run = project.run(support.TICKET_ID)
        support.assert_clean(run)
        support.assert_outcome(run, support.SECOND_FAILS_EXPECTED, support.EXIT_FAIL)
        outside = _tops_outside(project, run, "locked")
        assert not outside, "\n".join(outside)
    finally:
        _unlock_all(project)


def test_r3_folders_without_permissions_held_at_a_timeout_are_removed(tmp_path):
    """A planted test locks the same folders up, then sleeps; ``--timeout 8`` kills the run."""
    project = support.Project(tmp_path, _locked("test_qzv96leak_locked_sleeper", "locked_sleep"),
                              support.SECOND_README)
    try:
        run = project.run(support.TICKET_ID, "--timeout", str(support.TIMEOUT_OPTION_S), timeout=150)
        support.assert_clean(run)
        support.assert_outcome(run, support.error_result("timeout"), support.EXIT_ERROR)
        sleeping = project.records("sleeping")
        assert sleeping, "the planted test never locked its folders and slept (the run ended before it)"
        assert support.pid_gone(sleeping[0]["pid"]), "the child pytest still runs after the timeout"
        outside = _tops_outside(project, run, "sleeping")
        assert not outside, "\n".join(outside)
    finally:
        project.kill_recorded()
        _unlock_all(project)


# R4 -----------------------------------------------------------------------------------------------------------

@pytest.mark.parametrize("kind", list(support.UNREADABLE_ROWS))
def test_r4_a_row_whose_kpi_cell_names_no_line_the_reader_takes_refuses_the_run(tmp_path, kind):
    """``Failure:`` with no number, ``Success 3a``, ``S8b``, a cell naming no line: each beside a readable row,
    its Tests cell naming the failing planted file, case or function."""
    project = support.Project(tmp_path, support.SECOND_FAILS, support.UNREADABLE_ROWS[kind])
    run = project.run(support.TICKET_ID)
    support.assert_refusal(run, support.MAP_UNREADABLE)
    assert project.records() == [], f"a planted test ran: the refusal comes before any test runs\n{run.describe()}"
    support.assert_no_raw_output(run)
    support.assert_clean(run)


@pytest.mark.parametrize("kind", list(support.UNREADABLE_HEADINGS))
def test_r4_a_tests_table_under_a_success_failure_or_kpi_heading_naming_no_line_refuses_the_run(tmp_path, kind):
    """``### Failure: …`` with no number, ``## SUCCESS …``, ``#### kpi …`` over a Tests table with no KPI column,
    each after a readable heading-form table."""
    project = support.Project(tmp_path, support.SECOND_FAILS, support.UNREADABLE_HEADINGS[kind])
    run = project.run(support.TICKET_ID)
    support.assert_refusal(run, support.MAP_UNREADABLE)
    assert project.records() == [], f"a planted test ran: the refusal comes before any test runs\n{run.describe()}"
    support.assert_no_raw_output(run)
    support.assert_clean(run)


def test_r4_the_text_form_of_accept_map_unreadable_gives_its_code_and_runs_nothing(tmp_path):
    project = support.Project(tmp_path, support.SECOND_FAILS, support.UNREADABLE_ROWS["failure-without-a-number"])
    run = project.run(support.TICKET_ID, json_mode=False)
    assert run.returncode == support.EXIT_REFUSED, f"exit code {run.returncode}, expected 1\n{run.describe()}"
    assert support.MAP_UNREADABLE in run.stderr, f"the refusal names its code on stderr\n{run.describe()}"
    assert project.records() == [], f"a planted test ran: the refusal comes before any test runs\n{run.describe()}"
    support.assert_no_raw_output(run)
    support.assert_clean(run)


# R5 -----------------------------------------------------------------------------------------------------------

def test_r5_items_holding_a_double_colon_with_no_py_file_before_it_map_by_function_name(tmp_path):
    """``::name``, ``stem::name`` and ``any_word::name`` map every test of the folder whose function is ``name``
    (two files share one name); the failing one fails its line."""
    project = support.Project(tmp_path, support.ITEMS_FILES, support.ITEMS_COLON_README)
    run = project.run(support.TICKET_ID)
    support.assert_outcome(run, support.ITEMS_COLON_EXPECTED, support.EXIT_FAIL)
    support.assert_clean(run)


def test_r5_an_item_naming_a_test_that_matches_no_case_fails_its_line(tmp_path):
    """A ``test_`` word, a ``file.py::test`` item, a ``test_….py`` file and a ``::test`` item matching nothing
    each fail their line (counted, never named); a line whose items all match and pass passes, and so does one
    beside whose cases a word naming no test matches nothing."""
    project = support.Project(tmp_path, support.ITEMS_FILES, support.ITEMS_UNMATCHED_README)
    run = project.run(support.TICKET_ID)
    support.assert_outcome(run, support.ITEMS_UNMATCHED_EXPECTED, support.EXIT_FAIL)
    support.assert_clean(run)


# R6 -----------------------------------------------------------------------------------------------------------

@pytest.mark.parametrize("where", list(support.LOG_FILES))
def test_r6_no_log_file_is_written_whatever_the_projects_pytest_configuration_says(tmp_path, where):
    """The planted ``pyproject.toml`` names a ``log_file`` in the project (relative to the root, or absolute)."""
    project = support.Project(tmp_path, dict(support.ALPHA), support.SIMPLE_README,
                              root_files=support.log_file_config(where))
    run = project.run(support.TICKET_ID)
    log = project.root / support.LOG_FILES[where]
    assert not log.exists(), f"pytest's log file was written in the project: {log}\n{run.describe()}"
    support.assert_outcome(run, support.SIMPLE_EXPECTED, support.EXIT_PASS)
    support.assert_clean(run)


# R7 -----------------------------------------------------------------------------------------------------------

def test_r7_a_tests_failed_exit_with_no_failed_case_in_the_report_is_a_crash(tmp_path):
    """Three cases pass, then a test calls ``pytest.exit(returncode=1)``; the failing test after it never runs."""
    project = support.Project(tmp_path, support.EXIT_FILES, support.SECOND_README)
    run = project.run(support.TICKET_ID)
    support.assert_outcome(run, support.error_result("crash"), support.EXIT_ERROR)
    support.assert_clean(run)


# Premises: the planted projects do what the cases above rely on (green before the implementation, by design) ---

def test_premise_r1_the_planted_conftest_refuses_a_per_run_base_folder_and_nothing_else(tmp_path):
    project = support.Project(tmp_path, support.SECOND_FAILS, support.SECOND_README,
                              root_files=support.REFUSING_CONFTEST)
    done, outcomes = project.raw_pytest()
    assert done.returncode == 4 and outcomes is None, f"with --basetemp: exit {done.returncode}\n{done.stderr[-2000:]}"
    assert support.MARKER in (done.stdout + done.stderr).lower(), "the refusal's message holds the marker"
    assert project.records("ran") == [], "the refusal comes before any planted test runs"
    done, outcomes = project.raw_pytest(basetemp=False)
    assert outcomes == SECOND_FAILS_RAW, f"without --basetemp: {outcomes}\n{done.stdout[-3000:]}"
    assert [record["basetemp"] for record in project.records("conftest")] == [None], "the conftest ran once"


def test_premise_r3_a_plain_removal_leaves_the_planted_locked_folders(tmp_path):
    project = support.Project(tmp_path, _locked("test_qzv96leak_locked_fails", "locked_fail"),
                              support.SECOND_README)
    try:
        done, outcomes = project.raw_pytest()
        expected = {**{k: v for k, v in SECOND_FAILS_RAW.items() if "second" not in k},
                    "test_qzv96leak_second::test_qzv96leak_locked_fails": "failed"}
        assert outcomes == expected, f"raw pytest: {outcomes}\n{done.stdout[-3000:]}"
        records = project.records("locked")
        assert len(records) == 1 and len(records[0]["tops"]) == 2, f"the planted test locked two folders: {records}"
        for top in records[0]["tops"]:
            shutil.rmtree(top, ignore_errors=True)
            assert Path(top).exists(), f"a plain removal removed {top}: R3's cases would prove nothing"
    finally:
        _unlock_all(project)


def test_premise_r4_each_unreadable_readme_holds_a_readable_line_beside_its_unreadable_one():
    for kind, text in support.UNREADABLE_ROWS.items():
        (header, body), = [table for table in support.markdown_tables(text) if table[0][0] == "KPI line"]
        assert [support.line_names(row[0]) for row in body] == [["success-1"], []], kind
        assert all(re.search(r"`[^`]+`", row[1]) for row in body), f"{kind}: each row holds an item"
    for kind, text in support.UNREADABLE_HEADINGS.items():
        headings = re.findall(r"^#{2,6}\s+(.*)$", text, re.MULTILINE)
        assert [support.line_names(heading) for heading in headings] == [["success-1"], []], kind
        assert re.match(r"(success|failure|kpi)\b", headings[1], re.IGNORECASE), kind
        assert len(support.markdown_tables(text)) == 2, f"{kind}: a Tests table under each heading"


def test_premise_r5_the_items_files_give_the_designed_outcomes(tmp_path):
    project = support.Project(tmp_path, support.ITEMS_FILES, support.SIMPLE_README)
    done, outcomes = project.raw_pytest()
    assert outcomes == support.ITEMS_RAW, f"raw pytest: {outcomes}\n{done.stdout[-3000:]}"


@pytest.mark.parametrize("where", list(support.LOG_FILES))
def test_premise_r6_raw_pytest_writes_the_configured_log_file_holding_the_marker(tmp_path, where):
    project = support.Project(tmp_path, dict(support.ALPHA), support.SIMPLE_README,
                              root_files=support.log_file_config(where))
    done, outcomes = project.raw_pytest()
    assert outcomes and set(outcomes.values()) == {"passed"}, f"raw pytest: {outcomes}\n{done.stdout[-3000:]}"
    log = project.root / support.LOG_FILES[where]
    assert log.is_file(), f"raw pytest wrote no log file at {log}"
    assert support.MARKER in log.read_text(encoding="utf-8").lower(), "the log file holds the tests' log lines"


def test_premise_r7_the_planted_exit_ends_pytest_with_code_1_and_a_report_without_failures(tmp_path):
    project = support.Project(tmp_path, support.EXIT_FILES, support.SECOND_README)
    done, outcomes = project.raw_pytest()
    assert done.returncode == 1, f"raw pytest ended {done.returncode}\n{done.stdout[-3000:]}"
    assert outcomes is not None and "failed" not in outcomes.values(), f"the report: {outcomes}"
    ran = project.ran()
    assert ran.get("test_qzv96leak_exits") == 1 and "test_qzv96leak_after_exit" not in ran, f"what ran: {ran}"
