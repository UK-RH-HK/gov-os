"""W2-56 S1 (round 2, the CTO's item 3): where a ``gov`` process a test session starts lands its daemon folder.

The shape of W1-27's rebuild cases (D-2): a case makes a repository under its pytest temp folder and starts a ``gov``
process whose environment is built anew with a ``TMPDIR`` of its own, so neither ``CODEINTEL_DAEMON_BASE`` nor
``CLAUDE_CODE_TMPDIR`` reaches it; the case's own clean-up, in the session's process, removes ``daemon_dir(repo)`` as
that process sees it. Before round 2 the nested process fell back to ``/tmp/gov-cbm-<uid>`` and the clean-up looked in
the session's folder: the shared folder was left. The nested process now finds the session's folder from the mark the
conftest writes in each process's pytest temp base. The binary is never run: a stand-in on ``PATH`` records the
runtime folder it is given. Nothing is written to ``/tmp/gov-cbm-<uid>``.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov import codeintel  # noqa: E402

SHARED = Path(f"/tmp/gov-cbm-{os.getuid()}")
STAND_IN = ("#!/bin/sh\n"
            "here=$(dirname \"$0\")\n"
            "echo \"$1|$CBM_RUNTIME_DIR\" >> \"$here/calls.txt\"\n"
            "cat \"$here/answer.json\"\n")
# The nested process: what it sees as its daemon folder, then one call of the tool (which makes that folder).
NESTED = ("import json, sys\n"
          "from pathlib import Path\n"
          "from gov import codeintel\n"
          "root = Path(sys.argv[1])\n"
          "seen = str(codeintel.daemon_dir(root))\n"
          "codeintel.projects(root)\n"
          "print(json.dumps({'seen': seen}))\n")


def _repository(root: Path) -> Path:
    root.mkdir(parents=True)
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    (root / "a.py").write_text("def a():\n    return 1\n", encoding="utf-8")
    return root


def _tools(tmp_path: Path) -> Path:
    tools = tmp_path / "tools"
    tools.mkdir()
    (tools / codeintel.TOOL).write_text(STAND_IN, encoding="utf-8")
    (tools / codeintel.TOOL).chmod(0o755)
    (tools / "answer.json").write_text(json.dumps(
        {"isError": False, "content": [{"type": "text", "text": "{\"projects\": []}"}]}), encoding="utf-8")
    return tools


def _nested(tmp_path: Path, root: Path, tools: Path) -> dict:
    """Start a ``gov`` process on ``root`` with an environment built anew: PATH (the stand-in first), HOME,
    PYTHONPATH and a TMPDIR of its own; no CODEINTEL_DAEMON_BASE, no CLAUDE_CODE_TMPDIR."""
    own_tmp = tmp_path / "own-tmp"
    own_tmp.mkdir(exist_ok=True)
    env = {"PATH": f"{tools}{os.pathsep}{os.environ['PATH']}", "HOME": os.environ.get("HOME", "/"),
           "PYTHONPATH": str(REPO / "src"), "TMPDIR": str(own_tmp)}
    done = subprocess.run([sys.executable, "-c", NESTED, str(root)], capture_output=True, text=True, env=env,
                          timeout=120)
    assert done.returncode == 0, done.stderr[-2000:]
    calls = (tools / "calls.txt").read_text(encoding="utf-8").splitlines()
    return {"seen": json.loads(done.stdout)["seen"], "runtime": {line.split("|", 1)[1] for line in calls}}


def _hash(root: Path) -> str:
    return hashlib.sha256(os.fsencode(root.resolve())).hexdigest()[:16]


def test_a_nested_gov_process_with_an_environment_built_anew_lands_in_the_sessions_folder(tmp_path):
    """The real wiring: the conftest's mark in this process's temp base names this session's folder; a nested process
    started on a repository in this case's folder lands its daemon folder there, never in the shared place, and the
    clean-up this process makes (``daemon_dir`` with the variable set) finds that same folder."""
    session = Path(os.environ[codeintel.BASE_ENV])
    root = _repository(tmp_path / "repo")
    got = _nested(tmp_path, root, _tools(tmp_path))
    landed = session / _hash(root)
    assert got["seen"] == str(landed) and got["runtime"] == {str(landed)}
    assert landed.is_dir() and not (SHARED / _hash(root)).exists()
    assert codeintel.daemon_dir(root) == landed  # where the case's clean-up, in this process, looks
    landed.rmdir()


def test_a_nested_process_takes_the_nearest_mark_above_the_repository(tmp_path):
    base = tmp_path / "base"
    base.mkdir()
    named = tmp_path / "s"
    codeintel.write_mark(base, named)
    root = _repository(base / "case" / "repo")
    got = _nested(tmp_path, root, _tools(tmp_path))
    assert got["seen"] == str(named / _hash(root)) and (named / _hash(root)).is_dir()


def test_a_mark_this_process_wrote_is_not_followed_here(tmp_path, monkeypatch):
    """A case that removes the variable in the session's own process asks for the place outside a test session."""
    monkeypatch.delenv(codeintel.BASE_ENV, raising=False)
    monkeypatch.delenv(codeintel.LAUNCH_TMP_ENV, raising=False)
    monkeypatch.setattr(codeintel, "DAEMON_BASE", tmp_path / "daemons")
    codeintel.write_mark(tmp_path, tmp_path / "s")
    assert codeintel.marked_base(tmp_path / "repo") is None
    assert codeintel.daemon_dir(tmp_path / "repo").parent == tmp_path / "daemons"


