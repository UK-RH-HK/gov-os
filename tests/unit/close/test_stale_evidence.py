"""Unit tests for governance-file-check logic in gov close (A7)."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from gov.close.command import _check_governance, _GOVERNANCE_PREFIXES


def _commit(sha: str, paths: list[str]) -> dict:
    return {"sha": sha, "trailers": {}, "paths": paths}


class TestCheckGovernance:
    def test_no_governance_files_returns_none(self):
        commits = [_commit("aaa", ["src/app.py"]),
                   _commit("bbb", ["src/util.py"])]
        assert _check_governance(Path("/fake"), commits) is None

    def test_governance_prefixes_is_tuple(self):
        assert isinstance(_GOVERNANCE_PREFIXES, tuple)
        assert len(_GOVERNANCE_PREFIXES) > 1

    @patch("gov.check.runner.run_checks")
    def test_governance_change_triggers_run_checks(self, mock_run):
        mock_run.return_value = ({"checks": []}, False)
        prefix = _GOVERNANCE_PREFIXES[0]
        commits = [_commit("aaa", [f"{prefix}foo.yaml"])]
        result = _check_governance(Path("/fake"), commits)
        mock_run.assert_called_once()
        assert result == {"checks": []}

    @patch("gov.check.runner.run_checks")
    def test_checks_prefix_change_triggers(self, mock_run):
        mock_run.return_value = ({"checks": []}, False)
        commits = [_commit("aaa", ["template/governance/kernel/checks/x.yaml"])]
        result = _check_governance(Path("/fake"), commits)
        mock_run.assert_called_once()
        assert result is not None

    @patch("gov.check.runner.run_checks")
    def test_schema_prefix_change_triggers(self, mock_run):
        mock_run.return_value = ({"checks": []}, False)
        commits = [_commit("aaa", ["template/governance/kernel/schemas/s.yaml"])]
        result = _check_governance(Path("/fake"), commits)
        mock_run.assert_called_once()

    @patch("gov.check.runner.run_checks")
    def test_project_prefix_change_triggers(self, mock_run):
        mock_run.return_value = ({"checks": []}, False)
        commits = [_commit("aaa", ["governance/project/config.yaml"])]
        result = _check_governance(Path("/fake"), commits)
        mock_run.assert_called_once()

    @patch("gov.check.runner.run_checks")
    def test_hard_block_red_check_raises(self, mock_run, tmp_path):
        check_file = tmp_path / "template" / "governance" / "kernel" / "checks" / "bad.yaml"
        check_file.parent.mkdir(parents=True)
        check_file.write_text("id: product-traceability\n", encoding="utf-8")
        mock_run.return_value = (
            {"checks": [{"id": "product-traceability",
                         "severity": "hard-block", "status": "RED"}]},
            True,
        )
        commits = [_commit("aaa", [
            "template/governance/kernel/checks/bad.yaml"])]
        from gov.cli.errors import GovError
        with pytest.raises(GovError) as exc:
            _check_governance(tmp_path, commits)
        assert exc.value.code == "CHECK_FAILED"
        assert "product-traceability" in str(exc.value.details)

    @patch("gov.check.runner.run_checks")
    def test_red_status_check_raises(self, mock_run, tmp_path):
        check_file = tmp_path / "template" / "governance" / "kernel" / "checks" / "c.yaml"
        check_file.parent.mkdir(parents=True)
        check_file.write_text("id: my-check\n", encoding="utf-8")
        mock_run.return_value = (
            {"checks": [{"id": "my-check", "severity": "warning",
                         "status": "RED"}]},
            False,
        )
        commits = [_commit("aaa", [
            "template/governance/kernel/checks/c.yaml"])]
        from gov.cli.errors import GovError
        with pytest.raises(GovError) as exc:
            _check_governance(tmp_path, commits)
        assert exc.value.code == "CHECK_FAILED"

    @patch("gov.check.runner.run_checks")
    def test_green_non_hardblock_check_passes(self, mock_run, tmp_path):
        check_file = tmp_path / "template" / "governance" / "kernel" / "checks" / "ok.yaml"
        check_file.parent.mkdir(parents=True)
        check_file.write_text("id: my-check\n", encoding="utf-8")
        mock_run.return_value = (
            {"checks": [{"id": "my-check", "severity": "warning",
                         "status": "GREEN"}]},
            False,
        )
        commits = [_commit("aaa", [
            "template/governance/kernel/checks/ok.yaml"])]
        result = _check_governance(tmp_path, commits)
        assert result is not None

    @patch("gov.check.runner.run_checks")
    def test_unrelated_check_red_does_not_block(self, mock_run, tmp_path):
        check_file = tmp_path / "template" / "governance" / "kernel" / "checks" / "mine.yaml"
        check_file.parent.mkdir(parents=True)
        check_file.write_text("id: mine\n", encoding="utf-8")
        mock_run.return_value = (
            {"checks": [{"id": "other-check", "severity": "hard-block",
                         "status": "RED"},
                        {"id": "mine", "severity": "warning",
                         "status": "GREEN"}]},
            True,
        )
        commits = [_commit("aaa", [
            "template/governance/kernel/checks/mine.yaml"])]
        result = _check_governance(tmp_path, commits)
        assert result is not None

    def test_non_governance_template_path_ignored(self):
        commits = [_commit("aaa", ["template/other/file.yaml"]),
                   _commit("bbb", ["template/other/file.yaml"])]
        assert _check_governance(Path("/fake"), commits) is None
