"""W2-96 (DAEO-ouet), D-10's red-fix list (DEC-1112 (3)): builder tests of S-D10a and S-D10b.

S-D10a: ``gov accept`` runs the opt-in suites (``tests/optin-lifted*.txt``) its own map's cases need, for that
ticket's folder only, and names them; a line whose mapped cases still run zero stays a fail. S-D10b: the map reader
reads every KPI line a cell lists, or refuses the map naming the cell. Each run plants a tiny project in a temporary
folder, with a stand-in ``tests/conftest.py`` that leaves listed cases out as the repository's own does.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from gov.accept import runner
from gov.cli.errors import GovError
from gov.cli.main import main

MARK = "PLANTED-LEAK-d10b"

STAND_IN_CONFTEST = '''
import os
from pathlib import Path

HERE = Path(__file__).resolve().parent


def _hit(nodeid, entry):
    return (nodeid == entry or nodeid.startswith(entry if entry.endswith("/") else entry + "::")
            or nodeid.startswith(entry + "["))


def pytest_collection_modifyitems(config, items):
    opted = {name.strip() for name in os.environ.get("GOV_TESTS_OPTIN", "").split(",") if name.strip()}
    entries = []
    for listing in HERE.glob("optin-lifted*.txt"):
        if ("breadth" if "breadth" in listing.name else "lifted") in opted:
            continue
        for raw in listing.read_text().splitlines():
            line = raw.split("#", 1)[0].strip()
            entries.append(line[4:].strip() if line.startswith("rep:") else line)
    left = [item for item in items if any(entry and _hit(item.nodeid, entry) for entry in entries)]
    if left:
        items[:] = [item for item in items if item not in left]
        config.hook.pytest_deselected(items=left)
'''

TESTS = f"""
def test_default():
    assert True

def test_wide():
    assert True

def test_wide_fails():
    assert "{MARK}" == "x", "{MARK}"
