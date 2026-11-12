"""W2-96 (DAEO-ouet), D-10 round 2 (DEC-1112 (3), PKG-D10a-scope (b), DEC-1061 (2)): builder tests.

F1: the map reader reads every further line a cell names, or refuses the cell; never the first kept and the rest
dropped. Scope (b): a formal ``gov accept`` enables only ``breadth``; a line resting only on cases the ``lifted``
list leaves out is ``report-only``, fails nothing by itself, and ``lifted`` is named under ``report_only``, never
under ``optin``. F3: once the groups are set, every result names them, a crash included.
"""

from __future__ import annotations

import json

import pytest

from gov.accept import runner
from gov.cli.main import main
from test_w2_96_d10 import MARK, _accept, _plant, project  # noqa: F401  (project: the fixture)

# --- F1: every further line name is read or the cell refused ---------------------------------------------------------


@pytest.mark.parametrize("cell, names", [
    ("Success 5 [CAP-37.g], first half, and failure 1: the PreCompact hook never blocks", ["success-5", "failure-1"]),
    ("Success 5 [CAP-37.g], second half, and failure 2: the injection warns", ["success-5", "failure-2"]),
    ("Success 6 with success 4.", ["success-6", "success-4"]),
    ("**Success 6 with success 4.** Nothing else in the bundle changes", ["success-6", "success-4"]),
    ("S2-S4", ["success-2", "success-3", "success-4"]),
    ("Success 2–Success 4", ["success-2", "success-3", "success-4"]),
    ("Success 1 to 3", ["success-1", "success-2", "success-3"]),
    ("Success 1 or failure 2", ["success-1", "failure-2"]),
    ("Success 1 (and failure 2)", ["success-1", "failure-2"]),
    ("Success 1 — and failure 2", ["success-1", "failure-2"]),
    ("Success 4 [CAP-61.c], failures 4, 5", ["success-4", "failure-4", "failure-5"]),
    ("S6 (S1)", ["success-6", "success-1"]),
    ("F1: a merge keeps git's own merge (KPI 1, DEC-918 item 1)", ["failure-1", "success-1"]),
    ("S1 first; failures 2, 3.", ["success-1", "failure-2", "failure-3"]),
    # a line named again, in prose or a note, changes nothing
    ("KPI 1 (S1; CAP-15, CAP-15.d): the ceiling", ["success-1"]),
    ("Success 1 (DEC-242: no KPI line of its own; refusals in the words of success 1)", ["success-1"]),
    ("F1: a planted GIT_DIR; and (review F1) the gate", ["failure-1"]),
    # no line name: a count, a possessive ticket, a test or file name
    ("S6: W2-61's 20-question measure is run again", ["success-6"]),
    ("Success 1 to 3 cases", ["success-1"]),
    ("S1 and `test_f2.py::test_s3`", ["success-1"]),
    ("Success 3 — 2 cases", ["success-3"]),
])
def test_w2_96_d10r2_every_further_line_is_read(cell, names):
    assert runner.line_names(cell) == names


@pytest.mark.parametrize("cell", [
    "S9: one relation check (D-6 part 2 item F2; DEC-1109 (2))",
    "S2 a hidden worktree keeps its index; F1's fixture keeps them",
    "S4: the ratchet's reading of both lists [I4 F14]",
    "S4 [F14]",
    "Success 6 with success 4. S1's record route answers as before",
    "S1-F3",
    "Success 2–Failure 4",
    "S1 then S2",
    "S1 first; and then failures 2, 3",
    "Success 1 (see S2-1)",
])
def test_w2_96_d10r2_a_further_line_it_cannot_read_refuses_the_cell(cell):
    with pytest.raises(runner.Unlisted):
        runner.line_names(cell)


def test_w2_96_d10r2_a_row_naming_a_line_after_words_maps_its_items_to_both():
    readme = ("| KPI | Test |\n|---|---|\n| Success 5 [CAP-37.g], first half, and failure 1: the hook | `test_a.py` |\n"
              "| Success 6 with success 4. | `test_b.py::test_g` |\n")
    assert runner.parse_map(readme) == {"success-5": ["test_a.py"], "failure-1": ["test_a.py"],
                                        "success-6": ["test_b.py::test_g"], "success-4": ["test_b.py::test_g"]}


def test_w2_96_d10r2_the_refusal_names_the_row():
    readme = "| KPI | Test |\n|---|---|\n| S1 | `a` |\n| S2 then F1's fixture | `b` |\n"
    with pytest.raises(runner.Unlisted) as raised:
        runner.parse_map(readme)
    assert raised.value.args == (4, "S2 then F1's fixture")


