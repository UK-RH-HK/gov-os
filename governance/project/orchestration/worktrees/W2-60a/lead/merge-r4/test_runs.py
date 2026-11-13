"""Builder tests for the session's own folder in the launcher (W2-50, DEC-728, DEC-743 R2).

Regression evidence only (DEC-136). No CLI is started: ``subprocess.Popen`` is
replaced, HOME and the project are temporary; the real ``~/gov-os-runs`` is
never named.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov.guard import runs  # noqa: E402
from gov.launch import launcher  # noqa: E402

TICKET = "---\nid: TST-a001\nstatus: in_progress\nexternal-ref: W2-90\nrole: engineer\nallowed_paths:\n- src/**\n---\n"

# The engineer's role file each launch reads (W2-60a, DEC-826 Q1): its version and default lines, nothing else.
ROLE = "# engineer\n\n- **Version:** 1.0.0\n- **Launch default:** model claude-opus-5-5, effort high\n"


def _role_file(project):
    path = project / "template" / "governance" / "kernel" / "roles" / "engineer.md"
    path.parent.mkdir(parents=True)
    path.write_text(ROLE, encoding="utf-8")


def _plant_template(project: Path, role: str = "engineer") -> None:
    """The role's template copy every session starts with (W2-153 S1, DEC-1112 (3))."""
    path = project / launcher.TEMPLATES_REL / f"{launcher.ROLE_TEMPLATES[role]}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"# {role}\n", encoding="utf-8")


def _open_gate(home: Path, monkeypatch) -> None:
    """An open resource gate under this HOME (W2-20 S19: every launch runs the start check): the gate file and its
    readings planted, nothing of the real machine's gate read."""
    from gov.resources import config as gate_config
    folder = home / ".gov-os" / "machine"
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "gate.json").write_text(json.dumps(gate_config.template(cpus=list(range(20)))), encoding="utf-8")
    (folder / "meminfo").write_text("MemAvailable: 67108864 kB\n", encoding="utf-8")
    (folder / "loadavg").write_text("0.1 0.1 0.1 1/1 1\n", encoding="utf-8")
    for name, value in (("GOV_RESOURCES_MEMINFO", folder / "meminfo"), ("GOV_RESOURCES_LOADAVG", folder / "loadavg"),
                        ("GOV_RESOURCES_NPROC", 20), ("GOV_RESOURCES_BUSY_CORES", 0),
                        ("GOV_RESOURCES_EMBEDDING_CPU", '{"shared": 0, "query": 0}'),
                        ("GOV_RESOURCES_EMBEDDING_CPU_NOW", '{"shared": 0, "query": 0}'),
                        ("GOV_RESOURCES_DISK", '{"free_bytes": 1000000000000000, "free_inodes": 1000000000}')):
        monkeypatch.setenv(name, str(value))


def _places(allow):
    """The write list less the reranker's log (W2-56 S11, D-11 (a)), which every worker's list ends with."""
    assert allow[-1].endswith("/.cache/gov-os/rerank.log"), allow
    return allow[:-1]


@pytest.fixture
def started(tmp_path, monkeypatch):
    """``started()`` launches an engineer on TST-a001 and returns the settings and what the session found."""
    home, temp, project = tmp_path / "home", tmp_path / "temp", tmp_path / "project"
    for folder in (home / ".local" / "bin", temp, project / ".tickets", project / ".git"):
        folder.mkdir(parents=True)
    (home / launcher.CLI_REL).write_text("", encoding="utf-8")
    (project / ".tickets" / "TST-a001.md").write_text(TICKET, encoding="utf-8")
    _role_file(project)
    _plant_template(project)
    monkeypatch.setenv("HOME", str(home))
    _open_gate(home, monkeypatch)
    monkeypatch.setattr(launcher.tempfile, "tempdir", str(temp))
    monkeypatch.setattr(launcher, "_check_repository_settings", lambda *args: None)
    found = {}

    class Session:
        def __init__(self, argv, cwd, env):
            found["settings"] = json.loads(argv[argv.index("--settings") + 1])
            found["root"] = sorted(os.listdir(home / runs.ROOT_NAME)) if (home / runs.ROOT_NAME).is_dir() else None

        def wait(self):
            return 0

        def poll(self):
            return 0

    monkeypatch.setattr(launcher.subprocess, "Popen", Session)

    def _started():
        assert launcher.launch(project, "engineer", "TST-a001", []) == 0
        return found

    _started.root = home / runs.ROOT_NAME
    return _started


