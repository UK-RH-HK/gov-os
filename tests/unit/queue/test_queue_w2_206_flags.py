"""W2-206 (L2 A6, A8): ``gov queue --dry-run``, ``--select``, ``--full`` and the after-step on planted projects."""
from __future__ import annotations

import json

import pytest
import yaml

from gov.cli.errors import GovError
from gov.close import select
from gov.queue import command

from queue_support import OTHER, TICKET, WBS

GREEN = {"src/pkg/feature.py": "def twice(x):\n    return 2 * x\n"}
RED = {"src/pkg/feature.py": "def twice(x):\n    return 2 * x + 1\n"}
SLIP = {"src/pkg/other.py": "def other():\n    return 1  # a\n"}
# a test no selection reaches (it imports nothing by name) and a change that breaks it alone
FAR = "tests/unit/test_far.py"
FAR_TEST = {FAR: "import importlib\n\n\ndef test_far():\n"
                 "    assert importlib.import_module('pkg.' + 'feature').__doc__ is None\n"}
BREAKS_FAR = {"src/pkg/feature.py": '"""A docstring."""\n\n\ndef twice(x):\n    return 2 * x\n'}


def _refs(project):
    return project.git("for-each-ref"), project.git("log", "--all", "--format=%H"), project.git("status", "--porcelain")


def _clone_head(project):
    return project.git("-C", str(project.root / ".gov-runtime/close/clone"), "rev-parse", "HEAD").strip()


# -- --dry-run --------------------------------------------------------------------------------------------------

def test_a_dry_run_answers_as_the_landing_and_moves_writes_and_leaves_nothing(project, tmp_path):
    base = project.sha("main")
    project.branch("topic/a", {**GREEN, **SLIP}, f"Task: {TICKET}", "Role: engineer")
    before, out = _refs(project), tmp_path / "out"
    result, code = command.dry_run(project.root, [f"{TICKET}=topic/a"], out=str(out))
    assert code == 0 and result["landed"] == [TICKET] and result["dry_run"] is True
    assert result["head"] is None and result["closes"] == [] and "after" not in result
    assert _refs(project) == before and project.sha("main") == base and _clone_head(project) == base
    assert not (project.root / "docs" / "close").exists() and project.status_of(TICKET) == "open"
    assert project.git("-C", str(project.root / ".gov-runtime/close/clone"), "ls-tree", "-r", "--name-only",
                       result["tested"], "docs/").strip() == ""
    assert sorted(p.name for p in out.iterdir()) == ["parallel.xml", "select.json", "serial.xml", "summary.txt",
                                                     "verify.exit"]
    assert (out / "verify.exit").read_text(encoding="utf-8") == "0\n"
    chosen = json.loads((out / "select.json").read_text(encoding="utf-8"))
    assert (chosen["ticket"], chosen["tickets"]) == (TICKET, [TICKET])
    assert "tests/unit/test_other.py" in chosen["suites"]
    assert "exit 0" in (out / "summary.txt").read_text(encoding="utf-8")
    # the landing itself then gives the same answer
    landed, landed_code = command.land(project.root, [f"{TICKET}=topic/a"])
    assert (landed_code, landed["landed"], landed["tested"] is not None) == (0, [TICKET], True)


def test_a_dry_run_with_a_culprit_says_3_in_its_answer_and_its_exit_file_and_leaves_no_ref(project):
    project.branch("topic/a", GREEN, f"Task: {TICKET}", "Role: engineer")
    project.branch("topic/b", {"src/pkg/gadget.py": "def gadget():\n    return 2\n"}, f"Task: {OTHER}",
                   "Role: engineer")
    before, base = _refs(project), project.sha("main")
    result, code = command.dry_run(project.root, [f"{TICKET}=topic/a", f"{OTHER}=topic/b"])
    assert code == 3 and result["culprits"] == [OTHER] and result["landed"] == [TICKET]
    out = project.root / ".gov-runtime" / "queue" / "dry" / f"{TICKET}+{OTHER}"
    assert (out / "verify.exit").read_text(encoding="utf-8") == "3\n"
    assert _refs(project) == before and _clone_head(project) == base


