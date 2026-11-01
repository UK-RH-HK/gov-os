"""Premises of W2-96's acceptance tests: the probes can see what they look for.

The planted suites give the outcomes the cases expect under raw pytest, and raw pytest's output holds the marker
(so a runner that passed it on would be caught); the planted collection errors and crashes end pytest as designed;
the decoy library fails a planted test when it comes first; the marker is nowhere in the code under test; and this
folder's README is a KPI map in the design note's form, so ``gov accept DAEO-ouet`` can run this folder.

Green before the implementation, by design: these cases test the tests, not ``gov accept``.
"""

from __future__ import annotations

import os
import re
import signal
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_96_support as support  # noqa: E402


@pytest.mark.parametrize("files, raw", [(support.common_files, support.COMMON_RAW),
                                        (support.fails_files, support.FAILS_RAW)], ids=["common", "fails"])
def test_the_planted_suites_give_the_designed_outcomes_and_raw_output_holds_the_marker(tmp_path, files, raw):
    project = support.Project(tmp_path, files(), support.SIMPLE_README)
    done, outcomes = project.raw_pytest()
    assert outcomes == raw, f"raw pytest gave other outcomes: {outcomes}\n{done.stdout[-3000:]}"
    assert support.MARKER in (done.stdout + done.stderr).lower(), "raw pytest output should hold the marker"
    if files is support.common_files:
        assert project.ran() == support.COMMON_RAN, "every planted case that runs leaves its probe record"


@pytest.mark.parametrize("kind, code", [("import", 2), ("syntax", 2), ("empty", 5)])
def test_the_planted_collection_errors_end_pytest_as_collection_errors(tmp_path, kind, code):
    project = support.Project(tmp_path, support.collection_files(kind), support.SECOND_README)
    done, _ = project.raw_pytest()
    assert done.returncode == code, f"raw pytest ended {done.returncode}\n{done.stdout[-3000:]}"
    if kind != "empty":
        assert support.MARKER in (done.stdout + done.stderr).lower(), "the collection error's message holds it"


@pytest.mark.parametrize("kind, code", [("crash_signal", -signal.SIGKILL), ("crash_internal", 3)])
def test_the_planted_crashes_end_pytest_before_its_report(tmp_path, kind, code):
    project = support.Project(tmp_path, support.second_file(kind, f"test_qzv96leak_{kind}"), support.SECOND_README)
    done, outcomes = project.raw_pytest()
    assert done.returncode == code, f"raw pytest ended {done.returncode}\n{done.stdout[-3000:]}"
    assert outcomes is None, "pytest wrote no report: it never finished"


def test_the_decoy_library_fails_a_planted_test_when_it_comes_first(tmp_path):
    project = support.Project(tmp_path, dict(support.ALPHA), support.SIMPLE_README)
    tree_first = os.pathsep.join([str(project.root / "src"), str(project.decoy)])
    decoy_first = os.pathsep.join([str(project.decoy), str(project.root / "src")])
    _, outcomes = project.raw_pytest(python_path=tree_first)
    assert outcomes and set(outcomes.values()) == {"passed"}, f"the planted tree first: {outcomes}"
    _, outcomes = project.raw_pytest(python_path=decoy_first)
    assert outcomes and set(outcomes.values()) == {"failed"}, f"the decoy first: {outcomes}"


def test_the_marker_is_nowhere_in_the_code_under_test():
    held = [str(path) for path in support.SRC.rglob("*.py")
            if support.MARKER in path.read_text(encoding="utf-8", errors="replace").lower()]
    assert not held, f"the marker must come only from the planted tests: {held}"


def test_this_readme_is_a_kpi_map_gov_accept_can_run():
    """Revised for review 1: the map names the review file's cases one by one (bare words, their function names),
    and the premises without backticks, since a row holding an item whose KPI cell names no line refuses the whole
    run (R4); every row holding an item begins with a line name the reader takes."""
    text = (support.HERE / "README.md").read_text(encoding="utf-8")
    tables = [(header, body) for header, body in support.markdown_tables(text)
              if any(cell.lower().startswith(("test", "file")) for cell in header)]
    assert len(tables) == 1, "the README holds one table with a Test or File column: its map"
    header, body = tables[0]
    kpi = next((i for i, cell in enumerate(header) if cell.lower().startswith("kpi")), None)
    tests = next(i for i, cell in enumerate(header) if cell.lower().startswith(("test", "file")))
    assert kpi is not None, "the map is in the row form: a KPI column"
    named, files, words = set(), set(), set()
    for row in body:
        items = re.findall(r"`([^`]+)`", row[tests])
        if not items:
            continue
        names = support.line_names(row[kpi])
        assert names, f"a row holding items names no line, which refuses the whole run (R4): {row[kpi]!r}"
        named |= set(names)
        for item in items:
            (files if item.endswith(".py") else words).add(item)
    every_line = {f"success-{n}" for n in range(1, 6)} | {f"failure-{n}" for n in range(1, 5)}
    assert named == every_line, f"the map names success 1 to 5 and failure 1 to 4, not success 6: {sorted(named)}"
    defined = {path.name: support.test_functions(path) for path in support.HERE.glob("test_*.py")}
    premises = {"test_w2_96_at_premises.py"}
    assert files <= set(defined) - premises, f"file items that are no test file here, or the premises: {files}"
    owner = {name: file for file, names in defined.items() for name in names}
    stray = sorted(word for word in words
                   if word not in owner or owner[word] in premises or word.startswith("test_premise_"))
    assert not stray, f"names in the map that are no test function here, or are premises: {stray}"
    missing = sorted(f"{file} {name}" for file, names in defined.items() if file not in files | premises
                     for name in names if name not in words and not name.startswith("test_premise_"))
    assert not missing, f"tests the map names neither by their file nor by their name: {missing}"
