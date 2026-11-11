"""S-D10a's cases for ``gov accept`` (DEC-1112 (3), DEC-1061, DEC-959 item 6): the opt-in groups its map needs.

The ticket's line: ``gov accept`` runs the opt-in groups (the ``tests/optin-lifted*.txt`` suites) that its own map's
cases need, and only for that ticket's cases, so a KPI line whose mapped cases an opt-in list leaves out of a default
run is measured, not failed with no failed case; a line whose mapped cases still run zero stays a fail; the report
names which opt-in groups it enabled.

Each case plants a project whose ``tests/conftest.py`` holds this repository's opt-in rules (``OPTIN_CONFTEST``)
and whose ``tests/optin-lifted*.txt`` lists name planted cases, of this ticket (``W9-61``) and of the other
(``W9-62``). Checked, through the envelope, the exit code and the probe records only:

- a line whose cases only an opt-in list holds (a case in ``breadth`` or in ``lifted``, a whole file, the other rows
  of a ``rep:`` function, lines in both groups through all four list names) is measured: it passes when they pass
  and fails, with the failed case counted, when one fails;
- a line whose named case exists nowhere (in no file, or only in a list) still fails with no case;
- the other ticket's cases in a list are not run, a function of the same name included;
- a group no mapped case needs is not enabled, and none when none is needed;
- the report names the groups it enabled (``support.groups_named``), in ``--json`` and in text;
- nothing of the tests' content reaches the caller: every case runs the suite's leak probe (the lists, whose node
  ids carry the marker, included).

Scope (b) (the CTO's PKG-D10a-scope (b), DEC-1112 (3); DEC-1061 (2): lifted is report-only). A formal accept enables
only ``breadth`` for its map's cases, never ``lifted``:

- a line whose mapped cases rest only on ``lifted`` cases is ``"outcome": "report-only"`` (no case counted), neither
  pass nor fail, and does not by itself fail the run; the text form prints ``report-only (lifted)`` for it; the
  result's top-level ``"report_only"`` is ``["lifted"]`` and its ``"optin"`` never holds ``lifted``;
- a line with cases in ``lifted`` and elsewhere is measured on the cases that run;
- a line whose cases run zero for any other reason still fails, beside a report-only line;
- a ``lifted`` case never runs (a failing one changes nothing);
- a run that enables a group and ends in an ``error`` (a collection error, a crash) still names the groups it
  enabled in ``"optin"``, in ``--json`` and in text (round 1's F3).

The two variants that read ``lifted`` as enabled (``a-case-in-lifted-passes``, ``lines-in-both-groups-through-every-
list-name``) and the unneeded-group variant whose mapped case sat in ``lifted`` were revised to this reading
(``Rewrite-Reason: PKG-D10a-scope (b)``).
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_96_support as support  # noqa: E402

line, counts, result = support.line, support.counts, support.result
entry = support.optin_entry
BREADTH, LIFTED = "tests/optin-lifted-breadth.txt", "tests/optin-lifted.txt"
ALPHA_ROW = ("Success 1: qzv96leak", "`test_qzv96leak_alpha.py`")
ALPHA_RAN = {"test_qzv96leak_alpha_one": 1, "test_qzv96leak_alpha_param": 2}


def _optin_file(*cases):
    return {**support.ALPHA, support.OPTIN_FILE: support.planted_file(*cases)}


def _project(tmp_path, files, readme, lists, extra=None):
    """A planted project with the opt-in conftest, the lists ``{path from the root: [entries]}``, and ``extra``
    files in the root (the other ticket's folder, for instance)."""
    root_files = {**support.OPTIN_CONFTEST, **{path: support.optin_list(*entries) for path, entries in lists.items()},
                  **(extra or {})}
    return support.Project(tmp_path, files, readme, root_files=root_files)


def _check(project, run, expected, exit_code, ran, groups, optin_only=False):
    """The leak probe first, then the result, the exit code, what ran (by function, times run) and the groups the
    report names (with ``optin_only``, those its ``"optin"`` names, absent meaning none: scope (b))."""
    support.assert_clean(run)
    found = support.assert_outcome(run, expected, exit_code)
    assert project.ran() == ran, (f"the planted functions that ran (and how often) are not the expected ones\n"
                                  f"expected: {ran}\ngot:      {project.ran()}\n"
                                  f"groups the child saw: {[r.get('opted') for r in project.records('optin')]}\n"
                                  f"{run.describe()}")
    named = support.groups_named(found.get("optin")) if optin_only else _enabled(found)
    assert named == set(groups), (f"the report names the opt-in groups {sorted(named)}, expected {sorted(groups)} "
                                  f"(the groups it enabled)\n{run.describe()}")


def _enabled(found):
    """The groups the report names as enabled: anywhere in the result but its ``report_only`` key, which names the
    group a formal accept leaves report-only (scope (b))."""
    if isinstance(found, dict):
        found = {key: value for key, value in found.items() if key != "report_only"}
    return support.groups_named(found)


def _check_b(project, run, expected, exit_code, ran, enabled, report_only):
    """Scope (b): the leak probe, the result, the exit code and what ran; ``"optin"`` names exactly ``enabled`` and
    never ``lifted``; ``"report_only"`` is ``report_only`` (not judged when None)."""
    support.assert_clean(run)
    found = support.assert_outcome(run, expected, exit_code)
    assert project.ran() == ran, (f"the planted functions that ran (and how often) are not the expected ones "
                                  f"(a lifted case never runs in a formal accept)\nexpected: {ran}\n"
                                  f"got:      {project.ran()}\n"
                                  f"groups the child saw: {[r.get('opted') for r in project.records('optin')]}\n"
                                  f"{run.describe()}")
    optin = support.groups_named(found.get("optin"))
    assert optin == set(enabled), (f"\"optin\" names {sorted(optin)}, expected {sorted(enabled)} (never lifted)\n"
                                   f"{run.describe()}")
    if report_only is not None:
        assert found.get("report_only") == report_only, \
            f"\"report_only\" is {found.get('report_only')!r}, expected {report_only!r}\n{run.describe()}"
    return found


# A line whose cases sit only in an opt-in list is measured --------------------------------------------------------

WIDE = "test_qzv96leak_optin_wide"
NARROW = "test_qzv96leak_optin_narrow"
DEEP = "test_qzv96leak_optin_deep"
ROWS = "test_qzv96leak_optin_rows"

MEASURED = {
    # name: (cases of OPTIN_FILE, lists, the README's second and later rows, expected, exit code, ran, groups)
    "a-case-in-breadth-passes": (
        [("pass", WIDE)], {BREADTH: [entry(WIDE)]},
        [("Success 2: qzv96leak", f"`{support.OPTIN_FILE}::{WIDE}`")],
        result("pass", [line("success-1", "pass", 3), line("success-2", "pass", 1)], totals=counts(4)),
        support.EXIT_PASS, {WIDE: 1}, {"breadth"}),
    "a-case-in-breadth-fails": (
        [("fail", WIDE)], {BREADTH: [entry(WIDE)]},
        [("Success 2: qzv96leak", f"`{support.OPTIN_FILE}::{WIDE}`")],
        result("fail", [line("success-1", "pass", 3), line("success-2", "fail", 0, 1)], totals=counts(3, 1)),
        support.EXIT_FAIL, {WIDE: 1}, {"breadth"}),
    "a-whole-file-in-breadth": (
        [("pass", WIDE), ("pass", NARROW)], {BREADTH: [entry()]},
        [("Failure 1: qzv96leak", f"`{support.OPTIN_FILE}`")],
        result("pass", [line("success-1", "pass", 3), line("failure-1", "pass", 2)], totals=counts(5)),
        support.EXIT_PASS, {WIDE: 1, NARROW: 1}, {"breadth"}),
    "the-other-rows-of-a-rep-function": (
        [("rows_second_fails", ROWS)], {BREADTH: [f"rep: {entry(ROWS)}"]},
        [("Success 2: qzv96leak", f"`{ROWS}`")],
        result("fail", [line("success-1", "pass", 3), line("success-2", "fail", 1, 1)], totals=counts(4, 1)),
        support.EXIT_FAIL, {ROWS: 2}, {"breadth"}),
}


@pytest.mark.parametrize("variant", list(MEASURED))
def test_s_d10a_a_line_whose_cases_only_an_opt_in_list_holds_is_measured(tmp_path, variant):
    cases, lists, rows, expected, exit_code, ran, groups = MEASURED[variant]
    project = _project(tmp_path, _optin_file(*cases), support.rows_readme(ALPHA_ROW, *rows), lists)
    run = project.run(support.TICKET_ID)
    _check(project, run, expected, exit_code, {**ALPHA_RAN, **ran}, groups)


def test_s_d10a_the_text_form_gives_the_measured_line_and_names_the_group(tmp_path):
    cases, lists, rows, expected, exit_code, _, _ = MEASURED["a-case-in-breadth-fails"]
    project = _project(tmp_path, _optin_file(*cases), support.rows_readme(ALPHA_ROW, *rows), lists)
    run = project.run(support.TICKET_ID, json_mode=False)
    support.assert_clean(run)
    assert run.returncode == exit_code, f"exit code {run.returncode}, expected {exit_code}\n{run.describe()}"
    problems = support.text_problems(run.stdout, expected)
    assert not problems, "\n".join(problems) + "\n" + run.describe()
    assert re.search(r"(?<![\w-])breadth(?![\w-])", run.stdout.lower()), \
        f"the text does not name the opt-in group it enabled (breadth)\n{run.describe()}"


# A line whose mapped cases still run zero stays a fail ------------------------------------------------------------

GHOST = "test_qzv96leak_optin_ghost"

ZERO = {
    # name: (cases of OPTIN_FILE, lists, rows after ALPHA's, expected, ran, groups or None when not judged)
    "a-case-named-nowhere-beside-a-measured-line": (
        [("pass", WIDE)], {BREADTH: [entry(WIDE)]},
        [("Success 2: qzv96leak", f"`{WIDE}`"), ("Success 3: qzv96leak", f"`{support.OPTIN_FILE}::{GHOST}`")],
        result("fail", [line("success-1", "pass", 3), line("success-2", "pass", 1), line("success-3", "fail")],
               totals=counts(4)),
        {WIDE: 1}, {"breadth"}),
    "a-case-a-list-names-but-no-file-defines-beside-a-measured-line": (
        [("pass", WIDE)], {BREADTH: [entry(WIDE), entry(GHOST)]},
        [("Success 2: qzv96leak", f"`{WIDE}`"), ("Success 3: qzv96leak", f"`{support.OPTIN_FILE}::{GHOST}`")],
        result("fail", [line("success-1", "pass", 3), line("success-2", "pass", 1), line("success-3", "fail")],
               totals=counts(4)),
        {WIDE: 1}, {"breadth"}),
    "only-a-case-a-list-names-but-no-file-defines": (
        [], {BREADTH: [entry(GHOST)]},
        [("Success 2: qzv96leak", f"`{GHOST}`")],
        result("fail", [line("success-1", "pass", 3), line("success-2", "fail")], totals=counts(3)),
        {}, None),
}


@pytest.mark.parametrize("variant", list(ZERO))
def test_s_d10a_a_line_whose_named_case_exists_nowhere_still_fails(tmp_path, variant):
    """The third variant passes already (a guard): the ghost's line fails with no case, and nothing else needs a
    group; enabling the group for it is not judged."""
    cases, lists, rows, expected, ran, groups = ZERO[variant]
    files = _optin_file(*cases) if cases else dict(support.ALPHA)
    project = _project(tmp_path, files, support.rows_readme(ALPHA_ROW, *rows), lists)
    run = project.run(support.TICKET_ID)
    support.assert_clean(run)
    found = support.assert_outcome(run, expected, support.EXIT_FAIL)
    wanted = {**ALPHA_RAN, **ran}
    assert project.ran() == wanted, \
        f"what ran is not the expected\nexpected: {wanted}\ngot: {project.ran()}\n{run.describe()}"
    if groups is not None:
        named = support.groups_named(found)
        assert named == groups, f"the report names {sorted(named)}, expected {sorted(groups)}\n{run.describe()}"


# Only that ticket's cases ----------------------------------------------------------------------------------------

def test_s_d10a_the_other_tickets_cases_in_an_opt_in_list_are_not_run(tmp_path):
    """The other ticket's folder holds a failing function of the same name as the mapped one, and its own failing
    file; the list names both beside this ticket's case, and the map names the case by its function name."""
    twin = "test_qzv96leak_other_twin.py"
    extra = {f"{support.OTHER_FOLDER}/{twin}": support.planted_file(("fail", WIDE))}
    lists = {BREADTH: [entry(WIDE), entry(WIDE, file=twin, folder=support.OTHER_FOLDER),
                       entry(file="test_qzv96leak_other.py", folder=support.OTHER_FOLDER)]}
    project = _project(tmp_path, _optin_file(("pass", WIDE)),
                       support.rows_readme(ALPHA_ROW, ("Success 2: qzv96leak", f"`{WIDE}`")), lists, extra)
    run = project.run(support.TICKET_ID)
    expected = result("pass", [line("success-1", "pass", 3), line("success-2", "pass", 1)], totals=counts(4))
    _check(project, run, expected, support.EXIT_PASS, {**ALPHA_RAN, WIDE: 1}, {"breadth"})


STRAY = "test_qzv96leak_optin_stray"

UNNEEDED = {
    # name: (cases of OPTIN_FILE, lists, rows after ALPHA's, expected, ran, groups)
    # Revised for scope (b): the mapped case sits in lifted, so its line is report-only and lifted is not enabled;
    # breadth, which only the unmapped failing case needs, is not enabled either.
    "an-unneeded-breadth-beside-a-report-only-line": (
        [("pass", WIDE), ("fail", STRAY)], {LIFTED: [entry(WIDE)], BREADTH: [entry(STRAY)]},
        [("Success 2: qzv96leak", f"`{WIDE}`")],
        result("pass", [line("success-1", "pass", 3), line("success-2", "report-only")], totals=counts(3)),
        {}, set()),
    "no-mapped-case-needs-a-group": (
        [("fail", STRAY)], {BREADTH: [entry(STRAY)], LIFTED: [entry(file="test_qzv96leak_other.py",
                                                                      folder=support.OTHER_FOLDER)]},
        [],
        result("pass", [line("success-1", "pass", 3)], totals=counts(3)),
        {}, set()),
}


@pytest.mark.parametrize("variant", list(UNNEEDED))
def test_s_d10a_a_group_no_mapped_case_needs_is_not_enabled(tmp_path, variant):
    """The unneeded group's list holds a failing case of this ticket that the map never names: had the group been
    enabled, it would run and fail the run (PKG-1 (a)). The groups enabled are those the result's ``"optin"`` names
    (absent meaning none), as scope (b) states, never a report-only line's own wording (``report-only (lifted)``)."""
    cases, lists, rows, expected, ran, groups = UNNEEDED[variant]
    project = _project(tmp_path, _optin_file(*cases), support.rows_readme(ALPHA_ROW, *rows), lists)
    run = project.run(support.TICKET_ID)
    _check(project, run, expected, support.EXIT_PASS, {**ALPHA_RAN, **ran}, groups, optin_only=True)


# Scope (b): lifted is report-only in a formal accept (PKG-D10a-scope (b), DEC-1061 (2)) ----------------------------

GUARD_BREADTH, GUARD_LIFTED = "tests/optin-lifted-guard-breadth.txt", "tests/optin-lifted-guard.txt"

REPORT_ONLY = {
    # name: (cases of OPTIN_FILE, lists, rows after ALPHA's, expected, exit code, ran, "optin", "report_only")
    "a-case-in-lifted-passes": (
        [("pass", WIDE)], {LIFTED: [entry(WIDE)]},
        [("Success 2: qzv96leak", f"`{WIDE}`")],
        result("pass", [line("success-1", "pass", 3), line("success-2", "report-only")], totals=counts(3)),
        support.EXIT_PASS, {}, set(), ["lifted"]),
    "a-case-in-lifted-fails": (
        [("fail", WIDE)], {LIFTED: [entry(WIDE)]},
        [("Success 2: qzv96leak", f"`{support.OPTIN_FILE}::{WIDE}`")],
        result("pass", [line("success-1", "pass", 3), line("success-2", "report-only")], totals=counts(3)),
        support.EXIT_PASS, {}, set(), ["lifted"]),
    "a-whole-file-in-lifted": (
        [("fail", WIDE), ("pass", NARROW)], {LIFTED: [entry()]},
        [("Failure 1: qzv96leak", f"`{support.OPTIN_FILE}`")],
        result("pass", [line("success-1", "pass", 3), line("failure-1", "report-only")], totals=counts(3)),
        support.EXIT_PASS, {}, set(), ["lifted"]),
    "lines-in-both-groups-through-every-list-name": (
        [("pass", WIDE), ("fail", DEEP)], {GUARD_BREADTH: [entry(WIDE)], GUARD_LIFTED: [entry(DEEP)]},
        [("Success 2: qzv96leak", f"`{support.OPTIN_FILE}::{WIDE}`"), ("Success 3: qzv96leak", f"`{DEEP}`")],
        result("pass", [line("success-1", "pass", 3), line("success-2", "pass", 1), line("success-3", "report-only")],
               totals=counts(4)),
        support.EXIT_PASS, {WIDE: 1}, {"breadth"}, ["lifted"]),
}


@pytest.mark.parametrize("variant", list(REPORT_ONLY))
def test_s_d10a_a_line_whose_cases_rest_only_on_lifted_is_report_only(tmp_path, variant):
    """The lifted case never runs (passing or failing, it changes nothing); its line is report-only, neither pass
    nor fail, and does not fail the run; ``"optin"`` never holds lifted, ``"report_only"`` names it."""
    cases, lists, rows, expected, exit_code, ran, enabled, report_only = REPORT_ONLY[variant]
    project = _project(tmp_path, _optin_file(*cases), support.rows_readme(ALPHA_ROW, *rows), lists)
    run = project.run(support.TICKET_ID)
    _check_b(project, run, expected, exit_code, {**ALPHA_RAN, **ran}, enabled, report_only)


def test_s_d10a_the_text_form_prints_a_report_only_line_as_report_only_lifted(tmp_path):
    cases, lists, rows, expected, exit_code, _, _, _ = REPORT_ONLY["lines-in-both-groups-through-every-list-name"]
    project = _project(tmp_path, _optin_file(*cases), support.rows_readme(ALPHA_ROW, *rows), lists)
    run = project.run(support.TICKET_ID, json_mode=False)
    support.assert_clean(run)
    assert run.returncode == exit_code, f"exit code {run.returncode}, expected {exit_code}\n{run.describe()}"
    try:
        printed = json.loads(run.stdout)
    except ValueError:
        printed = None
    if isinstance(printed, dict):
        # The command line printed the result as JSON: the result as expected, and the report-only line's own
        # object holds the words.
        problems = support.text_problems(run.stdout, expected)
        items = [item for item in printed.get("lines") or [] if isinstance(item, dict)
                 and item.get("kpi") == "success-3"]
        shown = [support.strings_of(item) for item in items]
    else:
        # A text form of the runner's own: the measured lines as the other text cases read them, and the report-only
        # line on a printed line of its own.
        measured = {**expected, "lines": [item for item in expected["lines"] if item["outcome"] != "report-only"]}
        problems = support.text_problems(run.stdout, measured)
        pattern = re.compile(r"(?<![\w-])success-3(?![\w-])")
        shown = [row for row in run.stdout.splitlines() if pattern.search(row)]
    assert not problems, "\n".join(problems) + "\n" + run.describe()
    assert any("report-only (lifted)" in text.lower() for text in shown), \
        f"the line of success-3 does not print 'report-only (lifted)': {shown}\n{run.describe()}"


MIXED = {
    # name: (cases of OPTIN_FILE, lists, rows after ALPHA's, expected, exit code, ran, "optin")
    "lifted-and-breadth": (
        [("pass", WIDE), ("fail", DEEP)], {BREADTH: [entry(WIDE)], LIFTED: [entry(DEEP)]},
        [("Success 2: qzv96leak", f"`{WIDE}`, `{DEEP}`")],
        result("pass", [line("success-1", "pass", 3), line("success-2", "pass", 1)], totals=counts(4)),
        support.EXIT_PASS, {WIDE: 1}, {"breadth"}),
    "lifted-and-in-no-list": (
        [("pass", WIDE), ("fail", DEEP)], {LIFTED: [entry(DEEP)]},
        [("Success 2: qzv96leak", f"`{WIDE}`, `{support.OPTIN_FILE}::{DEEP}`")],
        result("pass", [line("success-1", "pass", 3), line("success-2", "pass", 1)], totals=counts(4)),
        support.EXIT_PASS, {WIDE: 1}, set()),
    "lifted-and-a-failing-breadth-case": (
        [("fail", WIDE), ("pass", DEEP)], {BREADTH: [entry(WIDE)], LIFTED: [entry(DEEP)]},
        [("Success 2: qzv96leak", f"`{WIDE}`, `{DEEP}`")],
        result("fail", [line("success-1", "pass", 3), line("success-2", "fail", 0, 1)], totals=counts(3, 1)),
        support.EXIT_FAIL, {WIDE: 1}, {"breadth"}),
}


@pytest.mark.parametrize("variant", list(MIXED))
def test_s_d10a_a_line_with_cases_in_lifted_and_elsewhere_is_measured_on_the_cases_that_run(tmp_path, variant):
    """The line's lifted case never runs (it would fail, or pass, the line otherwise); the line is measured on its
    other case alone."""
    cases, lists, rows, expected, exit_code, ran, enabled = MIXED[variant]
    project = _project(tmp_path, _optin_file(*cases), support.rows_readme(ALPHA_ROW, *rows), lists)
    run = project.run(support.TICKET_ID)
    _check_b(project, run, expected, exit_code, {**ALPHA_RAN, **ran}, enabled, None)


ZERO_B = {
    # name: (cases of OPTIN_FILE, lists, rows after ALPHA's, expected, "optin" or None when not judged)
    "a-case-named-nowhere-beside-a-report-only-line": (
        [("pass", WIDE)], {LIFTED: [entry(WIDE)]},
        [("Success 2: qzv96leak", f"`{WIDE}`"), ("Success 3: qzv96leak", f"`{support.OPTIN_FILE}::{GHOST}`")],
        result("fail", [line("success-1", "pass", 3), line("success-2", "report-only"), line("success-3", "fail")],
               totals=counts(3)),
        set()),
    "a-case-a-breadth-list-names-but-no-file-defines-beside-a-report-only-line": (
        [("pass", WIDE)], {LIFTED: [entry(WIDE)], BREADTH: [entry(GHOST)]},
        [("Success 2: qzv96leak", f"`{WIDE}`"), ("Success 3: qzv96leak", f"`{support.OPTIN_FILE}::{GHOST}`")],
        result("fail", [line("success-1", "pass", 3), line("success-2", "report-only"), line("success-3", "fail")],
               totals=counts(3)),
        None),
}


@pytest.mark.parametrize("variant", list(ZERO_B))
def test_s_d10a_a_line_that_runs_zero_for_another_reason_still_fails_beside_a_report_only_line(tmp_path, variant):
    """A report-only line beside does not turn a line whose case exists nowhere into report-only or pass."""
    cases, lists, rows, expected, enabled = ZERO_B[variant]
    project = _project(tmp_path, _optin_file(*cases), support.rows_readme(ALPHA_ROW, *rows), lists)
    run = project.run(support.TICKET_ID)
    support.assert_clean(run)
    found = support.assert_outcome(run, expected, support.EXIT_FAIL)
    assert project.ran() == ALPHA_RAN, \
        f"what ran is not the expected\nexpected: {ALPHA_RAN}\ngot: {project.ran()}\n{run.describe()}"
    assert "lifted" not in support.groups_named(found.get("optin")), f"\"optin\" holds lifted\n{run.describe()}"
    if enabled is not None:
        optin = support.groups_named(found.get("optin"))
        assert optin == enabled, f"\"optin\" names {sorted(optin)}, expected {sorted(enabled)}\n{run.describe()}"


# Round 1's F3: a run that ends in an error still names the groups it enabled -----------------------------------------

ERROR_FILE = "test_qzv96leak_second.py"


def _error_files(kind):
    """``OPTIN_FILE`` with a passing case only ``breadth`` holds (mapped, so breadth is enabled), beside a file that
    breaks the run: an import error (kind ``collection``) or pytest's internal-error exit (kind ``crash``)."""
    if kind == "collection":
        broken = support.planted_file(("pass", "test_qzv96leak_import_victim"), extra=support._IMPORT_ERROR)
    else:
        broken = support.planted_file(("crash_internal", "test_qzv96leak_crash_internal"))
    return {**_optin_file(("pass", WIDE)), ERROR_FILE: broken}


ERROR_README_ROWS = [("Success 2: qzv96leak", f"`{WIDE}`"), ("Success 3: qzv96leak", f"`{ERROR_FILE}`")]


@pytest.mark.parametrize("kind", ["collection", "crash"])
def test_s_d10a_an_error_result_still_names_the_groups_it_enabled(tmp_path, kind):
    project = _project(tmp_path, _error_files(kind), support.rows_readme(ALPHA_ROW, *ERROR_README_ROWS),
                       {BREADTH: [entry(WIDE)]})
    run = project.run(support.TICKET_ID)
    support.assert_clean(run)
    found = support.assert_outcome(run, support.error_result(kind), support.EXIT_ERROR)
    optin = support.groups_named(found.get("optin"))
    assert optin == {"breadth"}, (f"the error result's \"optin\" names {sorted(optin)}, expected ['breadth'] (the "
                                  f"group the run enabled)\n{run.describe()}")


def test_s_d10a_the_text_form_of_an_error_result_names_the_groups_it_enabled(tmp_path):
    project = _project(tmp_path, _error_files("collection"), support.rows_readme(ALPHA_ROW, *ERROR_README_ROWS),
                       {BREADTH: [entry(WIDE)]})
    run = project.run(support.TICKET_ID, json_mode=False)
    support.assert_clean(run)
    assert run.returncode == support.EXIT_ERROR, f"exit code {run.returncode}, expected 4\n{run.describe()}"
    problems = support.text_problems(run.stdout, support.error_result("collection"))
    assert not problems, "\n".join(problems) + "\n" + run.describe()
    assert re.search(r"(?<![\w-])breadth(?![\w-])", run.stdout.lower()), \
        f"the error's text does not name the opt-in group the run enabled (breadth)\n{run.describe()}"


# Premises: the planted projects do what the cases above rely on (green before the implementation, by design) -----

def _raw(project, *extra, env=None):
    """Raw pytest on the planted folder with ``extra`` arguments (``--optin=…``) or ``env``: the outcomes."""
    import subprocess
    project.runs += 1
    raw = project.base / f"raw-{project.runs}"
    (raw / "tmp").mkdir(parents=True)
    report = raw / "report.xml"
    run_env = {**project.env(raw / "tmp"), "PYTHONPATH": str(project.root / "src"), "PYTHONDONTWRITEBYTECODE": "1",
               **(env or {})}
    command = [sys.executable, "-m", "pytest", support.FOLDER, "-p", "no:cacheprovider", "--junitxml", str(report),
               "-o", "junit_family=xunit2", *extra]
    subprocess.run(command, cwd=project.root, env=run_env, capture_output=True, text=True, timeout=300,
                   stdin=subprocess.DEVNULL, start_new_session=True)
    return support.junit_outcomes(report) if report.is_file() else None


@pytest.mark.parametrize("variant", list(MEASURED))
def test_premise_s_d10a_a_default_run_leaves_the_listed_cases_out_and_the_groups_bring_them_back(tmp_path,
                                                                                                variant):
    cases, lists, rows, _, _, _, groups = MEASURED[variant]
    project = _project(tmp_path, _optin_file(*cases), support.rows_readme(ALPHA_ROW, *rows), lists)
    alpha = {key: "passed" for key in support.COMMON_RAW if key.startswith("test_qzv96leak_alpha::")}
    default = _raw(project)
    assert default is not None, "raw pytest wrote no report"
    stem = support.OPTIN_FILE[:-3]
    listed_default = {key for key in default if key.startswith(stem + "::")}
    if variant == "the-other-rows-of-a-rep-function":
        assert listed_default == {f"{stem}::{ROWS}[qzv96leak-row-a]"}, default
    else:
        assert not listed_default, f"a default run collected a listed case: {default}"
    assert {key: value for key, value in default.items() if key.startswith("test_qzv96leak_alpha::")} == alpha
    for how in ("option", "variable"):
        opted = (_raw(project, *[f"--optin={group}" for group in sorted(groups)]) if how == "option"
                 else _raw(project, env={"GOV_TESTS_OPTIN": ",".join(sorted(groups))}))
        listed = {key: value for key, value in opted.items() if key.startswith(stem + "::")}
        names = {name for _, name in cases}
        assert {key.split("::")[1].split("[")[0] for key in listed} == names, (how, opted)
        if variant == "the-other-rows-of-a-rep-function":
            assert sorted(listed.values()) == ["failed", "passed"], (how, opted)


SCOPE_B = {**{name: spec[:3] for name, spec in REPORT_ONLY.items()},
           **{name: spec[:3] for name, spec in MIXED.items()},
           **{name: spec[:3] for name, spec in ZERO_B.items()},
           **{f"unneeded:{name}": spec[:3] for name, spec in UNNEEDED.items()}}


def _lifted_names(cases, lists):
    """The planted functions a ``lifted`` list (a file name without ``breadth``) holds."""
    names = set()
    for path, entries in lists.items():
        if "breadth" in Path(path).name:
            continue
        for item in entries:
            path_part, _, name = item.removeprefix("rep:").strip().partition("::")
            if Path(path_part).name != support.OPTIN_FILE:
                continue
            names |= {case for _, case in cases if not name or case == name}
    return names


@pytest.mark.parametrize("variant", list(SCOPE_B))
def test_premise_s_d10a_a_lifted_case_is_left_out_by_default_and_would_run_were_lifted_enabled(tmp_path, variant):
    """What makes "a lifted case never runs" discriminating: each planted lifted case is out of a default run and
    in a run opting in to both groups."""
    cases, lists, rows = SCOPE_B[variant]
    project = _project(tmp_path, _optin_file(*cases), support.rows_readme(ALPHA_ROW, *rows), lists)
    lifted = _lifted_names(cases, lists)
    stem = support.OPTIN_FILE[:-3]
    ran = lambda outcomes: {key.split("::")[1].split("[")[0] for key in outcomes if key.startswith(stem + "::")}  # noqa: E731
    default = _raw(project)
    assert default is not None, "raw pytest wrote no report"
    assert not (ran(default) & lifted), (lifted, default)
    opted = _raw(project, "--optin=breadth", "--optin=lifted")
    assert lifted <= ran(opted), (lifted, opted)


def test_premise_s_d10a_the_other_tickets_twin_would_fail_and_runs_in_its_own_folder(tmp_path):
    twin = "test_qzv96leak_other_twin.py"
    extra = {f"{support.OTHER_FOLDER}/{twin}": support.planted_file(("fail", WIDE))}
    project = _project(tmp_path, _optin_file(("pass", WIDE)),
                       support.rows_readme(ALPHA_ROW, ("Success 2: qzv96leak", f"`{WIDE}`")),
                       {BREADTH: [entry(WIDE)]}, extra)
    assert (project.root / support.OTHER_FOLDER / twin).is_file()
    assert support.test_functions(project.root / support.OTHER_FOLDER / twin) == {WIDE}


def test_premise_s_d10a_groups_named_reads_a_group_but_not_a_list_file_name():
    assert support.groups_named({"optin": ["breadth"]}) == {"breadth"}
    assert support.groups_named({"optin_groups": "breadth, lifted"}) == {"breadth", "lifted"}
    assert support.groups_named({"enabled": {"lifted": True}}) == {"lifted"}
    assert support.groups_named({"lists": ["tests/optin-lifted-breadth.txt"]}) == set()
    assert support.groups_named(support.result("pass", [support.line("success-1", "pass", 3)])) == set()
