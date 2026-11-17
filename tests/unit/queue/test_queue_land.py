"""``gov queue`` on planted projects (W2-115b): the green landing, the red that moves nothing, a refusal, the
settings and the head that moved during the run."""
from __future__ import annotations

import json
import os
import subprocess
import sys

import pytest
import yaml

from gov.cli.errors import GovError
from gov.close import batch
from gov.queue import command

from queue_support import OTHER, OTHER_WBS, REPO_ROOT, TICKET, WBS

GREEN = {"src/pkg/feature.py": "def twice(x):\n    return 2 * x\n"}
RED = {"src/pkg/feature.py": "def twice(x):\n    return 2 * x + 1\n"}


def _close_front(project, ticket, rev="main"):
    text = project.git("show", f"{rev}:docs/close/{ticket}/CL-{ticket}.md")
    return yaml.safe_load(text.split("---")[1])


def _paths(project, commit):
    return project.git("diff-tree", "--no-commit-id", "--name-only", "-r", commit).split()


def test_a_green_ticket_lands_through_its_close_commit(project):
    base = project.sha("main")
    tip = project.branch("topic/a", GREEN, f"Task: {TICKET}", "Role: engineer")
    project.git("checkout", "-q", "topic/a")
    project.commit("slip", "Role: engineer", files={"src/pkg/other.py": "def other():\n    return 1  # a\n"})
    tip = project.sha()
    project.git("checkout", "-q", "main")
    result, code = command.land(project.root, [f"{TICKET}=topic/a"])
    assert code == 0 and result["landed"] == [TICKET] and result["culprits"] == []
    head, tested = project.sha("main"), result["tested"]
    assert result["head"] == head and result["base"] == base
    assert project.git("rev-list", "--parents", "-n", "1", tested).split()[1:] == [base, tip]
    assert project.git("rev-list", "--parents", "-n", "1", head).split()[1:] == [tested]
    assert set(_paths(project, head)) <= {f".tickets/{TICKET}.md", f"docs/close/{TICKET}/CL-{TICKET}.md"} | {
        p for p in _paths(project, head) if p.startswith(f"docs/checkpoints/{TICKET}/")}
    assert f"Task: {TICKET}" in project.git("log", "-1", "--format=%B", head)
    assert result["closes"] == [{"ticket": TICKET, "close_record": f"docs/close/{TICKET}/CL-{TICKET}.md",
                                 "commit": head}]
    assert project.status_of(TICKET, "main") == "closed"
    assert "tests/unit/test_other.py" in result["selection"]["suites"]
    assert "tests/unit/test_lonely.py" not in result["selection"]["suites"]
    front = _close_front(project, TICKET)
    assert front["close"] == "queue" and front["commit"] == tested and front["base"] == base
    assert front["runs"] == result["runs"] and front["queue"] == result["record"]
    assert front["branch"] == {"name": "topic/a", "tip": tip} and front["onto"] == "main"
    assert (project.root / "docs" / "close" / TICKET).is_dir()  # the root's tree follows the branch
    assert project.git("status", "--porcelain") == ""
    record = json.loads((project.root / result["record"]).read_text())
    assert record["result"] == result
    seconds = result["seconds"]
    assert all(seconds[k] >= 0 for k in ("merge", "selection", "run", "close", "total"))
    assert seconds["total"] >= max(seconds[k] for k in ("merge", "selection", "run", "close"))


def test_a_red_ticket_moves_nothing(project):
    base = project.sha("main")
    tip = project.branch("topic/a", RED, f"Task: {TICKET}", "Role: engineer")
    result, code = command.land(project.root, [f"{TICKET}=topic/a"])
    assert code == 3 and result["landed"] == [] and result["culprits"] == [TICKET]
    assert result["reds"] == [f"tests/acceptance/{WBS}/test_w1.py::test_twice"]
    assert project.sha("main") == base and project.sha("topic/a") == tip and result["head"] is None
    assert project.status_of(TICKET, "main") == "open"


def test_of_two_the_culprit_goes_back_and_the_other_lands(project):
    base = project.sha("main")
    project.branch("topic/a", GREEN, f"Task: {TICKET}", "Role: engineer")
    project.branch("topic/b", {"src/pkg/gadget.py": "def gadget():\n    return 2\n"}, f"Task: {OTHER}",
                   "Role: engineer")
    result, code = command.land(project.root, [f"{TICKET}=topic/a", f"{OTHER}=topic/b"])
    assert code == 3 and result["landed"] == [TICKET] and result["culprits"] == [OTHER]
    front = _close_front(project, TICKET)
    assert front["culprits"] == [OTHER]
    assert project.git("rev-list", "--parents", "-n", "1", front["commit"]).split()[1:] == [
        base, project.sha("topic/a")]
    assert project.status_of(OTHER, "main") == "open" and project.status_of(TICKET, "main") == "closed"


