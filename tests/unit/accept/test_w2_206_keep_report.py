"""W2-206, W2-202's fix 1: ``gov.accept.runner.accept(root, ticket, timeout, keep_report=<path>)`` copies the run's
JUnit report to the path before it is read and changes nothing else."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

from gov.accept import runner

README = "# T\n\n| KPI | Test |\n|-----|------|\n| S1 | `test_one.py::test_good` |\n| F1 | `test_one.py::test_bad` |\n"
TESTS = "def test_good():\n    assert 1\n\n\ndef test_bad():\n    assert 0\n"


def _plant(root: Path, tests: str = TESTS) -> Path:
    (root / ".tickets").mkdir(parents=True)
    (root / ".tickets" / "DAEO-t001.md").write_text(
        "---\nid: DAEO-t001\nwbs_id: W9-01\nstatus: in_progress\nacceptance_tests:\n  path: tests/acceptance/T1/\n"
        "---\n# t\n", encoding="utf-8")
    folder = root / "tests" / "acceptance" / "T1"
    folder.mkdir(parents=True)
    (folder / "README.md").write_text(README, encoding="utf-8")
    (folder / "test_one.py").write_text(tests, encoding="utf-8")
    return root


def test_the_report_is_kept_at_the_path_and_the_answer_is_the_same(tmp_path):
    root = _plant(tmp_path / "p")
    kept = tmp_path / "kept" / "report.xml"
    kept.parent.mkdir()
    plain = runner.accept(root, "DAEO-t001", 120)
    with_report = runner.accept(root, "DAEO-t001", 120, keep_report=kept)
    assert with_report == plain and plain[0]["outcome"] == "fail"
    names = sorted(case.get("name") for case in ET.parse(kept).iter("testcase"))
    assert names == ["test_bad", "test_good"]


def test_without_the_parameter_nothing_is_kept(tmp_path):
    root = _plant(tmp_path / "p")
    runner.accept(root, "DAEO-t001", 120)
    assert sorted(p.name for p in tmp_path.iterdir()) == ["p"]


def test_a_run_that_writes_no_report_keeps_none_and_answers_as_before(tmp_path):
    root = _plant(tmp_path / "p", "import nothing_like_this\n")
    kept = tmp_path / "report.xml"
    answer, code = runner.accept(root, "DAEO-t001", 120, keep_report=kept)
    assert (answer["outcome"], answer["error_kind"], code) == ("error", "collection", runner.EXIT_ERROR)
    assert runner.accept(root, "DAEO-t001", 120) == (answer, code)
