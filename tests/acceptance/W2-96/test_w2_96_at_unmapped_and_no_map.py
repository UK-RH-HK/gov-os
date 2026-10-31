"""KPI success 3 and failure 2: a test the README does not map is counted under ``unmapped`` (pass, fail and skip
counts), never named; a folder with no README, or a README with no map, is refused with ``ACCEPT_NO_MAP`` and
never answered with raw output.

Revised for run 2 (DEC-970, PKG-1 (a), R8): an unmapped failed case now fails the run (exit code 3), while it is
still only counted, never named. The two cases that held "an unmapped failure never changes the exit code" hold
the new rule; run 2's own R8 cases are in ``test_w2_96_at_run_2.py``.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_96_support as support  # noqa: E402

# READMEs that hold no map (the design note's §1): no row maps a line.
NO_MAP_READMES = {
    "empty": "",
    "prose-only": ("# qzv96leak planted suite\n\nSuccess 1: `test_qzv96leak_alpha.py` covers it (qzv96leak).\n\n"
                   "- KPI 2: `test_qzv96leak_beta.py`, qzv96leak\n"),
    # Review 1 (R4) revised this case: a row holding a backticked item whose KPI cell names no line now refuses with
    # ACCEPT_MAP_UNREADABLE, and which code a README answers when it is also mapless is open (returned as a
    # package), so its rows hold no backticked item and name no line: no row maps a line.
    "rows-naming-no-line": support.rows_readme(
        ("Edge qzv96leak", "test_qzv96leak_alpha.py, with no backticks"),
        ("Notes qzv96leak", "no item at all, qzv96leak")),
    "heading-naming-no-line": ("# qzv96leak planted suite\n\n## Notes qzv96leak\n\n| Test | Notes |\n|---|---|\n"
                               "| `test_qzv96leak_alpha.py` | qzv96leak |\n"),
    "kpi-table-without-a-test-column": support.rows_readme(
        ("Success 1: qzv96leak", "`test_qzv96leak_alpha.py`"), header=("KPI line", "Why qzv96leak")),
}


@pytest.fixture(scope="module")
def rows(tmp_path_factory):
    return support.Project(tmp_path_factory.mktemp("rows"), support.common_files(), support.ROWS_README)


def test_unmapped_cases_are_counted_never_named(rows):
    run = rows.run(support.TICKET_ID)
    # unmapped: 3 passed, 1 failed; R8: the unmapped failure fails the run, every mapped line still passing
    support.assert_outcome(run, support.ROWS_EXPECTED, support.EXIT_FAIL)
    named = [name for name in support.ROWS_UNMAPPED_NAMES if name in (run.stdout + run.stderr).lower()]
    assert not named, f"unmapped cases are named: {named}\n{run.describe()}"
    support.assert_clean(run)


def test_an_unmapped_failure_fails_the_run_in_text_too_and_is_never_named(rows):
    """Revised for run 2 (R8) from ``test_an_unmapped_failure_never_changes_the_exit_code_in_text_either``."""
    run = rows.run(support.TICKET_ID, json_mode=False)
    assert run.returncode == support.EXIT_FAIL, f"exit code {run.returncode}, expected 3 (R8)\n{run.describe()}"
    assert "unmapped" in run.stdout.lower(), f"the text gives the unmapped counts\n{run.describe()}"
    named = [name for name in support.ROWS_UNMAPPED_NAMES if name in (run.stdout + run.stderr).lower()]
    assert not named, f"unmapped cases are named: {named}\n{run.describe()}"
    support.assert_clean(run)


def test_a_folder_without_a_readme_is_refused_with_accept_no_map(tmp_path):
    project = support.Project(tmp_path, support.common_files(), None)
    run = project.run(support.TICKET_ID)
    support.assert_refusal(run, support.NO_MAP)
    support.assert_no_raw_output(run)
    support.assert_clean(run)


@pytest.mark.parametrize("kind", list(NO_MAP_READMES))
def test_a_readme_without_a_map_is_refused_with_accept_no_map(tmp_path, kind):
    project = support.Project(tmp_path, support.common_files(), NO_MAP_READMES[kind])
    run = project.run(support.TICKET_ID)
    support.assert_refusal(run, support.NO_MAP)
    support.assert_no_raw_output(run)
    support.assert_clean(run)


def test_the_text_form_of_the_refusal_gives_its_code_and_no_raw_output(tmp_path):
    project = support.Project(tmp_path, support.common_files(), NO_MAP_READMES["rows-naming-no-line"])
    run = project.run(support.TICKET_ID, json_mode=False)
    assert run.returncode == support.EXIT_REFUSED, f"exit code {run.returncode}, expected 1\n{run.describe()}"
    assert support.NO_MAP in run.stderr, f"the refusal names its code on stderr\n{run.describe()}"
    support.assert_no_raw_output(run)
    support.assert_clean(run)
