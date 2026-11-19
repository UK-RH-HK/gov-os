"""``gov queue`` becomes the landing-and-close, part 1 (W2-202; L2 A1, A3, A4, A5), on planted projects: the pause, the
acceptance tests at the landing, a ticket judged on its record, a branch already merged, a known base red, and the
queue settings ``gov adopt --facts`` writes."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import xml.etree.ElementTree as ET

import pytest
import yaml

from gov.cli.errors import GovError
from gov.queue import command

from queue_support import OTHER, OTHER_WBS, REPO_ROOT, TICKET, WBS, ticket_text

GREEN = {"src/pkg/feature.py": "def twice(x):\n    return 2 * x\n"}
RED = {"src/pkg/feature.py": "def twice(x):\n    return 2 * x + 1\n"}
SLIP = {"src/pkg/other.py": "def other():\n    return 1  # a\n"}
OWN_NODE = f"tests/acceptance/{WBS}/test_w1.py::test_twice"
KNOWN = "tests/unit/test_known.py"
KNOWN_NODE = f"{KNOWN}::test_known"
KNOWN_RED = {KNOWN: "from pkg.other import other\n\n\ndef test_known():\n    assert other() == 2\n"}
RESEARCH, RECORD = "T-rrrr", "docs/research/r.md"


def _close_front(project, ticket, rev="main"):
    text = project.git("show", f"{rev}:docs/close/{ticket}/CL-{ticket}.md")
    return yaml.safe_load(text.split("---")[1])


def _parents(project, commit):
    return project.git("rev-list", "--parents", "-n", "1", commit).split()[1:]


def _remove(project, rel, message):
    (project.root / rel).unlink()
    return project.commit(message)


# -- A5: the pause ----------------------------------------------------------------------------------------------

def test_a_paused_project_is_refused_before_anything_is_written_and_lands_once_lifted(project):
    base = project.sha("main")
    project.branch("topic/a", GREEN, f"Task: {TICKET}", "Role: engineer")
    flag = project.root / ".gov-runtime" / "freeze"
    flag.parent.mkdir()
    flag.write_text("FROZEN\n", encoding="utf-8")
    with pytest.raises(GovError) as raised:
        command.land(project.root, [f"{TICKET}=topic/a"])
    assert raised.value.code == "PROJECT_PAUSED" and raised.value.exit_code == 1
    assert sorted(p.name for p in flag.parent.iterdir()) == ["freeze"]
    assert project.sha("main") == base and project.status_of(TICKET, "main") == "open"
    flag.unlink()
    result, code = command.land(project.root, [f"{TICKET}=topic/a"])
    assert code == 0 and result["landed"] == [TICKET]


def test_the_pause_is_read_before_the_settings(project):
    project.git("checkout", "-q", "--detach")
    flag = project.root / ".gov-runtime" / "freeze"
    flag.parent.mkdir()
    flag.write_text("FROZEN\n", encoding="utf-8")
    with pytest.raises(GovError) as raised:
        command.land(project.root, [f"{TICKET}=topic/a"])
    assert raised.value.code == "PROJECT_PAUSED"


# -- A3: the acceptance tests at the landing --------------------------------------------------------------------

def test_a_ticket_whose_acceptance_folder_holds_no_test_is_out_of_the_batch_and_the_other_lands(project):
    _remove(project, f"tests/acceptance/{OTHER_WBS}/test_w2.py", "a folder with its README alone")
    project.branch("topic/b", {"src/pkg/gadget.py": "def gadget():\n    return 1  # b\n"}, f"Task: {OTHER}",
                   "Role: engineer")
    project.branch("topic/a", GREEN, f"Task: {TICKET}", "Role: engineer")
    result, code = command.land(project.root, [f"{OTHER}=topic/b", f"{TICKET}=topic/a"])
    assert code == 3 and result["landed"] == [TICKET]
    assert [(r["ticket"], r["code"]) for r in result["refused"]] == [(OTHER, "NO_ACCEPTANCE_TESTS")]
    assert project.status_of(OTHER, "main") == "open"
    assert "# b" not in project.git("show", "main:src/pkg/gadget.py")


def test_a_ticket_without_tests_alone_moves_nothing_and_runs_nothing(project):
    base = _remove(project, f"tests/acceptance/{WBS}/test_w1.py", "a folder with its README alone")
    project.branch("topic/a", GREEN, f"Task: {TICKET}", "Role: engineer")
    result, code = command.land(project.root, [f"{TICKET}=topic/a"])
    assert code == 3 and result["landed"] == [] and result["tested"] is None and result["runs"] == []
    assert result["refused"][0]["code"] == "NO_ACCEPTANCE_TESTS"
    assert project.sha("main") == base


def test_a_folder_with_tests_and_no_kpi_map_is_refused_with_the_runner_s_code(project):
    base = _remove(project, f"tests/acceptance/{WBS}/README.md", "tests and no map")
    project.branch("topic/a", GREEN, f"Task: {TICKET}", "Role: engineer")
    result, code = command.land(project.root, [f"{TICKET}=topic/a"])
    assert code == 3 and result["landed"] == [] and result["tested"] is None
    assert [(r["ticket"], r["code"]) for r in result["refused"]] == [(TICKET, "ACCEPT_NO_MAP")]
    assert project.sha("main") == base


def test_the_acceptance_folder_runs_once_through_the_runner_and_its_lines_are_in_the_record(project):
    from gov.accept import runner

    project.branch("topic/a", {**GREEN, **SLIP}, f"Task: {TICKET}", "Role: engineer")
    result, code = command.land(project.root, [f"{TICKET}=topic/a"])
    assert code == 0
    front = _close_front(project, TICKET)
    line = {"kpi": "success-1", "outcome": "pass", "passed": 1, "failed": 0, "skipped": 0}
    assert front["acceptance"] == {"folder": f"tests/acceptance/{WBS}/", "lines": [line, {**line, "kpi": "failure-1"}]}
    project.git("checkout", "-q", "--detach", result["tested"])
    assert runner.accept(project.root, TICKET, 120)[0]["lines"] == front["acceptance"]["lines"]
    project.git("checkout", "-q", "main")
    # the selection's run leaves the folder out; its run is one of the record's runs, its JUnit file kept
    assert result["selection"]["suites"] == ["tests/unit/test_other.py"]
    assert {"name": f"acceptance:{TICKET}", "passed": 1, "failed": 0, "errors": 0, "skipped": 0} in result["runs"]
    assert front["runs"] == result["runs"]
    names = [case.get("name") for path in (project.root / ".gov-runtime").rglob("*.xml")
             if "clone" not in path.parts for case in ET.parse(path).iter("testcase")]
    assert sorted(names) == ["test_other", "test_twice"]
    assert result["seconds"]["acceptance"] > 0


def test_a_change_that_reaches_no_other_test_lands_on_its_acceptance_run_alone(project):
    project.branch("topic/a", GREEN, f"Task: {TICKET}", "Role: engineer")
    result, code = command.land(project.root, [f"{TICKET}=topic/a"])
    assert code == 0 and result["landed"] == [TICKET] and result["selection"]["suites"] == []
    assert sum(r["passed"] for r in result["runs"]) == 1


def test_a_failing_acceptance_test_is_the_red_named_and_its_ticket_the_culprit(project):
    project.branch("topic/a", RED, f"Task: {TICKET}", "Role: engineer")
    result, code = command.land(project.root, [f"{TICKET}=topic/a"])
    assert code == 3 and result["culprits"] == [TICKET] and result["reds"] == [OWN_NODE]
    assert result["base_reds"] == [] and result["tested"] is None


# -- A3: a ticket judged on its record --------------------------------------------------------------------------

def _research(project, record: str):
    project.commit("a research ticket", files={f".tickets/{RESEARCH}.md": ticket_text(
        RESEARCH, "W-9", ["docs/research/**"], **{"class": "research"}).replace(
        "path: tests/acceptance/W-9/", f"evidence:\n  - {RECORD}")})
    front = yaml.safe_load(project.git("show", f"main:.tickets/{RESEARCH}.md").split("---")[1])
    assert front["acceptance_tests"] == {"evidence": [RECORD]}, "fixture: the research ticket's file"
    project.branch("topic/r", {RECORD: record}, f"Task: {RESEARCH}", "Role: research")
    return project.sha("main")


def test_a_research_ticket_is_judged_on_its_record_and_lands_without_a_test_folder(project):
    _research(project, "---\ntype: research\n---\n# What was found\n")
    result, code = command.land(project.root, [f"{RESEARCH}=topic/r"])
    assert code == 0 and result["landed"] == [RESEARCH] and result["refused"] == []
    assert project.status_of(RESEARCH, "main") == "closed"
    assert _close_front(project, RESEARCH)["acceptance"] == {"folder": None, "lines": [], "record": [RECORD]}


def test_a_research_ticket_whose_record_the_gate_refuses_does_not_land(project):
    base = _research(project, "# No record of type research\n")
    result, code = command.land(project.root, [f"{RESEARCH}=topic/r"])
    assert code == 3 and result["landed"] == [] and result["tested"] is None
    assert [(r["ticket"], r["code"]) for r in result["refused"]] == [(RESEARCH, "EVIDENCE_REFUSED")]
    assert project.sha("main") == base and project.status_of(RESEARCH, "main") == "open"


# -- A4: a branch already merged --------------------------------------------------------------------------------

def _merged_by_hand(project, planted, *trailers, how="--no-ff"):
    tip = project.branch("topic/a", planted, *trailers)
    project.git("merge", how, "-q", "--no-edit", "topic/a")
    return tip, project.sha("main")


def test_a_ticket_merged_by_hand_is_closed_on_the_head_and_no_merge_is_made(project):
    tip, head = _merged_by_hand(project, {**GREEN, **SLIP}, f"Task: {TICKET}", "Role: engineer")
    result, code = command.land(project.root, [f"{TICKET}=topic/a"])
    assert code == 0 and result["landed"] == [TICKET] and result["tested"] == head and result["base"] == head
    assert _parents(project, project.sha("main")) == [head] and result["head"] == project.sha("main")
    front = _close_front(project, TICKET)
    assert front["commit"] == head and front["branch"] == {"name": "topic/a", "tip": tip}
    assert front["acceptance"]["lines"] and all(line["outcome"] == "pass" for line in front["acceptance"]["lines"])
    assert result["selection"]["suites"] == ["tests/unit/test_other.py"]
    assert sum(r["passed"] for r in result["runs"]) == 2
    assert project.status_of(TICKET, "main") == "closed" and project.git("status", "--porcelain") == ""
    with pytest.raises(GovError) as raised:
        command.land(project.root, [f"{TICKET}=topic/a"])
    assert raised.value.code == "TICKET_CLOSED"


def test_the_checks_still_run_on_a_branch_merged_by_hand(project):
    _, head = _merged_by_hand(project, {f"tests/acceptance/{WBS}/test_w1.py": "def test_twice():\n    pass\n"},
                              f"Task: {TICKET}", "Role: engineer")
    result, code = command.land(project.root, [f"{TICKET}=topic/a"])
    assert code == 3 and result["landed"] == [] and result["refused"][0]["code"] == "TEST_AUTHOR_REFUSED"
    assert project.sha("main") == head and project.status_of(TICKET, "main") == "open"


def test_a_red_on_the_head_that_was_green_before_the_merge_keeps_the_ticket_open(project):
    before = project.sha("main")
    _, head = _merged_by_hand(project, RED, f"Task: {TICKET}", "Role: engineer")
    result, code = command.land(project.root, [f"{TICKET}=topic/a"])
    assert code == 3 and result["culprits"] == [TICKET] and result["reds"] == [OWN_NODE]
    assert result["base_reds"] == [] and before != head
    assert project.sha("main") == head and project.status_of(TICKET, "main") == "open"


def test_a_red_on_the_head_that_was_red_before_the_merge_is_a_base_red_of_the_hand_merged_ticket(project):
    before = project.commit("a red on the base", files=KNOWN_RED)
    _merged_by_hand(project, {**GREEN, **SLIP}, f"Task: {TICKET}", "Role: engineer")
    result, code = command.land(project.root, [f"{TICKET}=topic/a"])
    assert code == 0 and result["landed"] == [TICKET]
    assert result["base_reds"] == [{"test": KNOWN_NODE, "failure_type": "AssertionError", "base": before}]


def test_a_branch_fast_forwarded_onto_the_head_is_refused_as_before(project):
    _, head = _merged_by_hand(project, GREEN, f"Task: {TICKET}", "Role: engineer", how="--ff-only")
    with pytest.raises(GovError) as raised:
        command.land(project.root, [f"{TICKET}=topic/a"])
    assert raised.value.code == "CANDIDATE_NOT_ISOLATED" and raised.value.exit_code == 3
    assert project.sha("main") == head and project.status_of(TICKET, "main") == "open"


def test_a_ticket_already_merged_is_landed_alone(project):
    _, head = _merged_by_hand(project, GREEN, f"Task: {TICKET}", "Role: engineer")
    project.branch("topic/b", {"src/pkg/gadget.py": "def gadget():\n    return 1  # b\n"}, f"Task: {OTHER}",
                   "Role: engineer")
    with pytest.raises(GovError) as raised:
        command.land(project.root, [f"{TICKET}=topic/a", f"{OTHER}=topic/b"])
    assert raised.value.code == "CANDIDATE_NOT_ISOLATED" and raised.value.exit_code == 3
    assert project.sha("main") == head


# -- A1: a known base red ---------------------------------------------------------------------------------------

def test_a_base_red_is_in_the_answer_the_queue_s_record_and_the_close_record(project):
    base = project.commit("a red on the base", files=KNOWN_RED)
    project.branch("topic/a", {**GREEN, **SLIP}, f"Task: {TICKET}", "Role: engineer")
    result, code = command.land(project.root, [f"{TICKET}=topic/a"])
    assert code == 0 and result["landed"] == [TICKET] and result["culprits"] == []
    entry = {"test": KNOWN_NODE, "failure_type": "AssertionError", "base": base}
    assert result["base_reds"] == [entry]
    assert json.loads((project.root / result["record"]).read_text())["result"]["base_reds"] == [entry]
    front = _close_front(project, TICKET)
    assert front["reds"] == [{**entry, "verdict": "base"}] and front["base_reds"] == [KNOWN_NODE]
    changed = project.git("diff", "--name-only", base, "main").split()
    assert not [p for p in changed if p.startswith(".tickets/") and p != f".tickets/{TICKET}.md"]
    assert not [p for p in changed if p.startswith("docs/") and not p.startswith(("docs/close/", "docs/checkpoints/"))]


# -- A5: the settings gov adopt --facts writes ------------------------------------------------------------------

def test_adopt_facts_writes_queue_yaml_where_absent_and_no_close_yaml(tmp_path):
    env = {**os.environ, "PYTHONPATH": str(REPO_ROOT / "src")}
    command_line = [sys.executable, "-m", "gov.cli.main", "adopt", "--facts", "--root", str(tmp_path), "--json"]
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    done = subprocess.run(command_line, capture_output=True, text=True, env=env)
    assert done.returncode == 0, done.stdout + done.stderr
    settings = tmp_path / "governance" / "project" / "queue.yaml"
    assert yaml.safe_load(settings.read_text()) == {"integration": "main", "work_branch": "{ticket}"}
    assert command._settings(tmp_path) == {"integration": "main", "work_branch": "{ticket}"}
    assert not (tmp_path / "governance" / "project" / "close.yaml").exists()
    settings.write_text("integration: develop\n", encoding="utf-8")
    (tmp_path / "governance" / "project" / "facts.yaml").unlink()
    assert subprocess.run(command_line, capture_output=True, text=True, env=env).returncode == 0
    assert settings.read_text() == "integration: develop\n"  # a present queue.yaml is left as it is
    assert (tmp_path / "governance" / "project" / "facts.yaml").is_file()


def test_adopt_facts_leaves_a_repository_with_its_own_facts_file_wholly_as_it_is(tmp_path):
    env = {**os.environ, "PYTHONPATH": str(REPO_ROOT / "src")}
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    own = tmp_path / "governance" / "project" / "facts.yaml"
    own.parent.mkdir(parents=True)
    own.write_text("paths: {main: '.'}\n", encoding="utf-8")
    done = subprocess.run([sys.executable, "-m", "gov.cli.main", "adopt", "--facts", "--root", str(tmp_path),
                           "--json"], capture_output=True, text=True, env=env)
    assert done.returncode == 0, done.stdout + done.stderr
    assert sorted(p.name for p in own.parent.iterdir()) == ["facts.yaml"]
