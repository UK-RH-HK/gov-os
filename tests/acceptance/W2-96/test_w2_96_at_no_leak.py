"""KPI success 2 and failure 1: nothing of the tests' content reaches the caller.

No test source, assertion text or value, traceback, captured output, fixture or file name of the acceptance folder
in the output, the ``--json`` envelope, the exit message or any file left behind; pytest runs in a child process
whose output is discarded, and the run's temporary files are removed. Leaks are probed by the marker
(``w2_96_support.MARKER``), which every planted name, message, value and print carries; ``assert_clean`` searches
stdout, stderr, every file created or changed in the planted project, the given ``TMPDIR`` and ``HOME``.
Run errors (collection, timeout, crash) are probed the same way in ``test_w2_96_at_run_errors.py``, refusals in
``test_w2_96_at_unmapped_and_no_map.py`` and ``test_w2_96_at_exit_codes.py``.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_96_support as support  # noqa: E402


@pytest.fixture(scope="module")
def fails(tmp_path_factory):
    """A failing assertion with its values, a setup error, a teardown error, a skip, prints, logs and warnings."""
    return support.Project(tmp_path_factory.mktemp("fails"), support.fails_files(), support.FAILS_README)


def test_a_failing_run_shows_no_assertion_text_value_traceback_or_captured_output(fails):
    run = fails.run(support.TICKET_ID)
    support.assert_outcome(run, support.FAILS_EXPECTED, support.EXIT_FAIL)
    support.assert_clean(run)


def test_the_text_output_of_a_failing_run_shows_none_of_it_either(fails):
    run = fails.run(support.TICKET_ID, json_mode=False)
    assert run.returncode == support.EXIT_FAIL, f"exit code {run.returncode}, expected 3\n{run.describe()}"
    problems = support.text_problems(run.stdout, support.FAILS_EXPECTED)
    assert not problems, "\n".join(problems) + "\n" + run.describe()
    support.assert_clean(run)


def test_the_tests_temporary_folders_are_made_in_the_runs_private_folder_and_removed(fails):
    run = fails.run(support.TICKET_ID)
    support.assert_outcome(run, support.FAILS_EXPECTED, support.EXIT_FAIL)
    records = fails.records("ran")
    assert records, "the planted tests left no probe record"
    given = run.tmpdir.resolve()
    for record in records:
        folder = Path(record["tmp_path"]).resolve()
        assert given in folder.parents, f"a test's temporary folder {folder} is not under the given TMPDIR {given}"
        assert not folder.exists(), f"a test's temporary folder is left behind: {folder}"
    support.assert_clean(run)


def test_an_interrupted_run_stops_its_child_and_leaves_nothing(tmp_path):
    """SIGINT to gov alone, while a planted test sleeps: the child is stopped, nothing is left, nothing shown."""
    project = support.Project(tmp_path, support.second_file("sleep", "test_qzv96leak_sleeper"),
                              support.SECOND_README)
    started = project.start(support.TICKET_ID)
    try:
        sleeping = started.wait_for("sleeping", support.START_WAIT_S)
        run = started.interrupt()
        assert support.pid_gone(sleeping["pid"]), "the child pytest still runs after gov accept was interrupted"
        support.assert_clean(run, generic=False)
    finally:
        started.stop()
