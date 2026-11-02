"""Unit tests for the tickets the context-reproducibility check selects (DEC-628)."""

from __future__ import annotations

import sqlite3
import subprocess

import pytest

import gov.context
import gov.store
from gov.context import context_check


@pytest.fixture
def project(tmp_path, monkeypatch):
    """A project root whose store holds the records given: ``store(rows)`` with rows ``(path, id, type)``."""
    def store(rows):
        def connect(root):
            conn = sqlite3.connect(":memory:")
            conn.execute("CREATE TABLE records (path TEXT, id TEXT, type TEXT, status TEXT)")
            conn.executemany("INSERT INTO records VALUES (?, ?, ?, 'open')", rows)
            return conn
        monkeypatch.setattr(gov.store, "connect", connect)
        monkeypatch.setattr(context_check, "stale_store", lambda root: None)  # the store is HEAD's (W2-04)
        for path, _, _ in rows:
            (tmp_path / path).parent.mkdir(parents=True, exist_ok=True)
            (tmp_path / path).write_text("---\n---\n", encoding="utf-8")
        return tmp_path
    monkeypatch.chdir(tmp_path)
    return store


TEMPLATE = ("governance/kernel/templates/ticket.md", "PROJ-0000", "task")


def test_only_the_records_of_the_ticket_folder_are_selected_whatever_their_type(project):
    root = project([TEMPLATE, (".tickets/PROJ-aaaa.md", "PROJ-aaaa", "task"),
                    (".tickets/PROJ-bbbb.md", "PROJ-bbbb", "story"), ("docs/PROJ-eeee.md", "PROJ-eeee", "ticket")])
    assert context_check.project_tickets(root) == (["PROJ-aaaa", "PROJ-bbbb"], [])


def test_a_file_of_the_ticket_folder_the_store_does_not_hold_is_returned_as_unheld(project):
    root = project([(".tickets/PROJ-aaaa.md", "PROJ-aaaa", "task")])
    (root / ".tickets" / "PROJ-dddd.md").write_text("no frontmatter", encoding="utf-8")
    assert context_check.project_tickets(root) == (["PROJ-aaaa"], [".tickets/PROJ-dddd.md"])


def test_the_template_ticket_alone_reads_unmeasured(project, capsys):
    project([TEMPLATE])
    assert context_check.main() == 1
    out = capsys.readouterr().out
    assert "unmeasured" in out and "PROJ-0000" not in out


def test_an_unheld_ticket_file_is_named_and_the_check_is_not_green(project, monkeypatch, capsys):
    root = project([TEMPLATE, (".tickets/PROJ-aaaa.md", "PROJ-aaaa", "task")])
    (root / ".tickets" / "PROJ-dddd.md").write_text("no frontmatter", encoding="utf-8")
    monkeypatch.setattr(gov.context, "context", lambda root, ticket: {"hash": "h"})
    assert context_check.main() == 1
    out = capsys.readouterr().out
    assert "PROJ-dddd" in out and "PROJ-aaaa" not in out and "PROJ-0000" not in out


def test_sound_project_tickets_beside_the_template_are_green(project, monkeypatch):
    project([TEMPLATE, (".tickets/PROJ-aaaa.md", "PROJ-aaaa", "task")])
    monkeypatch.setattr(gov.context, "context", lambda root, ticket: {"hash": "h"})
    assert context_check.main() == 0


def test_a_stale_store_is_unmeasured_by_name(project, monkeypatch, capsys):
    project([(".tickets/PROJ-aaaa.md", "PROJ-aaaa", "task")])
    monkeypatch.setattr(context_check, "stale_store", lambda root: "the store was built from aaaa, not from HEAD bbbb")
    monkeypatch.setattr(gov.context, "context", lambda root, ticket: {"hash": "h"})
    assert context_check.main() == 1
    out = capsys.readouterr().out
    assert "unmeasured" in out and "stale store" in out and "green" not in out


