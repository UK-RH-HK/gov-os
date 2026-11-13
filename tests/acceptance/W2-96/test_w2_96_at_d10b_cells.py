"""S-D10b's cases for ``gov accept`` (DEC-1112 (3), DEC-959 item 6): the map reader reads every line a cell lists.

The ticket's line: the map reader reads every KPI line a map cell lists (a cell such as ``Success 4, failures 4,
5`` names success-4, failure-4 and failure-5), or refuses the map naming the cell; it never keeps the first line
and drops the rest silently.

- **The KPI line's own form** (``Success 4, failures 4, 5``, with words after it or alone) reads in full: each of
  its three lines is reported, passing or failing with the row's case.
- **The forms of the maps in use** (the maps review's F1: ``Success 4 [CAP-61.c], failures 4, 5``; W1-49's rows 88
  and 94, a citation and words between the names; W2-87's row 36, a parenthesis between; bare numbers after a
  singular word; a plural with ``and``; the KPI line's form as a heading) are read in full or refused naming the
  cell (``ACCEPT_MAP_UNREADABLE``, review 1's R4 code); never read as their first line alone.
  Round 2 (the review's F1) adds one variant per listed form still read as its first line: W1-49's row 89
  (``…, second half, and failure 2``), W2-92's row 128 (``Success 6 with success 4.``), the ranges ``S2-S4``,
  ``Success 2–Success 4`` and ``Success 1 to 3`` (each naming the lines between), ``or``, ``(and …)`` and ``— and``
  between two names.
- **The fail-open shape** (round 2): each listed line after the first is also mapped on a passing row of its own
  while the cell's case fails; each such line reads ``fail``, or the map is refused naming the cell, never ``pass``.
  (The other shape, the listed line mapped nowhere else, is the variants above: a dropped line is missing.)
- **A cell the reader cannot read in full** (a listed name whose number is followed by a letter, mid-list or last)
  refuses the map, naming the cell, before any test runs.
- **Every readable form of the maps in use still reads as before** (a guard, green before the change): a citation
  or a parenthesis after the names, words with commas, numbers and semicolons after a colon or a dash.

A cell the reader may name in its refusal carries no marker (as a ticket id or a declared path may be named); the
rest of every planted README does. Every case runs the suite's leak probe.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_96_support as support  # noqa: E402

line, counts, result = support.line, support.counts, support.result


# The KPI line's own form reads in full -----------------------------------------------------------------------------

KPI_LINE_FORMS = {
    "with-words-after": "Success 4, failures 4, 5: qzv96leak words",
    "alone": "Success 4, failures 4, 5",
}
KPI_LINE_NAMES = ["success-4", "failure-4", "failure-5"]


@pytest.mark.parametrize("kind", ["pass", "fail"])
@pytest.mark.parametrize("form", list(KPI_LINE_FORMS))
def test_s_d10b_the_kpi_lines_own_cell_form_reads_every_line_it_lists(tmp_path, form, kind):
    project = support.Project(tmp_path, support.cells_files(kind), support.cell_readme(KPI_LINE_FORMS[form]))
    run = project.run(support.TICKET_ID)
    support.assert_clean(run)
    exit_code = support.EXIT_PASS if kind == "pass" else support.EXIT_FAIL
    support.assert_outcome(run, support.cells_expected(KPI_LINE_NAMES, kind), exit_code)


# The forms of the maps in use: read in full, or refused naming the cell --------------------------------------------

# name: (the cell, or the heading for a heading-form map; the lines it lists; the README's form)
IN_USE_FORMS = {
    "a-citation-between-the-names": ("Success 4 [CAP-61.c], failures 4, 5", KPI_LINE_NAMES, "rows"),
    "words-between-the-names": ("Success 5 [CAP-37.g], first half, and failure 1",
                                ["success-5", "failure-1"], "rows"),
    "a-comma-and-between-the-names": ("Success 4 [CAP-37.g], failure 4, and failure 1 in a real session",
                                      ["success-4", "failure-4", "failure-1"], "rows"),
    "a-parenthesis-between-the-names": ("Success 4 (what the bundle leaves out is unchanged; W2-55's) and failure 4",
                                        ["success-4", "failure-4"], "rows"),
    "a-bare-number-after-a-singular-word": ("Success 2, 3", ["success-2", "success-3"], "rows"),
    "a-plural-word-with-and": ("Successes 2 and 3, failure 2", ["success-2", "success-3", "failure-2"], "rows"),
    "the-kpi-lines-form-as-a-heading": ("Success 4, failures 4, 5", KPI_LINE_NAMES, "heading"),
    # Round 2 (the review's F1): every listed form of the maps in use, one variant each.
    "words-between-the-names-second-half": ("Success 5 [CAP-37.g], second half, and failure 2",
                                            ["success-5", "failure-2"], "rows"),
    "with-between-the-names": ("Success 6 with success 4.", ["success-6", "success-4"], "rows"),
    "a-range-with-a-hyphen": ("S2-S4", ["success-2", "success-3", "success-4"], "rows"),
    "a-range-with-an-en-dash": ("Success 2–Success 4", ["success-2", "success-3", "success-4"], "rows"),
    "a-range-with-to": ("Success 1 to 3", ["success-1", "success-2", "success-3"], "rows"),
    "or-between-the-names": ("Success 1 or failure 2", ["success-1", "failure-2"], "rows"),
    "and-in-a-parenthesis": ("Success 1 (and failure 2)", ["success-1", "failure-2"], "rows"),
    "a-dash-then-and": ("Success 1 — and failure 2", ["success-1", "failure-2"], "rows"),
}


def _in_use_readme(cell, form):
    return support.cell_readme(cell) if form == "rows" else support.heading_cell_readme(cell)


OTHER_FILE = "test_qzv96leak_cells_other.py"
OTHER_CASE = "test_qzv96leak_cells_other_case"


def _expected(names, kind, also=()):
    """The result for ``cell_readme`` (and its fail-open form): success 1 with ALPHA's three passing cases, each line
    of ``names`` with the cell's one case of ``kind``, each line of ``also`` with ``OTHER_CASE`` (passing). Equal to
    ``support.cells_expected`` when neither names success 1 nor ``also`` is given; a line named twice adds up."""
    tally = {"success-1": [3, 0]}
    for name in also:
        tally.setdefault(name, [0, 0])[0] += 1
    for name in names:
        tally.setdefault(name, [0, 0])[0 if kind == "pass" else 1] += 1
    lines = sorted((line(name, "fail" if failed else "pass", passed, failed) for name, (passed, failed) in tally.items()),
                   key=lambda item: support.line_order(item["kpi"]))
    passed, failed = 3 + (1 if also else 0) + (kind == "pass"), int(kind == "fail")
    return result("fail" if failed else "pass", lines, totals=counts(passed, failed))


def _label(name):
    word, number = name.split("-")
    return f"{word.capitalize()} {number}: qzv96leak"


@pytest.mark.parametrize("variant", list(IN_USE_FORMS))
def test_s_d10b_a_cell_of_the_maps_in_use_reads_every_line_or_refuses_naming_the_cell(tmp_path, variant):
    cell, names, form = IN_USE_FORMS[variant]
    project = support.Project(tmp_path, support.cells_files("pass"), _in_use_readme(cell, form))
    run = project.run(support.TICKET_ID)
    support.assert_clean(run)
    envelope = run.envelope()
    if envelope["ok"] is False:
        error = support.assert_refusal(run, support.MAP_UNREADABLE)
        assert support.names_cell(support.strings_of(error), cell), \
            f"the refusal does not name the cell {cell!r}\n{run.describe()}"
        assert project.ran() == {}, f"a planted test ran: the refusal comes before any test runs\n{run.describe()}"
        support.assert_no_raw_output(run)
        return
    expected = _expected(names, "pass")
    got = support.projection(envelope["result"])
    assert got == expected, (f"the cell {cell!r} was neither read in full nor refused naming it\n"
                             f"expected (read in full): {expected}\ngot: {got}\n{run.describe()}")
    assert run.returncode == support.EXIT_PASS, f"exit code {run.returncode}, expected 0\n{run.describe()}"


# The fail-open shape: a listed line also mapped on another, passing row -------------------------------------------

FAIL_OPEN_FORMS = {"the-kpi-lines-form": ("Success 4, failures 4, 5", KPI_LINE_NAMES),
                   **{name: (cell, names) for name, (cell, names, form) in IN_USE_FORMS.items() if form == "rows"}}


@pytest.mark.parametrize("variant", list(FAIL_OPEN_FORMS))
def test_s_d10b_a_listed_line_also_mapped_on_a_passing_row_never_reads_pass_when_this_rows_case_fails(tmp_path,
                                                                                                       variant):
    """Each line the cell lists after its first is also mapped on a row of its own over a passing case, and the
    cell's own case fails: a reader that kept the first line alone would report those lines ``pass``. Each must
    read ``fail`` (the passing case and the failing one), or the map is refused naming the cell."""
    cell, names = FAIL_OPEN_FORMS[variant]
    also = [name for name in names[1:] if name != "success-1"]
    files = {**support.cells_files("fail"), OTHER_FILE: support.planted_file(("pass", OTHER_CASE))}
    readme = support.rows_readme(("Success 1: qzv96leak", "`test_qzv96leak_alpha.py`"),
                                 *[(_label(name), f"`{OTHER_FILE}`") for name in also],
                                 (cell, f"`{support.CELLS_FILE}`"))
    project = support.Project(tmp_path, files, readme)
    run = project.run(support.TICKET_ID)
    support.assert_clean(run)
    envelope = run.envelope()
    if envelope["ok"] is False:
        error = support.assert_refusal(run, support.MAP_UNREADABLE)
        assert support.names_cell(support.strings_of(error), cell), \
            f"the refusal does not name the cell {cell!r}\n{run.describe()}"
        assert project.ran() == {}, f"a planted test ran: the refusal comes before any test runs\n{run.describe()}"
        support.assert_no_raw_output(run)
        return
    expected = _expected(names, "fail", also)
    got = support.projection(envelope["result"])
    passing = [item["kpi"] for item in got.get("lines", []) if isinstance(item, dict)
               and item.get("kpi") in also and item.get("outcome") == "pass"]
    assert got == expected, (f"the cell {cell!r} was neither read in full nor refused naming it"
                             f"{f' (fails open: {passing} read pass)' if passing else ''}\n"
                             f"expected (read in full): {expected}\ngot: {got}\n{run.describe()}")
    assert run.returncode == support.EXIT_FAIL, f"exit code {run.returncode}, expected 3\n{run.describe()}"


# A cell the reader cannot read in full refuses the map, naming it --------------------------------------------------

UNREADABLE_CELLS = {
    "a-number-with-a-letter-mid-list": "Success 2, F 3a / F4",
    "a-number-with-a-letter-last": "Success 4, failures 4, 5b",
}


@pytest.mark.parametrize("variant", list(UNREADABLE_CELLS))
def test_s_d10b_a_cell_the_reader_cannot_read_in_full_refuses_the_map_naming_it(tmp_path, variant):
    cell = UNREADABLE_CELLS[variant]
    project = support.Project(tmp_path, support.cells_files("fail"), support.cell_readme(cell))
    run = project.run(support.TICKET_ID)
    support.assert_clean(run)
    error = support.assert_refusal(run, support.MAP_UNREADABLE)
    assert support.names_cell(support.strings_of(error), cell), \
        f"the refusal does not name the cell {cell!r}\n{run.describe()}"
    assert project.records() == [], f"a planted test ran: the refusal comes before any test runs\n{run.describe()}"
    support.assert_no_raw_output(run)


def test_s_d10b_the_text_form_of_the_refusal_gives_its_code_and_the_cell(tmp_path):
    cell = UNREADABLE_CELLS["a-number-with-a-letter-mid-list"]
    project = support.Project(tmp_path, support.cells_files("fail"), support.cell_readme(cell))
    run = project.run(support.TICKET_ID, json_mode=False)
    support.assert_clean(run)
    assert run.returncode == support.EXIT_REFUSED, f"exit code {run.returncode}, expected 1\n{run.describe()}"
    assert support.MAP_UNREADABLE in run.stderr, f"the refusal names its code on stderr\n{run.describe()}"
    assert support.names_cell(run.stderr, cell), f"the refusal does not name the cell {cell!r}\n{run.describe()}"
    assert project.records() == [], f"a planted test ran: the refusal comes before any test runs\n{run.describe()}"
    support.assert_no_raw_output(run)


# Every readable form of the maps in use still reads as before (a guard) --------------------------------------------

FORMS_FILE = "test_qzv96leak_forms.py"
# (the KPI cell, the function its row maps, the lines the cell names)
READABLE_ROWS = [
    ("Success 1 [CAP-37.g]: qzv96leak words, or more words; a test proves whether it can",
     "test_qzv96leak_forms_a", ["success-1"]),
    ("Success 2 / Success 5 (qzv96leak review 1, R6)", "test_qzv96leak_forms_b", ["success-2", "success-5"]),
    ("Failure 3: qzv96leak injects more than the cap, or leaves out the prompt path or the section",
     "test_qzv96leak_forms_c", ["failure-3"]),
    ("S3: qzv96leak runs that ticket's tests (its declared path) with the tree's own src/ and reports, per KPI line",
     "test_qzv96leak_forms_d", ["success-3"]),
    ("Success 4 / Failure 1 (qzv96leak run 2, R10)", "test_qzv96leak_forms_e", ["success-4", "failure-1"]),
    ("F2 — qzv96leak 3 runs, 4 races", "test_qzv96leak_forms_f", ["failure-2"]),
    ("Success 6 [CAP-37.g]: the qzv96leak injection is role-specific (DEC-263)", "test_qzv96leak_forms_g",
     ["success-6"]),
]


def test_s_d10b_every_readable_form_of_the_maps_in_use_still_reads_as_before(tmp_path):
    """Passes already (a guard): the reader that reads every listed line still reads these cells as the reader
    before it did, ending each cell's names at its citation, parenthesis, colon or dash."""
    files = {FORMS_FILE: support.planted_file(*[("pass", name) for _, name, _ in READABLE_ROWS])}
    readme = support.rows_readme(*[(cell, f"`{name}`") for cell, name, _ in READABLE_ROWS])
    project = support.Project(tmp_path, files, readme)
    run = project.run(support.TICKET_ID)
    support.assert_clean(run)
    tally = {}
    for _, _, names in READABLE_ROWS:
        for name in names:
            tally[name] = tally.get(name, 0) + 1
    lines = sorted((line(name, "pass", times) for name, times in tally.items()),
                   key=lambda item: support.line_order(item["kpi"]))
    support.assert_outcome(run, result("pass", lines, totals=counts(len(READABLE_ROWS))), support.EXIT_PASS)