def test_a_ticket_refused_by_g1_alone_moves_nothing(project):
    base = project.sha("main")
    tip = project.branch("topic/a", {f"tests/acceptance/{WBS}/test_w1.py": "def test_twice():\n    pass\n"},
                         f"Task: {TICKET}", "Role: engineer")
    result, code = command.land(project.root, [f"{TICKET}=topic/a"])
    assert code == 3 and result["landed"] == [] and result["tested"] is None
    assert result["refused"] == [{"ticket": TICKET, "code": "TEST_AUTHOR_REFUSED",
                                  "reason": result["refused"][0]["reason"], "commits": [tip]}]
    assert project.sha("main") == base


def test_a_path_outside_the_allowed_paths_is_listed_and_the_ticket_lands(project):
    project.branch("topic/a", {**GREEN, "src/pkg/lonely.py": "VALUE = 1  # x\n"}, f"Task: {TICKET}",
                   "Role: engineer")
    result, code = command.land(project.root, [f"{TICKET}=topic/a"])
    assert code == 0
    tip = project.sha("topic/a")
    assert result["path_notices"] == [{"ticket": TICKET, "commit": tip, "path": "src/pkg/lonely.py"}]
    assert _close_front(project, TICKET)["path_notices"] == result["path_notices"]


def test_queue_yaml_names_the_integration_and_the_work_branch(project):
    project.commit("queue settings", files={"governance/project/queue.yaml":
                                           "integration: main\nwork_branch: \"feature/{wbs}\"\n"})
    project.branch(f"feature/{WBS}", GREEN, f"Task: {TICKET}", "Role: engineer")
    project.git("checkout", "-q", "--detach")
    result, code = command.land(project.root, [TICKET])
    assert code == 0 and result["onto"] == "main" and project.status_of(TICKET, "main") == "closed"


def test_a_detached_root_without_settings_is_integration_unknown(project):
    project.branch("topic/a", GREEN, f"Task: {TICKET}")
    project.git("checkout", "-q", "--detach")
    with pytest.raises(GovError) as raised:
        command.land(project.root, [f"{TICKET}=topic/a"])
    assert raised.value.code == "INTEGRATION_UNKNOWN" and raised.value.exit_code == 1


@pytest.mark.parametrize("given", [TICKET, f"{TICKET}=nowhere"])
def test_a_ticket_without_a_work_branch_is_branch_unknown(project, given):
    with pytest.raises(GovError) as raised:
        command.land(project.root, [given])
    assert raised.value.code == "BRANCH_UNKNOWN"


def test_an_unknown_or_closed_ticket_is_refused(project):
    project.branch("topic/a", GREEN)
    with pytest.raises(GovError) as raised:
        command.land(project.root, ["T-zzzz=topic/a"])
    assert raised.value.code == "TICKET_UNKNOWN"
    project.commit("closed", files={f".tickets/{TICKET}.md": project.git("show", f"main:.tickets/{TICKET}.md")
                                    .replace("status: open", "status: closed")})
    with pytest.raises(GovError) as raised:
        command.land(project.root, [f"{TICKET}=topic/a"])
    assert raised.value.code == "TICKET_CLOSED"


def test_a_head_moved_during_the_run_is_head_moved_and_stays_as_moved(project, monkeypatch):
    project.branch("topic/a", GREEN, f"Task: {TICKET}", "Role: engineer")
    real = batch.isolate

    def moving(*args, **kwargs):
        out = real(*args, **kwargs)
        project.commit("meanwhile")
        return out

    monkeypatch.setattr(batch, "isolate", moving)
    with pytest.raises(GovError) as raised:
        command.land(project.root, [f"{TICKET}=topic/a"])
    assert raised.value.code == "HEAD_MOVED" and raised.value.exit_code == 3
    assert project.git("log", "-1", "--format=%s", "main").strip() == "meanwhile"
    assert project.status_of(TICKET, "main") == "open"


def test_the_command_prints_the_envelope(project):
    project.branch("topic/a", GREEN, f"Task: {TICKET}", "Role: engineer")
    env = {**os.environ, "PYTHONPATH": str(REPO_ROOT / "src")}
    done = subprocess.run([sys.executable, "-m", "gov.cli.main", "queue", f"{TICKET}=topic/a", "--root",
                           str(project.root), "--json"], capture_output=True, text=True, env=env)
    envelope = json.loads(done.stdout)
    assert done.returncode == 0, done.stderr
    assert envelope["ok"] and envelope["command"] == "queue" and envelope["result"]["landed"] == [TICKET]