def test_a_dry_run_keeps_a_ref_the_root_already_had(project):
    project.branch("topic/a", GREEN, f"Task: {TICKET}", "Role: engineer")
    project.git("update-ref", "refs/gov-close/land", project.sha("main"))
    before = _refs(project)
    assert command.dry_run(project.root, [f"{TICKET}=topic/a"])[1] == 0
    assert _refs(project) == before


def test_a_dry_run_refused_as_a_whole_writes_its_exit_file_with_1(project):
    with pytest.raises(GovError) as raised:
        command.dry_run(project.root, ["T-none=topic/a"])
    assert raised.value.code == "TICKET_UNKNOWN" and raised.value.exit_code == 1
    out = project.root / ".gov-runtime" / "queue" / "dry" / "T-none"
    assert (out / "verify.exit").read_text(encoding="utf-8") == "1\n"
    assert "TICKET_UNKNOWN" in (out / "summary.txt").read_text(encoding="utf-8")


# -- --select ---------------------------------------------------------------------------------------------------

def test_select_prints_the_selection_and_runs_and_records_nothing(project, capsys):
    project.branch("topic/a", {**GREEN, **SLIP}, f"Task: {TICKET}", "Role: engineer")
    before, base = _refs(project), project.sha("main")
    assert command.select(project.root, [f"{TICKET}=topic/a"]) == 0
    printed = json.loads(capsys.readouterr().out)
    tracked = len(project.git("ls-tree", "-r", "--name-only", "topic/a").splitlines())
    assert printed == {"ticket": TICKET, "tickets": [TICKET], "suites": [f"tests/acceptance/{WBS}/", "tests/unit/test_other.py"],
                       "pytest_options": select.pytest_options(select.load_map(project.root)[0]),
                       "unplaced_base": [], "unplaced": [], "deleted": [], "records": [], "notices": [],
                       "path_map": f"path map: {tracked} tracked, 0 in none, 0 in two",
                       "impact": {TICKET: {"records": [], "complete": True}}}
    assert _refs(project) == before and _clone_head(project) == base
    assert not (project.root / ".gov-runtime" / "queue").exists()
    assert not list((project.root / ".gov-runtime").rglob("*.xml"))


def test_select_of_two_names_the_tickets_and_the_union(project, capsys):
    project.branch("topic/a", {**GREEN, **SLIP}, f"Task: {TICKET}", "Role: engineer")
    project.branch("topic/b", {"src/pkg/lonely.py": "VALUE = 1  # b\n"}, f"Task: {OTHER}", "Role: engineer")
    assert command.select(project.root, [f"{TICKET}=topic/a", f"{OTHER}=topic/b"]) == 0
    printed = json.loads(capsys.readouterr().out)
    assert printed["tickets"] == [TICKET, OTHER] and "ticket" not in printed
    assert {"tests/unit/test_other.py", "tests/unit/test_lonely.py"} <= set(printed["suites"])


def test_a_selection_refused_goes_to_stderr_with_2(project, capsys):
    project.branch("topic/a", {"data/unmapped.bin": "x\n"}, f"Task: {TICKET}", "Role: engineer")
    base = project.sha("main")
    assert command.select(project.root, [f"{TICKET}=topic/a"]) == 2
    said = capsys.readouterr()
    assert said.out == "" and said.err.startswith(f"SELECTION_REFUSED: {TICKET}: ")
    assert _clone_head(project) == base


# -- --full -----------------------------------------------------------------------------------------------------

def test_without_full_a_change_that_breaks_a_test_outside_its_selection_lands(project):
    project.commit("a far test", files=FAR_TEST)
    project.branch("topic/a", BREAKS_FAR, f"Task: {TICKET}", "Role: engineer")
    result, code = command.land(project.root, [f"{TICKET}=topic/a"])
    assert code == 0 and result["landed"] == [TICKET] and "full" not in result


