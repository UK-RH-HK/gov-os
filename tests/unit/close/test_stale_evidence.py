"""Unit tests for stale evidence detection in gov close."""
from __future__ import annotations

import pytest

from gov.close.command import _check_stale_evidence, _GOV_CHECKS_PREFIX


def _commit(sha: str, paths: list[str]) -> dict:
    return {"sha": sha, "trailers": {}, "paths": paths}


class TestStaleEvidence:
    def test_no_governance_files_passes(self):
        commits = [_commit("aaa", ["src/app.py"]),
                   _commit("bbb", ["src/util.py"])]
        _check_stale_evidence(None, commits)

    def test_single_commit_with_governance_passes(self):
        commits = [_commit("aaa", [f"{_GOV_CHECKS_PREFIX}check.yaml"])]
        _check_stale_evidence(None, commits)

    def test_same_governance_file_in_two_commits_raises(self):
        from gov.cli.errors import GovError

        gov_path = f"{_GOV_CHECKS_PREFIX}schema.yaml"
        commits = [_commit("aaa", [gov_path, "src/app.py"]),
                   _commit("bbb", [gov_path])]
        with pytest.raises(GovError) as exc:
            _check_stale_evidence(None, commits)
        assert exc.value.code == "STALE_EVIDENCE"

    def test_different_governance_files_in_two_commits_passes(self):
        commits = [_commit("aaa", [f"{_GOV_CHECKS_PREFIX}check_a.yaml"]),
                   _commit("bbb", [f"{_GOV_CHECKS_PREFIX}check_b.yaml"])]
        _check_stale_evidence(None, commits)

    def test_non_governance_template_paths_ignored(self):
        commits = [_commit("aaa", ["template/other/file.yaml"]),
                   _commit("bbb", ["template/other/file.yaml"])]
        _check_stale_evidence(None, commits)