# --- scope (b): breadth only; a line resting only on lifted cases is report-only -------------------------------------

TESTS = f"""
def test_default():
    assert True

def test_wide():
    assert True

def test_off():
    assert "{MARK}" == "x", "{MARK}"

def test_off_too():
    assert False
"""
BREADTH = "tests/acceptance/T1/test_a.py::test_wide  # cut\n"
LIFTED = "tests/acceptance/T1/test_a.py::test_off  # off\ntests/acceptance/T1/test_a.py::test_off_too\n"
LISTS = {"optin-lifted-breadth.txt": BREADTH, "optin-lifted.txt": LIFTED}


def _lines(result: dict) -> list[tuple]:
    return [(line["kpi"], line["outcome"], line["passed"], line["failed"]) for line in result["lines"]]


def test_w2_96_d10r2_lifted_is_never_enabled_and_its_only_line_is_report_only(project, capsys):
    root, temp = project
    readme = ("| KPI | Test |\n|---|---|\n| S1 | `test_a.py::test_off` |\n| S2 | `test_a.py::test_wide` |\n"
              "| S3 | `test_a.py::test_off_too`, `test_a.py::test_default` |\n")
    _plant(root, readme, {"test_a.py": TESTS}, LISTS)
    code, envelope, text = _accept(root, capsys)
    result = envelope["result"]
    assert code == 0, envelope
    assert result["outcome"] == "pass"
    assert result["optin"] == ["breadth"] and result["report_only"] == ["lifted"]
    assert _lines(result) == [("success-1", "report-only", 0, 0), ("success-2", "pass", 1, 0),
                              ("success-3", "pass", 1, 0)]  # S3: measured on the case that ran
    assert result["lines"][0]["note"] == "report-only (lifted)"
    assert result["totals"] == {"passed": 2, "failed": 0, "skipped": 0}  # the lifted cases never ran
    assert MARK not in text and "test_off" not in text
    assert list(temp.iterdir()) == []


def test_w2_96_d10r2_the_text_form_says_report_only_lifted(project, capsys):
    root, _ = project
    readme = "| KPI | Test |\n|---|---|\n| S1 | `test_a.py::test_off` |\n| S2 | `test_a.py::test_wide` |\n"
    _plant(root, readme, {"test_a.py": TESTS}, LISTS)
    code = main(["accept", "DAEO-t001", "--root", str(root)])
    out, err = capsys.readouterr()
    assert code == 0
    assert "report-only (lifted)" in out and '"report_only"' in out and MARK not in out + err


def test_w2_96_d10r2_a_line_running_zero_for_another_reason_still_fails(project, capsys):
    root, _ = project
    readme = ("| KPI | Test |\n|---|---|\n| S1 | `test_a.py::test_off`, `test_a.py::test_gone` |\n"
              "| S2 | `test_a.py::test_off`, `nothing_here` |\n| S3 | `test_a.py::test_gone` |\n"
              "| S4 | `test_a.py::test_wide` |\n")
    _plant(root, readme, {"test_a.py": TESTS}, LISTS)
    code, envelope, _ = _accept(root, capsys)
    assert code == 3
    assert _lines(envelope["result"]) == [("success-1", "fail", 0, 0), ("success-2", "fail", 0, 0),
                                          ("success-3", "fail", 0, 0), ("success-4", "pass", 1, 0)]


def test_w2_96_d10r2_a_line_with_a_lifted_case_and_a_named_test_that_is_missing_fails(project, capsys):
    root, _ = project
    readme = "| KPI | Test |\n|---|---|\n| S1 | `test_a.py::test_off`, `test_a.py::test_default`, `test_a.py::test_gone` |\n"
    _plant(root, readme, {"test_a.py": TESTS}, LISTS)
    code, envelope, _ = _accept(root, capsys)
    assert code == 3 and _lines(envelope["result"]) == [("success-1", "fail", 1, 0)]


def test_w2_96_d10r2_a_run_whose_every_line_is_report_only_fails(project, capsys):
    root, _ = project
    readme = "| KPI | Test |\n|---|---|\n| S1 | `test_a.py::test_off` |\n| F1 | `test_a.py::test_off_too` |\n"
    _plant(root, readme, {"test_a.py": TESTS}, {"optin-lifted.txt": LIFTED})
    code, envelope, _ = _accept(root, capsys)
    result = envelope["result"]
    assert code == 3 and result["outcome"] == "fail"
    assert "optin" not in result and result["report_only"] == ["lifted"]
    assert [line["outcome"] for line in result["lines"]] == ["report-only", "report-only"]


