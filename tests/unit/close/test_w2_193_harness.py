"""W2-193 (DAEO-7jln) S1 (colliding suites each in their own pytest process), S2 (a collection error re-run as its
module file), S3 (the default base: --base, the green record, the ticket's parent) and S4 (a red judged by the
base run)."""
from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

from gov.close import attribution, command, select

from .test_w2_115_support import TICKET, change, green_night, project


def _plant(root: Path, files: dict) -> None:
    for rel, text in files.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")


PASS = "def test_ok():\n    assert True\n"
BUILDS = "from conftest import build_tree\n\n\ndef test_builds():\n    assert build_tree() == 1\n"


# --- S2: the node id of a collection error ------------------------------------------

def test_s2_a_collection_errors_node_is_its_module_file():
    case = ET.fromstring('<testcase classname="" name="tests.a.test_x" file="tests/a/test_x.py" line="0"/>')
    assert attribution._node(Path("."), case) == "tests/a/test_x.py"


def test_s2_a_tests_node_is_still_its_own_id():
    case = ET.fromstring('<testcase classname="tests.a.test_x.TestK" name="test_y[p]" file="tests/a/test_x.py"/>')
    assert attribution._node(Path("."), case) == "tests/a/test_x.py::TestK::test_y[p]"
    case = ET.fromstring('<testcase classname="tests.a.test_x" name="test_y" file="tests/a/test_x.py"/>')
    assert attribution._node(Path("."), case) == "tests/a/test_x.py::test_y"


def test_s2_a_module_that_fails_to_import_is_run_alone_by_its_file(tmp_path):
    _plant(tmp_path, {"tests/a/test_x.py": "import no_such_module_here\n\n\ndef test_x():\n    pass\n",
                      "tests/a/b/test_y.py": "def test_y():\n    assert 1 == 2\n"})
    # the full run goes on past the collection error, as an xdist run does
    done = attribution.run_pytest(tmp_path, ["tests/a/"], ["-p", "no:cacheprovider", "-o", "junit_family=xunit1",
                                                           "--continue-on-collection-errors"],
                                  tmp_path / "out/run.xml", tmp_path / "out/run.log", 120)
    results = attribution.read_results(Path(done["junit"]), tmp_path)
    tests = {f["test"]: f["failure_type"] for f in results["failures"]}
    assert tests == {"tests/a/test_x.py": "ModuleNotFoundError", "tests/a/b/test_y.py::test_y": "AssertionError"}
    for test, kind in tests.items():
        assert attribution.run_alone(tmp_path, test, ["-p", "no:cacheprovider"], tmp_path / "alone", 120,
                                     "with") == kind


# --- S1: the colliding suites ----------------------------------------------------

def test_s1_folders_holding_a_module_of_the_same_name_go_to_separate_processes(tmp_path):
    _plant(tmp_path, {"a/test_same.py": PASS, "b/test_same.py": PASS, "c/test_other.py": PASS})
    assert command._process_groups(tmp_path, ["a/", "b/", "c/"]) == [["a/", "c/"], ["b/"]]


def test_s1_a_module_importing_conftest_by_name_parts_from_every_other_conftest(tmp_path):
    _plant(tmp_path, {"a/conftest.py": "def build_tree():\n    return 1\n", "a/test_a.py": BUILDS,
                      "b/conftest.py": "", "b/test_b.py": PASS, "c/test_c.py": PASS})
    assert command._process_groups(tmp_path, ["a/", "b/", "c/"]) == [["a/", "c/"], ["b/"]]
    # the import written as ``import conftest`` counts as well
    _plant(tmp_path, {"a/test_a.py": "import conftest\n\n\ndef test_a():\n    assert conftest.build_tree()\n"})
    assert command._process_groups(tmp_path, ["a/", "b/", "c/"]) == [["a/", "c/"], ["b/"]]


def test_s1_two_conftests_alone_or_packages_do_not_collide(tmp_path):
    _plant(tmp_path, {"a/conftest.py": "", "a/test_a.py": PASS, "b/conftest.py": "", "b/test_b.py": PASS,
                      "p/__init__.py": "", "p/test_same.py": PASS, "q/__init__.py": "", "q/test_same.py": PASS})
    assert command._process_groups(tmp_path, ["a/", "b/", "p/", "q/"]) == [["a/", "b/", "p/", "q/"]]


def test_s1_a_file_target_is_grouped_by_its_folder(tmp_path):
    _plant(tmp_path, {"g/s/conftest.py": "def build_tree():\n    return 1\n", "g/s/test_one.py": BUILDS,
                      "g/k/s/conftest.py": "def build_tree():\n    return 1\n", "g/k/s/test_one.py": BUILDS,
                      "g/k/s/test_two.py": BUILDS, "t/conftest.py": "", "t/test_t.py": PASS})
    groups = command._process_groups(tmp_path, ["g/k/s/test_one.py", "g/k/s/test_two.py", "g/s/test_one.py",
                                                "t/"])
    assert groups == [["g/k/s/test_one.py", "g/k/s/test_two.py"], ["g/s/test_one.py"], ["t/"]]