def test_a_readme_alone_in_the_ticket_folder_is_named_and_said_so(project, capsys):
    root = project([TEMPLATE])
    (root / ".tickets").mkdir()
    (root / ".tickets" / "README.md").write_text("# The tickets\n", encoding="utf-8")
    assert context_check.main() == 1
    out = capsys.readouterr().out
    assert ".tickets/README.md" in out and "every ticket's context computation failed" not in out


def test_a_ticket_file_not_named_md_is_named(project, monkeypatch, capsys):
    root = project([(".tickets/PROJ-aaaa.md", "PROJ-aaaa", "task")])
    (root / ".tickets" / "PROJ-cccc.MD").write_text("---\nid: PROJ-cccc\n---\n", encoding="utf-8")
    monkeypatch.setattr(gov.context, "context", lambda root, ticket: {"hash": "h"})
    assert context_check.main() == 1
    out = capsys.readouterr().out
    assert ".tickets/PROJ-cccc.MD" in out and "does not end in .md" in out


def test_two_ticket_files_with_one_id_are_a_duplicate_id(project, monkeypatch, capsys):
    root = project([(".tickets/PROJ-aaaa.md", "PROJ-aaaa", "task")])
    (root / ".tickets" / "PROJ-aaaa.md").write_text("---\nid: PROJ-aaaa\n---\n", encoding="utf-8")
    (root / ".tickets" / "sub").mkdir()
    (root / ".tickets" / "sub" / "PROJ-aaaa.md").write_text("---\nid: PROJ-aaaa\n---\n", encoding="utf-8")
    monkeypatch.setattr(gov.context, "context", lambda root, ticket: {"hash": "h"})
    assert context_check.main() == 1
    out = capsys.readouterr().out
    assert "duplicate id" in out and "PROJ-aaaa" in out and ".tickets/sub/PROJ-aaaa.md" in out


def _refusing(refused):
    """A context that refuses over the ceiling for the tickets in ``refused`` and builds a packet for the others."""
    from gov.cli.errors import GovError

    def context(root, ticket):
        if ticket in refused:
            raise GovError("CONTEXT_OVER_CEILING", "over", {"ticket": ticket, "limit": 6000, "mandatory_tokens": 7000})
        return {"hash": "h"}
    return context


def test_the_same_refusal_twice_beside_a_packet_is_reproduced_named_and_green(project, monkeypatch, capsys):
    project([(".tickets/PROJ-aaaa.md", "PROJ-aaaa", "task"), (".tickets/PROJ-bbbb.md", "PROJ-bbbb", "task")])
    monkeypatch.setattr(gov.context, "context", _refusing({"PROJ-aaaa"}))
    assert context_check.main() == 0
    out = capsys.readouterr().out
    assert "REFUSED: PROJ-aaaa" in out and "green (1 packet(s) built twice alike, 1 refused" in out
    assert "unmeasured" not in out


@pytest.mark.parametrize("tickets", [["PROJ-aaaa"], ["PROJ-aaaa", "PROJ-bbbb"]])
def test_every_ticket_refused_is_unmeasured_and_never_green(project, monkeypatch, capsys, tickets):
    # DEC-1025 item 2: no packet was built twice, so none was compared
    project([(f".tickets/{rid}.md", rid, "task") for rid in tickets])
    monkeypatch.setattr(gov.context, "context", _refusing(set(tickets)))
    assert context_check.main() == 1
    lines = capsys.readouterr().out.splitlines()
    assert [line for line in lines if line.startswith("REFUSED: ")] == [f"REFUSED: {rid}: 7000 tokens of its own "
                                                                       f"text and mandatory inputs, over the ceiling "
                                                                       f"of 6000" for rid in tickets]
    unmeasured = [line for line in lines if line.startswith("unmeasured:")]
    assert len(unmeasured) == 1 and "no packet was built" in unmeasured[0]
    assert not any("green" in line for line in lines)


