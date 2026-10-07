"""Unit tests for YAML-safe ticket closing."""
from __future__ import annotations

from pathlib import Path

import pytest
import yaml


@pytest.fixture
def root(tmp_path):
    r = tmp_path / "project"
    tickets = r / ".tickets"
    tickets.mkdir(parents=True)
    return r


class TestSetTicketClosed:
    def test_sets_status_to_closed(self, root):
        from gov.close.command import _set_ticket_closed

        path = root / ".tickets" / "T-0001.md"
        path.write_text("---\nid: T-0001\nstatus: open\n---\n\n# Title\n",
                        encoding="utf-8")
        _set_ticket_closed(root, "T-0001")
        text = path.read_text(encoding="utf-8")
        parts = text.split("---", 2)
        front = yaml.safe_load(parts[1])
        assert front["status"] == "closed"

    def test_preserves_other_fields(self, root):
        from gov.close.command import _set_ticket_closed

        path = root / ".tickets" / "T-0001.md"
        path.write_text(
            "---\nid: T-0001\nstatus: open\nwbs_id: W1-test\nprofile: FULL\n---\n\n# Title\n",
            encoding="utf-8")
        _set_ticket_closed(root, "T-0001")
        text = path.read_text(encoding="utf-8")
        parts = text.split("---", 2)
        front = yaml.safe_load(parts[1])
        assert front["id"] == "T-0001"
        assert front["wbs_id"] == "W1-test"
        assert front["profile"] == "FULL"
        assert front["status"] == "closed"

    def test_preserves_body(self, root):
        from gov.close.command import _set_ticket_closed

        path = root / ".tickets" / "T-0001.md"
        path.write_text(
            "---\nid: T-0001\nstatus: open\n---\n\n# Body content\n",
            encoding="utf-8")
        _set_ticket_closed(root, "T-0001")
        text = path.read_text(encoding="utf-8")
        assert "Body content" in text

    def test_missing_file_is_noop(self, root):
        from gov.close.command import _set_ticket_closed
        _set_ticket_closed(root, "T-nonexistent")
