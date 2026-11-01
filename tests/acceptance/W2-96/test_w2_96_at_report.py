"""KPI success 1: ``gov accept <ticket>`` runs that ticket's declared acceptance folder with the tree's own ``src/``
and reports, per KPI line of the folder's README map, pass or fail with the counts under each line; ``--json``
gives the same in the API-0002 envelope.

Both map forms of the design note's §1 are tried on the same six planted files (12 cases pass, 1 fails, 1 is
skipped): every KPI line name form, every separator, every item form, numeric line order, text outside the map,
and a table under a heading that names no line. Every case also checks KPI 2's and KPI 5's rules (``assert_clean``).

Revised for run 2 (DEC-970, PKG-1 (a), R8): both maps leave the one failing case unmapped, and any failed case,
mapped or not, fails the run, so these runs answer ``outcome: fail`` with exit code 3. Every line is still
reported exactly as before (each passes, with its counts).
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_96_support as support  # noqa: E402


@pytest.fixture(scope="module")
def rows(tmp_path_factory):
    """The six common files under the row-form map (one project, several runs)."""
    return support.Project(tmp_path_factory.mktemp("rows"), support.common_files(), support.ROWS_README)


def test_a_row_form_map_is_reported_per_kpi_line_with_its_counts(rows):
    run = rows.run(support.TICKET_ID)
    support.assert_outcome(run, support.ROWS_EXPECTED, support.EXIT_FAIL)   # R8: the unmapped failure fails the run
    assert rows.ran() == support.COMMON_RAN, f"every case of the declared folder runs, and only those: {rows.ran()}"
    support.assert_clean(run)


def test_a_heading_form_map_is_reported_per_kpi_line_with_its_counts(tmp_path):
    project = support.Project(tmp_path, support.common_files(), support.HEADINGS_README)
    run = project.run(support.TICKET_ID)
    support.assert_outcome(run, support.HEADINGS_EXPECTED, support.EXIT_FAIL)   # R8
    support.assert_clean(run)


def test_the_wbs_id_names_the_same_ticket(rows):
    run = rows.run(support.WBS_ID)
    support.assert_outcome(run, support.ROWS_EXPECTED, support.EXIT_FAIL)  # "ticket" is the ticket id; R8
    support.assert_clean(run)


def test_each_ticket_runs_its_own_declared_folder(rows):
    run = rows.run(support.OTHER_ID)
    expected = support.result("fail", [support.line("success-1", "fail", 0, 1)], totals=support.counts(0, 1),
                              ticket=support.OTHER_ID)
    support.assert_outcome(run, expected, support.EXIT_FAIL)
    assert rows.ran() == {"test_qzv96leak_other_fails": 1}, f"only the other ticket's folder ran: {rows.ran()}"
    support.assert_clean(run)


def test_the_child_runs_in_the_root_with_the_trees_own_src_first(tmp_path):
    """The planted cases pass only if they import the planted ``src/`` before the decoy the run was given."""
    project = support.Project(tmp_path, dict(support.ALPHA), support.SIMPLE_README)
    run = project.run(support.TICKET_ID)
    support.assert_outcome(run, support.SIMPLE_EXPECTED, support.EXIT_PASS)
    working = {record["cwd"] for record in project.records("ran")}
    assert working == {str(project.root.resolve())}, f"the child's working folder is the root: {working}"
    support.assert_clean(run)


def test_the_root_option_runs_the_named_project_from_another_folder(rows):
    run = rows.run(support.TICKET_ID, "--root", str(rows.root), cwd=rows.elsewhere)
    support.assert_outcome(run, support.ROWS_EXPECTED, support.EXIT_FAIL)   # R8
    working = {record["cwd"] for record in rows.records("ran")}
    assert working == {str(rows.root.resolve())}, f"the child's working folder is the root: {working}"
    support.assert_clean(run)


def test_the_text_output_gives_the_same_result_as_json(rows):
    run = rows.run(support.TICKET_ID, json_mode=False)
    assert run.returncode == support.EXIT_FAIL, f"exit code {run.returncode}, expected 3 (R8)\n{run.describe()}"
    problems = support.text_problems(run.stdout, support.ROWS_EXPECTED)
    assert not problems, "\n".join(problems) + "\n" + run.describe()
    support.assert_clean(run)