def test_the_own_folder_is_made_and_added_to_the_write_list(started):
    found = started()
    own = os.path.join(os.path.realpath(started.root), "W2-90")
    assert found["root"] == ["W2-90"]
    assert f"/{own}" in found["settings"]["sandbox"]["filesystem"]["allowWrite"]
    assert len(_places(found["settings"]["sandbox"]["filesystem"]["allowWrite"])) == 2
    assert os.path.isdir(own)  # the launcher never removes it
    assert os.listdir(own) == [runs.MARKER]
    allow = _places(started()["settings"]["sandbox"]["filesystem"]["allowWrite"])  # a later launch keeps the folder
    assert len(allow) == 2 and allow[1] == f"/{own}"
    assert os.listdir(own) == [runs.MARKER]


@pytest.mark.parametrize("content", ((), ("work.txt",)))
def test_a_folder_already_there_is_neither_marked_nor_added(started, content):
    """DEC-751 1: the launcher marks only a folder it has just made."""
    (started.root / "W2-90").mkdir(parents=True)
    for name in content:
        (started.root / "W2-90" / name).write_text("x", encoding="utf-8")
    allow = _places(started()["settings"]["sandbox"]["filesystem"]["allowWrite"])
    assert len(allow) == 1 and "W2-90" not in allow[0]
    assert sorted(os.listdir(started.root / "W2-90")) == list(content)


def test_a_name_two_tickets_give_is_neither_made_nor_added(started, tmp_path):
    (tmp_path / "project" / ".tickets" / "TST-a002.md").write_text(
        TICKET.replace("TST-a001", "TST-a002").replace("in_progress", "closed"), encoding="utf-8")
    allow = _places(started()["settings"]["sandbox"]["filesystem"]["allowWrite"])
    assert len(allow) == 1 and "W2-90" not in allow[0]
    assert not os.path.lexists(started.root / "W2-90")


def test_a_project_under_the_root_gets_no_folder_made_or_added(tmp_path, monkeypatch):
    """DEC-758 1 (F2): a launch from a project in the root makes nothing there and adds only its temp folder."""
    home, temp = tmp_path / "home", tmp_path / "temp"
    project = home / runs.ROOT_NAME / "TST-a002" / "clone"
    for folder in (home / ".local" / "bin", temp, project / ".tickets", project / ".git"):
        folder.mkdir(parents=True)
    (home / launcher.CLI_REL).write_text("", encoding="utf-8")
    (project / ".tickets" / "TST-a001.md").write_text(TICKET, encoding="utf-8")
    _role_file(project)
    _plant_template(project)
    monkeypatch.setenv("HOME", str(home))
    _open_gate(home, monkeypatch)
    monkeypatch.setattr(launcher.tempfile, "tempdir", str(temp))
    monkeypatch.setattr(launcher, "_check_repository_settings", lambda *args: None)
    found = {}

    class Session:
        def __init__(self, argv, cwd, env):
            found["allow"] = json.loads(argv[argv.index("--settings") + 1])["sandbox"]["filesystem"]["allowWrite"]

        def wait(self):
            return 0

        def poll(self):
            return 0

    monkeypatch.setattr(launcher.subprocess, "Popen", Session)
    assert launcher.launch(project, "engineer", "TST-a001", []) == 0
    assert len(_places(found["allow"])) == 1 and runs.ROOT_NAME not in found["allow"][0]
    assert sorted(os.listdir(home / runs.ROOT_NAME)) == ["TST-a002"]


def test_an_own_folder_that_is_a_link_is_not_opened(started, tmp_path):
    (tmp_path / "elsewhere").mkdir()
    started.root.mkdir()
    (started.root / "W2-90").symlink_to(tmp_path / "elsewhere", target_is_directory=True)
    allow = _places(started()["settings"]["sandbox"]["filesystem"]["allowWrite"])
    assert len(allow) == 1 and "W2-90" not in allow[0]
