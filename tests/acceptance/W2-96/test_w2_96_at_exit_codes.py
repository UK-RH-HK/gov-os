"""KPI success 5 and failure 4: exit code 0 when every mapped line passes, 3 when a mapped line fails, 4 when the
run errors, 1 for a refusal (``ACCEPT_UNKNOWN_TICKET``, ``ACCEPT_NO_TESTS``, ``ACCEPT_NO_MAP``), with the
envelope's ``ok`` true for the first three and false for a refusal; a read command, it writes nothing in the
repository (its tree unchanged, ignored files included: no ``.pytest_cache``, no ``__pycache__``, no report).
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_96_support as support  # noqa: E402

line, counts = support.line, support.counts

# One failing mapped line beside a passing one: the files, the README, the failing line, unmapped and totals.
ONE_FAILING = {
    "assertion": (support.second_file("fail", "test_qzv96leak_second_fails"), support.SECOND_README,
                  line("success-2", "fail", 0, 1), counts(), counts(3, 1)),
    "setup-error": (support.second_file("setup_error", "test_qzv96leak_second_setup"), support.SECOND_README,
                    line("success-2", "fail", 0, 1), counts(), counts(3, 1)),
    "teardown-error": (support.second_file("teardown_error", "test_qzv96leak_second_teardown"),
                       support.SECOND_README, line("success-2", "fail", 0, 1), counts(), counts(3, 1)),
    "only-skipped": (support.second_file("skip", "test_qzv96leak_second_skip"), support.SECOND_README,
                     line("success-2", "fail", 0, 0, 1), counts(), counts(3, 0, 1)),
    "no-matching-case": (support.second_file("pass", "test_qzv96leak_second_unmapped"),
                         support.second_file_readme("`qzv96leak_matches_nothing`"), line("success-2", "fail"),
                         counts(1), counts(4)),
}

# Each outcome's exit code and ok: the files and the README.
EXIT_CASES = {
    "pass": (dict(support.ALPHA), support.SIMPLE_README, support.EXIT_PASS, True),
    "fail": (support.second_file("fail", "test_qzv96leak_second_fails"), support.SECOND_README,
             support.EXIT_FAIL, True),
    "error": (support.collection_files("empty"), support.SECOND_README, support.EXIT_ERROR, True),
    "refusal": (dict(support.ALPHA), None, support.EXIT_REFUSED, False),
}

# Tickets with no acceptance folder inside the root: the ticket's acceptance_tests block.
NO_TESTS = {
    "no-acceptance-tests": None,
    "no-path": "acceptance_tests:\n  author: independent-test-designer (planted)\n",
    "missing-folder": support.acceptance_block("tests/acceptance/W9-69/"),
    "a-file": support.acceptance_block(support.FOLDER + "/README.md"),
    "outside-the-root": support.acceptance_block("../outside/"),
}


@pytest.mark.parametrize("kind", list(EXIT_CASES))
def test_the_exit_code_and_ok_of_a_pass_a_fail_an_error_and_a_refusal(tmp_path, kind):
    files, readme, code, ok = EXIT_CASES[kind]
    project = support.Project(tmp_path, files, readme)
    run = project.run(support.TICKET_ID)
    envelope = run.envelope()
    assert envelope["ok"] is ok, f"ok is {envelope['ok']}, expected {ok}\n{run.describe()}"
    assert run.returncode == code, f"exit code {run.returncode}, expected {code}\n{run.describe()}"
    support.assert_clean(run)


@pytest.mark.parametrize("kind", list(ONE_FAILING))
def test_one_failing_mapped_line_fails_the_run_with_exit_code_3(tmp_path, kind):
    files, readme, failing, unmapped, totals = ONE_FAILING[kind]
    project = support.Project(tmp_path, files, readme)
    run = project.run(support.TICKET_ID)
    expected = support.result("fail", [line("success-1", "pass", 3), failing], unmapped, totals)
    support.assert_outcome(run, expected, support.EXIT_FAIL)
    support.assert_clean(run)


@pytest.mark.parametrize("ticket", ["TDPL-zzzz", "W9-98"], ids=["ticket-id", "wbs-id"])
def test_an_unknown_ticket_is_refused_with_accept_unknown_ticket(tmp_path, ticket):
    project = support.Project(tmp_path, dict(support.ALPHA), support.SIMPLE_README)
    run = project.run(ticket)
    support.assert_refusal(run, support.UNKNOWN_TICKET)
    assert project.records() == [], "a refusal runs nothing"
    support.assert_clean(run)


@pytest.mark.parametrize("kind", list(NO_TESTS))
def test_a_ticket_without_an_acceptance_folder_inside_the_root_is_refused_with_accept_no_tests(tmp_path, kind):
    project = support.Project(tmp_path, dict(support.ALPHA), support.SIMPLE_README, acceptance=NO_TESTS[kind],
                              outside=(dict(support.ALPHA), support.SIMPLE_README))
    run = project.run(support.TICKET_ID)
    support.assert_refusal(run, support.NO_TESTS)
    assert project.records() == [], "a refusal runs nothing (not the folder outside the root either)"
    support.assert_clean(run)


def test_nothing_is_written_in_the_repository_ignored_files_included(tmp_path):
    project = support.Project(tmp_path, support.fails_files(), support.FAILS_README)
    run = project.run(support.TICKET_ID)
    support.assert_outcome(run, support.FAILS_EXPECTED, support.EXIT_FAIL)
    assert run.changes() == {}, f"the run changed the project: {run.changes()}"
    status = subprocess.run(["git", "status", "--porcelain", "--ignored", "--untracked-files=all"],
                            cwd=project.root, env=support._git_env(project.home), capture_output=True, text=True,
                            check=True, stdin=subprocess.DEVNULL).stdout
    assert status == "", f"git sees new or ignored files in the project:\n{status}"
    left = [path for path in support.everything_under(project.root) if not path.startswith(".git" + "/")
            and (Path(path).name in ("__pycache__", ".pytest_cache") or path.endswith((".pyc", ".xml", ".json")))]
    assert not left, f"the run left caches or a report in the project: {left}"
    support.assert_clean(run)