def test_w2_96_d10r2_a_failed_case_still_fails_the_run_beside_a_report_only_line(project, capsys):
    root, _ = project
    readme = "| KPI | Test |\n|---|---|\n| S1 | `test_a.py::test_off` |\n| S2 | `test_a.py::test_wide` |\n"
    tests = TESTS.replace("def test_default():\n    assert True", "def test_default():\n    assert False")
    _plant(root, readme, {"test_a.py": tests}, LISTS)
    code, envelope, _ = _accept(root, capsys)
    assert code == 3 and envelope["result"]["outcome"] == "fail"
    assert envelope["result"]["unmapped"]["failed"] == 1


def test_w2_96_d10r2_the_run_records_the_cases_left_out(project):
    root, temp = project
    folder = _plant(root, "| KPI | Test |\n|---|---|\n| S1 | `test_a.py` |\n", {"test_a.py": TESTS}, LISTS)
    left: list = []
    kind, cases = runner._run(root.resolve(), folder.resolve(), 60, ["breadth"], left)
    assert kind is None
    assert sorted(case.name for case in cases) == ["test_default", "test_wide"]
    assert sorted(left) == [runner.Case("tests/acceptance/T1/test_a.py", "test_off", "left out"),
                            runner.Case("tests/acceptance/T1/test_a.py", "test_off_too", "left out")]
    assert list(temp.iterdir()) == []


def test_w2_96_d10r2_a_lifted_case_named_in_a_parametrised_row_is_held(project, capsys):
    root, _ = project
    tests = "import pytest\n\n@pytest.mark.parametrize('x', [1, 2])\ndef test_p(x):\n    assert x == 1\n" + TESTS
    readme = "| KPI | Test |\n|---|---|\n| S1 | `test_a.py::test_p[2]` |\n| S2 | `test_a.py::test_p[1]` |\n"
    _plant(root, readme, {"test_a.py": tests},
           {"optin-lifted.txt": LIFTED + "tests/acceptance/T1/test_a.py::test_p[2]\n"})
    code, envelope, _ = _accept(root, capsys)
    assert code == 0, envelope
    assert _lines(envelope["result"]) == [("success-1", "report-only", 0, 0), ("success-2", "pass", 1, 0)]


# --- F3: every result names the groups once they are set ----------------------------------------------------------------

def test_w2_96_d10r2_a_crash_names_the_groups(project, capsys, monkeypatch):
    root, _ = project
    readme = "| KPI | Test |\n|---|---|\n| S1 | `test_a.py::test_off` |\n| S2 | `test_a.py::test_wide` |\n"
    _plant(root, readme, {"test_a.py": TESTS}, LISTS)

    def broken(*args, **kwargs):
        raise RuntimeError(MARK)

    monkeypatch.setattr(runner, "_run", broken)
    code, envelope, text = _accept(root, capsys)
    result = envelope["result"]
    assert code == 4 and result["error_kind"] == "crash"
    assert result["optin"] == ["breadth"] and result["report_only"] == ["lifted"]
    assert MARK not in text
    code = main(["accept", "DAEO-t001", "--root", str(root)])
    out, _ = capsys.readouterr()
    assert code == 4 and json.loads(out)["optin"] == ["breadth"]


def test_w2_96_d10r2_a_crash_in_the_report_names_the_groups(project, capsys, monkeypatch):
    root, _ = project
    readme = "| KPI | Test |\n|---|---|\n| S2 | `test_a.py::test_wide` |\n"
    _plant(root, readme, {"test_a.py": TESTS}, {"optin-lifted-breadth.txt": BREADTH})
    monkeypatch.setattr(runner, "_report", lambda *args, **kwargs: 1 / 0)
    code, envelope, _ = _accept(root, capsys)
    assert code == 4 and envelope["result"]["optin"] == ["breadth"] and "report_only" not in envelope["result"]


def test_w2_96_d10r2_a_crash_before_the_groups_are_set_names_none(project, capsys, monkeypatch):
    root, _ = project
    _plant(root, "| KPI | Test |\n|---|---|\n| S2 | `test_a.py::test_wide` |\n", {"test_a.py": TESTS}, LISTS)
    monkeypatch.setattr(runner, "needed_optins", lambda *args: 1 / 0)
    code, envelope, _ = _accept(root, capsys)
    assert code == 4 and "optin" not in envelope["result"] and "report_only" not in envelope["result"]
