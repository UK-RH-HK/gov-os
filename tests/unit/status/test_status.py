"""Builder tests for ``gov status`` (W1-32). Regression evidence only (DEC-136).

They cover what the acceptance tests leave to the builder: no path of the command turns "could not read" into a
clean answer (DEC-449, DEC-454). Every project is a temporary directory made from scratch, and ``HOME`` is
temporary, so no freeze mirror and no session log of this machine is read.
"""
from __future__ import annotations

import argparse
import os
import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov import store  # noqa: E402
from gov.cli.errors import GovError  # noqa: E402
from gov.guard.decide import FREEZE_FLAG  # noqa: E402
from gov.status import command  # noqa: E402

ARGS = argparse.Namespace(json=True)
PARTS = ("tickets", "decision_packages", "readiness", "governance_share", "pause", "doctor")
TICKET = "---\nid: {id}\ntype: task\nstatus: {status}\ndeps: []\nwbs_id: W9-01\n---\n# A ticket\n"


def _git(root, *args):
    subprocess.run(["git", "-C", str(root), "-c", "user.name=t", "-c", "user.email=t@example.invalid", *args],
                   check=True, capture_output=True)


@pytest.fixture
def project(tmp_path, monkeypatch):
    """A git repository with one ticket in progress, committed, and its store loaded."""
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    root = tmp_path / "project"
    (root / ".tickets").mkdir(parents=True)
    (root / ".tickets" / "TST-u001.md").write_text(TICKET.format(id="TST-u001", status="in_progress"), encoding="utf-8")
    (root / ".gitignore").write_text(".gov-runtime/\n", encoding="utf-8")
    _git(root, "init", "-q", "-b", "main")
    _git(root, "add", "-A")
    _git(root, "commit", "-q", "-m", "fixture")
    store.load(root)
    return root


def _unread(part):
    assert part["read"] is False and part["reason"].strip()
    return part["reason"]


def test_a_reader_that_fails_is_a_part_not_read_with_its_reason():
    def read():
        raise PermissionError(13, "Permission denied")

    assert "Permission denied" in _unread(command._part(read))


def test_what_was_not_read_is_found_at_any_depth_with_its_place():
    answer = {"tickets": {"ready": [], "blocked": [{"id": "T", "read": False, "reason": "why"}]}, "pause": {"paused": True}}
    assert command._unread_in(answer) == ["tickets.blocked.0: why"]


def test_the_store_answers_only_for_a_history_that_holds_head(project):
    assert command._store_fault(project) is None
    _git(project, "commit", "-q", "--allow-empty", "-m", "after the load")
    assert "older than HEAD" in command._store_fault(project)
    (project / store.STORE_REL).unlink()
    assert "was not read" in command._store_fault(project)


def test_without_the_store_ready_blocked_and_packages_are_not_read_and_the_claimed_tickets_are(project):
    fault = "the record store was not read"
    tickets = command._tickets(project, fault)
    assert _unread(tickets["ready"]) == _unread(tickets["blocked"]) == _unread(command._packages(project, fault)) == fault
    assert tickets["claimed"] == [{"id": "TST-u001", "holder": None}]


def test_a_ticket_folder_that_cannot_be_listed_is_not_no_ticket(tmp_path):
    (tmp_path / ".tickets").write_text("a file where the folder should be\n", encoding="utf-8")
    _unread(command._part(command._tickets, tmp_path, None))


def test_a_ticket_file_that_cannot_be_read_is_listed_as_not_read(project):
    (project / ".tickets" / "TST-u002.md").write_text("---\nid: [unclosed\n---\n", encoding="utf-8")
    blocked = {entry["id"]: entry for entry in command._tickets(project, None)["blocked"]}
    assert "TST-u002" in _unread(blocked["TST-u002"]) and blocked["TST-u001"]["reasons"]


def test_the_share_is_never_a_figure(project):
    share = command._share(project, command._tickets(project, None))
    assert share["share"] == "not measured" and [entry["share"] for entry in share["tickets"]] == ["not measured"]
    assert "not measured" in share["tickets"][0]["reason"]
    _unread(command._part(command._share, project, {"read": False, "reason": "no folder"}))


