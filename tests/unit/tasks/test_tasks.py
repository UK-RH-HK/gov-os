"""Builder tests for the claim lock and the READY rule (W1-09).

Regression evidence only (DEC-136). They cover what the acceptance tests leave
to the builder: the READY rule does not fail open (no store, a ticket file that
cannot be read), a lock file whose holder is still being written is waited for,
and a ticket id with a path separator releases nothing.
"""
from __future__ import annotations

import sys
import threading
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov import tasks  # noqa: E402
from gov.cli.errors import GovError  # noqa: E402

TICKET = "---\nid: {id}\nstatus: open\ndeps: []\n---\n# A ticket\n"


def _project(tmp_path, *tickets):
    for ticket in tickets:
        path = tmp_path / ".tickets" / f"{ticket}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(TICKET.format(id=ticket), encoding="utf-8")
        (tmp_path / "tests" / "acceptance" / ticket).mkdir(parents=True)
    return tmp_path


def test_no_ticket_is_ready_while_the_store_cannot_be_read(tmp_path):
    root = _project(tmp_path, "TST-a001")
    assert tasks.ready(root) == []
    assert list(tasks.blocked(root)) == ["TST-a001"]


def test_a_ticket_file_that_cannot_be_read_is_not_ready(tmp_path, monkeypatch):
    root = _project(tmp_path, "TST-a001", "TST-a002")
    (root / ".tickets" / "TST-a002.md").write_text("---\nid: [\n---\n", encoding="utf-8")
    monkeypatch.setattr("gov.records.records", lambda root, type=None, status=None: [])
    monkeypatch.setattr("gov.records.edges", lambda root, type=None: [])
    assert tasks.ready(root) == ["TST-a001"]
    assert list(tasks.blocked(root)) == ["TST-a002"]


def test_a_holder_still_being_written_is_waited_for(tmp_path):
    root = _project(tmp_path, "TST-a001")
    lock = root / ".tickets" / ".claims" / "TST-a001"
    lock.parent.mkdir()
    lock.write_bytes(b"")
    timer = threading.Timer(0.2, lock.write_text, ["engineer:winner\n"])
    timer.start()
    try:
        with pytest.raises(GovError) as raised:
            tasks.claim(root, "TST-a001", "engineer:loser")
    finally:
        timer.join()
    assert raised.value.code == "CLAIM_HELD"
    assert raised.value.details == {"ticket": "TST-a001", "holder": "engineer:winner"}


def test_a_ticket_id_with_a_path_separator_releases_nothing(tmp_path):
    root = _project(tmp_path, "TST-a001")
    (root / "outside").write_text("engineer:session-1\n", encoding="utf-8")
    assert tasks.holder(root, "../../outside") is None
    with pytest.raises(GovError) as raised:
        tasks.release(root, "../../outside", "engineer:session-1")
    assert raised.value.code == "CLAIM_NOT_HELD"
    assert (root / "outside").is_file()