def test_with_full_it_is_the_culprit_and_nothing_lands(project, monkeypatch):
    monkeypatch.setenv("PYTEST_XDIST_AUTO_NUM_WORKERS", "2")
    project.commit("a far test", files=FAR_TEST)
    base = project.sha("main")
    project.branch("topic/a", BREAKS_FAR, f"Task: {TICKET}", "Role: engineer")
    result, code = command.land(project.root, [f"{TICKET}=topic/a"], full=True)
    assert code == 3 and result["culprits"] == [TICKET] and result["reds"] == [f"{FAR}::test_far"]
    assert project.sha("main") == base and result["full"]["workers"] == 2
    held = json.loads((project.root / result["record"]).read_text(encoding="utf-8"))["result"]
    assert held["full"] == result["full"] and held["full"]["runs"]
    assert not (project.root / "docs" / "close" / "nightly").exists()


def test_a_green_full_run_lands_and_the_record_s_selection_says_full(project, monkeypatch):
    monkeypatch.setenv("PYTEST_XDIST_AUTO_NUM_WORKERS", "2")
    monkeypatch.setenv("GOV_HEAVY_CPUS", "0-1")
    project.commit("a far test", files=FAR_TEST)
    project.branch("topic/a", GREEN, f"Task: {TICKET}", "Role: engineer")
    result, code = command.land(project.root, [f"{TICKET}=topic/a"], full=True)
    assert code == 0 and result["landed"] == [TICKET]
    assert result["full"] == {"runs": result["runs"], "workers": 2, "cpus": "0-1"}
    ran = {r["name"]: r["passed"] for r in result["runs"]}
    assert ran == {"parallel": 4, "serial": 0, f"acceptance:{TICKET}": 1}  # W-2's, the three unit files; W-1's once
    front = yaml.safe_load(project.git("show", f"main:docs/close/{TICKET}/CL-{TICKET}.md").split("---")[1])
    assert front["selection"]["full"] is True and front["selection"]["suites"] == ["tests"]
    assert f"--ignore=tests/acceptance/{WBS}" in front["selection"]["pytest_options"]


# -- the after-step ---------------------------------------------------------------------------------------------

def test_after_a_landing_the_notices_are_in_the_answer_and_in_queue_json(project):
    base = project.sha("main")
    project.branch("topic/a", GREEN, f"Task: {TICKET}", "Role: engineer")
    result, code = command.land(project.root, [f"{TICKET}=topic/a"])
    assert code == 0
    after = result["after"]
    assert after["rebuild"] == "not_configured"
    assert after["structural"]["exit"] == 0 and after["structural"]["ok"] is True
    assert any(line.startswith(f"structural pass at {result['head'][:12]}") for line in after["structural"]["lines"])
    assert json.loads((project.root / result["record"]).read_text(encoding="utf-8"))["result"]["after"] == after
    assert project.sha("main") == result["head"] != base


def test_failing_after_steps_change_neither_the_exit_code_nor_the_landing(project, monkeypatch):
    from gov.check import structural
    from gov.rebuild import integration

    def no_store(root, branch):
        raise GovError("REBUILD_FAILED", "the store cannot be built", {})

    seen = []

    def no_pass(tree, base, timeout, out):
        seen.append((project.sha("main"), base))
        return 2

    monkeypatch.setattr(integration, "refresh", no_store)
    monkeypatch.setattr(structural, "run_structural", no_pass)
    base = project.sha("main")
    project.commit("a store", files={"governance/project/rebuild.yaml": f"integration_store: {project.root}-store\n"})
    base = project.sha("main")
    project.branch("topic/a", GREEN, f"Task: {TICKET}", "Role: engineer")
    result, code = command.land(project.root, [f"{TICKET}=topic/a"])
    assert code == 0 and result["landed"] == [TICKET] and project.sha("main") == result["head"]
    assert project.status_of(TICKET, "main") == "closed"
    assert result["after"]["rebuild"]["ok"] is False and "REBUILD_FAILED" in result["after"]["rebuild"]["reason"]
    assert result["after"]["structural"]["ok"] is False and result["after"]["structural"]["exit"] == 2
    assert seen == [(result["head"], base)], "the pass runs once, after the move, with the landing's base"


def test_a_landing_that_lands_nothing_has_no_after(project, monkeypatch):
    from gov.queue import after

    monkeypatch.setattr(after, "run", lambda *a, **k: pytest.fail("the after-step ran"))
    project.branch("topic/a", RED, f"Task: {TICKET}", "Role: engineer")
    result, code = command.land(project.root, [f"{TICKET}=topic/a"])
    assert code == 3 and "after" not in result