def test_every_computed_ticket_refused_beside_an_error_is_unmeasured_and_red(project, monkeypatch, capsys):
    from gov.cli.errors import GovError
    project([(".tickets/PROJ-aaaa.md", "PROJ-aaaa", "task"), (".tickets/PROJ-bbbb.md", "PROJ-bbbb", "task")])
    refuse = _refusing({"PROJ-aaaa"})

    def context(root, ticket):
        if ticket == "PROJ-bbbb":
            raise GovError("BLOCKED", "a mandatory input is missing", {"ticket": ticket})
        return refuse(root, ticket)
    monkeypatch.setattr(gov.context, "context", context)
    assert context_check.main() == 1
    out = capsys.readouterr().out
    assert "REFUSED: PROJ-aaaa" in out and "ERROR: PROJ-bbbb" in out and "unmeasured: no packet was built" in out
    assert "green" not in out


def test_another_error_keeps_the_check_red(project, monkeypatch):
    from gov.cli.errors import GovError
    project([(".tickets/PROJ-aaaa.md", "PROJ-aaaa", "task")])

    def blocked(root, ticket):
        raise GovError("BLOCKED", "a mandatory input is missing", {"ticket": ticket})
    monkeypatch.setattr(gov.context, "context", blocked)
    assert context_check.main() == 1


def test_a_store_from_another_commit_is_stale(tmp_path):
    from test_bounded import _ENV, _commit
    from gov.store import load
    subprocess.run(["git", "-C", str(tmp_path), "init", "-q", "-b", "main"], check=True, capture_output=True, env=_ENV)
    _commit(tmp_path, {".gitignore": ".gov-runtime/\n", "a.md": "# A\n"})
    load(tmp_path)
    assert context_check.stale_store(tmp_path) is None
    _commit(tmp_path, {"b.md": "# B\n"})
    assert "not from HEAD" in context_check.stale_store(tmp_path)


def _repo(root, files):
    from test_bounded import _ENV, _commit
    root.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "-C", str(root), "init", "-q", "-b", "main"], check=True, capture_output=True, env=_ENV)
    _commit(root, files)
    return root


def test_head_is_read_in_the_root_whatever_git_directory_is_inherited(tmp_path, monkeypatch):
    """The commit is read through the store loader's pinned git call (AR-2): an inherited ``GIT_DIR`` naming
    another repository does not make the root's store stale, nor a stale one fresh."""
    from gov.store import load
    root = _repo(tmp_path / "root", {".gitignore": ".gov-runtime/\n", "a.md": "# A\n"})
    other = _repo(tmp_path / "other", {"z.md": "# Z\n"})
    load(root)
    monkeypatch.setenv("GIT_DIR", str(other / ".git"))
    monkeypatch.setenv("GIT_WORK_TREE", str(other))
    assert context_check.stale_store(root) is None
    monkeypatch.delenv("GIT_DIR")
    monkeypatch.delenv("GIT_WORK_TREE")
    from test_bounded import _commit
    _commit(root, {"b.md": "# B\n"})
    monkeypatch.setenv("GIT_DIR", str(other / ".git"))
    assert "not from HEAD" in context_check.stale_store(root)


def test_a_head_that_cannot_be_read_is_a_reason_and_the_check_is_not_green(tmp_path, monkeypatch, capsys):
    """A repository with no commit has no ``HEAD`` to read: the store is not taken as HEAD's (fail closed)."""
    from test_bounded import _ENV
    subprocess.run(["git", "-C", str(tmp_path), "init", "-q", "-b", "main"], check=True, capture_output=True, env=_ENV)
    assert context_check.stale_store(tmp_path) == "the commit HEAD cannot be read"
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(context_check, "project_tickets", lambda root: (["PROJ-aaaa"], []))
    monkeypatch.setattr(gov.context, "context", lambda root, ticket: {"hash": "h"})
    assert context_check.main() == 1
    out = capsys.readouterr().out
    assert "unmeasured: stale store: the commit HEAD cannot be read" in out and "green" not in out


def test_the_check_starts_no_git_of_its_own():
    """W2-05's rule (AR-2): git is started through a call the sweep names, never by this file."""
    from pathlib import Path
    text = Path(context_check.__file__).read_text(encoding="utf-8")
    assert "subprocess" not in text and '"git"' not in text and "'git'" not in text
