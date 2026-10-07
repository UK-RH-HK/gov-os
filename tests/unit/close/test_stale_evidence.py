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
    def test_hard_block_red_changed_check_raises(self, mock_run):
        mock_run.return_value = (
            {"checks": [{"id": "bad-check",
                         "severity": "hard-block", "status": "RED"}]},
            True,
        )
        commits = [_commit("aaa", [
            "template/governance/kernel/checks/bad-check.yaml"])]
        from gov.cli.errors import GovError
        with pytest.raises(GovError) as exc:
            _check_governance(Path("/fake"), commits)
        assert exc.value.code == "CHECK_FAILED"

    @patch("gov.check.runner.run_checks")
    def test_warning_red_check_does_not_block(self, mock_run):
        mock_run.return_value = (
            {"checks": [{"id": "warn-check", "severity": "warning",
                         "status": "RED"}]},
            False,
        )
        commits = [_commit("aaa", [
            "template/governance/kernel/checks/warn-check.yaml"])]
        result = _check_governance(Path("/fake"), commits)
        assert result is not None

    @patch("gov.check.runner.run_checks")
    def test_green_hard_block_check_passes(self, mock_run):
        mock_run.return_value = (
            {"checks": [{"id": "ok-check", "severity": "hard-block",
                         "status": "GREEN"}]},
            False,
        )
        commits = [_commit("aaa", [
            "template/governance/kernel/checks/ok-check.yaml"])]
        result = _check_governance(Path("/fake"), commits)
        assert result is not None

    @patch("gov.check.runner.run_checks")
    def test_unrelated_check_red_does_not_block(self, mock_run):
        mock_run.return_value = (
            {"checks": [{"id": "other-check", "severity": "hard-block",
                         "status": "RED"},
                        {"id": "mine", "severity": "warning",
                         "status": "GREEN"}]},
            True,
        )
        commits = [_commit("aaa", [
            "template/governance/kernel/checks/mine.yaml"])]
        result = _check_governance(Path("/fake"), commits)
        assert result is not None

    def test_check_touched_in_multiple_commits_raises_stale(self):
        commits = [
            _commit("aaa", ["template/governance/kernel/checks/x.yaml"]),
            _commit("bbb", ["template/governance/kernel/checks/x.yaml"]),
        ]
        from gov.cli.errors import GovError
        with pytest.raises(GovError) as exc:
            _check_governance(Path("/fake"), commits)
        assert exc.value.code == "STALE_EVIDENCE"

    def test_different_checks_in_different_commits_no_stale(self):
        from unittest.mock import patch as _p
        with _p("gov.check.runner.run_checks",
                return_value=({"checks": []}, False)):
            commits = [
                _commit("aaa", ["template/governance/kernel/checks/a.yaml"]),
                _commit("bbb", ["template/governance/kernel/checks/b.yaml"]),
            ]
            result = _check_governance(Path("/fake"), commits)
            assert result is not None

    def test_non_governance_template_path_ignored(self):
        commits = [_commit("aaa", ["template/other/file.yaml"]),
                   _commit("bbb", ["template/other/file.yaml"])]
        assert _check_governance(Path("/fake"), commits) is None