def test_a_flag_that_cannot_be_read_is_paused_and_who_paused_is_not_read(project):
    assert command._pause(project) == {"paused": False, "flag": "absent", "mirror": False}
    (project / FREEZE_FLAG).mkdir(parents=True)
    part = command._pause(project)
    assert part["paused"] is True and _unread(part["by"]) and _unread(part["since"])
    (project / FREEZE_FLAG).rmdir()
    (project / FREEZE_FLAG).write_text("FROZEN owner 2026-10-08T00:00:00Z\n", encoding="utf-8")
    assert command._pause(project) == {"paused": True, "flag": "frozen", "mirror": False, "by": "owner",
                                       "since": "2026-10-08T00:00:00Z"}


def test_a_device_at_the_flags_path_is_a_flag_not_read_and_only_the_mirror_can_say_paused(project):
    from gov.guard.decide import _mirror_path

    flag = project / FREEZE_FLAG
    flag.parent.mkdir(exist_ok=True)
    flag.write_bytes(b"")
    assert command._pause(project) == {"paused": False, "flag": "unmarked", "mirror": False}  # an empty file was read
    flag.unlink()
    os.symlink(os.devnull, flag)
    part = command._pause(project)
    assert FREEZE_FLAG in _unread(part) and "paused" not in part and part["mirror"] is False
    mirror = _mirror_path(str(project))
    assert Path(os.environ["HOME"]) in mirror.parents, "the mirror is not under the temporary HOME"
    mirror.parent.mkdir(parents=True)
    mirror.write_text("FROZEN owner 2026-10-08T00:00:00Z\n", encoding="utf-8")
    part = command._pause(project)
    assert part["paused"] is True and part["mirror"] is True and _unread(part["flag"]) and "read" not in part


@pytest.mark.parametrize("text", ("---\nid: [unclosed\n---\n", "---\nid: DP-1\ntype: decision-package\n---\n"))
def test_a_file_the_load_could_not_take_is_listed_with_the_packages_as_not_read(project, text):
    assert command._packages(project, None) == []
    (project / "DP-1.md").write_text(text, encoding="utf-8")
    (project / "DP-2.md").write_text("---\nid: DP-2\ntype: decision-package\nstatus: PROPOSED\n---\n", encoding="utf-8")
    _git(project, "add", "-A")
    _git(project, "commit", "-q", "-m", "a record that does not load")
    assert [entry["path"] for entry in store.load(project)["invalid"]] == ["DP-1.md"]
    listed, unread = command._packages(project, None)
    assert listed == {"id": "DP-2", "tickets": []} and unread["name"] == "DP-1.md" and "DP-1.md" in _unread(unread)


@pytest.mark.parametrize("table", ("records", "edges"))
def test_a_store_without_its_records_or_edges_does_not_answer(project, table):
    connection = sqlite3.connect(project / store.STORE_REL)
    connection.execute(f"DROP TABLE {table}")
    connection.commit()
    connection.close()
    assert table in command._store_fault(project)
    tickets = command._tickets(project, command._store_fault(project))
    assert table in _unread(tickets["ready"]) and table in _unread(tickets["blocked"])


def test_a_doctor_that_gives_no_verdict_or_no_state_is_not_read(project, monkeypatch):
    from gov.doctor import command as doctor

    monkeypatch.setattr(doctor, "run", lambda *args: (_ for _ in ()).throw(GovError("X", "doctor broke", {})))
    assert "doctor broke" in _unread(command._part(command._doctor, project, ARGS, {}))
    monkeypatch.setattr(doctor, "run", lambda *args: {"healthy": True, "tools": {"reason": "no state"}})
    _unread(command._part(command._doctor, project, ARGS, {}))
    monkeypatch.setattr(doctor, "run", lambda *args: (_ for _ in ()).throw(
        GovError("DOCTOR_UNHEALTHY", "failed", {"healthy": False, "path_map": {"status": "fail"}})))
    assert command._doctor(project, ARGS, {}) == {"healthy": False, "parts": {"path_map": "fail"}}


def test_a_status_with_a_part_not_read_names_every_such_place(project, monkeypatch):
    from gov.doctor import command as doctor

    monkeypatch.setattr(doctor, "run", lambda *args: {"healthy": True, "tools": {"status": "unmeasured"}})
    answer = command.run(project, ARGS, {})
    assert tuple(answer) == ("root", "config_files", *PARTS, "not_read") and answer["not_read"] == []
    assert answer["doctor"]["parts"] == {"tools": "unmeasured"}
    (project / store.STORE_REL).unlink()
    answer = command.run(project, ARGS, {})
    assert [place.split(":")[0] for place in answer["not_read"]] == ["tickets.ready", "tickets.blocked",
                                                                    "decision_packages"]
    assert answer["pause"]["paused"] is False and not (project / ".gov-runtime" / "store.db").exists()