"""


@pytest.fixture
def project(tmp_path, monkeypatch):
    root = tmp_path / "proj"
    (root / "tests").mkdir(parents=True)
    temp = tmp_path / "tmpdir"
    temp.mkdir()
    monkeypatch.setattr(tempfile, "tempdir", str(temp))
    monkeypatch.setenv("TMPDIR", str(temp))
    monkeypatch.delenv(runner.OPTIN_ENV, raising=False)
    return root, temp


def _plant(root: Path, readme: str, tests: dict[str, str], lists: dict[str, str], *, conftest: bool = True) -> Path:
    (root / ".tickets").mkdir(exist_ok=True)
    (root / ".tickets" / "DAEO-t001.md").write_text(
        "---\nid: DAEO-t001\nwbs_id: W9-01\nstatus: in_progress\nacceptance_tests:\n  path: tests/acceptance/T1/\n"
        "---\n# t\n", encoding="utf-8")
    folder = root / "tests" / "acceptance" / "T1"
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "README.md").write_text(readme, encoding="utf-8")
    for name, text in tests.items():
        (folder / name).write_text(text, encoding="utf-8")
    for name, text in lists.items():
        (root / "tests" / name).write_text(text, encoding="utf-8")
    if conftest:
        (root / "tests" / "conftest.py").write_text(STAND_IN_CONFTEST, encoding="utf-8")
    return folder


def _accept(root: Path, capsys) -> tuple[int, dict, str]:
    code = main(["accept", "DAEO-t001", "--json", "--root", str(root)])
    out, err = capsys.readouterr()
    return code, json.loads(out), out + err


WIDE = "tests/acceptance/T1/test_a.py::test_wide  # cap\n"


# --- S-D10a: which suites the map's cases need ------------------------------------------------------------------------

@pytest.mark.parametrize("lists, items, suites", [
    ({"optin-lifted-breadth.txt": WIDE}, ["test_a.py::test_wide"], ["breadth"]),
    ({"optin-lifted-breadth.txt": WIDE}, ["test_a.py::test_default"], []),
    ({"optin-lifted-breadth.txt": WIDE}, ["test_a.py"], ["breadth"]),
    ({"optin-lifted-breadth.txt": WIDE}, ["wide"], ["breadth"]),
    ({"optin-lifted-breadth.txt": WIDE}, ["test_b.py"], []),
    ({"optin-lifted-breadth.txt": WIDE}, ["sub/test_a.py::test_wide"], []),
    ({"optin-lifted-guard-breadth.txt": WIDE}, ["test_a.py::test_wide"], ["breadth"]),
    ({"optin-lifted-guard.txt": WIDE}, ["test_a.py::test_wide"], ["lifted"]),
    ({"optin-lifted.txt": "tests/acceptance/T1/  # off\n"}, ["test_a.py::test_default"], ["lifted"]),
    ({"optin-lifted.txt": "tests/acceptance/  # off\n"}, ["test_a.py::test_default"], ["lifted"]),
    ({"optin-lifted.txt": "tests/acceptance/T1/test_a.py  # off\n"}, ["test_a.py::test_default"], ["lifted"]),
    ({"optin-lifted.txt": "tests/acceptance/T1/sub/\n"}, ["test_a.py::test_default"], []),
    ({"optin-lifted.txt": "tests/acceptance/T1/sub/\n"}, ["test_s.py::test_x"], ["lifted"]),
    ({"optin-lifted-breadth.txt": "tests/acceptance/T2/test_a.py::test_wide\n"}, ["test_a.py::test_wide"], []),
    ({"optin-lifted-breadth.txt": "tests/acceptance/T10/\n"}, ["test_a.py::test_wide"], []),
    ({"optin-lifted-breadth.txt": "rep: tests/acceptance/T1/test_a.py::test_p  # one row\n"}, ["test_a.py::test_p"],
     ["breadth"]),
    ({"optin-lifted-breadth.txt": "tests/acceptance/T1/test_a.py::test_p[b]\n"}, ["test_a.py::test_p[a]"], []),
    ({"optin-lifted-breadth.txt": "tests/acceptance/T1/test_a.py::test_p[b]\n"}, ["test_a.py::test_p"], ["breadth"]),
    ({"optin-lifted-breadth.txt": "tests/acceptance/T1/test_a.py::TestK\n"}, ["test_a.py::test_m"], ["breadth"]),
    ({"optin-lifted-breadth.txt": "tests/acceptance/T1/test_a.py::TestK::test_m\n"}, ["test_a.py::test_m"],
     ["breadth"]),
    ({"optin-lifted-breadth.txt": WIDE, "optin-lifted.txt": "tests/acceptance/T1/test_a.py::test_default\n"},
     ["test_a.py::test_wide", "test_a.py::test_default"], ["breadth", "lifted"]),
    ({"optin-lifted-breadth.txt": WIDE}, ["sub/"], []),
    ({}, ["test_a.py::test_wide"], []),
])
def test_w2_96_d10a_the_suites_a_map_needs(tmp_path, lists, items, suites):
    root = tmp_path / "proj"
    folder = root / "tests" / "acceptance" / "T1"
    (folder / "sub").mkdir(parents=True)
    (folder / "sub" / "test_s.py").write_text("def test_x():\n    pass\n")
    for name, text in lists.items():
        (root / "tests" / name).write_text(text)
    assert runner.needed_optins(root.resolve(), folder.resolve(), {"success-1": items}) == suites


def test_w2_96_d10a_comments_and_blank_lines_are_not_entries(tmp_path):
    (tmp_path / "optin-lifted-breadth.txt").write_text("# head\n\nrep: a.py::b  # why\nc/  # x\n")
    (tmp_path / "notes.txt").write_text("d.py\n")
    assert runner.optin_entries(tmp_path) == [("breadth", "a.py::b"), ("breadth", "c/")]


def test_w2_96_d10a_a_line_left_out_by_a_list_is_measured_and_the_suite_named(project, capsys):
    root, temp = project
    readme = "| KPI | Test |\n|---|---|\n| S1 | `test_a.py::test_wide` |\n| S2 | `test_a.py::test_default` |\n"
    lists = {"optin-lifted-breadth.txt": WIDE + "tests/acceptance/T1/test_a.py::test_wide_fails\n"}
    _plant(root, readme, {"test_a.py": TESTS.replace("assert \"", "assert not \"")}, lists)
    code, envelope, text = _accept(root, capsys)
    assert code == 0, envelope
    result = envelope["result"]
    assert result["optin"] == ["breadth"]
    assert [(line["kpi"], line["outcome"], line["passed"]) for line in result["lines"]] == [
        ("success-1", "pass", 1), ("success-2", "pass", 1)]
    assert result["unmapped"]["passed"] == 1  # the suite's other case of the ticket's folder runs, counted only
    assert MARK not in text and "test_wide" not in text
    assert list(temp.iterdir()) == []


def test_w2_96_d10a_without_the_suite_the_line_fails_with_no_failed_case(project, capsys):
    """The premise: with no opt-in reading (a list the reader does not see), the same line runs zero and fails."""
    root, _ = project
    readme = "| KPI | Test |\n|---|---|\n| S1 | `test_a.py::test_wide` |\n"
    folder = _plant(root, readme, {"test_a.py": TESTS}, {"optin-lifted-breadth.txt": WIDE})
    assert runner._run(root.resolve(), folder.resolve(), 60)[1] == [
        runner.Case("tests/acceptance/T1/test_a.py", "test_default", "passed"),
        runner.Case("tests/acceptance/T1/test_a.py", "test_wide_fails", "failed")]
    code, envelope, _ = _accept(root, capsys)
    assert code == 3 and envelope["result"]["optin"] == ["breadth"]
    assert envelope["result"]["lines"] == [{"kpi": "success-1", "outcome": "pass", "passed": 1, "failed": 0,
                                            "skipped": 0}]
    assert envelope["result"]["totals"]["failed"] == 1  # the suite's failed case of the folder fails the run (PKG-1)


def test_w2_96_d10a_a_line_still_running_zero_stays_a_fail(project, capsys):
    root, _ = project
    readme = ("| KPI | Test |\n|---|---|\n| S1 | `test_a.py::test_wide` |\n| S2 | `nothing_here` |\n"
              "| S3 | `test_a.py::test_skipped` |\n")
    tests = TESTS.replace("def test_wide_fails", "def _off") + "\nimport pytest\n\ndef test_skipped():\n    pytest.skip()\n"
    _plant(root, readme, {"test_a.py": tests}, {"optin-lifted-breadth.txt": WIDE})
    code, envelope, _ = _accept(root, capsys)
    assert code == 3
    assert envelope["result"]["optin"] == ["breadth"]
    assert [(line["kpi"], line["outcome"]) for line in envelope["result"]["lines"]] == [
        ("success-1", "pass"), ("success-2", "fail"), ("success-3", "fail")]


def test_w2_96_d10a_the_callers_opt_in_never_reaches_the_run(project, capsys, monkeypatch):
    root, _ = project
    readme = "| KPI | Test |\n|---|---|\n| S1 | `test_a.py::test_default` |\n"
    _plant(root, readme, {"test_a.py": TESTS},
           {"optin-lifted-breadth.txt": WIDE + "tests/acceptance/T1/test_a.py::test_wide_fails\n"})
    monkeypatch.setenv(runner.OPTIN_ENV, "breadth,lifted")
    code, envelope, _ = _accept(root, capsys)
    assert code == 0, envelope
    assert "optin" not in envelope["result"]  # none needed, none enabled: the result is as before
    assert envelope["result"]["totals"] == {"passed": 1, "failed": 0, "skipped": 0}


def test_w2_96_d10a_the_suite_is_set_by_the_variable_conftest_reads(project, monkeypatch):
    root, _ = project
    readme = "| KPI | Test |\n|---|---|\n| S1 | `test_a.py::test_wide` |\n"
    folder = _plant(root, readme, {"test_a.py": "import os\n\ndef test_wide():\n    assert os.environ['GOV_TESTS_OPTIN']"
                                                " == 'breadth'\n"}, {"optin-lifted-breadth.txt": WIDE})
    kind, cases = runner._run(root.resolve(), folder.resolve(), 60, ["breadth"])
    assert kind is None and cases == [runner.Case("tests/acceptance/T1/test_a.py", "test_wide", "passed")]


def test_w2_96_d10a_an_errored_run_names_the_suites_it_enabled(project, capsys):
    root, _ = project
    readme = "| KPI | Test |\n|---|---|\n| S1 | `test_a.py::test_wide` |\n"
    _plant(root, readme, {"test_a.py": f"import no_such_module_d10b  # {MARK}\n"}, {"optin-lifted-breadth.txt": WIDE})
    code, envelope, text = _accept(root, capsys)
    assert code == 4
    assert envelope["result"]["error_kind"] == "collection" and envelope["result"]["optin"] == ["breadth"]
    assert MARK not in text


# --- S-D10b: every line a cell lists, or a refusal naming the cell ---------------------------------------------------

@pytest.mark.parametrize("cell, names", [
    ("Success 4 [CAP-61.c], failures 4, 5", ["success-4", "failure-4", "failure-5"]),
    ("Success 4, failure 4, failure 5 [CAP-61.c]", ["success-4", "failure-4", "failure-5"]),
    ("**Success 4** (the doctor; W2-55's) and failure 4", ["success-4", "failure-4"]),
    ("K4 (the second guard), K1 (the control)", ["success-4", "success-1"]),
    ("Successes 1 & 2 + F3", ["success-1", "success-2", "failure-3"]),
    ("Success 3–7. A minimal subagent", ["success-3", "success-4", "success-5", "success-6", "success-7"]),
    ("S3-5", ["success-3", "success-4", "success-5"]),
    ("F1..2", ["failure-1", "failure-2"]),
    ("S1, 2 and F3", ["success-1", "success-2", "failure-3"]),
    ("S5, DEC-447", ["success-5"]),
    ("Success 2, second half. Every pin", ["success-2"]),
    ("S7 (DEC-439)", ["success-7"]),
    ("KPI 2 and the failure line, first half", ["success-2"]),
    ("Success 3 — 2 cases", ["success-3"]),
    ("Success 1. Implementer sessions deny Edit on 3 paths", ["success-1"]),
    ("Notes about S1", []),
])
def test_w2_96_d10b_every_listed_line_is_read(cell, names):
    assert runner.line_names(cell) == names


@pytest.mark.parametrize("cell", [
    "S1, 2 cases", "Success 2 and failure line", "Success 4 and failures 4a", "S3-2", "S1-90", "S1 / F2, S3c",
    "Success 4 [CAP-61.c], failure 4b", "S1 (note); failures four", "S1 and 5x",
])
def test_w2_96_d10b_a_cell_listing_a_line_it_cannot_read_is_refused(cell):
    with pytest.raises(runner.Unlisted):
        runner.line_names(cell)


def test_w2_96_d10b_a_row_maps_its_items_to_every_listed_line():
    readme = "| KPI | Test |\n|---|---|\n| Success 4 [CAP-61.c], failures 4, 5 | `test_a.py::test_x`, `b` |\n"
    assert runner.parse_map(readme) == {name: ["test_a.py::test_x", "b"]
                                        for name in ("success-4", "failure-4", "failure-5")}


def test_w2_96_d10b_a_heading_maps_its_table_to_every_listed_line():
    readme = "## Success 2 [CAP-1.a], failures 1, 3\n| Test |\n|---|\n| `test_a.py` |\n"
    assert runner.parse_map(readme) == {"success-2": ["test_a.py"], "failure-1": ["test_a.py"],
                                        "failure-3": ["test_a.py"]}


def test_w2_96_d10b_the_refusal_names_the_readme_line_and_the_cell():
    readme = "# Map\n\n| KPI | Test |\n|---|---|\n| S1 | `a` |\n| S2, 3 cases | `b` |\n"
    with pytest.raises(runner.Unlisted) as raised:
        runner.parse_map(readme)
    assert raised.value.args == (6, "S2, 3 cases")
    heading = "## S1 and failures 2a\n| Test |\n|---|\n| `a` |\n"
    with pytest.raises(runner.Unlisted) as raised:
        runner.parse_map(heading)
    assert raised.value.args == (1, "S1 and failures 2a")


def test_w2_96_d10b_a_row_mapping_nothing_is_never_refused():
    readme = ("| KPI | Test |\n|---|---|\n| S2, 3 cases | — |\n| S1 | `a` |\n\n"
              "## S1 and failures 2a\n| Test |\n|---|\n| none |\n\n## S3\n| Test |\n|---|\n| `c` |\n")
    assert runner.parse_map(readme) == {"success-1": ["a"], "success-3": ["c"]}


def test_w2_96_d10b_gov_accept_refuses_before_any_test_naming_the_cell(project, capsys, tmp_path):
    root, temp = project
    flag = tmp_path / "ran"
    readme = "| KPI | Test |\n|---|---|\n| S1 | `test_a.py` |\n| S2, 3 cases `test_secretname.py` | `test_a.py` |\n"
    _plant(root, readme, {"test_a.py": f"def test_a():\n    open({str(flag)!r}, 'w').close()\n"}, {}, conftest=False)
    code, envelope, text = _accept(root, capsys)
    assert code == 1 and envelope["ok"] is False
    error = envelope["error"]
    assert error["code"] == "ACCEPT_MAP_UNREADABLE"
    assert error["details"] == {"ticket": "DAEO-t001", "path": "tests/acceptance/T1/", "line": 4,
                                "cell": "S2, 3 cases …"}
    assert "README line 4" in error["message"] and "S2, 3 cases …" in error["message"]
    assert "secretname" not in text and "test_a" not in text
    assert not flag.exists()
    assert list(temp.iterdir()) == []


def test_w2_96_d10b_the_named_cell_masks_test_and_file_names_and_is_bounded():
    assert runner._masked("S1, `x` and test_y in sub/test_z.py or a.py::b, 2 more") == "S1, … and … in … or …, 2 more"
    assert len(runner._masked("S1, 3 " + "word " * 60)) == runner.CELL_MAX


def test_w2_96_d10b_through_accept_a_gov_error_with_the_cell(project):
    root, _ = project
    _plant(root, "| KPI | Test |\n|---|---|\n| F1, 2 cases | `test_a.py` |\n", {"test_a.py": "pass\n"}, {})
    with pytest.raises(GovError) as raised:
        runner.accept(root, "DAEO-t001", 30)
    assert raised.value.code == "ACCEPT_MAP_UNREADABLE"
    assert raised.value.details["line"] == 3 and raised.value.details["cell"] == "F1, 2 cases"