def test_s1_the_phases_run_colliding_suites_apart_and_merge_their_results(tmp_path):
    _plant(tmp_path, {"a/conftest.py": "def build_tree():\n    return 1\n", "a/test_same.py": BUILDS,
                      "b/conftest.py": "def other():\n    return 2\n", "b/test_same.py": PASS,
                      "c/test_c.py": PASS})
    chosen = {"suites": ["a/", "b/", "c/"], "pytest_options": ["-p", "no:cacheprovider", "-o",
                                                               "junit_family=xunit1"]}
    out = command._phases(tmp_path, chosen, tmp_path / "out", 120, 1)
    assert out["complete"] and out["failing"] == [], out
    assert out["runs"][0] == {"name": "parallel", "passed": 3, "failed": 0, "errors": 0, "skipped": 0}
    assert out["parallel_processes"] == [["a/", "c/"], ["b/"]]
    merged = attribution.read_results(Path(out["parallel_xml"]), tmp_path)
    assert merged["passed"] == 3 and Path(out["parallel_xml"]).name == "parallel.xml"


def test_s1_suites_that_do_not_collide_share_one_process_as_before(tmp_path):
    _plant(tmp_path, {"a/test_a.py": PASS, "b/test_b.py": PASS})
    chosen = {"suites": ["a/", "b/"], "pytest_options": ["-p", "no:cacheprovider", "-o", "junit_family=xunit1"]}
    out = command._phases(tmp_path, chosen, tmp_path / "out", 120, 1)
    assert out["parallel_processes"] == [["a/", "b/"]]
    assert out["runs"][0]["passed"] == 2 and (tmp_path / "out" / "parallel.xml").is_file()
    assert not list((tmp_path / "out").glob("parallel-*.xml"))


# --- S3: the default base ----------------------------------------------------------

def _oldest_own_parent(repo) -> str:
    oldest = repo.git("log", "--format=%H", "--grep", f"Task: {TICKET}", "--no-merges").split()[-1]
    return repo.git("rev-parse", oldest + "^").strip()


def test_s3_with_no_green_record_the_base_is_the_parent_of_the_oldest_own_commit(tmp_path):
    repo = project(tmp_path)
    change(repo, {"src/pkg/feature.py": "from pkg.core import add\n\n\ndef twice(x):\n    return add(x, x)  # c\n"})
    change(repo, {"src/pkg/other.py": "def other():\n    return 1  # c\n"})
    chosen = select.scoped(repo.root, TICKET)
    assert chosen["base"] == _oldest_own_parent(repo) and chosen["base_from"] == "ticket"


def test_s3_a_green_record_on_heads_line_comes_first(tmp_path):
    repo = project(tmp_path)
    green = green_night(repo)
    change(repo, {"src/pkg/other.py": "def other():\n    return 1  # c\n"})
    chosen = select.scoped(repo.root, TICKET)
    assert chosen["base"] == green and chosen["base_from"] == "green_record"


def test_s3_no_own_commit_and_no_green_record_gives_no_base(tmp_path):
    repo = project(tmp_path)
    chosen = select.scoped(repo.root, TICKET)
    assert chosen["base"] is None and chosen["base_from"] is None


# --- S4: a red judged by the base run ----------------------------------------------

def test_s4_the_base_runs_result_judges_an_unjudgeable_red():
    caused, reason = attribution.judge_by_base_run("AssertionError", "AssertionError")
    assert caused is False and "base run" in reason
    for there in (None, attribution.NOT_COLLECTED, "ValueError", attribution.SKIPPED):
        assert attribution.judge_by_base_run("AssertionError", there)[0] is True, there
    for kind in attribution.NEVER_MATCH:
        assert attribution.judge_by_base_run(kind, kind)[0] is True, kind


def test_s4_a_red_needs_the_base_run_only_where_an_alone_run_is_absent_or_unknown():
    assert attribution.needs_base_run([attribution.ABSENT], [attribution.ABSENT])
    assert attribution.needs_base_run(["AssertionError"], [attribution.UNKNOWN])
    assert attribution.needs_base_run([attribution.UNKNOWN], ["AssertionError"])
    assert not attribution.needs_base_run(["AssertionError"], [None])
    assert not attribution.needs_base_run(["AssertionError"], ["AssertionError"])
    assert not attribution.needs_base_run([None], [])  # green alone: a flaky candidate
    assert not attribution.needs_base_run([attribution.TIMEOUT], [attribution.TIMEOUT])
