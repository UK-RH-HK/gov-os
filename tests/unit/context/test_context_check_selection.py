"""Unit tests for the tickets the context-reproducibility check selects (DEC-628)."""

from __future__ import annotations

import sqlite3

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