@pytest.mark.parametrize("planted", ("link", "folder", "not-json", "relative", "no-base"))
def test_a_mark_that_is_no_users_regular_file_naming_an_absolute_folder_is_not_followed(tmp_path, planted):
    mark = tmp_path / codeintel.MARK
    good = json.dumps({"base": str(tmp_path / "s"), "pid": os.getpid() + 1})
    if planted == "link":
        (tmp_path / "elsewhere").write_text(good, encoding="utf-8")
        mark.symlink_to(tmp_path / "elsewhere")
    elif planted == "folder":
        mark.mkdir()
    else:
        mark.write_text({"not-json": "{", "relative": json.dumps({"base": "s", "pid": 0}),
                         "no-base": json.dumps({"pid": 0})}[planted], encoding="utf-8")
    assert codeintel.marked_base(tmp_path / "deeper" / "repo") is None


def test_the_variable_and_a_launched_sessions_folder_come_before_a_mark(tmp_path, monkeypatch):
    """S1: inside a launched session the daemon folder is under the session's own temp folder, mark or none."""
    mark = tmp_path / codeintel.MARK
    mark.write_text(json.dumps({"base": str(tmp_path / "marked"), "pid": os.getpid() + 1}), encoding="utf-8")
    monkeypatch.setenv(codeintel.BASE_ENV, str(tmp_path / "given"))
    monkeypatch.setenv(codeintel.LAUNCH_TMP_ENV, "/tmp/gov-launch-abcd1234/claude-1000")
    assert codeintel.daemon_dir(tmp_path / "repo").parent == tmp_path / "given"
    monkeypatch.delenv(codeintel.BASE_ENV)
    assert codeintel.daemon_dir(tmp_path / "repo").parent == Path("/tmp/gov-launch-abcd1234") / codeintel.LAUNCH_SUB
    monkeypatch.delenv(codeintel.LAUNCH_TMP_ENV)
    assert codeintel.daemon_dir(tmp_path / "repo").parent == tmp_path / "marked"


def test_the_running_suite_wrote_its_mark_in_its_temp_base(tmp_path_factory):
    """W2-56 S1, through tests/conftest.py: the mark names this session's folder and this process."""
    mark = tmp_path_factory.getbasetemp() / codeintel.MARK
    named = json.loads(mark.read_text(encoding="utf-8"))
    assert named == {"base": os.environ[codeintel.BASE_ENV], "pid": os.getpid()}


def test_a_folder_made_for_a_tool_that_cannot_be_started_is_not_left(tmp_path, monkeypatch):
    monkeypatch.delenv(codeintel.BASE_ENV, raising=False)
    monkeypatch.delenv(codeintel.LAUNCH_TMP_ENV, raising=False)
    monkeypatch.setattr(codeintel, "DAEMON_BASE", tmp_path / "daemons")
    root = _repository(tmp_path / "repo")
    empty = tmp_path / "no-tool"
    empty.mkdir()
    git = Path(subprocess.run(["sh", "-c", "command -v git"], capture_output=True, text=True).stdout.strip())
    (empty / "git").symlink_to(git)
    monkeypatch.setenv("PATH", str(empty))
    with pytest.raises(OSError):
        codeintel.projects(root)
    assert not codeintel.daemon_dir(root).exists()
    existing = codeintel.daemon_dir(root)
    existing.mkdir()  # a folder there before the call is the tool's own: kept
    with pytest.raises(OSError):
        codeintel.projects(root)
    assert existing.is_dir()
