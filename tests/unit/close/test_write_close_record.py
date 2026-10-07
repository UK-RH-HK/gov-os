"""Unit tests for close record writing in gov close."""
from __future__ import annotations

from pathlib import Path

import pytest
import yaml


class TestWriteCloseRecord:
    def test_creates_close_record_file(self, tmp_path):
        from gov.close.command import _write_close_record

        rel = _write_close_record(
            tmp_path, "T-0001", "abc123", [], ["CAP-01"],
            ["DEC-1"], ["tests/acceptance/W1-test/test_foo.py"],
            [], {"path": "docs/checkpoints/T-0001/CP-T-0001-0001.md"},
            {"passed": 5, "failed": 0}, None, "deadbeef", ["src/app.py"],
        )
        assert rel == "docs/close/T-0001/CL-T-0001.md"
        path = tmp_path / rel
        assert path.is_file()
        text = path.read_text(encoding="utf-8")
        assert text.startswith("---\n")
        parts = text.split("---", 2)
        front = yaml.safe_load(parts[1])
        assert front["type"] == "close"
        assert front["task"] == "T-0001"
        assert front["packet_hash"] == "abc123"

    def test_includes_governance_checks_when_present(self, tmp_path):
        from gov.close.command import _write_close_record

        gov_result = {"checks": [{"id": "x", "status": "GREEN"}]}
        _write_close_record(
            tmp_path, "T-0002", "hash", [], [],
            [], [], [], {"path": ""}, {"passed": 1, "failed": 0},
            gov_result, "aaa", [],
        )
        path = tmp_path / "docs" / "close" / "T-0002" / "CL-T-0002.md"
        text = path.read_text(encoding="utf-8")
        parts = text.split("---", 2)
        front = yaml.safe_load(parts[1])
        assert "governance_checks" in front
        assert front["check_commit"] == "aaa"

    def test_no_governance_checks_when_none(self, tmp_path):
        from gov.close.command import _write_close_record

        _write_close_record(
            tmp_path, "T-0003", "hash", [], [],
            [], [], [], {"path": ""}, {"passed": 1, "failed": 0},
            None, "aaa", [],
        )
        path = tmp_path / "docs" / "close" / "T-0003" / "CL-T-0003.md"
        text = path.read_text(encoding="utf-8")
        parts = text.split("---", 2)
        front = yaml.safe_load(parts[1])
        assert "governance_checks" not in front

    def test_includes_skill_versions(self, tmp_path):
        from gov.close.command import _write_close_record

        skills = [{"name": "discovery", "version": "1.0.0"}]
        _write_close_record(
            tmp_path, "T-0004", "hash", [], [],
            [], [], skills, {"path": ""}, {"passed": 1, "failed": 0},
            None, "aaa", [],
        )
        path = tmp_path / "docs" / "close" / "T-0004" / "CL-T-0004.md"
        text = path.read_text(encoding="utf-8")
        parts = text.split("---", 2)
        front = yaml.safe_load(parts[1])
        assert front["skill_versions"] == skills

    def test_oserror_propagates(self, tmp_path):
        from gov.close.command import _write_close_record

        blocker = tmp_path / "docs" / "close" / "T-0005"
        blocker.parent.mkdir(parents=True, exist_ok=True)
        blocker.write_text("file blocking directory", encoding="utf-8")
        with pytest.raises(OSError):
            _write_close_record(
                tmp_path, "T-0005", "hash", [], [],
                [], [], [], {"path": ""}, {"passed": 0, "failed": 0},
                None, "aaa", [],
            )
