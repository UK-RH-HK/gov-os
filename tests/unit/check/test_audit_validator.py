"""Unit tests for gov.check.audit_validator."""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from unittest import mock

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src"))

from gov.check.audit_validator import validate_file, _parse_table_rows


@pytest.fixture
def git_repo(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    env = {
        "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
        "HOME": str(tmp_path),
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_CONFIG_GLOBAL": os.devnull,
    }
    subprocess.run(["git", "-C", str(repo), "init", "-q", "-b", "main"], env=env, check=True)
    subprocess.run(["git", "-C", str(repo), "config", "user.email", "t@t"], env=env, check=True)
    subprocess.run(["git", "-C", str(repo), "config", "user.name", "T"], env=env, check=True)
    (repo / "README.md").write_text("# Test\n")
    (repo / "src").mkdir()
    (repo / "src" / "main.py").write_text("print(1)\n")
    subprocess.run(["git", "-C", str(repo), "add", "."], env=env, check=True)
    subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m", "init"], env=env, check=True)
    commit = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "HEAD"],
        capture_output=True, text=True, env=env,
    ).stdout.strip()
    return repo, commit


def _report(commit, rows_text):
    return (
        f"---\nmilestone: W1\ncommit: {commit}\npack_sha256: {'ab' * 32}\n---\n\n"
        f"| item | class | evidence |\n|---|---|---|\n{rows_text}\n"
    )


class TestValidateFile:

    def test_valid_report(self, git_repo):
        repo, commit = git_repo
        p = repo / "audit.md"
        p.write_text(_report(commit, "| CAP-1 | OK | README.md |"))
        assert validate_file(p, str(repo)) == []

    def test_missing_frontmatter(self, git_repo):
        repo, commit = git_repo
        p = repo / "audit.md"
        p.write_text("# No frontmatter\n")
        findings = validate_file(p, str(repo))
        assert any(f["code"] == "AUDIT_NO_FRONTMATTER" for f in findings)

    def test_bad_commit(self, git_repo):
        repo, _ = git_repo
        p = repo / "audit.md"
        p.write_text(_report("deadbeef" * 5, "| CAP-1 | OK | README.md |"))
        findings = validate_file(p, str(repo))
        assert any(f["code"] == "AUDIT_BAD_COMMIT" for f in findings)

    def test_invalid_class(self, git_repo):
        repo, commit = git_repo
        p = repo / "audit.md"
        p.write_text(_report(commit, "| CAP-1 | BOGUS | - |"))
        findings = validate_file(p, str(repo))
        assert any(f["code"] == "AUDIT_INVALID_CLASS" for f in findings)

    def test_ok_no_evidence(self, git_repo):
        repo, commit = git_repo
        p = repo / "audit.md"
        p.write_text(_report(commit, "| CAP-1 | OK | - |"))
        findings = validate_file(p, str(repo))
        assert any(f["code"] == "AUDIT_OK_NO_EVIDENCE" for f in findings)

    def test_unreadable_returns_none(self, git_repo):
        repo, _ = git_repo
        p = repo / "nope.md"
        assert validate_file(p, str(repo)) is None


class TestParseTableRows:

    def test_skips_header_and_separator(self):
        body = "| item | class | evidence |\n|---|---|---|\n| A | OK | x |\n"
        rows = _parse_table_rows(body)
        assert len(rows) == 1
        assert "A" in rows[0]
