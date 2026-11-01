"""KPI success 4 and failure 3: a collection error, a timeout or a crash is reported as ``error`` for the run with
its kind only (``collection``, ``timeout``, ``crash``), never its message; no line is reported pass or fail
(``lines`` is empty and every count 0), the exit code is 4 and the envelope's ``ok`` is true.

Every planted error's message, and every name and print around it, carries the marker; ``assert_clean`` finds none.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_96_support as support  # noqa: E402


@pytest.mark.parametrize("kind", ["import", "syntax", "empty"])
def test_a_collection_error_is_an_error_of_kind_collection_with_no_message(tmp_path, kind):
    """An import error, a syntax error, or nothing collected."""
    project = support.Project(tmp_path, support.collection_files(kind), support.SECOND_README)
    run = project.run(support.TICKET_ID)
    support.assert_outcome(run, support.error_result("collection"), support.EXIT_ERROR)
    support.assert_clean(run)


def test_a_timeout_is_an_error_of_kind_timeout_and_the_childs_process_group_is_killed(tmp_path):
    """A planted test starts a grandchild, then sleeps; ``--timeout 8`` ends the run."""
    project = support.Project(tmp_path, support.second_file("sleep", "test_qzv96leak_sleeper"),
                              support.SECOND_README)
    try:
        run = project.run(support.TICKET_ID, "--timeout", str(support.TIMEOUT_OPTION_S), timeout=150)
        support.assert_outcome(run, support.error_result("timeout"), support.EXIT_ERROR)
        assert run.elapsed >= support.TIMEOUT_OPTION_S - 0.5, f"ended after {run.elapsed:.1f} s, before the timeout"
        sleeping = project.records("sleeping")
        assert sleeping, "the planted sleeping test never started (the timeout ended the run before it)"
        assert support.pid_gone(sleeping[0]["pid"]), "the child pytest still runs after the timeout"
        assert support.pid_gone(sleeping[0]["grandchild"]), "the child's process group was not killed"
        support.assert_clean(run)
    finally:
        project.kill_recorded()


@pytest.mark.parametrize("kind", ["crash_signal", "crash_internal"])
def test_a_crash_is_an_error_of_kind_crash_with_no_message(tmp_path, kind):
    """The child killed by a signal (SIGKILL), or ended with pytest's internal-error code (3) and no report."""
    project = support.Project(tmp_path, support.second_file(kind, f"test_qzv96leak_{kind}"), support.SECOND_README)
    run = project.run(support.TICKET_ID)
    support.assert_outcome(run, support.error_result("crash"), support.EXIT_ERROR)
    support.assert_clean(run)


def test_the_text_form_of_a_run_error_gives_its_kind_only(tmp_path):
    project = support.Project(tmp_path, support.collection_files("import"), support.SECOND_README)
    run = project.run(support.TICKET_ID, json_mode=False)
    assert run.returncode == support.EXIT_ERROR, f"exit code {run.returncode}, expected 4\n{run.describe()}"
    problems = support.text_problems(run.stdout, support.error_result("collection"))
    assert not problems, "\n".join(problems) + "\n" + run.describe()
    support.assert_clean(run)