# Premises (green before the implementation, by design) ------------------------------------------------------------

def test_premise_s_d10b_the_design_notes_reader_keeps_only_the_first_line_of_the_multi_line_cells():
    """What makes the cells above discriminating: the reader of the design note's form, as this suite models it,
    stops at the first name of each multi-line cell, and reads each guard cell as its row says."""
    for cell in KPI_LINE_FORMS.values():
        assert support.line_names(cell) == ["success-4"], cell
    for cell, names, _ in IN_USE_FORMS.values():
        assert len(support.line_names(cell)) < len(names), cell
    for cell, _, names in READABLE_ROWS:
        assert support.line_names(cell) == names, cell
    for cell in UNREADABLE_CELLS.values():
        assert support.MARKER not in cell.lower()
    for cell, _, _ in IN_USE_FORMS.values():
        assert support.MARKER not in cell.lower()


def test_premise_s_d10b_the_planted_maps_hold_their_cells():
    from_rows = support.markdown_tables(support.cell_readme("Success 4, failures 4, 5"))
    assert [row[0] for row in from_rows[0][1]] == ["Success 1: qzv96leak", "Success 4, failures 4, 5"]
    heading = support.heading_cell_readme("Success 4, failures 4, 5")
    assert "### Success 4, failures 4, 5\n" in heading
