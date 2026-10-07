"""Unit tests for ticket closing via tk in gov close."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest


@pytest.fixture
def root(tmp_path):
    r = tmp_path / "project"
    tickets = r / ".tickets"
    tickets.mkdir(parents=True)
    tk_dir = r / "governance" / "kernel" / "bin"
    tk_dir.mkdir(parents=True)
    tk = tk_dir / "tk"
    tk.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    tk.chmod(0o755)
    return r


class TestCloseTicketViaTk:
    def test_calls_tk_close(self, root):
        from gov.close.command import _close_ticket_via_tk

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = type("R", (), {"returncode": 0, "stderr": ""})()
            _close_ticket_via_tk(root, "T-0001")
            args = mock_run.call_args[0][0]
            assert args[-2:] == ["close", "T-0001"]

    def test_missing_tk_raises(self, root):
        from gov.cli.errors import GovError
        from gov.close.command import _close_ticket_via_tk

        (root / "governance" / "kernel" / "bin" / "tk").unlink()
        with pytest.raises(GovError) as exc:
            _close_ticket_via_tk(root, "T-0001")
        assert exc.value.code == "TICKET_TOOL_ABSENT"

    def test_tk_failure_raises(self, root):
        from gov.cli.errors import GovError
        from gov.close.command import _close_ticket_via_tk

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = type(
                "R", (), {"returncode": 1, "stderr": "something failed"})()
            with pytest.raises(GovError) as exc:
                _close_ticket_via_tk(root, "T-0001")
            assert exc.value.code == "TICKET_TOOL_FAILED"
