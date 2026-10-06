"""Builder tests for ``gov pause`` (W1-28).

Regression evidence only (DEC-136). They cover what the acceptance tests leave
to the builder: an empty ``GOV_ROLE`` is a role, not the owner, and a commit
of the ticket made after a rollback is the only one a second rollback reverts.
For W1-50 (DEC-402, DEC-404): the read-back with the guard's reader, a write
that fails, the marker line, and a linked runtime folder for ``--off`` too;
a rollback whose reverts touch the flag's path ends frozen, with success or
with an error (DEC-378), and never says paused over a flag that is no freeze.
For DEC-409: the lift goes through ``command._lift_test`` with a planted ancestry and a pseudo-terminal; the command
itself refuses under the session that runs these tests; the chain read from ``/proc`` starts at this process.
Every project is a temporary git repository made here.
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
import threading
from argparse import Namespace
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov.cli.errors import GovError  # noqa: E402
from gov.guard.decide import freeze_state  # noqa: E402
from gov.pause import command  # noqa: E402

TICKET = "TST-a001"


def _git(root, *args):
    return subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, check=True).stdout


def _commit(root, rel, text):
    (root / rel).write_text(text, encoding="utf-8")
    _git(root, "add", "--", rel)
    _git(root, "commit", "-q", "-m", f"change {rel}", "--trailer", f"Task: {TICKET}")
    return _git(root, "rev-parse", "HEAD").strip()


@pytest.fixture
def project(tmp_path, monkeypatch):
    assert REPO not in (tmp_path, *tmp_path.parents)
    monkeypatch.delenv("GOV_ROLE", raising=False)
    fake_home = tmp_path / "home"
    fake_home.mkdir()
    monkeypatch.setenv("HOME", str(fake_home))
    _git(tmp_path, "init", "-q")
    for key, value in (("user.name", "builder test"), ("user.email", "builder@example.invalid"),
                       ("commit.gpgsign", "false")):
        _git(tmp_path, "config", key, value)
    (tmp_path / ".tickets").mkdir()
    (tmp_path / ".gitignore").write_text(".gov-runtime/\nhome/\n", encoding="utf-8")
    (tmp_path / ".tickets" / f"{TICKET}.md").write_text(f"---\nid: {TICKET}\nstatus: in_progress\n---\n# A ticket\n",
                                                        encoding="utf-8")
    _git(tmp_path, "add", "--", ".gitignore", ".tickets")
    _git(tmp_path, "commit", "-q", "-m", "a project")
    return tmp_path


def _pause(root, **options):
    return command.run(root, Namespace(**{"off": False, "cancel_agents": False, "rollback": None, **options}), {})


SHELL = {"pid": 40, "ppid": 1, "comm": "bash", "exe": "/usr/bin/bash", "cmdline": ["-bash"]}
FIRST = {"pid": 1, "ppid": 0, "comm": "systemd", "exe": None, "cmdline": ["/sbin/init"]}
SESSION = {"pid": 30, "ppid": 40, "comm": "claude", "exe": None, "cmdline": ["claude", "-p", "x"]}


def _lift(root, ancestry=(SHELL, FIRST), reply=lambda code: code):
    """``command._lift_test`` on a pseudo-terminal; what is typed back is ``reply`` of the shown code."""
    master, slave = os.openpty()

    def typist():
        shown = b""
        try:
            while not (found := re.search(rb"LIFT-\d{4}", shown)):
                shown += os.read(master, 1024)
            os.write(master, reply(found.group(0)) + b"\n")
        except OSError:  # the lift ended before it showed a code
            pass

    threading.Thread(target=typist, daemon=True).start()
    try:
        return command._lift_test(root, ancestry=list(ancestry), terminal=(slave, slave))
    finally:
        os.close(slave)
        os.close(master)


@pytest.mark.parametrize("options", ({}, {"off": True}, {"cancel_agents": True}, {"rollback": TICKET}))
def test_an_empty_gov_role_is_refused_and_sets_nothing(project, monkeypatch, options):
    monkeypatch.setenv("GOV_ROLE", "")
    with pytest.raises(GovError) as refusal:
        _pause(project, **options)
    assert refusal.value.code == "PAUSE_REFUSED" and not (project / ".gov-runtime").exists()


def test_a_flag_the_guard_does_not_read_as_a_freeze_ends_in_an_error_not_paused(project, monkeypatch):
    monkeypatch.setattr("gov.guard.decide.freeze_state", lambda root: "unmarked")
    with pytest.raises(GovError) as refusal:
        _pause(project)
    assert refusal.value.code == "PAUSE_NOT_SET" and ".gov-runtime/freeze" in refusal.value.message


def test_a_write_that_fails_ends_in_an_error_and_leaves_no_temporary_file(project, monkeypatch):
    def fails(source, target):
        raise OSError("no rename today")
    monkeypatch.setattr(command.os, "replace", fails)
    with pytest.raises(GovError) as refusal:
        _pause(project)
    assert refusal.value.code == "PAUSE_NOT_SET" and os.listdir(project / ".gov-runtime") == []


def test_the_flag_is_one_marker_line_and_a_lifted_pause_removes_it(project, monkeypatch):
    monkeypatch.setenv("GOV_ROLE", "orchestrator")
    assert _pause(project) == {"paused": True}
    flag = project / ".gov-runtime" / "freeze"
    assert re.fullmatch(r"FROZEN orchestrator \d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ\n", flag.read_text(encoding="utf-8"))
    assert freeze_state(str(project)) == "frozen" and os.listdir(flag.parent) == ["freeze"]
    monkeypatch.delenv("GOV_ROLE")
    assert _lift(project) == {"paused": False} and freeze_state(str(project)) == "absent"


@pytest.mark.parametrize("off", (False, True), ids=("set", "off"))
def test_a_linked_runtime_folder_is_refused_and_nothing_is_written_or_removed(project, tmp_path_factory, off):
    elsewhere = tmp_path_factory.mktemp("elsewhere")
    (elsewhere / "freeze").write_text("FROZEN owner 2026-10-05T00:00:00Z\n", encoding="utf-8")
    (project / ".gov-runtime").symlink_to(elsewhere, target_is_directory=True)
    with pytest.raises(GovError) as refusal:
        _lift(project) if off else _pause(project)
    assert refusal.value.code == "PAUSE_RUNTIME_LINKED" and ".gov-runtime" in refusal.value.message
    assert os.listdir(elsewhere) == ["freeze"] and (project / ".gov-runtime").is_symlink()


def _frozen(project):
    flag = project / ".gov-runtime" / "freeze"
    flag.parent.mkdir()
    flag.write_text("FROZEN owner 2026-10-05T00:00:00Z\n", encoding="utf-8")
    return flag


def test_the_command_refuses_the_lift_under_the_session_that_runs_these_tests(project):
    """``run`` hands ``lift`` the project alone: the real chain (a session, or a sandbox's own first process) and
    the real descriptors refuse."""
    flag = _frozen(project)
    with pytest.raises(GovError) as refusal:
        _pause(project, off=True)
    assert refusal.value.code == "PAUSE_REFUSED" and flag.is_file()


@pytest.mark.parametrize("ancestry, reply, reason", [
    ((SHELL, SESSION | {"pid": 1, "ppid": 0}), bytes, "session"),
    ((SHELL,), bytes, "ancestry"),
    ((SHELL | {"cmdline": []}, FIRST), bytes, "ancestry"),      # a kernel thread, or a process that ended
    ((SHELL, FIRST | {"comm": "3"}), bytes, "ancestry"),        # a sandbox's own first process
    (("bash", FIRST), bytes, "ancestry"),
    ((SHELL, FIRST), lambda code: b"LIFT-" + code[:4], "code"),
], ids=("session", "short", "no-command-line", "sandbox", "malformed", "wrong-code"))
def test_a_lift_that_is_not_the_owner_in_person_is_refused_and_the_flag_stays(project, ancestry, reply, reason):
    flag = _frozen(project)
    with pytest.raises(GovError) as refusal:
        _lift(project, ancestry, reply)
    assert (refusal.value.code, refusal.value.details) == ("PAUSE_REFUSED", {"reason": reason})
    assert flag.read_text(encoding="utf-8").startswith("FROZEN owner") and os.listdir(flag.parent) == ["freeze"]


def test_a_chain_as_a_plain_terminal_of_this_machine_shows_it_lifts(project):
    """Processes whose ``exe`` cannot be read and whose command line is ``/init``, and an editor's ``node`` and
    ``sh``, are no session; a project folder named after Claude in the command's own options is none either."""
    names = ("python3", "bash", "node", "sh", "Relay(963)", "SessionLeader", "init-systemd(Ub", "systemd")
    chain = [{"pid": 100 - number, "ppid": 99 - number, "comm": name, "exe": None, "cmdline": ["/init"]}
             for number, name in enumerate(names)]
    chain[0]["cmdline"] = ["python3", "-m", "gov.cli.main", "pause", "--off", "--root", "/home/owner/claude-code"]
    chain[-1].update(pid=1, ppid=0)
    chain[-2]["ppid"] = 1
    _frozen(project)
    assert _lift(project, chain) == {"paused": False} and freeze_state(str(project)) == "absent"


def test_a_pipe_is_no_terminal_and_no_code_is_shown(project):
    flag, (source, shown) = _frozen(project), os.pipe()
    with pytest.raises(GovError) as refusal:
        command._lift_test(project, ancestry=[SHELL, FIRST], terminal=(source, shown))
    os.close(shown)
    assert refusal.value.details == {"reason": "terminal"} and os.read(source, 64) == b"" and flag.is_file()
    os.close(source)


def test_the_chain_read_from_proc_is_this_process_first_and_each_next_one_its_parent():
    chain = command.read_ancestry()
    assert chain[0]["pid"] == os.getpid() and chain[0]["ppid"] == os.getppid()
    assert chain[0]["exe"] == os.path.realpath(sys.executable) and "pytest" in " ".join(chain[0]["cmdline"])
    assert all(process["ppid"] == parent["pid"] for process, parent in zip(chain, chain[1:]))
    assert (chain[-1]["pid"], chain[-1]["ppid"]) == (1, 0) and all(process["comm"] for process in chain)


def test_a_second_rollback_reverts_only_what_was_committed_since_the_first(project):
    first = _commit(project, "a.txt", "a\n")
    assert _pause(project, rollback=TICKET)["reverted"] == [first]
    second = _commit(project, "b.txt", "b\n")
    assert _pause(project, rollback=TICKET)["reverted"] == [second]
    assert not (project / "a.txt").exists() and not (project / "b.txt").exists()
    assert _git(project, "status", "--porcelain") == "" and (project / ".gov-runtime" / "freeze").is_file()


def _flag_added_and_removed_by_the_ticket(root):
    """Two commits of the ticket: one force-adds an empty file at the flag's path, the next removes it."""
    flag = root / ".gov-runtime" / "freeze"
    flag.parent.mkdir()
    flag.write_text("", encoding="utf-8")
    _git(root, "add", "--force", "--", ".gov-runtime/freeze")
    _git(root, "commit", "-q", "-m", "the flag added", "--trailer", f"Task: {TICKET}")
    _git(root, "rm", "-q", "--", ".gov-runtime/freeze")
    _git(root, "commit", "-q", "-m", "the flag removed", "--trailer", f"Task: {TICKET}")
    assert not flag.exists()
    return flag


def _assert_frozen(root, flag):
    assert flag.is_file() and not flag.is_symlink() and freeze_state(str(root)) == "frozen"
    assert re.fullmatch(r"FROZEN owner \d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ\n", flag.read_text(encoding="utf-8"))


def test_a_rollback_whose_reverts_remove_the_flag_ends_frozen(project):
    flag = _flag_added_and_removed_by_the_ticket(project)
    result = _pause(project, rollback=TICKET)
    assert result["paused"] is True and len(result["reverted"]) == 2
    _assert_frozen(project, flag)


def test_a_rollback_that_aborts_after_its_reverts_removed_the_flag_ends_frozen(project):
    _commit(project, "a.txt", "a\n")  # of the ticket, and not revertible: the next commit changes the same line
    (project / "a.txt").write_text("b\n", encoding="utf-8")
    _git(project, "commit", "-q", "-m", "another change", "--", "a.txt")
    flag, start = _flag_added_and_removed_by_the_ticket(project), _git(project, "rev-parse", "HEAD")
    with pytest.raises(GovError) as refusal:
        _pause(project, rollback=TICKET)
    assert refusal.value.code == "PAUSE_ROLLBACK_ABORTED" and _git(project, "rev-parse", "HEAD") == start
    _assert_frozen(project, flag)


def test_a_rollback_whose_flag_is_no_freeze_at_its_end_ends_in_an_error_not_paused(project, monkeypatch):
    states = iter(("frozen", "unmarked"))  # the read-back before the reverts, then the one after them
    monkeypatch.setattr("gov.guard.decide.freeze_state", lambda root: next(states))
    _commit(project, "a.txt", "a\n")
    with pytest.raises(GovError) as refusal:
        _pause(project, rollback=TICKET)
    assert refusal.value.code == "PAUSE_NOT_SET"
