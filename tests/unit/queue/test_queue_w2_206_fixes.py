"""W2-206, the two fixes of W2-202: the queue's acceptance run keeps its JUnit report through the runner's own
parameter (nothing of ``gov.accept.runner`` is replaced), and an acceptance run that fails without naming a failing
test names its ticket as the culprit."""
from __future__ import annotations

import xml.etree.ElementTree as ET

import pytest

from gov.accept import runner
from gov.cli.errors import GovError
from gov.close import attribution
from gov.queue import acceptance, command

from queue_support import OTHER, OTHER_WBS, TICKET, WBS, readme_text, ticket_text

GREEN = {"src/pkg/feature.py": "def twice(x):\n    return 2 * x\n"}
CRASH = {"src/pkg/gadget.py": "def gizmo():\n    return 1\n"}  # the folder's test imports ``gadget``: no collection
NEW, NEW_WBS = "T-cccc", "W-3"
NEW_FOLDER = f"tests/acceptance/{NEW_WBS}/"


# -- fix 1 ------------------------------------------------------------------------------------------------------

def test_the_acceptance_run_keeps_its_report_and_replaces_nothing_of_the_runner(project, monkeypatch):
    seen = []
    read_cases = runner.read_cases

    def watching(report):
        seen.append(runner.read_cases)
        return read_cases(report)

    monkeypatch.setattr(runner, "read_cases", watching)
    junit = project.root / ".gov-runtime" / "kept.xml"
    done = acceptance.run(project.root, TICKET, f"tests/acceptance/{WBS}/", 120, junit)
    assert seen == [watching], "the runner's read_cases was replaced during the run"
    assert done["outcome"] == "pass" and done["failing"] == []
    assert done["run"] == {"name": f"acceptance:{TICKET}", "passed": 1, "failed": 0, "errors": 0, "skipped": 0}
    assert [case.get("name") for case in ET.parse(junit).iter("testcase")] == ["test_twice"]


def test_a_failing_test_is_named_by_its_node_and_carries_no_culprit(project):
    project.commit("red", files={"src/pkg/feature.py": "def twice(x):\n    return 0\n"})
    done = acceptance.run(project.root, TICKET, f"tests/acceptance/{WBS}/", 120, project.root / ".gov-runtime/k.xml")
    assert done["outcome"] == "fail"
    assert done["failing"] == [{"test": f"tests/acceptance/{WBS}/test_w1.py::test_twice",
                                "failure_type": "AssertionError"}]


def test_a_run_that_names_no_failing_test_names_the_folder_and_its_ticket(project):
    project.commit("crash", files=CRASH)
    done = acceptance.run(project.root, OTHER, f"tests/acceptance/{OTHER_WBS}/", 120,
                          project.root / ".gov-runtime/k.xml")
    assert (done["outcome"], done["error_kind"]) == ("error", "collection")
    assert done["failing"] == [{"test": f"tests/acceptance/{OTHER_WBS}/", "failure_type": attribution.UNKNOWN,
                                "culprit": OTHER}]


# -- fix 2 ------------------------------------------------------------------------------------------------------

def _no_alone_runs(monkeypatch):
    ran = []
    alone = attribution.run_alone

    def counted(clone, test, *args, **more):
        ran.append(test)
        return alone(clone, test, *args, **more)

    monkeypatch.setattr(attribution, "run_alone", counted)
    return ran


def test_of_two_the_ticket_whose_acceptance_run_crashes_is_the_culprit_and_the_other_lands(project, monkeypatch):
    ran = _no_alone_runs(monkeypatch)
    project.branch("topic/a", GREEN, f"Task: {TICKET}", "Role: engineer")
    project.branch("topic/b", CRASH, f"Task: {OTHER}", "Role: engineer")
    result, code = command.land(project.root, [f"{TICKET}=topic/a", f"{OTHER}=topic/b"])
    assert code == 3 and result["culprits"] == [OTHER] and result["landed"] == [TICKET]
    assert result["reds"] == [f"tests/acceptance/{OTHER_WBS}/"]
    assert project.status_of(TICKET, "main") == "closed" and project.status_of(OTHER, "main") == "open"
    assert ran == [], "a red named by its ticket needs no search"


def test_the_same_ticket_alone_is_a_culprit_and_nothing_lands(project):
    base = project.sha("main")
    project.branch("topic/b", CRASH, f"Task: {OTHER}", "Role: engineer")
    result, code = command.land(project.root, [f"{OTHER}=topic/b"])
    assert code == 3 and result["culprits"] == [OTHER] and result["landed"] == [] and result["tested"] is None
    assert project.sha("main") == base


def _new_ticket_with_a_line_no_test_runs_for(project):
    """A ticket whose acceptance folder is its branch's own (absent at the base) and whose README maps a line to a
    test that does not exist: the folder's pytest run is green, the runner's answer is not."""
    project.commit("a third ticket", files={f".tickets/{NEW}.md": ticket_text(
        NEW, NEW_WBS, ["src/pkg/lonely.py", f"{NEW_FOLDER}**"])})
    project.git("checkout", "-q", "-b", "topic/c", "main")
    project.commit("tests", f"Task: {NEW}", "Role: independent-test-designer", files={
        f"{NEW_FOLDER}test_w3.py": "def test_there():\n    assert True\n",
        f"{NEW_FOLDER}README.md": readme_text(NEW_WBS, "test_w3.py::test_there").replace(
            "| failure-1 | `test_w3.py::test_there` |", "| failure-1 | `test_w3.py::test_not_there` |")})
    project.commit("work", f"Task: {NEW}", "Role: engineer", files={"src/pkg/lonely.py": "VALUE = 1  # c\n"})
    project.git("checkout", "-q", "main")


def test_a_line_no_test_ran_for_makes_its_ticket_the_culprit_not_the_batch_unexplained(project):
    _new_ticket_with_a_line_no_test_runs_for(project)
    project.branch("topic/a", GREEN, f"Task: {TICKET}", "Role: engineer")
    result, code = command.land(project.root, [f"{NEW}=topic/c", f"{TICKET}=topic/a"])
    assert code == 3 and result["culprits"] == [NEW] and result["landed"] == [TICKET]
    assert project.status_of(TICKET, "main") == "closed" and project.status_of(NEW, "main") == "open"


def test_a_test_failing_by_name_is_still_attributed_by_the_search(project, monkeypatch):
    ran = _no_alone_runs(monkeypatch)
    project.branch("topic/a", GREEN, f"Task: {TICKET}", "Role: engineer")
    project.branch("topic/b", {"src/pkg/gadget.py": "def gadget():\n    return 2\n"}, f"Task: {OTHER}",
                   "Role: engineer")
    result, code = command.land(project.root, [f"{TICKET}=topic/a", f"{OTHER}=topic/b"])
    node = f"tests/acceptance/{OTHER_WBS}/test_w2.py::test_gadget"
    assert code == 3 and result["culprits"] == [OTHER] and result["reds"] == [node]
    assert node in ran


def test_a_hand_merged_ticket_whose_acceptance_run_crashes_is_the_culprit_without_a_search(project, monkeypatch):
    project.branch("topic/b", CRASH, f"Task: {OTHER}", "Role: engineer")
    project.git("merge", "-q", "--no-ff", "--no-edit", "topic/b")
    base = project.sha("main")
    ran = _no_alone_runs(monkeypatch)
    result, code = command.land(project.root, [f"{OTHER}=topic/b"])
    assert code == 3 and result["culprits"] == [OTHER] and result["landed"] == [] and result["base_reds"] == []
    assert project.sha("main") == base and ran == []
